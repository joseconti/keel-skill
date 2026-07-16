#!/usr/bin/env python3
"""Keel release linter.

Mechanically verifies everything the release hygiene rules promise, so version
drift and packaging regressions are caught BEFORE a tag instead of in the field.

Run from anywhere: paths resolve relative to this file. Exit code 0 = clean,
1 = at least one failure. CI runs this on every tag; run it locally before
proposing any release.

Checks:
  1. Version sync: SKILL.md frontmatter == SKILL.md heading == last CHANGELOG
     entry == MANIFEST.md header == README.md version line.
  2. NOTICE carries no version line of its own (by design since v2.0.0).
  3. Frontmatter description fits the 1024-character installer limit.
  4. CHANGELOG versions are strictly ascending (oldest -> newest).
  5. Reference parity: every keel/references/**/*.md is mentioned in SKILL.md,
     and every references/*.md mentioned in SKILL.md exists on disk.
  6. MANIFEST Table 2 parity: its rows match the keel/ tree exactly.
  7. Canonical lock-block stamp in references/project-state.md equals the
     current version.
  8. No stray literal version strings in SKILL.md outside the two governed
     spots (frontmatter and heading).
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEEL = ROOT / "keel"

failures = []
def ok(msg):
    print(f"OK    {msg}")
def fail(msg):
    failures.append(msg)
    print(f"FAIL  {msg}")

def semver_key(v):
    return tuple(int(p) for p in v.split("."))

# ---- Load files -----------------------------------------------------------
skill = (KEEL / "SKILL.md").read_text(encoding="utf-8")
manifest = (KEEL / "MANIFEST.md").read_text(encoding="utf-8")
changelog = (KEEL / "CHANGELOG.md").read_text(encoding="utf-8")
readme = (ROOT / "README.md").read_text(encoding="utf-8")
notice = (KEEL / "NOTICE").read_text(encoding="utf-8")
project_state = (KEEL / "references" / "project-state.md").read_text(encoding="utf-8")

# ---- 1. Version sync ------------------------------------------------------
m = re.search(r"^\s+version:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*$", skill, re.M)
if not m:
    fail("SKILL.md frontmatter: metadata.version not found")
    sys.exit(1)
version = m.group(1)
ok(f"frontmatter version: {version}")

def expect(name, pattern, text, expected):
    mm = re.search(pattern, text, re.M)
    if not mm:
        fail(f"{name}: pattern not found ({pattern})")
    elif mm.group(1) != expected:
        fail(f"{name}: says {mm.group(1)}, frontmatter says {expected}")
    else:
        ok(f"{name}: {mm.group(1)}")

expect("SKILL.md heading", r"^\*\*Keel v([0-9]+\.[0-9]+\.[0-9]+)\*\*", skill, version)
expect("MANIFEST.md header", r"^# Keel Manifest — v([0-9]+\.[0-9]+\.[0-9]+)", manifest, version)
expect("README.md version line", r"^- \*\*Version:\*\* ([0-9]+\.[0-9]+\.[0-9]+)", readme, version)

# ---- 2. NOTICE has no version line ---------------------------------------
if re.search(r"^Version [0-9]", notice, re.M):
    fail("NOTICE: carries a version line (it must not — the frontmatter is the source of truth)")
else:
    ok("NOTICE: no version line (as designed)")

# ---- 3. Description length ------------------------------------------------
m = re.search(r"^description: (.+)$", skill, re.M)
if not m:
    fail("SKILL.md frontmatter: description not found")
else:
    n = len(m.group(1))
    if n > 1024:
        fail(f"description: {n} characters (limit 1024 enforced by skill installers)")
    else:
        ok(f"description: {n} characters (limit 1024)")

# ---- 4. CHANGELOG order + last entry --------------------------------------
versions = re.findall(r"^## ([0-9]+\.[0-9]+\.[0-9]+)\s*$", changelog, re.M)
if not versions:
    fail("CHANGELOG.md: no version headings found")
else:
    keys = [semver_key(v) for v in versions]
    if keys != sorted(keys):
        fail(f"CHANGELOG.md: versions not in ascending order: {versions}")
    else:
        ok(f"CHANGELOG.md: {len(versions)} entries, ascending")
    if versions[-1] != version:
        fail(f"CHANGELOG.md: last entry is {versions[-1]}, frontmatter says {version}")
    else:
        ok(f"CHANGELOG.md: last entry matches {version}")

# ---- 5. Reference parity ---------------------------------------------------
disk_refs = {
    str(p.relative_to(KEEL)).replace("\\", "/")
    for p in (KEEL / "references").rglob("*.md")
}
mentioned = set(re.findall(r"references/[A-Za-z0-9/_-]+\.md", skill))
missing_on_disk = sorted(mentioned - disk_refs)
missing_in_skill = sorted(disk_refs - mentioned)
if missing_on_disk:
    fail(f"SKILL.md mentions references that do not exist: {missing_on_disk}")
else:
    ok("every reference mentioned in SKILL.md exists on disk")
if missing_in_skill:
    fail(f"references on disk never mentioned in SKILL.md (orphans): {missing_in_skill}")
else:
    ok(f"every reference on disk is mentioned in SKILL.md ({len(disk_refs)} files)")

# ---- 6. MANIFEST Table 2 parity -------------------------------------------
table2 = re.findall(r"^\| `([^`]+)` \| v([0-9]+\.[0-9]+\.[0-9]+) \|", manifest, re.M)
table2_paths = {p for p, _ in table2}
tree = {
    str(p.relative_to(KEEL)).replace("\\", "/")
    for p in KEEL.rglob("*")
    if p.is_file() and not p.name.startswith(".")
}
not_in_tree = sorted(table2_paths - tree)
not_in_table = sorted(tree - table2_paths)
if not_in_tree:
    fail(f"MANIFEST Table 2 lists files missing from keel/: {not_in_tree}")
else:
    ok("every MANIFEST Table 2 row exists in the tree")
if not_in_table:
    fail(f"files in keel/ missing from MANIFEST Table 2: {not_in_table}")
else:
    ok(f"every keel/ file has its MANIFEST Table 2 row ({len(tree)} files)")
stale = [f"{p} -> v{v}" for p, v in table2 if semver_key(v) > semver_key(version)]
if stale:
    fail(f"MANIFEST Table 2 rows newer than the release itself: {stale}")

# ---- 7. Canonical lock stamp ----------------------------------------------
m = re.search(r"KEEL:BEGIN — v([0-9]+\.[0-9]+\.[0-9]+) do not remove", project_state)
if not m:
    fail("project-state.md: canonical KEEL:BEGIN stamp not found")
elif m.group(1) != version:
    fail(f"project-state.md canonical lock stamp is v{m.group(1)}, release is v{version} — restamp it")
else:
    ok(f"canonical lock stamp: v{version}")

# ---- 8. No stray version literals in SKILL.md ------------------------------
stray = []
for i, line in enumerate(skill.splitlines(), 1):
    if re.match(r"^\s+version:", line) or line.startswith("**Keel v"):
        continue
    for hit in re.findall(r"\bv?[0-9]+\.[0-9]+\.[0-9]+\b", line):
        stray.append(f"line {i}: {hit}")
if stray:
    fail(f"SKILL.md carries version-shaped literals outside the governed spots: {stray}")
else:
    ok("SKILL.md: no stray version literals")

# ---- Result ----------------------------------------------------------------
print()
if failures:
    print(f"{len(failures)} check(s) FAILED — this tree is not releasable.")
    sys.exit(1)
print("All checks passed. Releasable.")
