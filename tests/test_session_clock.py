#!/usr/bin/env python3
"""Behavioral tests for Keel's session clock arithmetic (keel_clock.py)."""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELPER = ROOT / "keel" / "scripts" / "keel_clock.py"
SPEC = importlib.util.spec_from_file_location("keel_clock", HELPER)
kc = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(kc)

SESSION = "2026-10-16T10:00:00Z"


def ev(event, at, **fields):
    return {"schema": "keel.clock/1", "event": event, "at": at, "session": SESSION, **fields}


def start(at="2026-10-16T10:00:00Z"):
    return ev("session-start", at, planned=[], planned_hours=0)


def worker_result(slice_id, attempt, started, finished, paused=0):
    return {"slice_id": slice_id, "attempt_id": attempt,
            "timing": {"started_at": started, "finished_at": finished, "paused_seconds": paused,
                       "active_seconds": 0, "source": "fixture"}}


class SessionClockTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="keel clock ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_overlapping_slices_are_measured_independently(self):
        events = [start(),
                  ev("slice-start", "2026-10-16T10:00:00Z", slice="A"),
                  ev("slice-start", "2026-10-16T10:30:00Z", slice="B"),
                  ev("slice-end", "2026-10-16T11:00:00Z", slice="A", status="done"),
                  ev("slice-end", "2026-10-16T11:30:00Z", slice="B", status="done"),
                  ev("session-end", "2026-10-16T11:30:00Z")]
        report = kc.measure(events)
        hours = {s["id"]: s["session_hours"] for s in report["slices"]}
        self.assertAlmostEqual(hours["A"], 1.0)
        self.assertAlmostEqual(hours["B"], 1.0)
        self.assertAlmostEqual(report["wall_clock_hours"], 1.5)
        self.assertAlmostEqual(report["summed_slice_hours"], 2.0)
        self.assertEqual(report["max_concurrency"], 2)
        self.assertTrue(report["parallel"])

    def test_slice_start_is_concurrent_by_default(self):
        events = [start(), ev("slice-start", "2026-10-16T10:00:00Z", slice="A")]
        new = kc.slice_start_events(events, SESSION, "B", "2026-10-16T10:05:00Z", exclusive=False)
        self.assertEqual([(e["event"], e["slice"]) for e in new], [("slice-start", "B")])
        self.assertEqual(kc.open_coordinator_slices(events + new, SESSION), ["A", "B"])

    def test_exclusive_slice_start_keeps_single_writer_behaviour_explicit(self):
        events = [start(), ev("slice-start", "2026-10-16T10:00:00Z", slice="A")]
        new = kc.slice_start_events(events, SESSION, "B", "2026-10-16T10:20:00Z", exclusive=True)
        self.assertEqual([(e["event"], e["slice"], e.get("status")) for e in new],
                         [("slice-end", "A", "in-progress"), ("slice-start", "B", None)])
        report = kc.measure(events + new, now="2026-10-16T11:00:00Z")
        hours = {s["id"]: s["session_hours"] for s in report["slices"]}
        self.assertAlmostEqual(hours["A"], 20 / 60)
        self.assertAlmostEqual(hours["B"], 40 / 60)
        self.assertEqual(report["max_concurrency"], 1)
        self.assertFalse(report["parallel"])

    def test_restarting_an_open_slice_does_not_reset_it(self):
        events = [start(), ev("slice-start", "2026-10-16T10:00:00Z", slice="A")]
        self.assertEqual(kc.slice_start_events(events, SESSION, "A", "2026-10-16T10:30:00Z", False), [])

    def test_slice_end_closes_only_its_own_slice(self):
        events = [start(), ev("slice-start", "2026-10-16T10:00:00Z", slice="A"),
                  ev("slice-start", "2026-10-16T10:00:00Z", slice="B")]
        events += kc.slice_end_events(events, SESSION, "A", "2026-10-16T10:15:00Z", "done")
        self.assertEqual(kc.open_coordinator_slices(events, SESSION), ["B"])
        with self.assertRaises(kc.ClockError):
            kc.slice_end_events(events, SESSION, "A", "2026-10-16T10:20:00Z", "done")

    def test_pauses_are_subtracted_from_coordinator_slices_and_wall_clock(self):
        events = [start(), ev("slice-start", "2026-10-16T10:00:00Z", slice="A"),
                  ev("pause", "2026-10-16T10:30:00Z", reason="question"),
                  ev("resume", "2026-10-16T11:00:00Z"),
                  ev("slice-end", "2026-10-16T11:30:00Z", slice="A", status="done"),
                  ev("session-end", "2026-10-16T11:30:00Z")]
        report = kc.measure(events)
        self.assertAlmostEqual(report["slices"][0]["session_hours"], 1.0)
        self.assertAlmostEqual(report["wall_clock_hours"], 1.5)
        self.assertAlmostEqual(report["paused_hours"], 0.5)
        self.assertAlmostEqual(report["active_hours"], 1.0)

    def test_parallel_workers_reproduce_the_reported_defect_correctly(self):
        # Six workers, each 2 h of its own working time, inside a 2.5 h session.
        events = [start()]
        for n in range(6):
            begin = f"2026-10-16T10:{n * 5:02d}:00Z"
            finish = f"2026-10-16T12:{n * 5:02d}:00Z"
            events += kc.worker_events(SESSION, f"S-{n}", worker_result(f"S-{n}", f"a{n}", begin, finish), "done")
        events.append(ev("session-end", "2026-10-16T12:30:00Z"))
        plan = {"slices": [{"id": f"S-{n}", "original_hours": 2.0} for n in range(6)], "remaining_hours": 0}
        report = kc.measure(events, plan=plan)
        self.assertTrue(all(abs(s["session_hours"] - 2.0) < 1e-9 for s in report["slices"]))
        self.assertAlmostEqual(report["summed_slice_hours"], 12.0)
        self.assertAlmostEqual(report["wall_clock_hours"], 2.5)
        self.assertEqual(report["max_concurrency"], 6)
        self.assertAlmostEqual(report["deviation_hours"], 0.0)
        self.assertAlmostEqual(report["throughput"], 12.0 / 2.5)

    def test_worker_pause_and_coordinator_pause_are_kept_apart(self):
        events = [start(), ev("pause", "2026-10-16T10:30:00Z", reason="question"),
                  ev("resume", "2026-10-16T11:00:00Z")]
        events += kc.worker_events(SESSION, "W", worker_result("W", "a1", "2026-10-16T10:00:00Z",
                                                               "2026-10-16T11:00:00Z", paused=600), "done")
        events.append(ev("session-end", "2026-10-16T11:00:00Z"))
        report = kc.measure(events)
        # The worker kept working while the coordinator waited on the person; only its own pause counts.
        self.assertAlmostEqual(report["slices"][0]["session_hours"], 50 / 60)
        self.assertAlmostEqual(report["paused_hours"], 0.5)
        self.assertAlmostEqual(report["active_hours"], 1.0)

    def test_worker_timing_is_validated(self):
        with self.assertRaises(kc.ClockError):
            kc.worker_events(SESSION, "W", worker_result("W", "a1", "2026-10-16T11:00:00Z", "2026-10-16T10:00:00Z"), "done")
        with self.assertRaises(kc.ClockError):
            kc.worker_events(SESSION, "W", {"attempt_id": "a1", "timing": {"active_seconds": 5}}, "done")
        with self.assertRaises(kc.ClockError):
            kc.worker_events(SESSION, "W", worker_result("X", "a1", "2026-10-16T10:00:00Z", "2026-10-16T11:00:00Z"), "done")

    def test_projection_uses_throughput_when_work_runs_in_parallel(self):
        events = [start()]
        events += kc.worker_events(SESSION, "A", worker_result("A", "a", "2026-10-16T10:00:00Z", "2026-10-16T11:00:00Z"), "done")
        events += kc.worker_events(SESSION, "B", worker_result("B", "b", "2026-10-16T10:00:00Z", "2026-10-16T11:00:00Z"), "done")
        events.append(ev("session-end", "2026-10-16T11:00:00Z"))
        plan = {"slices": [{"id": "A", "original_hours": 2}, {"id": "B", "original_hours": 2}],
                "remaining_hours": 10, "pace_factor": 0.5}
        projection = kc.measure(events, plan=plan)["projection"]
        self.assertEqual(projection["basis"], "throughput")
        self.assertAlmostEqual(projection["throughput"], 4.0)
        self.assertAlmostEqual(projection["projected_remaining_hours"], 2.5)
        self.assertEqual(projection["throughput_sample"]["sessions"], 1)

    def test_projection_uses_pace_when_work_is_serial(self):
        events = [start(), ev("slice-start", "2026-10-16T10:00:00Z", slice="A"),
                  ev("slice-end", "2026-10-16T11:00:00Z", slice="A", status="done"),
                  ev("session-end", "2026-10-16T11:00:00Z")]
        plan = {"slices": [{"id": "A", "original_hours": 2}], "remaining_hours": 10, "pace_factor": 1.2}
        projection = kc.measure(events, plan=plan)["projection"]
        self.assertEqual(projection["basis"], "pace")
        self.assertAlmostEqual(projection["projected_remaining_hours"], 12.0)
        self.assertIsNone(projection["reason"])

    def test_parallel_card_without_throughput_falls_back_to_pace_and_says_so(self):
        events = [start(), ev("slice-start", "2026-10-16T10:00:00Z", slice="A"), ev("session-end", "2026-10-16T10:30:00Z")]
        plan = {"slices": [{"id": "A", "original_hours": 2}], "remaining_hours": 10, "pace_factor": 1.2}
        projection = kc.measure(events, plan=plan, parallel=True)["projection"]
        self.assertEqual(projection["basis"], "pace")
        self.assertIn("throughput unavailable", projection["reason"])

    def test_cumulative_throughput_reads_prior_parallel_sessions(self):
        sessions = self.root / "sessions.md"
        sessions.write_text(
            "# Sessions\n\n"
            "| Start | Est. h | Active h | Max concurrency | Notes |\n|---|---|---|---|---|\n"
            "| s1 | 6 | 2 | 3 | parallel |\n"
            "| s2 | 1 | 1 | 1 | serial — not in the throughput sample |\n"
            "| s3 | 3 | — | — | legacy |\n", encoding="utf-8")
        events = [start(), ev("slice-start", "2026-10-16T10:00:00Z", slice="A"), ev("session-end", "2026-10-16T11:00:00Z")]
        plan = {"slices": [{"id": "A", "original_hours": 2}], "remaining_hours": 9, "pace_factor": 1.0}
        projection = kc.measure(events, plan=plan, sessions_md=sessions, parallel=True)["projection"]
        self.assertEqual(projection["basis"], "throughput")
        self.assertAlmostEqual(projection["throughput"], 3.0)
        self.assertAlmostEqual(projection["projected_remaining_hours"], 3.0)
        self.assertEqual(projection["throughput_sample"], {"sessions": 1, "estimated_hours": 6.0, "active_hours": 2.0})

    def test_finished_slice_uses_lifetime_actual_from_the_plan(self):
        events = [start(), ev("slice-start", "2026-10-16T10:00:00Z", slice="A"),
                  ev("slice-end", "2026-10-16T10:30:00Z", slice="A", status="done"), ev("session-end", "2026-10-16T10:30:00Z")]
        plan = {"slices": [{"id": "A", "original_hours": 2, "actual_hours": 1.5}], "remaining_hours": 0}
        report = kc.measure(events, plan=plan)
        self.assertAlmostEqual(report["slices"][0]["session_hours"], 0.5)
        self.assertAlmostEqual(report["done_measured_hours"], 1.5)
        self.assertAlmostEqual(report["deviation_hours"], -0.5)
        self.assertEqual(report["projection"]["projected_remaining_hours"], 0.0)

    def test_cli_round_trip_is_idempotent_for_worker_results(self):
        log = self.root / "docs" / ".keel" / "clock.jsonl"
        kc.append_events(log, [start()])
        result = self.root / "result.json"
        result.write_text(json.dumps(worker_result("A", "a1", "2026-10-16T10:00:00Z", "2026-10-16T10:45:00Z")), encoding="utf-8")

        def run(*argv):
            done = subprocess.run([sys.executable, "-B", str(HELPER), *argv], capture_output=True, text=True)
            return done.returncode, json.loads(done.stdout)

        self.assertEqual(run("slice-start", "B", "--log", str(log), "--at", "2026-10-16T10:00:00Z")[0], 0)
        self.assertEqual(run("record-worker", "A", "--log", str(log), "--result", str(result), "--status", "done")[0], 0)
        code, again = run("record-worker", "A", "--log", str(log), "--result", str(result), "--status", "done")
        self.assertEqual((code, again["duplicate"]), (0, True))
        self.assertEqual(run("slice-end", "B", "--log", str(log), "--status", "done", "--at", "2026-10-16T11:00:00Z")[0], 0)
        code, report = run("report", "--log", str(log), "--now", "2026-10-16T11:00:00Z")
        self.assertEqual(code, 0)
        hours = {s["id"]: s["session_hours"] for s in report["slices"]}
        self.assertAlmostEqual(hours["A"], 0.75)
        self.assertAlmostEqual(hours["B"], 1.0)
        self.assertAlmostEqual(report["wall_clock_hours"], 1.0)
        self.assertEqual(report["max_concurrency"], 2)
        code, error = run("slice-end", "B", "--log", str(log), "--status", "done")
        self.assertEqual(code, 1)
        self.assertIn("no open interval", error["error"])


if __name__ == "__main__":
    unittest.main()
