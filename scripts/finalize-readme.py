#!/usr/bin/env python3
"""Insert only real Newman/Node output into the Lab05 report."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
README_PATH = ROOT / "README.md"
README = README_PATH.read_text(encoding="utf-8")

def read_result(name):
    path = RESULTS / name
    if not path.is_file():
        raise SystemExit(f"Missing required result: {name}")
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        raise SystemExit(f"Empty required result: {name}")
    return text

def stats(name):
    text = read_result(name)
    matches = re.findall(r"assertions\s*[│|]\s*(\d+)\s*[│|]\s*(\d+)", text)
    if not matches:
        raise SystemExit(f"Newman assertion summary not found in {name}")
    executed, failed = map(int, matches[-1])
    exits = re.findall(r"exit_code=(\d+)", text)
    if not exits:
        raise SystemExit(f"Newman exit code not recorded in {name}")
    return executed, failed, int(exits[-1]), text

node = read_result("node-version.txt").strip()
newman = read_result("newman-version.txt").strip()
pass_count, pass_failed, pass_exit, pass_text = stats("newman-pass.txt")
fail_count, fail_failed, fail_exit, fail_text = stats("newman-fail.txt")
down_count, down_failed, down_exit, down_text = stats("newman-down.txt")

if (pass_count, pass_failed, pass_exit) != (27, 0, 0):
    raise SystemExit(f"PASS run mismatch: {(pass_count, pass_failed, pass_exit)}")
if (fail_count, fail_failed, fail_exit) != (27, 1, 1):
    raise SystemExit(f"FAIL run mismatch: {(fail_count, fail_failed, fail_exit)}")
if "ECONNREFUSED" not in down_text or down_exit != 1:
    raise SystemExit("DOWN run did not prove ECONNREFUSED with exit code 1.")

fence = chr(96) * 3
env_start = "<!-- ENV-RESULTS-START -->"
env_end = "<!-- ENV-RESULTS-END -->"
if env_start not in README or env_end not in README:
    raise SystemExit("Environment markers not found in README.md.")
env = (
    "### node -v\n\n" + fence + "text\n" + node + "\n" + fence + "\n\n"
    "### newman -v\n\n" + fence + "text\n" + newman + "\n" + fence + "\n"
)
before, rest = README.split(env_start, 1)
_, after = rest.split(env_end, 1)
README = before + env_start + "\n\n" + env + "\n" + env_end + after

results_start = "<!-- RUN-RESULTS-START -->"
results_end = "<!-- RUN-RESULTS-END -->"
if results_start not in README or results_end not in README:
    raise SystemExit("Run-result markers not found in README.md.")
table = (
    "| Ажиллуулалт | Assertions executed | Failed | Newman exit code | Нотолгоо |\n"
    "|---|---:|---:|---:|---|\n"
    f"| PASS | {pass_count} | {pass_failed} | {pass_exit} | results/newman-pass.txt |\n"
    f"| FAIL (зориудын буруу oracle) | {fail_count} | {fail_failed} | {fail_exit} | results/newman-fail.txt |\n"
    f"| DOWN (сервер унтарсан) | {down_count} | {down_failed} | {down_exit} | results/newman-down.txt |\n"
    "\n"
    "PASS үед бүх assertion амжилттай; FAIL үед яг нэг HTTP status oracle унасан; DOWN үед ECONNREFUSED гарсан. "
    "Newman-ийн бүрэн CLI гаралт болон exit code мөр тус бүрийн results/ файлуудад хадгалагдсан.\n"
)
before, rest = README.split(results_start, 1)
_, after = rest.split(results_end, 1)
README_PATH.write_text(before + results_start + "\n\n" + table + "\n" + results_end + after, encoding="utf-8")
print("README.md шинэчлэгдлээ: PASS=27/0/exit0, FAIL=27/1/exit1, DOWN=ECONNREFUSED/exit1.")
