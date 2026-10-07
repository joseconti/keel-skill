#!/usr/bin/env python3
"""Deterministic scheduler state for Keel parallel development.

This helper validates and records work. It never calls a model service, grants
permission, merges branches, pushes, installs software, or chooses product scope.
Projects copy it to ``scripts/keel-parallel`` when parallel development is on.
"""

from __future__ import annotations

import argparse
try:
    import fcntl
except ImportError:  # Windows: no tested local locking/process-group backend.
    fcntl = None
import hashlib
import json
import os
import signal
import re
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path, PurePosixPath

PLAN_SCHEMAS = {"keel.plan/1", "keel.plan/2", None}
RUN_SCHEMA = "keel.parallel-run/1"
ASSIGNMENT_SCHEMA = "keel.worker-assignment/1"
RESULT_SCHEMA = "keel.worker-result/1"
ACTIVE = {"claimed", "launching", "running", "stuck", "awaiting-result", "awaiting-review", "ready-to-integrate"}
TERMINAL = {"integrated", "blocked", "failed", "cancelled"}
AGGREGATE_PREFIXES = (
    "docs/PROGRESS.md",
    "docs/decisions.md",
    "docs/lessons-learned.md",
    "docs/issues.md",
    "docs/sprints/",
    "docs/.keel/plan.json",
    "docs/sessions.md",
    "docs/token-ledger.md",
    "docs/05-test-points.md",
    "docs/api/INDEX.md",
    "docs/continuation-prompt.md",
    "docs/03-technical-plan.md",
    "docs/threat-model.md",
    "docs/playground.md",
    ".git/",
)


class ParallelError(Exception):
    """A user-facing validation or state-transition failure."""


def read_json(path: str | Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ParallelError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ParallelError(f"JSON root must be an object: {path}")
    return value


def write_json_atomic(path: str | Path, value: dict, create_only: bool = False) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        if create_only:
            try:
                os.link(temporary, target)
            except FileExistsError as exc:
                raise ParallelError(f"run already exists: {target}") from exc
        else:
            os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def output(value: dict, code: int = 0) -> int:
    print(json.dumps(value, sort_keys=True))
    return code


def normalized_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or any(c in value for c in "*?["):
        raise ParallelError(f"invalid repository path: {value!r}")
    pure = PurePosixPath(value)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in value.rstrip("/").split("/")):
        raise ParallelError(f"path must be normalized and repository-relative: {value}")
    return pure.as_posix().rstrip("/") + ("/" if value.endswith("/") else "")


def path_contains(owner: str, path: str) -> bool:
    path = path.rstrip("/")
    return path == owner.rstrip("/") or (owner.endswith("/") and path.startswith(owner))


def paths_overlap(left: list[str], right: list[str]) -> bool:
    return any(path_contains(a, b) or path_contains(b, a) for a in left for b in right)


def is_aggregate(path: str) -> bool:
    return any(path_contains(prefix, path) or path_contains(path, prefix) for prefix in AGGREGATE_PREFIXES)


def slices_from_plan(plan: dict) -> tuple[list[dict], dict[str, dict]]:
    if plan.get("schema") not in PLAN_SCHEMAS:
        raise ParallelError(f"unsupported plan schema: {plan.get('schema')}")
    raw: list = []
    if isinstance(plan.get("slices"), list):
        raw.extend(plan["slices"])
    for sprint in plan.get("sprints", []):
        if isinstance(sprint, dict) and isinstance(sprint.get("slices"), list):
            raw.extend(dict(item, _sprint=sprint.get("sprint")) for item in sprint["slices"])
    if not raw:
        raise ParallelError("plan contains no slices")
    ordered: list[dict] = []
    indexed: dict[str, dict] = {}
    for item in raw:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ParallelError("every slice needs a string id")
        slice_id = item["id"]
        if slice_id in indexed:
            raise ParallelError(f"duplicate slice id: {slice_id}")
        item = dict(item)
        item.setdefault("depends_on", [])
        item.setdefault("status", "not-started")
        if item["status"] not in {"not-started", "in-progress", "done", "dropped"}:
            raise ParallelError(f"{slice_id}: invalid status")
        execution = item.get("execution")
        if not isinstance(execution, dict):
            # Historical and future scope is readable without migrating it. Only
            # executable current-sprint work needs an ownership mapping.
            item["execution"] = None
            ordered.append(item)
            indexed[slice_id] = item
            continue
        execution = dict(execution)
        if not isinstance(execution.get("write_paths"), list) or not execution["write_paths"]:
            raise ParallelError(f"{slice_id}: write_paths must be a nonempty array")
        execution["write_paths"] = [normalized_path(p) for p in execution["write_paths"]]
        contracts = execution.get("contracts", {})
        if not isinstance(contracts, dict):
            raise ParallelError(f"{slice_id}: execution.contracts must be an object")
        for label, values in (("reads", contracts.get("reads", [])), ("writes", contracts.get("writes", [])),
                              ("exclusive_resources", execution.get("exclusive_resources", []))):
            if not isinstance(values, list) or any(not isinstance(v, str) or not v for v in values):
                raise ParallelError(f"{slice_id}: {label} must be an array of nonempty strings")
        execution["contracts"] = {
            "reads": sorted(set(contracts.get("reads", []))),
            "writes": sorted(set(contracts.get("writes", []))),
        }
        execution["exclusive_resources"] = sorted(set(execution.get("exclusive_resources", [])))
        if execution.get("parallel") not in {"eligible", "serial"}:
            raise ParallelError(f"{slice_id}: parallel must be eligible or serial")
        if execution.get("parallel") == "serial" and not execution.get("serial_reason"):
            raise ParallelError(f"{slice_id}: serial slice needs serial_reason")
        if execution.get("parallel") != "serial" and any(is_aggregate(path) for path in execution["write_paths"]):
            raise ParallelError(f"{slice_id}: worker write_paths contains coordinator-owned aggregate state")
        item["execution"] = execution
        ordered.append(item)
        indexed[slice_id] = item
    for item in ordered:
        if not isinstance(item["depends_on"], list):
            raise ParallelError(f"{item['id']}: depends_on must be a list")
        for dependency in item["depends_on"]:
            if dependency == item["id"]:
                raise ParallelError(f"{item['id']}: self dependency")
            if dependency not in indexed:
                raise ParallelError(f"{item['id']}: unknown dependency {dependency}")
            if indexed[dependency].get("status") == "dropped":
                raise ParallelError(f"{item['id']}: dependency {dependency} is dropped")
            if item.get("_sprint") is not None and indexed[dependency].get("_sprint") is not None:
                if indexed[dependency]["_sprint"] > item["_sprint"]:
                    raise ParallelError(f"{item['id']}: dependency {dependency} belongs to a later sprint")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(slice_id: str) -> None:
        if slice_id in visiting:
            raise ParallelError(f"dependency cycle contains {slice_id}")
        if slice_id in visited:
            return
        visiting.add(slice_id)
        for dependency in indexed[slice_id]["depends_on"]:
            visit(dependency)
        visiting.remove(slice_id)
        visited.add(slice_id)

    for item in ordered:
        visit(item["id"])
    return ordered, indexed


def validate_plan(plan: dict) -> dict:
    ordered, _ = slices_from_plan(plan)
    return {"valid": True, "slice_count": len(ordered), "slice_ids": [item["id"] for item in ordered]}


def plan_fingerprint(plan: dict) -> str:
    ordered, _ = slices_from_plan(plan)
    # Accounting/status updates during an integration must not invalidate the
    # run. Changes to scope, dependencies or execution ownership must.
    scope = [{key: item.get(key) for key in ("id", "depends_on", "execution", "_sprint", "owns", "criteria")}
             for item in ordered]
    return hashlib.sha256(json.dumps(scope, sort_keys=True).encode()).hexdigest()


def bound_plan(run: dict, path: str) -> dict:
    plan = read_json(path)
    if str(Path(path).resolve()) != run["plan"] or plan_fingerprint(plan) != run.get("plan_fingerprint"):
        raise ParallelError("plan changed since run initialization; reconcile scope in a new run")
    return run["plan_snapshot"]


def new_run(
    plan_path: str,
    run_id: str,
    integration_ref: str,
    max_workers: int,
    coordinator_repo_id: str | None = None,
) -> dict:
    if max_workers < 1:
        raise ParallelError("max_workers must be positive")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", run_id):
        raise ParallelError("invalid run_id")
    plan = read_json(plan_path)
    ordered, _ = slices_from_plan(plan)
    sprints = plan.get("sprints", [])
    current = [s["sprint"] for s in sprints if s.get("status") == "in-progress"]
    if len(current) > 1:
        raise ParallelError("multiple active sprints; choose one before initializing a run")
    if sprints and not current:
        raise ParallelError("mark the approved sprint in-progress before initializing a run")
    return {
        "schema": RUN_SCHEMA,
        "run_id": run_id,
        "plan": str(Path(plan_path).resolve()),
        "integration_ref": integration_ref,
        "coordinator_repo_id": str(Path(coordinator_repo_id).resolve()) if coordinator_repo_id else None,
        "plan_fingerprint": plan_fingerprint(plan),
        "plan_snapshot": plan,
        "sprint": current[0] if current else None,
        "baseline_done": [s["id"] for s in ordered if s["status"] == "done"],
        "max_workers": max_workers,
        "attempts": {},
        "integrated": {},
        "events": [],
    }


def git_output(worktree: Path, *argv: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(worktree), *argv],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise ParallelError(f"git identity check failed in {worktree}: {detail}")
    return completed.stdout.strip()


def worktree_identity(worktree: str | Path) -> dict:
    requested = Path(worktree).resolve()
    if not requested.is_dir():
        raise ParallelError(f"worker cwd does not exist: {requested}")
    root = Path(git_output(requested, "rev-parse", "--show-toplevel")).resolve()
    if root != requested:
        raise ParallelError(f"worker cwd must be the worktree root: expected {root}, got {requested}")
    common_raw = Path(git_output(requested, "rev-parse", "--git-common-dir"))
    common = (requested / common_raw).resolve() if not common_raw.is_absolute() else common_raw.resolve()
    branch = git_output(requested, "symbolic-ref", "--quiet", "--short", "HEAD")
    head = git_output(requested, "rev-parse", "HEAD")
    return {"worktree": str(root), "repo_id": str(common), "branch": branch, "head": head}


def validate_assignment_identity(assignment: dict) -> dict:
    identity = worktree_identity(assignment["worktree"])
    for key in ("worktree", "repo_id", "branch"):
        if identity[key] != assignment[key]:
            raise ParallelError(f"assignment {key} mismatch: expected {assignment[key]}, got {identity[key]}")
    base = assignment["base_commit"]
    completed = subprocess.run(
        ["git", "-C", identity["worktree"], "merge-base", "--is-ancestor", base, identity["head"]],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if completed.returncode != 0:
        raise ParallelError(f"assignment base_commit is not an ancestor of worker HEAD: {base}")
    root = Path(identity["worktree"])
    for owner in assignment["write_paths"]:
        relative = normalized_path(owner).rstrip("/")
        target = root / relative
        resolved = target.resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ParallelError(f"assigned path escapes worktree through a symlink: {owner}") from exc
    return identity


def load_run(path: str | Path) -> dict:
    run = read_json(path)
    if run.get("schema") != RUN_SCHEMA:
        raise ParallelError(f"unsupported run schema: {run.get('schema')}")
    return run


def active_attempts(run: dict) -> list[dict]:
    return [attempt for attempt in run.get("attempts", {}).values()
            if attempt.get("state") in ACTIVE or
            (attempt.get("state") in {"blocked", "failed", "cancelled"} and not attempt.get("claims_released"))]


def conflict_reason(candidate: dict, attempt: dict, indexed: dict[str, dict]) -> str | None:
    active_slice = indexed.get(attempt.get("slice_id"))
    if not active_slice:
        return f"active attempt refers to unknown slice {attempt.get('slice_id')}"
    left = candidate["execution"]
    right = active_slice["execution"]
    if paths_overlap(left["write_paths"], right["write_paths"]):
        return f"write paths overlap {active_slice['id']}"
    if set(left["exclusive_resources"]) & set(right["exclusive_resources"]):
        return f"exclusive resource held by {active_slice['id']}"
    left_reads = set(left["contracts"]["reads"])
    left_writes = set(left["contracts"]["writes"])
    right_reads = set(right["contracts"]["reads"])
    right_writes = set(right["contracts"]["writes"])
    if left_writes & (right_reads | right_writes) or right_writes & (left_reads | left_writes):
        return f"contract conflict with {active_slice['id']}"
    if left["parallel"] == "serial" or right["parallel"] == "serial":
        return "serial slice active or requested"
    return None


def ready_slices(plan: dict, run: dict) -> dict:
    ordered, indexed = slices_from_plan(plan)
    active = active_attempts(run)
    # A stopped worker retains source/resource claims through review without
    # consuming a live execution slot. Independent work may use that slot.
    executing = sum(a.get("state") in {"claimed", "launching", "running", "stuck"} for a in active)
    capacity = max(0, int(run["max_workers"]) - executing)
    integrated = set(run.get("integrated", {}))
    ready: list[str] = []
    waiting: dict[str, str] = {}
    active_ids = {attempt.get("slice_id") for attempt in active}
    attempted_ids = {
        attempt.get("slice_id")
        for attempt in run.get("attempts", {}).values()
        if not attempt.get("claims_released")
    }
    for item in ordered:
        slice_id = item["id"]
        if item.get("_sprint") != run.get("sprint"):
            continue
        if item.get("status") in {"done", "dropped"} or slice_id in integrated or slice_id in active_ids:
            continue
        if slice_id in attempted_ids:
            waiting[slice_id] = "existing non-retryable attempt"
            continue
        if sum(a.get("slice_id") == slice_id for a in run.get("attempts", {}).values()) >= 3:
            waiting[slice_id] = "three-attempt repair limit reached"
            continue
        if not item.get("execution"):
            waiting[slice_id] = "missing execution mapping; scoped planning required"
            continue
        if item["execution"]["parallel"] == "serial":
            waiting[slice_id] = "coordinator-owned serial slice"
            continue
        unmet = [d for d in item["depends_on"] if d not in integrated and d not in run.get("baseline_done", [])]
        if unmet:
            waiting[slice_id] = "dependencies not integrated: " + ", ".join(unmet)
            continue
        conflict = next((reason for attempt in active if (reason := conflict_reason(item, attempt, indexed))), None)
        if conflict:
            waiting[slice_id] = conflict
            continue
        if len(ready) < capacity:
            # Treat the selection being built as claims for this scheduling decision.
            selected_attempts = active + [{"slice_id": selected, "state": "claimed"} for selected in ready]
            conflict = next((reason for attempt in selected_attempts if (reason := conflict_reason(item, attempt, indexed))), None)
            if not conflict:
                ready.append(slice_id)
                continue
            waiting[slice_id] = conflict
        else:
            waiting[slice_id] = "capacity exhausted"
    return {"ready": ready, "waiting": waiting, "capacity": capacity, "active": len(active), "executing": executing}


def process_alive(pid: int, start_identity: str | None = None) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    if start_identity == "unavailable":
        # A live PID without a start identity may have been reused. Fail closed:
        # retain claims and require coordinator inspection instead of guessing.
        return True
    if start_identity and Path(f"/proc/{pid}/stat").exists():
        try:
            current = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rsplit(")", 1)[1].split()[19]
        except OSError:
            return False
        return current == start_identity
    if start_identity:
        try:
            completed = subprocess.run(
                ["ps", "-o", "lstart=", "-p", str(pid)], check=False, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            )
        except OSError:
            return True
        return completed.returncode == 0 and completed.stdout.strip() == start_identity
    return True


def process_start_identity(pid: int) -> str:
    proc = Path(f"/proc/{pid}/stat")
    if proc.exists():
        return proc.read_text(encoding="utf-8").rsplit(")", 1)[1].split()[19]
    try:
        completed = subprocess.run(
            ["ps", "-o", "lstart=", "-p", str(pid)], check=False, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        )
    except OSError:
        return "unavailable"
    if completed.returncode != 0 or not completed.stdout.strip():
        return "unavailable"
    return completed.stdout.strip()


@contextmanager
def run_lock(run_path: Path):
    if fcntl is None:
        raise ParallelError("parallel writing requires POSIX flock; use serial development on this platform")
    unlocked = load_run(run_path)
    repo = unlocked.get("coordinator_repo_id")
    if not repo or not Path(repo).is_dir():
        raise ParallelError("run has no valid canonical Git common directory")
    key = f"{Path(repo).resolve()}\0{unlocked['integration_ref']}"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
    lock_dir = Path(repo) / "keel-parallel"
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock = lock_dir / f"{digest}.lock"
    # Never unlink a flock inode: all worktrees must lock the same object.
    with lock.open("a+") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ParallelError("coordinator lock held by another operation") from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def registered_attempt(run: dict, assignment: dict) -> dict:
    attempt = run.get("attempts", {}).get(assignment["attempt_id"])
    if not attempt or attempt.get("assignment_snapshot") != assignment:
        raise ParallelError("assignment does not match immutable registered assignment")
    return attempt


def claim_run_owner(run: dict, run_path: Path) -> None:
    key = hashlib.sha256(run["integration_ref"].encode()).hexdigest()
    path = Path(run["coordinator_repo_id"]) / "keel-parallel" / (key + ".owner.json")
    if path.exists():
        owner = read_json(path)
        if owner["run"] != str(run_path.resolve()):
            old = load_run(owner["run"])
            if active_attempts(old):
                raise ParallelError("another run holds claims for this integration branch")
    write_json_atomic(path, {"run": str(run_path.resolve())})


def validate_assignment(assignment: dict, run: dict, plan: dict) -> dict:
    if assignment.get("schema") != ASSIGNMENT_SCHEMA:
        raise ParallelError("invalid assignment schema")
    required = {
        "run_id", "attempt_id", "slice_id", "repo_id", "worktree", "branch", "base_commit",
        "coordinator_id", "write_paths", "inputs", "acceptance_criteria", "test_commands",
        "environment", "deadline_seconds",
    }
    missing = sorted(required - assignment.keys())
    if missing:
        raise ParallelError("assignment missing: " + ", ".join(missing))
    if assignment["run_id"] != run["run_id"]:
        raise ParallelError("assignment run_id does not match run")
    for key in ("run_id", "attempt_id", "slice_id"):
        if not isinstance(assignment[key], str) or not re.fullmatch(r"[A-Za-z0-9_-]+", assignment[key]):
            raise ParallelError(f"invalid {key}")
    _, indexed = slices_from_plan(plan)
    item = indexed.get(assignment["slice_id"])
    if not item or not item.get("execution"):
        raise ParallelError("assignment slice is not in plan")
    if item["execution"]["parallel"] != "eligible":
        raise ParallelError("serial slice belongs to the coordinator")
    assigned_paths = [normalized_path(p) for p in assignment["write_paths"]]
    if assigned_paths != item["execution"]["write_paths"]:
        raise ParallelError("assignment write_paths do not match approved plan")
    if int(assignment["deadline_seconds"]) < 1:
        raise ParallelError("deadline_seconds must be positive")
    return {"valid": True, "slice_id": item["id"], "attempt_id": assignment["attempt_id"]}


def validate_result(result: dict, assignment: dict) -> dict:
    if result.get("schema") != RESULT_SCHEMA:
        raise ParallelError("invalid worker result schema")
    identity = ("run_id", "attempt_id", "slice_id", "repo_id", "worktree", "branch", "base_commit")
    for key in identity:
        if result.get(key) != assignment.get(key):
            raise ParallelError(f"worker result {key} does not match assignment")
    if result.get("outcome") not in {"ready", "blocked", "failed", "cancelled"}:
        raise ParallelError("invalid worker result outcome")
    required = {"changed_paths", "tests", "review_findings", "state_contributions", "timing"}
    missing = sorted(required - result.keys())
    if missing:
        raise ParallelError("worker result missing: " + ", ".join(missing))
    if result["outcome"] == "blocked" and not result.get("needs_user"):
        raise ParallelError("blocked result needs needs_user")
    changed = [normalized_path(p) for p in result.get("changed_paths", [])]
    allowed = [normalized_path(p) for p in assignment["write_paths"]]
    unexpected = [path for path in changed if not any(path_contains(owner, path) for owner in allowed)]
    aggregate = [path for path in changed if is_aggregate(path)]
    if unexpected or aggregate:
        raise ParallelError("worker changed out-of-scope paths: " + ", ".join(sorted(set(unexpected + aggregate))))
    if result["outcome"] == "ready" and not result.get("code_commit"):
        raise ParallelError("ready result needs code_commit")
    if not isinstance(result["tests"], list) or not isinstance(result["review_findings"], list):
        raise ParallelError("tests and review_findings must be arrays")
    if not isinstance(result["state_contributions"], dict) or not isinstance(result["timing"], dict):
        raise ParallelError("contributions and timing must be objects")
    if result["outcome"] == "ready":
        root = Path(assignment["worktree"])
        for command in assignment["test_commands"]:
            matches = [test for test in result["tests"] if isinstance(test, dict) and test.get("command") == command]
            if not matches or not all(test.get("exit_code") == 0 and test.get("result") == "pass" for test in matches):
                raise ParallelError(f"required worker test is missing or failed: {command}")
            for test in matches:
                evidence = root / normalized_path(test.get("evidence", ""))
                try:
                    evidence.resolve().relative_to(root)
                except ValueError as exc:
                    raise ParallelError("test evidence escapes worktree") from exc
                if not evidence.is_file():
                    raise ParallelError("worker test evidence is missing")
    return {"valid": True, "outcome": result["outcome"], "changed_paths": changed}


def git_changed_paths(worktree: Path, old: str, new: str) -> list[str]:
    completed = subprocess.run(
        ["git", "-C", str(worktree), "diff", "--name-status", "-z", "-M", old, new],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise ParallelError(f"cannot inspect worker diff: {completed.stderr.decode(errors='replace').strip()}")
    fields = completed.stdout.decode("utf-8", errors="strict").split("\0")
    paths: list[str] = []
    index = 0
    while index < len(fields) and fields[index]:
        status = fields[index]
        index += 1
        if status.startswith(("R", "C")):
            paths.extend((normalized_path(fields[index]), normalized_path(fields[index + 1])))
            index += 2
        else:
            paths.append(normalized_path(fields[index]))
            index += 1
    return sorted(set(paths))


def validate_result_git(result: dict, assignment: dict, result_path: str | Path) -> dict:
    identity = validate_assignment_identity(assignment)
    worktree = Path(identity["worktree"])
    code_commit = result.get("code_commit")
    if not isinstance(code_commit, str) or not re.fullmatch(r"[0-9a-f]{40,64}", code_commit):
        raise ParallelError("every committed worker result requires a full code_commit")
    ancestry = subprocess.run(
        ["git", "-C", str(worktree), "merge-base", "--is-ancestor", assignment["base_commit"], code_commit],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if ancestry.returncode != 0:
        raise ParallelError("worker code_commit does not descend from assignment base_commit")
    at_head = subprocess.run(
        ["git", "-C", str(worktree), "merge-base", "--is-ancestor", code_commit, identity["head"]],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if at_head.returncode != 0:
        raise ParallelError("worker code_commit is not on the assigned branch")
    actual = git_changed_paths(worktree, assignment["base_commit"], code_commit)
    claimed = sorted(set(normalized_path(path) for path in result.get("changed_paths", [])))
    if actual != claimed:
        raise ParallelError(f"worker changed_paths do not match Git diff: claimed={claimed}, actual={actual}")
    for path in actual:
        try:
            (worktree / path).resolve().relative_to(worktree)
        except ValueError as exc:
            raise ParallelError(f"changed path escapes worktree through symlink: {path}") from exc
    expected_report = normalized_path(
        f"docs/.keel/slices/{assignment['run_id']}/{assignment['slice_id']}/{assignment['attempt_id']}.json"
    )
    report_file = Path(result_path).resolve()
    try:
        report_relative = report_file.relative_to(worktree).as_posix()
    except ValueError as exc:
        raise ParallelError("worker result must be read from its assigned worktree") from exc
    if report_relative != expected_report:
        raise ParallelError(f"worker result path must be {expected_report}")
    if identity["head"] == code_commit:
        raise ParallelError("worker result report is not committed separately from code_commit")
    if git_output(worktree, "rev-list", "--parents", "-n", "1", identity["head"]).split()[1:] != [code_commit]:
        raise ParallelError("unexpected commits after code_commit: report must be its direct single-parent child")
    post_code = git_changed_paths(worktree, code_commit, identity["head"])
    if post_code != [expected_report]:
        raise ParallelError(f"unexpected commits after code_commit changed: {post_code}")
    committed = git_output(worktree, "show", f"{identity['head']}:{expected_report}")
    try:
        committed_result = json.loads(committed)
    except json.JSONDecodeError as exc:
        raise ParallelError("committed worker result is not valid JSON") from exc
    if committed_result != result:
        raise ParallelError("worker result file does not match the report commit")
    status = git_output(worktree, "status", "--porcelain")
    if status:
        raise ParallelError("worker worktree is not clean after reporting")
    return {**identity, "changed_paths": actual}


def append_event(run: dict, kind: str, **fields: object) -> None:
    run.setdefault("events", []).append({"event": kind, "at": time.time(), **fields})


def command_validate(args: argparse.Namespace) -> dict:
    return validate_plan(read_json(args.plan))


def command_init(args: argparse.Namespace) -> dict:
    plan = read_json(args.plan)
    validate_plan(plan)
    run_path = Path(args.run)
    if run_path.exists():
        raise ParallelError(f"run already exists: {run_path}")
    repository = Path(args.repo or Path(args.plan).resolve().parent).resolve()
    git_output(repository, "check-ref-format", "refs/heads/" + args.integration_ref)
    git_output(repository, "rev-parse", "--verify", "refs/heads/" + args.integration_ref)
    common_raw = Path(git_output(repository, "rev-parse", "--git-common-dir"))
    repo_id = (repository / common_raw).resolve() if not common_raw.is_absolute() else common_raw.resolve()
    run = new_run(args.plan, args.run_id, args.integration_ref, args.max_workers, str(repo_id))
    write_json_atomic(run_path, run, create_only=True)
    return {"created": str(run_path.resolve()), "run_id": args.run_id, "max_workers": args.max_workers}


def command_ready(args: argparse.Namespace) -> dict:
    run = load_run(args.run)
    return ready_slices(bound_plan(run, args.plan), run)


def command_claim(args: argparse.Namespace) -> dict:
    run_path = Path(args.run)
    with run_lock(run_path):
        run = load_run(run_path)
        plan = bound_plan(run, args.plan)
        assignment = read_json(args.assignment)
        validate_assignment(assignment, run, plan)
        identity = validate_assignment_identity(assignment)
        if run.get("coordinator_repo_id") and assignment["repo_id"] != run["coordinator_repo_id"]:
            raise ParallelError("assignment repository does not match coordinator repository")
        if assignment["attempt_id"] in run["attempts"]:
            raise ParallelError(f"attempt already exists: {assignment['attempt_id']}")
        if assignment["branch"] == run["integration_ref"]:
            raise ParallelError("worker cannot use the integration branch")
        integration_head = git_output(Path(assignment["worktree"]), "rev-parse", "refs/heads/" + run["integration_ref"])
        if assignment["base_commit"] != integration_head:
            raise ParallelError("worker base must equal the current integration head")
        if identity["head"] != assignment["base_commit"] or git_output(Path(assignment["worktree"]), "status", "--porcelain"):
            raise ParallelError("worker must start clean at its exact base_commit")
        for attempt in active_attempts(run):
            previous = attempt.get("assignment_snapshot", {})
            if previous.get("worktree") == assignment["worktree"] or previous.get("branch") == assignment["branch"]:
                raise ParallelError("worktree or branch is already assigned")
        claim_run_owner(run, run_path)
        readiness = ready_slices(plan, run)
        if assignment["slice_id"] not in readiness["ready"]:
            reason = readiness["waiting"].get(assignment["slice_id"], "not selected within available capacity")
            raise ParallelError(f"slice is not claimable: {reason}")
        run["attempts"][assignment["attempt_id"]] = {
            "slice_id": assignment["slice_id"],
            "state": "claimed",
            "assignment": str(Path(args.assignment).resolve()),
            "assignment_snapshot": assignment,
        }
        append_event(run, "claimed", attempt_id=assignment["attempt_id"], slice_id=assignment["slice_id"])
        write_json_atomic(run_path, run)
    return {"claimed": assignment["slice_id"], "attempt_id": assignment["attempt_id"]}


def command_status(args: argparse.Namespace) -> dict:
    run = load_run(args.run)
    states: dict[str, int] = {}
    for attempt in run.get("attempts", {}).values():
        states[attempt["state"]] = states.get(attempt["state"], 0) + 1
    return {"run_id": run["run_id"], "states": states, "integrated": run.get("integrated", {}), "events": len(run.get("events", []))}


def command_record_result(args: argparse.Namespace) -> dict:
    run_path = Path(args.run)
    with run_lock(run_path):
        run = load_run(run_path)
        plan = bound_plan(run, args.plan)
        assignment = read_json(args.assignment)
        result = read_json(args.result)
        validate_assignment(assignment, run, plan)
        attempt = registered_attempt(run, assignment)
        if attempt.get("state") not in {"claimed", "awaiting-result", "awaiting-review", "ready-to-integrate", "integrated"}:
            raise ParallelError("worker must be quiescent before accepting a result")
        checked = validate_result(result, assignment)
        if attempt.get("result_fingerprint"):
            fingerprint = json.dumps(result, sort_keys=True)
            if attempt["result_fingerprint"] == fingerprint:
                return {"recorded": False, "idempotent": True, "attempt_id": assignment["attempt_id"]}
            raise ParallelError("attempt already has a different result")
        git_facts = validate_result_git(result, assignment, args.result)
        state = {"ready": "awaiting-review", "blocked": "blocked", "failed": "failed", "cancelled": "cancelled"}[checked["outcome"]]
        attempt.update({
            "state": state,
            "result": str(Path(args.result).resolve()),
            "report_commit": git_facts["head"],
            "result_fingerprint": json.dumps(result, sort_keys=True),
        })
        append_event(run, "result-recorded", attempt_id=assignment["attempt_id"], outcome=checked["outcome"])
        write_json_atomic(run_path, run)
    return {"recorded": True, "state": state, "attempt_id": assignment["attempt_id"]}


def command_record_review(args: argparse.Namespace) -> dict:
    run_path = Path(args.run)
    with run_lock(run_path):
        run = load_run(run_path)
        attempt = run["attempts"].get(args.attempt)
        if not attempt:
            raise ParallelError("unknown attempt")
        if attempt["state"] != "awaiting-review":
            raise ParallelError(f"attempt is not awaiting review: {attempt['state']}")
        if not args.evidence:
            raise ParallelError("review evidence is required")
        if args.verdict not in {"pass", "fail"}:
            raise ParallelError("invalid review verdict")
        if report_head := attempt.get("report_commit"):
            identity = validate_assignment_identity(attempt["assignment_snapshot"])
            if identity["head"] != report_head:
                raise ParallelError("worker branch changed after result acceptance")
        result = json.loads(attempt.get("result_fingerprint", "{}"))
        if result.get("code_commit") != args.code_commit:
            raise ParallelError("review code_commit does not match the recorded worker result")
        attempt["review"] = {
            "verdict": args.verdict,
            "code_commit": args.code_commit,
            "evidence": args.evidence,
        }
        attempt["state"] = "ready-to-integrate" if args.verdict == "pass" else "failed"
        append_event(
            run,
            "review-recorded",
            attempt_id=args.attempt,
            verdict=args.verdict,
            code_commit=args.code_commit,
        )
        write_json_atomic(run_path, run)
    return {"recorded": True, "state": attempt["state"], "attempt_id": args.attempt}


def command_record_integration(args: argparse.Namespace) -> dict:
    run_path = Path(args.run)
    with run_lock(run_path):
        run = load_run(run_path)
        attempt = run["attempts"].get(args.attempt)
        if not attempt:
            raise ParallelError("unknown attempt")
        if attempt["state"] != "ready-to-integrate":
            if attempt["state"] == "integrated" and run.get("integrated", {}).get(attempt["slice_id"]) == args.commit:
                return {"recorded": False, "idempotent": True, "slice_id": attempt["slice_id"]}
            raise ParallelError(f"attempt is not ready for integration: {attempt['state']}")
        slice_id = attempt["slice_id"]
        if slice_id in run.get("integrated", {}):
            raise ParallelError(f"slice already integrated by another attempt: {slice_id}")
        if not getattr(args, "evidence", None):
            raise ParallelError("integration evidence is required")
        evidence = read_json(args.evidence)
        if evidence != attempt.get("verified_candidate"):
            raise ParallelError("integration evidence must come from verify-integration for this attempt")
        assignment = attempt.get("assignment_snapshot")
        if not assignment or not attempt.get("review") or attempt["review"]["verdict"] != "pass":
            raise ParallelError("integration requires registered assignment and passing review")
        worktree = Path(assignment["worktree"])
        head = git_output(worktree, "rev-parse", "--verify", f"refs/heads/{run['integration_ref']}^{{commit}}")
        if not re.fullmatch(r"[0-9a-f]{40,64}", args.commit) or head != args.commit:
            raise ParallelError("integration commit must be the actual integration branch head")
        if evidence.get("schema") != "keel.integration-evidence/1" or evidence.get("commit") != head or evidence.get("attempt_id") != args.attempt:
            raise ParallelError("integration evidence identity does not match candidate")
        for ancestor in (attempt["report_commit"], attempt["review"]["code_commit"], evidence.get("previous_head", "")):
            completed = subprocess.run(["git", "-C", str(worktree), "merge-base", "--is-ancestor", ancestor, head],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if completed.returncode:
                raise ParallelError("integration commit lacks required worker or previous-head ancestry")
        checks = evidence.get("checks")
        if not isinstance(checks, list) or not checks or not all(
            isinstance(check, dict) and check.get("exit_code") == 0 and check.get("command")
            and check.get("evidence") and Path(check["evidence"]).is_file() for check in checks
        ):
            raise ParallelError("integration requires passing checks with existing evidence files")
        if git_output(worktree, "rev-parse", f"refs/heads/{run['integration_ref']}") != head:
            raise ParallelError("integration branch moved during validation")
        attempt["state"] = "integrated"
        attempt["integration_commit"] = args.commit
        run.setdefault("integrated", {})[slice_id] = args.commit
        append_event(run, "integrated", attempt_id=args.attempt, slice_id=slice_id, commit=args.commit)
        write_json_atomic(run_path, run)
    return {"recorded": True, "slice_id": slice_id, "commit": args.commit}


def command_verify_integration(args: argparse.Namespace) -> dict:
    """Execute coordinator checks on a clean candidate before branch promotion."""
    path = Path(args.run)
    with run_lock(path):
        run = load_run(path)
        attempt = run["attempts"].get(args.attempt)
        if not attempt or attempt.get("state") != "ready-to-integrate" or not attempt.get("review"):
            raise ParallelError("candidate requires a reviewed attempt")
        worker = validate_assignment_identity(attempt["assignment_snapshot"])
        if worker["head"] != attempt["report_commit"]:
            raise ParallelError("worker branch changed after review; collect a new attempt and review")
        if any(a.get("candidate_in_flight") for a in run["attempts"].values()):
            raise ParallelError("candidate verification already in flight; reconcile before retry")
        candidate = worktree_identity(args.candidate)
        root = Path(candidate["worktree"])
        if candidate["repo_id"] != run["coordinator_repo_id"] or candidate["branch"] == run["integration_ref"]:
            raise ParallelError("candidate must use a separate branch of the coordinator repository")
        if any(a.get("assignment_snapshot", {}).get("worktree") == str(root) for a in active_attempts(run)):
            raise ParallelError("candidate checkout belongs to a worker")
        before = git_output(root, "rev-parse", "refs/heads/" + run["integration_ref"])
        if before != args.previous_head:
            raise ParallelError("integration branch moved; rebuild candidate")
        if git_output(root, "status", "--porcelain"):
            raise ParallelError("integration candidate must be clean")
        for ancestor in (before, attempt["report_commit"], attempt["review"]["code_commit"]):
            check = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", ancestor, candidate["head"]],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if check.returncode:
                raise ParallelError("candidate is missing required ancestry")
        if not args.check_command:
            raise ParallelError("an integration verification command is required")
        attempt.pop("verified_candidate", None)
        attempt["candidate_in_flight"] = {"commit": candidate["head"], "pid": os.getpid(),
                                          "process_start": process_start_identity(os.getpid())}
        write_json_atomic(path, run)
    # Checks may be slow; do not hold the scheduler mutex while they run.
    log = Path(args.evidence).with_suffix(".log").resolve()
    log.parent.mkdir(parents=True, exist_ok=True)
    try:
        with log.open("wb") as stream:
            completed = subprocess.run(args.check_command, cwd=root, stdout=stream, stderr=subprocess.STDOUT,
                                       timeout=args.timeout)
    except (OSError, subprocess.TimeoutExpired):
        with run_lock(path):
            run = load_run(path)
            run["attempts"][args.attempt].pop("candidate_in_flight", None)
            run["attempts"][args.attempt].pop("verified_candidate", None)
            write_json_atomic(path, run)
        raise
    with run_lock(path):
        run = load_run(path); attempt = run["attempts"][args.attempt]
        if completed.returncode:
            attempt.pop("candidate_in_flight", None)
            attempt.pop("verified_candidate", None)
            write_json_atomic(path, run)
            raise ParallelError(f"integration checks failed ({completed.returncode}); integration branch unchanged")
        if (attempt["state"] != "ready-to-integrate" or git_output(root, "rev-parse", "HEAD") != candidate["head"]
                or git_output(root, "status", "--porcelain")
                or git_output(root, "rev-parse", "refs/heads/" + run["integration_ref"]) != before):
            attempt.pop("candidate_in_flight", None)
            attempt.pop("verified_candidate", None)
            write_json_atomic(path, run)
            raise ParallelError("candidate or integration branch changed during checks; evidence rejected")
        evidence = {"schema": "keel.integration-evidence/1", "attempt_id": args.attempt,
                    "commit": candidate["head"], "previous_head": before,
                    "checks": [{"command": args.check_command, "exit_code": 0, "evidence": str(log)}]}
        attempt["verified_candidate"] = evidence
        attempt.pop("candidate_in_flight", None)
        write_json_atomic(path, run)
        write_json_atomic(args.evidence, evidence)
    return evidence


def command_reconcile(args: argparse.Namespace) -> dict:
    run_path = Path(args.run)
    with run_lock(run_path):
        run = load_run(run_path)
        plan = bound_plan(run, args.plan)
        _, indexed = slices_from_plan(plan)
        changes: list[dict] = []
        for attempt_id, attempt in run.get("attempts", {}).items():
            if attempt.get("slice_id") not in indexed:
                changes.append({"attempt_id": attempt_id, "problem": "slice missing from plan"})
            if attempt.get("state") == "running" and attempt.get("pid"):
                if not process_alive(int(attempt["pid"]), attempt.get("process_start")):
                    assignment = attempt.get("assignment_snapshot", {})
                    report = Path(assignment.get("worktree", "")) / "docs/.keel/slices" / run["run_id"] / attempt["slice_id"] / (attempt_id + ".json")
                    attempt["state"] = ("stuck" if group_alive(attempt["pid"]) else
                                        "awaiting-result" if report.is_file() else "failed")
                    attempt["failure"] = "supervisor interrupted; recover committed report or resolve failed attempt"
                    changes.append({"attempt_id": attempt_id, "state": attempt["state"]})
        if changes:
            append_event(run, "reconciled", changes=changes)
            write_json_atomic(run_path, run)
    return {"changes": changes, "ready": ready_slices(plan, run)}


def command_run_worker(args: argparse.Namespace) -> dict:
    assignment = read_json(args.assignment)
    run_path = Path(args.run)
    if not args.worker_command:
        raise ParallelError("run-worker needs a command after --")
    deadline = int(assignment.get("deadline_seconds", 1800))
    start = time.monotonic()
    with run_lock(run_path):
        run = load_run(run_path)
        plan = bound_plan(run, args.plan)
        validate_assignment(assignment, run, plan)
        attempt = registered_attempt(run, assignment)
        if attempt.get("state") != "claimed":
            raise ParallelError("run-worker requires the registered claimed attempt")
        identity = validate_assignment_identity(assignment)
        worktree = Path(identity["worktree"])
        if identity["head"] != assignment["base_commit"] or git_output(worktree, "status", "--porcelain"):
            raise ParallelError("worker changed since claim")
        attempt["state"] = "launching"
        write_json_atomic(run_path, run)
        process = None
        try:
            log = Path(args.envelope).with_suffix(".log")
            log.parent.mkdir(parents=True, exist_ok=True)
            with log.open("ab") as stream:
                process = subprocess.Popen(args.worker_command, cwd=worktree, start_new_session=True,
                                           stdout=stream, stderr=subprocess.STDOUT)
            attempt.update({"state": "running", "pid": process.pid, "process_start": process_start_identity(process.pid)})
            append_event(run, "worker-started", attempt_id=assignment["attempt_id"], pid=process.pid)
            write_json_atomic(run_path, run)
        except Exception:
            if process is not None:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                    process.wait(timeout=5)
                except (ProcessLookupError, subprocess.TimeoutExpired):
                    pass
            attempt["state"] = "stuck" if process is not None else "failed"
            write_json_atomic(run_path, run)
            raise
    timed_out = False
    try:
        returncode = process.wait(timeout=deadline)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            returncode = process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            returncode = None
    envelope = {
        "schema": "keel.worker-execution/1",
        "run_id": assignment.get("run_id"),
        "attempt_id": assignment.get("attempt_id"),
        "slice_id": assignment.get("slice_id"),
        "pid": process.pid,
        "elapsed_seconds": round(time.monotonic() - start, 6),
        "timed_out": timed_out,
        "returncode": returncode,
    }
    write_json_atomic(args.envelope, envelope)
    with run_lock(run_path):
        run = load_run(run_path)
        attempt = registered_attempt(run, assignment)
        attempt["execution"] = envelope
        attempt["state"] = ("stuck" if returncode is None or group_alive(process.pid) else
                            "failed" if timed_out or returncode != 0 else "awaiting-result")
        write_json_atomic(run_path, run)
    if timed_out:
        raise ParallelError("worker deadline expired; SIGTERM sent and partial work preserved")
    if returncode != 0:
        raise ParallelError(f"worker exited with status {returncode} and no success was inferred")
    return envelope


def group_alive(pid: int) -> bool:
    if pid <= 1:
        raise ParallelError("invalid owned process group")
    try:
        os.killpg(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def command_resolve(args: argparse.Namespace) -> dict:
    path = Path(args.run)
    with run_lock(path):
        run = load_run(path)
        attempt = run["attempts"].get(args.attempt)
        if not attempt or attempt["state"] not in {"failed", "cancelled", "blocked", "awaiting-result", "stuck"}:
            raise ParallelError("attempt cannot be resolved in this state")
        if attempt.get("pid") and (process_alive(attempt["pid"], attempt.get("process_start")) or group_alive(attempt["pid"])):
            raise ParallelError("worker or descendants may still be live; claims retained")
        if not args.evidence:
            raise ParallelError("resolution evidence is required")
        attempt.update(state="cancelled", claims_released=True, resolution=args.evidence)
        append_event(run, "claims-released", attempt_id=args.attempt)
        write_json_atomic(path, run)
    return {"resolved": args.attempt}


def command_worker_check(args: argparse.Namespace) -> dict:
    run = load_run(args.run)
    assignment = read_json(args.assignment)
    attempt = registered_attempt(run, assignment)
    if attempt["state"] not in {"claimed", "running", "awaiting-result"}:
        raise ParallelError("worker attempt is not active")
    if str(Path.cwd().resolve()) != assignment["worktree"]:
        raise ParallelError("worker check must run inside its assigned cwd")
    validate_assignment_identity(assignment)
    root = Path(assignment["worktree"])
    changed = set(git_changed_paths(root, assignment["base_commit"], "HEAD"))
    for command in (["diff", "--name-only", "--no-renames", "-z"],
                    ["diff", "--cached", "--name-only", "--no-renames", "-z", "HEAD"],
                    ["ls-files", "--others", "--exclude-standard", "-z"]):
        completed = subprocess.run(["git", "-C", str(root), *command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if completed.returncode:
            raise ParallelError("cannot inspect worker scope")
        changed.update(p for p in completed.stdout.decode("utf-8").split("\0") if p)
    report = f"docs/.keel/slices/{assignment['run_id']}/{assignment['slice_id']}/{assignment['attempt_id']}.json"
    for path in sorted(changed):
        normalized_path(path)
        if path != report and (is_aggregate(path) or not any(path_contains(owner, path) for owner in assignment["write_paths"])):
            raise ParallelError(f"worker changed out-of-scope path: {path}")
        try:
            (root / path).resolve().relative_to(root)
        except ValueError as exc:
            raise ParallelError(f"worker path escapes worktree: {path}") from exc
    return {"valid": True, "role": "worker", "attempt_id": assignment["attempt_id"], "changed_paths": sorted(changed)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    initialize = sub.add_parser("init")
    initialize.add_argument("--plan", required=True)
    initialize.add_argument("--run", required=True)
    initialize.add_argument("--run-id", required=True)
    initialize.add_argument("--integration-ref", required=True)
    initialize.add_argument("--max-workers", required=True, type=int)
    initialize.add_argument("--repo", help="repository path; defaults to the plan directory")
    initialize.set_defaults(func=command_init)
    validate = sub.add_parser("validate")
    validate.add_argument("--plan", required=True)
    validate.set_defaults(func=command_validate)
    ready = sub.add_parser("ready")
    ready.add_argument("--plan", required=True)
    ready.add_argument("--run", required=True)
    ready.set_defaults(func=command_ready)
    claim = sub.add_parser("claim")
    claim.add_argument("--plan", required=True)
    claim.add_argument("--run", required=True)
    claim.add_argument("--assignment", required=True)
    claim.set_defaults(func=command_claim)
    status = sub.add_parser("status")
    status.add_argument("--run", required=True)
    status.set_defaults(func=command_status)
    result = sub.add_parser("record-result")
    result.add_argument("--plan", required=True)
    result.add_argument("--run", required=True)
    result.add_argument("--assignment", required=True)
    result.add_argument("--result", required=True)
    result.set_defaults(func=command_record_result)
    review = sub.add_parser("record-review")
    review.add_argument("--run", required=True)
    review.add_argument("--attempt", required=True)
    review.add_argument("--code-commit", required=True)
    review.add_argument("--verdict", required=True, choices=("pass", "fail"))
    review.add_argument("--evidence", required=True)
    review.set_defaults(func=command_record_review)
    integration = sub.add_parser("record-integration")
    integration.add_argument("--run", required=True)
    integration.add_argument("--attempt", required=True)
    integration.add_argument("--commit", required=True)
    integration.add_argument("--evidence", required=True)
    integration.set_defaults(func=command_record_integration)
    verify = sub.add_parser("verify-integration")
    verify.add_argument("--run", required=True)
    verify.add_argument("--attempt", required=True)
    verify.add_argument("--candidate", required=True)
    verify.add_argument("--previous-head", required=True)
    verify.add_argument("--evidence", required=True)
    verify.add_argument("--timeout", type=int, default=1800)
    verify.add_argument("check_command", nargs=argparse.REMAINDER)
    verify.set_defaults(func=command_verify_integration)
    reconcile = sub.add_parser("reconcile")
    reconcile.add_argument("--plan", required=True)
    reconcile.add_argument("--run", required=True)
    reconcile.set_defaults(func=command_reconcile)
    worker = sub.add_parser("run-worker")
    worker.add_argument("--plan", required=True)
    worker.add_argument("--run", required=True)
    worker.add_argument("--assignment", required=True)
    worker.add_argument("--envelope", required=True)
    worker.add_argument("worker_command", nargs=argparse.REMAINDER)
    worker.set_defaults(func=command_run_worker)
    check = sub.add_parser("worker-check")
    check.add_argument("--run", required=True)
    check.add_argument("--assignment", required=True)
    check.set_defaults(func=command_worker_check)
    resolve = sub.add_parser("resolve")
    resolve.add_argument("--run", required=True)
    resolve.add_argument("--attempt", required=True)
    resolve.add_argument("--evidence", required=True)
    resolve.set_defaults(func=command_resolve)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "worker_command", None) and args.worker_command[0] == "--":
        args.worker_command = args.worker_command[1:]
    if getattr(args, "check_command", None) and args.check_command[0] == "--":
        args.check_command = args.check_command[1:]
    try:
        return output(args.func(args))
    except (ParallelError, OSError, ValueError, TypeError, KeyError, subprocess.TimeoutExpired) as exc:
        return output({"error": str(exc)}, 1)


if __name__ == "__main__":
    raise SystemExit(main())
