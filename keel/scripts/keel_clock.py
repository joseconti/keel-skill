#!/usr/bin/env python3
"""Interval arithmetic for Keel's session clock.

``scripts/keel-time`` is the only reader of the clock; this helper is the part of
it that must not be re-derived per project: appending ``keel.clock/1`` events and
turning them into measured hours. Slice intervals may overlap. Each slice is
measured from its own intervals only, the session from its window, and the
remaining-time projection states the basis it used. Projects copy it to
``scripts/keel-clock`` beside ``scripts/keel-time``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

CLOCK_SCHEMA = "keel.clock/1"
REPORT_SCHEMA = "keel.clock-report/1"
EVENTS = {"session-start", "slice-start", "slice-end", "pause", "resume", "session-end"}
SLICE_STATUSES = {"done", "in-progress", "blocked"}


class ClockError(Exception):
    """A user-facing validation failure."""


def parse_time(value: str) -> float:
    if not isinstance(value, str):
        raise ClockError(f"timestamp must be a string: {value!r}")
    try:
        moment = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ClockError(f"timestamp must be UTC YYYY-MM-DDTHH:MM:SSZ: {value!r}") from exc
    return moment.replace(tzinfo=timezone.utc).timestamp()


def format_time(seconds: float) -> str:
    return datetime.fromtimestamp(seconds, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---- Interval sets ---------------------------------------------------------

def merge(intervals: list[tuple[float, float]]) -> list[tuple[float, float]]:
    merged: list[tuple[float, float]] = []
    for start, end in sorted(i for i in intervals if i[1] > i[0]):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def length(intervals: list[tuple[float, float]]) -> float:
    return sum(end - start for start, end in merge(intervals))


def subtract(intervals: list[tuple[float, float]], holes: list[tuple[float, float]]) -> list[tuple[float, float]]:
    result = []
    holes = merge(holes)
    for start, end in intervals:
        cursor = start
        for hole_start, hole_end in holes:
            if hole_end <= cursor or hole_start >= end:
                continue
            if hole_start > cursor:
                result.append((cursor, hole_start))
            cursor = max(cursor, hole_end)
        if cursor < end:
            result.append((cursor, end))
    return result


def clip(intervals: list[tuple[float, float]], window: tuple[float, float]) -> list[tuple[float, float]]:
    return [(max(s, window[0]), min(e, window[1])) for s, e in intervals if min(e, window[1]) > max(s, window[0])]


def max_overlap(intervals: list[tuple[float, float]]) -> int:
    points = []
    for start, end in intervals:
        if end > start:
            points.append((start, 1))
            points.append((end, -1))
    current = peak = 0
    for _, delta in sorted(points, key=lambda p: (p[0], p[1])):
        current += delta
        peak = max(peak, current)
    return peak


# ---- The log ---------------------------------------------------------------

def read_log(path: str | Path) -> list[dict]:
    events = []
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ClockError(f"{path}:{number}: not JSON: {exc}") from exc
        if not isinstance(event, dict) or event.get("schema") != CLOCK_SCHEMA or event.get("event") not in EVENTS:
            raise ClockError(f"{path}:{number}: not a {CLOCK_SCHEMA} event")
        parse_time(event.get("at"))
        events.append(event)
    return events


def append_events(path: str | Path, events: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(event, sort_keys=True) + "\n" for event in events)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(text)


def current_session(events: list[dict]) -> str:
    starts = [e["session"] for e in events if e["event"] == "session-start"]
    if not starts:
        raise ClockError("no session-start in the clock log")
    return starts[-1]


def open_coordinator_slices(events: list[dict], session: str) -> list[str]:
    open_slices: list[str] = []
    for event in events:
        if event.get("session") != session or event.get("source") == "worker":
            continue
        if event["event"] == "slice-start" and event["slice"] not in open_slices:
            open_slices.append(event["slice"])
        elif event["event"] == "slice-end" and event["slice"] in open_slices:
            open_slices.remove(event["slice"])
    return open_slices


def slice_start_events(events: list[dict], session: str, slice_id: str, at: str, exclusive: bool) -> list[dict]:
    """Events for ``slice-start``. Concurrent by default: other open slices stay open.

    ``exclusive`` keeps the single-writer behaviour by closing every other open
    coordinator slice explicitly, so the log itself says what happened.
    """
    base = {"schema": CLOCK_SCHEMA, "at": at, "session": session}
    out = []
    open_slices = open_coordinator_slices(events, session)
    if exclusive:
        out += [dict(base, event="slice-end", slice=other, status="in-progress")
                for other in open_slices if other != slice_id]
    if slice_id not in open_slices:
        out.append(dict(base, event="slice-start", slice=slice_id))
    return out


def slice_end_events(events: list[dict], session: str, slice_id: str, at: str, status: str) -> list[dict]:
    if status not in SLICE_STATUSES:
        raise ClockError(f"status must be one of {sorted(SLICE_STATUSES)}")
    if slice_id not in open_coordinator_slices(events, session):
        raise ClockError(f"slice {slice_id} has no open interval in session {session}")
    return [{"schema": CLOCK_SCHEMA, "at": at, "session": session, "event": "slice-end",
             "slice": slice_id, "status": status}]


def worker_events(session: str, slice_id: str, result: dict, status: str) -> list[dict]:
    """A worker's own observed interval, taken from its ``keel.worker-result/1`` timing."""
    if status not in SLICE_STATUSES:
        raise ClockError(f"status must be one of {sorted(SLICE_STATUSES)}")
    timing = result.get("timing")
    if not isinstance(timing, dict):
        raise ClockError("worker result has no timing object")
    started, finished = timing.get("started_at"), timing.get("finished_at")
    if parse_time(finished) < parse_time(started):
        raise ClockError("worker timing finished_at is before started_at")
    paused = timing.get("paused_seconds", 0)
    if not isinstance(paused, (int, float)) or paused < 0:
        raise ClockError("worker timing paused_seconds must be a non-negative number")
    if result.get("slice_id") not in (None, slice_id):
        raise ClockError("worker result slice_id does not match the slice")
    attempt = result.get("attempt_id")
    if not attempt:
        raise ClockError("worker result has no attempt_id")
    base = {"schema": CLOCK_SCHEMA, "session": session, "slice": slice_id, "source": "worker", "attempt": attempt}
    end = dict(base, event="slice-end", at=finished, status=status, paused_seconds=paused)
    if isinstance(timing.get("active_seconds"), (int, float)):
        end["active_seconds"] = timing["active_seconds"]
    return [dict(base, event="slice-start", at=started), end]


# ---- Measurement -----------------------------------------------------------

def plan_slices(plan: dict) -> dict[str, dict]:
    raw = list(plan.get("slices", []) or [])
    for sprint in plan.get("sprints", []) or []:
        if isinstance(sprint, dict):
            raw.extend(sprint.get("slices", []) or [])
    return {item["id"]: item for item in raw if isinstance(item, dict) and "id" in item}


def plan_total(plan: dict, key: str):
    for source in (plan, plan.get("totals") or {}, plan.get("plan") or {}):
        if isinstance(source, dict) and isinstance(source.get(key), (int, float)):
            return float(source[key])
    return None


def number(cell: str):
    try:
        return float(cell.strip().replace(",", "."))
    except (ValueError, AttributeError):
        return None


def prior_parallel_sample(sessions_md: str | Path | None) -> tuple[int, float, float]:
    """Sessions already recorded with overlapping slices: (count, estimated h, active h).

    Read before the measured session's own row is appended, so it is never counted twice.
    """
    if not sessions_md or not Path(sessions_md).is_file():
        return 0, 0.0, 0.0
    header = None
    count, estimated, active = 0, 0.0, 0.0
    for line in Path(sessions_md).read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0] == "Start":
            header = cells
            continue
        if header is None or set("".join(cells)) <= set("-: "):
            continue
        row = dict(zip(header, cells))
        concurrency, est, act = (number(row.get(k, "")) for k in ("Max concurrency", "Est. h", "Active h"))
        if concurrency is None or concurrency <= 1 or est is None or act is None or act <= 0:
            continue
        count, estimated, active = count + 1, estimated + est, active + act
    return count, estimated, active


def measure(events: list[dict], session: str | None = None, now: str | None = None,
            plan: dict | None = None, sessions_md: str | Path | None = None,
            parallel: bool = False) -> dict:
    session = session or current_session(events)
    mine = [e for e in events if e.get("session") == session]
    starts = [e for e in mine if e["event"] == "session-start"]
    if not starts:
        raise ClockError(f"session {session} has no session-start")
    begin = parse_time(starts[0]["at"])
    ends = [e for e in mine if e["event"] == "session-end"]
    finished = bool(ends)
    if ends:
        end = parse_time(ends[-1]["at"])
    elif now:
        end = parse_time(now)
    else:
        end = max(parse_time(e["at"]) for e in mine if e.get("source") != "worker")
    end = max(end, begin)
    window = (begin, end)

    pauses, paused_at = [], None
    for event in mine:
        if event["event"] == "pause" and paused_at is None:
            paused_at = parse_time(event["at"])
        elif event["event"] == "resume" and paused_at is not None:
            pauses.append((paused_at, parse_time(event["at"])))
            paused_at = None
    if paused_at is not None:
        pauses.append((paused_at, end))
    pauses = clip(merge(pauses), window)

    # Each slice keeps its own intervals; nothing here closes one slice because another opened.
    per_slice: dict[str, dict] = {}

    def record(slice_id: str) -> dict:
        return per_slice.setdefault(slice_id, {"intervals": [], "worker_seconds": 0.0, "sources": set(),
                                               "status": "in-progress", "worker_intervals": []})

    opened: dict[str, float] = {}
    worker_open: dict[tuple[str, str], float] = {}
    for event in mine:
        kind, slice_id = event["event"], event.get("slice")
        if kind not in {"slice-start", "slice-end"}:
            continue
        item = record(slice_id)
        at = parse_time(event["at"])
        if event.get("source") == "worker":
            key = (slice_id, event.get("attempt", ""))
            if kind == "slice-start":
                worker_open[key] = at
            elif key in worker_open:
                start = worker_open.pop(key)
                item["worker_intervals"].append((start, at))
                item["worker_seconds"] += max(0.0, at - start - float(event.get("paused_seconds", 0)))
                item["sources"].add("worker")
                item["status"] = event.get("status", item["status"])
            continue
        if kind == "slice-start":
            opened.setdefault(slice_id, at)
        elif slice_id in opened:
            item["intervals"].append((opened.pop(slice_id), at))
            item["sources"].add("coordinator")
            item["status"] = event.get("status", item["status"])
    for slice_id, start in opened.items():
        per_slice[slice_id]["intervals"].append((start, end))
        per_slice[slice_id]["sources"].add("coordinator")

    slices_by_id = plan_slices(plan or {})
    rows, all_intervals = [], []
    for slice_id, item in per_slice.items():
        coordinator = subtract(clip(item["intervals"], window), pauses)
        hours = (length(coordinator) + item["worker_seconds"]) / 3600
        all_intervals += merge(coordinator) + item["worker_intervals"]
        planned = slices_by_id.get(slice_id, {})
        estimated = planned.get("original_hours", planned.get("hours"))
        lifetime = planned.get("actual_hours")
        row = {
            "id": slice_id,
            "session_hours": hours,
            "status": item["status"],
            "source": "/".join(sorted(item["sources"])) or "coordinator",
            "estimated_hours": float(estimated) if isinstance(estimated, (int, float)) else None,
        }
        # A finished slice is compared over its whole lifetime: the plan, regenerated after
        # slice-end, carries the cumulative figure; without it the session's own hours are all there is.
        row["measured_hours"] = (float(lifetime) if item["status"] == "done" and isinstance(lifetime, (int, float))
                                 and lifetime >= hours - 1e-9 else hours)
        row["deviation_hours"] = (row["measured_hours"] - row["estimated_hours"]
                                  if row["estimated_hours"] is not None else None)
        rows.append(row)

    wall = (end - begin) / 3600
    paused = length(pauses) / 3600
    worker_spans = clip([i for item in per_slice.values() for i in item["worker_intervals"]], window)
    active = length(subtract([window], pauses) + worker_spans) / 3600
    concurrency = max_overlap(all_intervals)
    done = [r for r in rows if r["status"] == "done"]
    done_est = sum(r["estimated_hours"] or 0 for r in done)
    done_measured = sum(r["measured_hours"] for r in done)
    throughput = done_est / active if active > 0 and done_est > 0 else None

    parallel_mode = parallel or concurrency > 1
    remaining = plan_total(plan or {}, "remaining_hours")
    pace = plan_total(plan or {}, "pace_factor")
    count, sample_est, sample_active = prior_parallel_sample(sessions_md)
    if concurrency > 1 and active > 0:
        # Same rule keel-verify recomputes from the table: every overlapping session counts,
        # including one that finished nothing, so an idle parallel session lowers throughput.
        count, sample_est, sample_active = count + 1, sample_est + done_est, sample_active + active
    cumulative_throughput = sample_est / sample_active if sample_active > 0 and sample_est > 0 else None

    projection = {"remaining_hours": remaining, "pace_factor": pace, "basis": None,
                  "throughput": cumulative_throughput,
                  "throughput_sample": {"sessions": count, "estimated_hours": sample_est, "active_hours": sample_active},
                  "projected_remaining_hours": None, "reason": None}
    if remaining is None:
        projection["reason"] = "unavailable — no time plan"
    elif remaining == 0:
        projection.update(basis="none", projected_remaining_hours=0.0)
    elif parallel_mode and cumulative_throughput:
        projection.update(basis="throughput", projected_remaining_hours=remaining / cumulative_throughput)
    elif pace is not None:
        projection.update(basis="pace", projected_remaining_hours=remaining * pace)
        if parallel_mode:
            projection["reason"] = ("throughput unavailable — no parallel session has finished estimated work; "
                                    "pace projection is effort hours, not elapsed time")
    else:
        projection["reason"] = "unavailable — no measured completed work"

    deviation = done_measured - done_est
    return {
        "schema": REPORT_SCHEMA,
        "session": session,
        "start": format_time(begin),
        "end": format_time(end),
        "finished": finished,
        "wall_clock_hours": wall,
        "paused_hours": paused,
        "active_hours": active,
        "summed_slice_hours": sum(r["session_hours"] for r in rows),
        "max_concurrency": concurrency,
        "parallel": parallel_mode,
        "slices": rows,
        "done": [r["id"] for r in done],
        "done_estimated_hours": done_est,
        "done_measured_hours": done_measured,
        "deviation_hours": deviation,
        "deviation_percent": deviation / done_est * 100 if done_est else None,
        "throughput": throughput,
        "projection": projection,
    }


# ---- CLI -------------------------------------------------------------------

def load_plan(path: str | None) -> dict:
    if not path or not Path(path).is_file():
        return {}
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ClockError("plan root must be an object")
    return value


def command_slice_start(args) -> dict:
    events = read_log(args.log)
    session = args.session or current_session(events)
    new = slice_start_events(events, session, args.slice, args.at or now_utc(), args.exclusive)
    append_events(args.log, new)
    return {"appended": new}


def command_slice_end(args) -> dict:
    events = read_log(args.log)
    session = args.session or current_session(events)
    new = slice_end_events(events, session, args.slice, args.at or now_utc(), args.status)
    append_events(args.log, new)
    return {"appended": new}


def command_record_worker(args) -> dict:
    events = read_log(args.log)
    session = args.session or current_session(events)
    result = json.loads(Path(args.result).read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ClockError("worker result root must be an object")
    new = worker_events(session, args.slice, result, args.status)
    duplicate = any(e.get("source") == "worker" and e.get("attempt") == new[0]["attempt"]
                    and e.get("slice") == args.slice for e in events)
    if duplicate:
        return {"appended": [], "duplicate": True}
    append_events(args.log, new)
    return {"appended": new}


def command_report(args) -> dict:
    events = read_log(args.log)
    return measure(events, session=args.session, now=args.now, plan=load_plan(args.plan),
                   sessions_md=args.sessions, parallel=args.parallel)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("slice-start")
    start.add_argument("slice")
    start.add_argument("--log", required=True)
    start.add_argument("--session")
    start.add_argument("--at")
    start.add_argument("--exclusive", action="store_true",
                       help="single-writer mode: close every other open slice first")
    start.set_defaults(func=command_slice_start)
    end = sub.add_parser("slice-end")
    end.add_argument("slice")
    end.add_argument("--log", required=True)
    end.add_argument("--status", required=True, choices=sorted(SLICE_STATUSES))
    end.add_argument("--session")
    end.add_argument("--at")
    end.set_defaults(func=command_slice_end)
    worker = sub.add_parser("record-worker")
    worker.add_argument("slice")
    worker.add_argument("--log", required=True)
    worker.add_argument("--result", required=True)
    worker.add_argument("--status", required=True, choices=sorted(SLICE_STATUSES))
    worker.add_argument("--session")
    worker.set_defaults(func=command_record_worker)
    report = sub.add_parser("report")
    report.add_argument("--log", required=True)
    report.add_argument("--plan")
    report.add_argument("--sessions")
    report.add_argument("--session")
    report.add_argument("--now")
    report.add_argument("--parallel", action="store_true",
                        help="the card runs parallel development with an effective cap above 1")
    report.set_defaults(func=command_report)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        print(json.dumps(args.func(args), indent=2, sort_keys=True))
        return 0
    except (ClockError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
