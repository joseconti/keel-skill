#!/usr/bin/env python3
"""Disposable Git-writing worker used by the concurrency regression fixture."""

import json
import subprocess
import sys
import time
from pathlib import Path


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


assignment = json.loads(Path(sys.argv[1]).read_text())
started = Path(sys.argv[2])
release = Path(sys.argv[3]) if len(sys.argv) > 3 else None
started.touch()
if release:
    deadline = time.monotonic() + 20
    while not release.exists():
        if time.monotonic() > deadline:
            raise SystemExit("fixture barrier timed out")
        time.sleep(.01)

target = Path(assignment["write_paths"][0]) / "value.txt"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(assignment["slice_id"] + "\n")
git("add", str(target))
git("commit", "-m", "fixture implementation " + assignment["slice_id"])
result = {key: assignment[key] for key in (
    "run_id", "attempt_id", "slice_id", "repo_id", "worktree", "branch", "base_commit"
)}
result.update(schema="keel.worker-result/1", outcome="ready", code_commit=git("rev-parse", "HEAD"),
              changed_paths=[target.as_posix()], tests=[], review_findings=[], state_contributions={},
              timing={"active_seconds": 0, "source": "fixture"})
report = Path("docs/.keel/slices") / assignment["run_id"] / assignment["slice_id"] / (assignment["attempt_id"] + ".json")
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text(json.dumps(result))
git("add", str(report))
git("commit", "-m", "fixture report " + assignment["slice_id"])
