#!/usr/bin/env python3
"""Behavioral tests for Keel's deterministic parallel scheduler."""

import importlib.util
import json
import subprocess
import sys
import tempfile
import time
import unittest
from types import SimpleNamespace as Args
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "keel" / "scripts" / "keel_parallel.py"
WORKER = ROOT / "tests" / "fixtures" / "parallel_worker.py"
SPEC = importlib.util.spec_from_file_location("keel_parallel", HELPER)
kp = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(kp)


def execution(paths, resources=(), reads=(), writes=(), parallel="eligible"):
    return {
        "write_paths": list(paths),
        "contracts": {"reads": list(reads), "writes": list(writes)},
        "exclusive_resources": list(resources),
        "parallel": parallel,
        "serial_reason": "must run alone" if parallel == "serial" else None,
    }


def slice_(slice_id, paths, depends=(), **kwargs):
    return {"id": slice_id, "status": "not-started", "depends_on": list(depends), "execution": execution(paths, **kwargs)}


class ParallelSchedulerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="keel parallel ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plan_path = self.root / "plan.json"
        self.run_path = self.root / "run.json"
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-b", "develop"], cwd=self.repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Keel Test"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "keel@example.invalid"], cwd=self.repo, check=True)
        (self.repo / "README.md").write_text("fixture\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-m", "fixture"], cwd=self.repo, check=True, capture_output=True)
        self.base_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.repo, check=True, text=True, capture_output=True
        ).stdout.strip()

    def write(self, path, value):
        Path(path).write_text(json.dumps(value), encoding="utf-8")

    def plan(self, slices):
        value = {"schema": "keel.plan/2", "slices": slices}
        self.write(self.plan_path, value)
        return value

    def make_run(self, plan, max_workers=2):
        value = kp.new_run(str(self.plan_path), "R-1", "develop", max_workers, str((self.repo / ".git").resolve()))
        self.write(self.run_path, value)
        return value

    def assignment(self, item, attempt):
        worktree = self.root / f"worktree {attempt}"
        branch = f"slice/{item['id']}-{attempt}"
        base = kp.git_output(self.repo, "rev-parse", "HEAD")
        subprocess.run(
            ["git", "worktree", "add", "-b", branch, str(worktree), base],
            cwd=self.repo,
            check=True,
            capture_output=True,
        )
        return {
            "schema": kp.ASSIGNMENT_SCHEMA,
            "run_id": "R-1",
            "attempt_id": attempt,
            "slice_id": item["id"],
            "repo_id": str((self.repo / ".git").resolve()),
            "worktree": str(worktree.resolve()),
            "branch": branch,
            "base_commit": base,
            "coordinator_id": "test-coordinator",
            "write_paths": item["execution"]["write_paths"],
            "inputs": [],
            "acceptance_criteria": [],
            "test_commands": [],
            "environment": {},
            "deadline_seconds": 20,
        }

    def claim(self, plan, item, attempt, deadline=20):
        assignment = self.assignment(item, attempt)
        assignment["deadline_seconds"] = deadline
        path = self.root / f"{attempt}.assignment.json"
        self.write(path, assignment)
        args = type("Args", (), {"run": str(self.run_path), "plan": str(self.plan_path), "assignment": str(path)})
        kp.command_claim(args)
        return assignment, path

    def report(self, assignment, assignment_path, changed=()):
        worktree = Path(assignment["worktree"])
        code = kp.git_output(worktree, "rev-parse", "HEAD")
        result = {key: assignment[key] for key in ("run_id", "attempt_id", "slice_id", "repo_id", "worktree", "branch", "base_commit")}
        result.update(schema=kp.RESULT_SCHEMA, outcome="ready", code_commit=code, changed_paths=list(changed),
                      tests=[], review_findings=[], state_contributions={}, timing={"active_seconds": 0})
        path = worktree / "docs/.keel/slices" / assignment["run_id"] / assignment["slice_id"] / (assignment["attempt_id"] + ".json")
        path.parent.mkdir(parents=True); self.write(path, result)
        kp.git_output(worktree, "add", str(path.relative_to(worktree)))
        kp.git_output(worktree, "commit", "-m", "worker report")
        kp.command_record_result(Args(run=str(self.run_path), plan=str(self.plan_path), assignment=str(assignment_path), result=str(path)))
        return code

    def integrate(self, assignment):
        previous = kp.git_output(self.repo, "rev-parse", "HEAD")
        candidate = self.root / ("candidate-" + assignment["attempt_id"])
        branch = "candidate/" + assignment["attempt_id"]
        kp.git_output(self.repo, "worktree", "add", "-b", branch, str(candidate), previous)
        kp.git_output(candidate, "merge", "--no-ff", assignment["branch"], "-m", "integrate worker")
        commit = kp.git_output(candidate, "rev-parse", "HEAD")
        evidence = self.root / "integration.json"
        result = json.loads(kp.load_run(self.run_path)["attempts"][assignment["attempt_id"]]["result_fingerprint"])
        verification = ("from pathlib import Path; import json; "
                        "paths=json.loads(" + repr(json.dumps(result["changed_paths"])) + "); "
                        "assert Path('README.md').is_file(); "
                        "assert all(Path(p).is_file() for p in paths)")
        kp.command_verify_integration(Args(run=str(self.run_path), attempt=assignment["attempt_id"],
            candidate=str(candidate), previous_head=previous, evidence=str(evidence), timeout=5,
            check_command=[sys.executable, "-c", verification]))
        kp.git_output(self.repo, "merge", "--ff-only", branch)
        return Args(run=str(self.run_path), attempt=assignment["attempt_id"], commit=commit, evidence=str(evidence))

    def test_reject_two_claims_in_same_checkout(self):
        a, b = slice_("A", ["a/"]), slice_("B", ["b/"])
        plan = self.plan([a, b]); self.make_run(plan)
        assignment, _ = self.claim(plan, a, "A-1")
        same = dict(assignment, slice_id="B", attempt_id="B-1", write_paths=["b/"])
        path = self.root / "b.json"; self.write(path, same)
        with self.assertRaises(kp.ParallelError):
            kp.command_claim(Args(run=str(self.run_path), plan=str(self.plan_path), assignment=str(path)))

    def test_locks_are_shared_across_journal_directories(self):
        self.plan([slice_("A", ["a/"])]); run = self.make_run(None)
        other = self.root / "other" / "run.json"; other.parent.mkdir()
        kp.write_json_atomic(other, dict(run, run_id="R-2"))
        with kp.run_lock(self.run_path):
            with self.assertRaises(kp.ParallelError):
                with kp.run_lock(other):
                    self.fail("second lock acquired")

    def test_fake_integration_is_rejected(self):
        plan = self.plan([slice_("A", ["a/"])]); run = self.make_run(plan)
        run["attempts"]["A-1"] = {"slice_id": "A", "state": "ready-to-integrate"}
        kp.write_json_atomic(self.run_path, run)
        with self.assertRaises(kp.ParallelError):
            kp.command_record_integration(Args(run=str(self.run_path), attempt="A-1", commit="not-a-commit", evidence=None))

    def test_legacy_done_dependency_and_future_sprint(self):
        plan = {"schema": "keel.plan/2", "sprints": [
            {"sprint": 1, "status": "done", "slices": [{"id": "OLD", "status": "done"}]},
            {"sprint": 2, "status": "in-progress", "slices": [slice_("A", ["a/"], depends=["OLD"])]},
            {"sprint": 3, "status": "not-started", "slices": [slice_("B", ["b/"])]},
        ]}
        self.write(self.plan_path, plan)
        self.assertEqual(kp.ready_slices(plan, self.make_run(plan))["ready"], ["A"])

    def test_changed_registered_assignment_rejected_before_launch(self):
        item = slice_("A", ["a/"]); plan = self.plan([item]); self.make_run(plan)
        assignment, path = self.claim(plan, item, "A-1")
        assignment["deadline_seconds"] += 10; self.write(path, assignment)
        with patch.object(kp.subprocess, "Popen") as launch:
            with self.assertRaises(kp.ParallelError):
                kp.command_run_worker(Args(run=str(self.run_path), plan=str(self.plan_path), assignment=str(path),
                    envelope=str(self.root / "exit.json"), worker_command=[sys.executable, "-c", "pass"]))
            launch.assert_not_called()

    def test_launch_under_held_lock_does_not_start_process(self):
        item = slice_("A", ["a/"]); plan = self.plan([item]); self.make_run(plan)
        assignment, path = self.claim(plan, item, "A-1")
        marker = self.root / "should-not-exist"
        with kp.run_lock(self.run_path):
            with self.assertRaises(kp.ParallelError):
                kp.command_run_worker(Args(run=str(self.run_path), plan=str(self.plan_path), assignment=str(path),
                    envelope=str(self.root / "exit.json"), worker_command=[sys.executable, "-c",
                    "from pathlib import Path; Path(%r).touch()" % str(marker)]))
        self.assertFalse(marker.exists())
        self.assertEqual(kp.load_run(self.run_path)["attempts"]["A-1"]["state"], "claimed")

    def test_second_run_cannot_claim_while_first_holds_resources(self):
        item = slice_("A", ["a/"]); plan = self.plan([item]); self.make_run(plan)
        self.claim(plan, item, "A-1")
        other = self.root / "second.json"
        kp.write_json_atomic(other, kp.new_run(str(self.plan_path), "R-2", "develop", 2, str(self.repo / ".git")))
        assignment = self.assignment(item, "A-2"); assignment["run_id"] = "R-2"
        path = self.root / "second-assignment.json"; self.write(path, assignment)
        with self.assertRaisesRegex(kp.ParallelError, "another run"):
            kp.command_claim(Args(run=str(other), plan=str(self.plan_path), assignment=str(path)))

    def test_substituted_assignment_cannot_change_another_attempt(self):
        a, b = slice_("A", ["a/"]), slice_("B", ["b/"])
        plan = self.plan([a, b]); self.make_run(plan); self.claim(plan, a, "A-1")
        replacement = self.assignment(b, "replacement"); replacement["attempt_id"] = "A-1"
        path = self.root / "replacement.json"; self.write(path, replacement)
        result = dict(replacement, schema=kp.RESULT_SCHEMA, outcome="blocked", needs_user="question",
                      changed_paths=[], tests=[], review_findings=[], state_contributions={}, timing={})
        result_path = self.root / "result.json"; self.write(result_path, result)
        with self.assertRaisesRegex(kp.ParallelError, "immutable registered"):
            kp.command_record_result(Args(run=str(self.run_path), plan=str(self.plan_path), assignment=str(path), result=str(result_path)))
        self.assertEqual(kp.load_run(self.run_path)["attempts"]["A-1"]["state"], "claimed")

    def test_changed_scope_is_rejected_but_accounting_can_update(self):
        item = slice_("A", ["a/"]); plan = self.plan([item]); run = self.make_run(plan)
        item["actual_hours"] = 2; item["status"] = "done"; self.plan([item])
        self.assertEqual(kp.bound_plan(run, str(self.plan_path))["slices"][0]["status"], "not-started")
        item["execution"]["write_paths"] = ["other/"]; self.plan([item])
        with self.assertRaisesRegex(kp.ParallelError, "plan changed"):
            kp.command_ready(Args(run=str(self.run_path), plan=str(self.plan_path)))

    def test_missing_ownership_is_waiting_and_serial_stays_coordinator_owned(self):
        plan = self.plan([{"id": "legacy", "status": "not-started"}, slice_("serial", ["docs/"], parallel="serial")])
        ready = kp.ready_slices(plan, self.make_run(plan))
        self.assertEqual(ready["ready"], [])
        self.assertIn("missing execution", ready["waiting"]["legacy"])
        self.assertIn("coordinator-owned", ready["waiting"]["serial"])

    def test_failed_review_retains_claims_until_explicit_resolution(self):
        a, b = slice_("A", ["a/"]), slice_("B", ["a/"])
        plan = self.plan([a, b]); self.make_run(plan)
        assignment, path = self.claim(plan, a, "A-1")
        code = self.report(assignment, path)
        kp.command_record_review(Args(run=str(self.run_path), attempt="A-1", code_commit=code,
                                     verdict="fail", evidence="repair required"))
        self.assertEqual(kp.ready_slices(plan, kp.load_run(self.run_path))["ready"], [])
        kp.command_resolve(Args(run=str(self.run_path), attempt="A-1", evidence="native worker stopped; branch preserved"))
        self.assertEqual(kp.ready_slices(plan, kp.load_run(self.run_path))["ready"], ["A"])

    def test_finished_worker_frees_capacity_but_keeps_source_claim(self):
        a, b, c = slice_("A", ["a/"]), slice_("B", ["a/"]), slice_("C", ["c/"])
        plan = self.plan([a, b, c]); self.make_run(plan, max_workers=1)
        assignment, path = self.claim(plan, a, "A-1")
        self.report(assignment, path)
        readiness = kp.ready_slices(plan, kp.load_run(self.run_path))
        self.assertEqual(readiness["ready"], ["C"])
        self.assertIn("overlap", readiness["waiting"]["B"])
        self.assertEqual(readiness["executing"], 0)

    def test_integration_evidence_must_cover_current_head_and_green_checks(self):
        item = slice_("A", ["a/"]); plan = self.plan([item]); self.make_run(plan)
        assignment, path = self.claim(plan, item, "A-1")
        code = self.report(assignment, path)
        kp.command_record_review(Args(run=str(self.run_path), attempt="A-1", code_commit=code, verdict="pass", evidence="fixture review"))
        args = self.integrate(assignment)
        evidence = kp.read_json(args.evidence); evidence["checks"][0]["exit_code"] = 1; self.write(args.evidence, evidence)
        with self.assertRaisesRegex(kp.ParallelError, "verify-integration"):
            kp.command_record_integration(args)
        self.assertEqual(kp.load_run(self.run_path)["integrated"], {})
        evidence["checks"][0]["exit_code"] = 0; self.write(args.evidence, evidence)
        kp.git_output(self.repo, "commit", "--allow-empty", "-m", "branch moved")
        with self.assertRaisesRegex(kp.ParallelError, "actual integration branch head"):
            kp.command_record_integration(args)

    def integrated_slices(self, ids):
        items = [slice_(i, [i.lower() + "/"]) for i in ids]
        plan = self.plan(items); self.make_run(plan, max_workers=len(ids))
        claimed = [self.claim(plan, item, item["id"] + "-1") for item in items]
        for assignment, path in claimed:
            code = self.report(assignment, path)
            kp.command_record_review(Args(run=str(self.run_path), attempt=assignment["attempt_id"],
                                          code_commit=code, verdict="pass", evidence="review"))
            kp.command_record_integration(self.integrate(assignment))
        return claimed

    def batch(self, command, candidate=None):
        return kp.command_verify_batch(Args(run=str(self.run_path), candidate=str(candidate or self.repo),
            evidence=str(self.root / "batch.json"), timeout=5, check_command=command))

    def test_full_suite_runs_once_after_the_workers_are_integrated(self):
        self.integrated_slices(["A", "B"])
        self.assertEqual(kp.command_status(Args(run=str(self.run_path)))["batch"]["state"], "pending")
        record = self.batch([sys.executable, "-c", "pass"])
        self.assertTrue(record["passed"])
        self.assertEqual(record["covers"], ["A", "B"])
        self.assertEqual(kp.command_status(Args(run=str(self.run_path)))["batch"]["state"], "verified")

    def test_batch_waits_for_workers_in_flight(self):
        a, b = slice_("A", ["a/"]), slice_("B", ["b/"])
        plan = self.plan([a, b]); self.make_run(plan)
        assignment, path = self.claim(plan, a, "A-1"); code = self.report(assignment, path)
        kp.command_record_review(Args(run=str(self.run_path), attempt="A-1", code_commit=code, verdict="pass", evidence="r"))
        kp.command_record_integration(self.integrate(assignment))
        self.claim(plan, b, "B-1")
        with self.assertRaisesRegex(kp.ParallelError, "no worker is in flight: B"):
            self.batch([sys.executable, "-c", "pass"])

    def test_failed_batch_stays_failed_until_a_fix_is_verified(self):
        self.integrated_slices(["A"])
        with self.assertRaisesRegex(kp.ParallelError, "batch checks failed"):
            self.batch([sys.executable, "-c", "raise SystemExit(3)"])
        self.assertEqual(kp.command_status(Args(run=str(self.run_path)))["batch"]["state"], "failed")
        kp.git_output(self.repo, "commit", "--allow-empty", "-m", "coordinator fix")
        self.assertEqual(kp.command_status(Args(run=str(self.run_path)))["batch"]["state"], "pending")
        self.assertTrue(self.batch([sys.executable, "-c", "pass"])["passed"])
        self.assertEqual(kp.command_status(Args(run=str(self.run_path)))["batch"]["state"], "verified")

    def test_batch_requires_a_clean_checkout_at_the_integration_head(self):
        self.integrated_slices(["A"])
        stale = self.root / "stale"
        kp.git_output(self.repo, "worktree", "add", "-b", "stale", str(stale), self.base_commit)
        with self.assertRaisesRegex(kp.ParallelError, "integration head"):
            self.batch([sys.executable, "-c", "pass"], stale)
        (self.repo / "dirty.txt").write_text("x")
        with self.assertRaisesRegex(kp.ParallelError, "clean"):
            self.batch([sys.executable, "-c", "pass"])

    def test_test_lane_never_runs_two_suites_at_once(self):
        self.integrated_slices(["A"])
        marker = self.root / "suite-started"
        slow = ("import time, pathlib; pathlib.Path(%r).write_text('x'); time.sleep(2)" % str(marker))
        command = [sys.executable, "-B", str(HELPER), "verify-batch", "--run", str(self.run_path),
                   "--candidate", str(self.repo), "--evidence", str(self.root / "first.json"),
                   "--", sys.executable, "-c", slow]
        first = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        deadline = time.monotonic() + 8
        while not marker.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertTrue(marker.exists())
        with kp.run_lock(self.run_path):
            run = kp.load_run(self.run_path)
        with self.assertRaisesRegex(kp.ParallelError, "test lane busy"):
            with kp.test_lane(run):
                pass
        first.communicate(timeout=10)
        self.assertEqual(first.returncode, 0)

    def test_worker_role_checks_real_cwd_and_registration(self):
        item = slice_("A", ["a/"]); plan = self.plan([item]); self.make_run(plan)
        assignment, path = self.claim(plan, item, "A-1")
        command = [sys.executable, "-B", str(HELPER), "worker-check", "--run", str(self.run_path), "--assignment", str(path)]
        valid = subprocess.run(command, cwd=assignment["worktree"], capture_output=True, text=True)
        invalid = subprocess.run(command, cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(valid.returncode, 0, valid.stdout)
        self.assertNotEqual(invalid.returncode, 0)
        aggregate = Path(assignment["worktree"]) / "docs/PROGRESS.md"
        aggregate.parent.mkdir(); aggregate.write_text("unauthorized update")
        blocked = subprocess.run(command, cwd=assignment["worktree"], capture_output=True, text=True)
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("docs/PROGRESS.md", blocked.stdout)

    def test_two_concurrent_launches_execute_the_worker_once(self):
        item = slice_("A", ["a/"]); plan = self.plan([item]); self.make_run(plan)
        assignment, path = self.claim(plan, item, "A-1")
        marker = self.root / "launch-count"
        script = "import time; f=open(%r,'a'); f.write('started\\n'); f.close(); time.sleep(.3)" % str(marker)
        command = [sys.executable, "-B", str(HELPER), "run-worker", "--run", str(self.run_path),
                   "--plan", str(self.plan_path), "--assignment", str(path), "--envelope", str(self.root / "exit.json"),
                   "--", sys.executable, "-c", script]
        processes = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
        for process in processes:
            process.communicate(timeout=8)
        self.assertEqual(sorted(p.returncode for p in processes), [0, 1])
        self.assertEqual(marker.read_text().splitlines(), ["started"])

    def test_failed_candidate_check_never_moves_integration_branch(self):
        item = slice_("A", ["a/"]); plan = self.plan([item]); self.make_run(plan)
        assignment, path = self.claim(plan, item, "A-1"); code = self.report(assignment, path)
        kp.command_record_review(Args(run=str(self.run_path), attempt="A-1", code_commit=code, verdict="pass", evidence="review"))
        candidate = self.root / "candidate"
        kp.git_output(self.repo, "worktree", "add", "-b", "candidate", str(candidate), "develop")
        kp.git_output(candidate, "merge", "--no-ff", assignment["branch"], "-m", "candidate")
        with self.assertRaisesRegex(kp.ParallelError, "checks failed"):
            kp.command_verify_integration(Args(run=str(self.run_path), attempt="A-1", candidate=str(candidate),
                previous_head=self.base_commit, evidence=str(self.root / "checks.json"), timeout=5,
                check_command=[sys.executable, "-c", "raise SystemExit(1)"]))
        self.assertEqual(kp.git_output(self.repo, "rev-parse", "HEAD"), self.base_commit)
        self.assertEqual(kp.load_run(self.run_path)["integrated"], {})

    def test_integration_record_is_idempotent_after_restart(self):
        item = slice_("A", ["a/"]); plan = self.plan([item]); self.make_run(plan)
        assignment, path = self.claim(plan, item, "A-1"); code = self.report(assignment, path)
        kp.command_record_review(Args(run=str(self.run_path), attempt="A-1", code_commit=code, verdict="pass", evidence="review"))
        args = self.integrate(assignment)
        kp.command_record_integration(args)
        self.assertTrue(kp.command_record_integration(args)["idempotent"])
        self.assertEqual(sum(e["event"] == "integrated" for e in kp.load_run(self.run_path)["events"]), 1)

    def test_symlink_created_under_owned_directory_cannot_escape(self):
        item = slice_("A", ["a/"]); plan = self.plan([item]); self.make_run(plan)
        assignment, path = self.claim(plan, item, "A-1")
        root = Path(assignment["worktree"]); (root / "a").mkdir()
        (root / "a" / "escape").symlink_to(self.root / "outside")
        kp.git_output(root, "add", "a/escape"); kp.git_output(root, "commit", "-m", "symlink")
        with self.assertRaisesRegex(kp.ParallelError, "escapes worktree"):
            self.report(assignment, path, ["a/escape"])

    def test_dependency_rolling_queue_starts_c_after_a_integration_while_b_active(self):
        a = slice_("A", ["src/a/"])
        b = slice_("B", ["src/b/"])
        c = slice_("C", ["src/c/"], depends=["A"])
        plan = self.plan([a, b, c])
        run = self.make_run(plan)
        self.assertEqual(kp.ready_slices(plan, run)["ready"], ["A", "B"])
        assignment, path = self.claim(plan, a, "A-1")
        other, other_path = self.claim(plan, b, "B-1")
        started, release = self.root / "b-started", self.root / "b-release"
        process = subprocess.Popen([sys.executable, "-B", str(HELPER), "run-worker", "--plan", str(self.plan_path),
            "--run", str(self.run_path), "--assignment", str(other_path), "--envelope", str(self.root / "b-exit.json"),
            "--", sys.executable, "-B", str(WORKER), str(other_path), str(started), str(release)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + 10
            while not started.exists() and time.monotonic() < deadline:
                time.sleep(.01)
            self.assertTrue(started.exists(), "B never reached synchronization barrier")
            self.assertIsNone(process.poll())
            kp.command_run_worker(Args(run=str(self.run_path), plan=str(self.plan_path), assignment=str(path),
                envelope=str(self.root / "a-exit.json"), worker_command=[sys.executable, "-B", str(WORKER), str(path), str(self.root / "a-started")]))
            report = Path(assignment["worktree"]) / "docs/.keel/slices/R-1/A/A-1.json"
            code = kp.read_json(report)["code_commit"]
            kp.command_record_result(Args(run=str(self.run_path), plan=str(self.plan_path), assignment=str(path), result=str(report)))
            kp.command_record_review(Args(run=str(self.run_path), attempt="A-1", code_commit=code,
                                         verdict="pass", evidence="independent fixture review"))
            kp.command_record_integration(self.integrate(assignment))
            third, third_path = self.claim(plan, c, "C-1")
            kp.command_run_worker(Args(run=str(self.run_path), plan=str(self.plan_path), assignment=str(third_path),
                envelope=str(self.root / "c-exit.json"), worker_command=[sys.executable, "-B", str(WORKER), str(third_path), str(self.root / "c-started")]))
            self.assertTrue((Path(third["worktree"]) / "src/a/value.txt").is_file())
            self.assertIsNone(process.poll(), "B must still be held when C becomes ready")
        finally:
            release.touch()
            process.communicate(timeout=8)
        ready = kp.ready_slices(plan, kp.load_run(self.run_path))
        self.assertEqual(ready["ready"], [])
        self.assertEqual(ready["active"], 2)

    def test_cycles_and_missing_dependencies_are_rejected(self):
        with self.assertRaisesRegex(kp.ParallelError, "cycle"):
            kp.validate_plan({"slices": [slice_("A", ["a"], depends=["B"]), slice_("B", ["b"], depends=["A"])]})
        with self.assertRaisesRegex(kp.ParallelError, "unknown dependency"):
            kp.validate_plan({"slices": [slice_("A", ["a"], depends=["MISSING"])]})

    def test_path_resource_and_contract_conflicts_serialize(self):
        cases = [
            (slice_("A", ["src/core/"]), slice_("B", ["src/core/file.py"]), "write paths overlap"),
            (slice_("A", ["a"], resources=["db"]), slice_("B", ["b"], resources=["db"]), "exclusive resource"),
            (slice_("A", ["a"], writes=["api-v1"]), slice_("B", ["b"], reads=["api-v1"]), "contract conflict"),
        ]
        for first, second, reason in cases:
            with self.subTest(reason=reason):
                plan = self.plan([first, second])
                run = self.make_run(plan)
                run["attempts"] = {"first": {"slice_id": "A", "state": "running"}}
                ready = kp.ready_slices(plan, run)
                self.assertEqual(ready["ready"], [])
                self.assertIn(reason, ready["waiting"]["B"])

    def test_aggregate_paths_and_traversal_are_rejected(self):
        for path in ["docs/PROGRESS.md", "../escape", "/absolute", "src/*", "src/../other", ".", "src//file"]:
            with self.subTest(path=path), self.assertRaises(kp.ParallelError):
                kp.validate_plan({"slices": [slice_("A", [path])]})
        self.assertFalse(kp.path_contains("src/file.py", "src/file.py/other"))

    def test_duplicate_claim_is_rejected_and_result_is_idempotent(self):
        item = slice_("A", ["src/a.py"])
        plan = self.plan([item])
        self.make_run(plan)
        assignment, assignment_path = self.claim(plan, item, "A-1")
        args = type("Args", (), {"run": str(self.run_path), "plan": str(self.plan_path), "assignment": str(assignment_path)})
        with self.assertRaisesRegex(kp.ParallelError, "already exists"):
            kp.command_claim(args)
        worktree = Path(assignment["worktree"])
        (worktree / "src").mkdir()
        (worktree / "src" / "a.py").write_text("value = 1\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/a.py"], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "-m", "implement A"], cwd=worktree, check=True, capture_output=True)
        code_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=worktree, check=True, text=True, capture_output=True
        ).stdout.strip()
        result = {**{key: assignment[key] for key in ("run_id", "attempt_id", "slice_id", "repo_id", "worktree", "branch", "base_commit")},
                  "schema": kp.RESULT_SCHEMA, "outcome": "ready", "code_commit": code_commit,
                  "changed_paths": ["src/a.py"], "tests": [], "review_findings": [],
                  "state_contributions": {}, "timing": {"active_seconds": 1}}
        result_path = worktree / "docs" / ".keel" / "slices" / "R-1" / "A" / "A-1.json"
        result_path.parent.mkdir(parents=True)
        self.write(result_path, result)
        subprocess.run(["git", "add", str(result_path.relative_to(worktree))], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "-m", "report A"], cwd=worktree, check=True, capture_output=True)
        record = type("Args", (), {"run": str(self.run_path), "plan": str(self.plan_path), "assignment": str(assignment_path), "result": str(result_path)})
        self.assertTrue(kp.command_record_result(record)["recorded"])
        self.assertTrue(kp.command_record_result(record)["idempotent"])

    def test_out_of_scope_result_is_rejected(self):
        item = slice_("A", ["src/a/"])
        plan = self.plan([item])
        run = self.make_run(plan)
        assignment = self.assignment(item, "A-1")
        result = {**{key: assignment[key] for key in ("run_id", "attempt_id", "slice_id", "repo_id", "worktree", "branch", "base_commit")},
                  "schema": kp.RESULT_SCHEMA, "outcome": "ready", "code_commit": "b" * 40,
                  "changed_paths": ["src/other.py"], "tests": [], "review_findings": [],
                  "state_contributions": {}, "timing": {"active_seconds": 1}}
        with self.assertRaisesRegex(kp.ParallelError, "out-of-scope"):
            kp.validate_result(result, assignment)

    def test_review_is_required_before_integration(self):
        item = slice_("A", ["src/a.py"])
        plan = self.plan([item])
        self.make_run(plan)
        assignment, assignment_path = self.claim(plan, item, "A-1")
        result = {**{key: assignment[key] for key in ("run_id", "attempt_id", "slice_id", "repo_id", "worktree", "branch", "base_commit")},
                  "schema": kp.RESULT_SCHEMA, "outcome": "ready", "code_commit": self.base_commit,
                  "changed_paths": [], "tests": [], "review_findings": [],
                  "state_contributions": {}, "timing": {"active_seconds": 1}}
        worktree = Path(assignment["worktree"])
        result_path = worktree / "docs" / ".keel" / "slices" / "R-1" / "A" / "A-1.json"
        result_path.parent.mkdir(parents=True)
        self.write(result_path, result)
        subprocess.run(["git", "add", str(result_path.relative_to(worktree))], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "-m", "report A"], cwd=worktree, check=True, capture_output=True)
        kp.command_record_result(type("Args", (), {"run": str(self.run_path), "plan": str(self.plan_path),
                                                    "assignment": str(assignment_path), "result": str(result_path)}))
        integrate = type("Args", (), {"run": str(self.run_path), "attempt": "A-1", "commit": self.base_commit})
        with self.assertRaisesRegex(kp.ParallelError, "not ready"):
            kp.command_record_integration(integrate)
        review = type("Args", (), {"run": str(self.run_path), "attempt": "A-1", "code_commit": self.base_commit,
                                    "verdict": "pass", "evidence": "reviewer:fixture"})
        self.assertEqual(kp.command_record_review(review)["state"], "ready-to-integrate")
        self.assertTrue(kp.command_record_integration(self.integrate(assignment))["recorded"])

    def test_wrong_branch_and_symlink_escape_fail_closed(self):
        item = slice_("A", ["src/a/"])
        assignment = self.assignment(item, "A-1")
        wrong = dict(assignment, branch="wrong-branch")
        with self.assertRaisesRegex(kp.ParallelError, "branch mismatch"):
            kp.validate_assignment_identity(wrong)
        outside = self.root / "outside"
        outside.mkdir()
        worktree = Path(assignment["worktree"])
        (worktree / "src").mkdir()
        (worktree / "src" / "a").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(kp.ParallelError, "escapes worktree"):
            kp.validate_assignment_identity(assignment)

    def test_unexpected_commit_after_report_is_rejected(self):
        item = slice_("A", ["src/a.py"])
        plan = self.plan([item])
        self.make_run(plan)
        assignment, assignment_path = self.claim(plan, item, "A-1")
        worktree = Path(assignment["worktree"])
        (worktree / "src").mkdir()
        (worktree / "src" / "a.py").write_text("one\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/a.py"], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "-m", "code"], cwd=worktree, check=True, capture_output=True)
        code_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=worktree, check=True, text=True, capture_output=True
        ).stdout.strip()
        result = {**{key: assignment[key] for key in ("run_id", "attempt_id", "slice_id", "repo_id", "worktree", "branch", "base_commit")},
                  "schema": kp.RESULT_SCHEMA, "outcome": "ready", "code_commit": code_commit,
                  "changed_paths": ["src/a.py"], "tests": [], "review_findings": [],
                  "state_contributions": {}, "timing": {"active_seconds": 1}}
        result_path = worktree / "docs" / ".keel" / "slices" / "R-1" / "A" / "A-1.json"
        result_path.parent.mkdir(parents=True)
        self.write(result_path, result)
        subprocess.run(["git", "add", str(result_path.relative_to(worktree))], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "-m", "report"], cwd=worktree, check=True, capture_output=True)
        (worktree / "src" / "a.py").write_text("two\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/a.py"], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "-m", "unexpected"], cwd=worktree, check=True, capture_output=True)
        args = type("Args", (), {"run": str(self.run_path), "plan": str(self.plan_path),
                                  "assignment": str(assignment_path), "result": str(result_path)})
        with self.assertRaisesRegex(kp.ParallelError, "unexpected commits"):
            kp.command_record_result(args)

    def test_reconcile_marks_a_dead_worker_failed(self):
        item = slice_("A", ["src/a.py"])
        plan = self.plan([item])
        run = self.make_run(plan)
        run["attempts"] = {"A-1": {"slice_id": "A", "state": "running", "pid": 99999999}}
        kp.write_json_atomic(self.run_path, run)
        args = type("Args", (), {"run": str(self.run_path), "plan": str(self.plan_path)})
        result = kp.command_reconcile(args)
        self.assertEqual(result["changes"], [{"attempt_id": "A-1", "state": "failed"}])

    def test_run_worker_sets_cwd_and_observes_success(self):
        item = slice_("A", ["src/a/"])
        plan = self.plan([item])
        self.make_run(plan)
        assignment, assignment_path = self.claim(plan, item, "A-1")
        envelope = self.root / "envelope.json"
        args = type("Args", (), {"plan": str(self.plan_path), "run": str(self.run_path),
                                  "assignment": str(assignment_path), "envelope": str(envelope),
                                  "worker_command": [sys.executable, "-c", "import pathlib; pathlib.Path('cwd-ok').write_text('yes')"]})
        result = kp.command_run_worker(args)
        self.assertEqual(result["returncode"], 0)
        self.assertTrue((Path(assignment["worktree"]) / "cwd-ok").exists())

    def test_run_worker_deadline_is_bounded_and_preserves_partial_work(self):
        item = slice_("A", ["src/a/"])
        plan = self.plan([item])
        self.make_run(plan)
        assignment, assignment_path = self.claim(plan, item, "A-1", deadline=1)
        envelope = self.root / "envelope.json"
        self.write(assignment_path, assignment)
        command = "import pathlib,time; pathlib.Path('partial').write_text('kept'); time.sleep(30)"
        args = type("Args", (), {"plan": str(self.plan_path), "run": str(self.run_path),
                                  "assignment": str(assignment_path), "envelope": str(envelope),
                                  "worker_command": [sys.executable, "-c", command]})
        started = time.monotonic()
        with self.assertRaisesRegex(kp.ParallelError, "deadline"):
            kp.command_run_worker(args)
        self.assertLess(time.monotonic() - started, 8)
        self.assertTrue((Path(assignment["worktree"]) / "partial").exists())
        self.assertTrue(json.loads(envelope.read_text())["timed_out"])

    def test_paths_with_spaces_work_through_cli(self):
        item = slice_("A", ["src/with space/"])
        self.plan([item])
        completed = subprocess.run([sys.executable, "-B", str(HELPER), "validate", "--plan", str(self.plan_path)],
                                   check=False, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        self.assertTrue(json.loads(completed.stdout)["valid"])

    def add_worktree(self, name, commit=False):
        path = self.root / name
        subprocess.run(["git", "worktree", "add", "-b", name, str(path), "develop"],
                       cwd=self.repo, check=True, capture_output=True)
        if commit:
            (path / f"{name}.txt").write_text("work\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=path, check=True)
            subprocess.run(["git", "commit", "-m", name], cwd=path, check=True, capture_output=True)
        return path

    def reap(self, apply=False, min_idle_hours=0.0, run=None):
        return kp.command_reap_worktrees(Args(
            repo=str(self.repo), integration_ref="develop", run=run,
            min_idle_hours=min_idle_hours, apply=apply,
        ))

    def branches(self):
        return subprocess.run(["git", "branch", "--format=%(refname:short)"], cwd=self.repo,
                              check=True, text=True, capture_output=True).stdout.split()

    def worktree(self, name, branch):
        path = self.root / name
        subprocess.run(["git", "worktree", "add", "-q", "-b", branch, str(path)], cwd=self.repo, check=True)
        return path

    def sweep(self, apply=False, stale=0.0, busy=frozenset()):
        return kp.sweep_repository(self.repo.resolve(), stale, apply, set(busy))

    def commit_in(self, path):
        (path / "work.txt").write_text("work\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=path, check=True)
        subprocess.run(["git", "commit", "-qm", "work"], cwd=path, check=True)

    def test_sweep_removes_a_clean_unmerged_worktree_and_keeps_its_branch(self):
        path = self.worktree("agent", "wip/agent")
        self.commit_in(path)
        report = self.sweep(apply=True)
        self.assertEqual(1, len(report["removed"]))
        self.assertFalse(path.exists())
        self.assertIn("wip/agent", self.branches())

    def test_sweep_only_reports_without_apply(self):
        path = self.worktree("agent", "wip/agent")
        self.assertEqual(1, len(self.sweep()["retirable"]))
        self.assertTrue(path.exists())

    def test_sweep_keeps_dirty_recent_and_busy_worktrees(self):
        dirty = self.worktree("dirty", "wip/dirty")
        (dirty / "new.txt").write_text("x\n", encoding="utf-8")
        recent = self.worktree("recent", "wip/recent")
        self.assertEqual({str(dirty.resolve()): "uncommitted changes",
                          str(recent.resolve()): "used recently"},
                         {str(Path(i["path"]).resolve()): i["reason"] for i in self.sweep(apply=True, stale=24.0)["kept"]})
        busy = self.worktree("busy", "wip/busy")
        report = self.sweep(apply=True, busy={busy.resolve() / "sub"})
        self.assertIn("a process is working in it", [i["reason"] for i in report["kept"]])

    def test_sweep_keeps_a_person_lock_and_removes_a_dead_process_lock(self):
        held = self.worktree("held", "wip/held")
        subprocess.run(["git", "worktree", "lock", "--reason", "mine", str(held)], cwd=self.repo, check=True)
        dead = self.worktree("dead", "wip/dead")
        spent = subprocess.Popen(["true"]); spent.wait()
        subprocess.run(["git", "worktree", "lock", "--reason", f"claude agent x (pid {spent.pid} start y)", str(dead)],
                       cwd=self.repo, check=True)
        report = self.sweep(apply=True)
        self.assertFalse(dead.exists())
        self.assertTrue(held.exists())
        self.assertEqual(["locked"], [i["reason"] for i in report["kept"]])

    def test_sweep_keeps_detached_commits_no_branch_holds(self):
        path = self.worktree("loose", "wip/loose")
        subprocess.run(["git", "checkout", "-q", "--detach"], cwd=path, check=True)
        self.commit_in(path)
        self.assertEqual(["detached commits no branch holds"], [i["reason"] for i in self.sweep(apply=True)["kept"]])

    def test_sweep_never_deletes_a_long_lived_branch(self):
        subprocess.run(["git", "branch", "main"], cwd=self.repo, check=True)
        path = self.root / "stable"
        subprocess.run(["git", "worktree", "add", "-q", str(path), "main"], cwd=self.repo, check=True)
        self.assertEqual(1, len(self.sweep(apply=True)["removed"]))
        self.assertIn("main", self.branches())

    def test_sweep_does_not_restart_the_idle_clock_it_measures(self):
        path = self.worktree("agent", "wip/agent")
        git_dir = Path(subprocess.run(["git", "rev-parse", "--absolute-git-dir"], cwd=path, check=True,
                                      text=True, capture_output=True).stdout.strip())
        old = time.time() - 7200
        (path / "README.md").touch()
        for item in (git_dir / "index", git_dir / "HEAD", path):
            kp.os.utime(item, (old, old))
        self.assertEqual(1, len(self.sweep(stale=1.0)["retirable"]))
        self.assertEqual(1, len(self.sweep(stale=1.0)["retirable"]))

    def test_sweep_reports_machines_of_both_kinds_and_never_deletes_them(self):
        machines = [
            {"Name": "old", "State": "stopped", "Description": "", "Home": str(self.root)},
            {"Name": "base", "State": "running", "Description": "keel-lease: owner=x until=never", "Home": str(self.root)},
            {"Name": "audit", "State": "stopped", "Description": "keel-lease: owner=x until=2020-01-01", "Home": str(self.root)},
        ]
        containers = [
            {"Names": "a", "State": "exited", "Labels": "com.docker.compose.project=shop"},
            {"Names": "b", "State": "exited", "Labels": "com.docker.compose.project=shop,keel.lease.until=2020-01-01"},
            {"Names": "c", "State": "running", "Labels": "keel.lease.until=never"},
        ]
        calls = []
        def run(argv, **kwargs):
            calls.append(argv)
            if argv[0] == "prlctl":
                return Args(returncode=0, stdout=json.dumps(machines))
            if argv[0] == "docker":
                return Args(returncode=0, stdout="\n".join(json.dumps(item) for item in containers))
            return Args(returncode=0, stdout="1\tx\n")
        with patch.object(kp.shutil, "which", return_value="found"), patch.object(kp.subprocess, "run", run):
            found = kp.sweep_virtual_machines() + kp.sweep_containers()
        self.assertEqual({"old": "no lease", "audit": "lease expired", "shop": "no lease"},
                         {item["name"]: item["reason"] for item in found})
        self.assertEqual({"prlctl list", "docker ps"}, {" ".join(c[:2]) for c in calls if c[0] != "du"})

    def test_a_stopped_docker_daemon_reports_nothing(self):
        with patch.object(kp.shutil, "which", return_value="found"), \
                patch.object(kp.subprocess, "run", return_value=Args(returncode=1, stdout="")):
            self.assertEqual([], kp.sweep_containers())

    def test_sweep_reaches_every_repository_past_a_broken_one(self):
        (self.repo / "docs" / ".keel" / "parallel" / "runs").mkdir(parents=True)
        (self.repo / "docs" / ".keel" / "parallel" / "runs" / "bad.json").write_text("{", encoding="utf-8")
        self.worktree("agent", "wip/agent")
        with patch.object(kp, "process_directories", return_value=set()):
            report = kp.command_sweep(Args(root=[str(self.root)], stale_hours=0.0, apply=True,
                                           report=None))
        self.assertIn("error", report["repositories"][0])
        self.assertTrue((self.root / "agent").exists())

    def test_reap_only_reports_without_apply(self):
        done = self.add_worktree("done")
        report = self.reap()
        self.assertFalse(report["applied"])
        self.assertEqual([done.resolve()], [Path(item["path"]).resolve() for item in report["retirable"]])
        self.assertTrue(done.is_dir())

    def test_reap_applies_to_merged_clean_worktree_and_branch(self):
        done = self.add_worktree("done", commit=True)
        subprocess.run(["git", "merge", "--ff-only", "done"], cwd=self.repo, check=True, capture_output=True)
        report = self.reap(apply=True)
        self.assertEqual(1, len(report["removed"]))
        self.assertFalse(done.exists())
        self.assertNotIn("done", self.branches())

    def test_reap_keeps_unmerged_dirty_recent_locked_and_active(self):
        self.add_worktree("unmerged", commit=True)
        dirty = self.add_worktree("dirty")
        (dirty / "new.txt").write_text("unsaved\n", encoding="utf-8")
        locked = self.add_worktree("locked")
        subprocess.run(["git", "worktree", "lock", str(locked)], cwd=self.repo, check=True)
        active = self.add_worktree("active")
        self.write(self.run_path, {"schema": kp.RUN_SCHEMA, "attempts": {
            "A-1": {"state": "running", "assignment_snapshot": {"worktree": str(active)}},
        }})
        report = self.reap(apply=True, run=[str(self.run_path)])
        reasons = {Path(item["path"]).name: item["reason"] for item in report["kept"]}
        self.assertEqual({
            "unmerged": "commits not in the integration ref",
            "dirty": "uncommitted changes",
            "locked": "locked",
            "active": "owned by an unresolved attempt",
        }, reasons)
        self.assertEqual([], report["removed"])
        for path in (dirty, locked, active):
            self.assertTrue(path.is_dir())

    def test_reap_keeps_a_fresh_worktree_by_default(self):
        self.add_worktree("fresh")
        report = self.reap(apply=True, min_idle_hours=24.0)
        self.assertEqual("used recently", report["kept"][0]["reason"])

    def test_reap_reads_the_repository_run_journal_without_being_told(self):
        active = self.add_worktree("active")
        journal = self.repo / "docs" / ".keel" / "parallel" / "runs" / "R-1"
        journal.mkdir(parents=True)
        self.write(journal / "run.json", {"schema": kp.RUN_SCHEMA, "attempts": {
            "A-1": {"state": "failed", "assignment_snapshot": {"worktree": str(active)}},
        }})
        self.assertEqual([], self.reap()["retirable"])

    def test_init_binds_run_to_repository_and_ref(self):
        self.plan([slice_("A", ["src/a.py"])])
        initialized = self.root / "initialized-run.json"
        args = type("Args", (), {"plan": str(self.plan_path), "run": str(initialized), "run_id": "R-init",
                                  "integration_ref": "develop", "max_workers": 2, "repo": str(self.repo)})
        result = kp.command_init(args)
        run = kp.load_run(initialized)
        self.assertEqual(result["run_id"], "R-init")
        self.assertEqual(run["coordinator_repo_id"], str((self.repo / ".git").resolve()))
        self.assertEqual(run["integration_ref"], "develop")


if __name__ == "__main__":
    unittest.main()
