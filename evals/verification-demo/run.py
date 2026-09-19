"""Demonstrate receipt mechanics against a plain shell sequence; no model calls."""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "scripts/verify.sh"
CASES = [
    {"name": "clean control", "first": "print('unit ok')", "last": "print('lint ok')", "expected": "passed"},
    {"name": "earlier check fails", "first": "raise SystemExit(7)", "last": "print('lint ok')", "expected": "failed"},
    {"name": "last check fails control", "first": "print('unit ok')", "last": "raise SystemExit(3)", "expected": "failed"},
    {"name": "unrelated edit before checks", "first": "print('unit ok')", "last": "print('lint ok')", "drift": True, "expected": "failed"},
    {"name": "check changes protected file", "first": "from pathlib import Path; Path('notes.md').write_text('overwritten')", "last": "print('lint ok')", "expected": "failed"},
]


def run_case(case, condition, folder):
    folder.mkdir()
    (folder / "notes.md").write_text("Unrelated user work\n")
    checks = [{"name": name, "argv": [sys.executable, "-B", "-c", case[key]], "timeout_seconds": 5}
              for name, key in (("unit", "first"), ("lint", "last"))]
    plan = folder / "checks.json"
    plan.write_text(json.dumps({"schema": 1, "checks": checks, "protect": ["notes.md"]}))
    snapshot = [str(TOOL), "snapshot", "--plan", str(plan), "--target", str(folder),
                "--output", str(folder / "before.json")]
    if condition == "receipt runner":
        subprocess.run(snapshot, check=True, capture_output=True, text=True)
    if case.get("drift"):
        (folder / "notes.md").write_text("Unrelated user work overwritten\n")
    if condition == "plain shell sequence":
        command = "; ".join(shlex.join(check["argv"]) for check in checks)
        result = subprocess.run(["/bin/sh", "-c", command], cwd=folder, capture_output=True, text=True, timeout=15)
        receipt = None
    else:
        command = [str(TOOL), "run", "--plan", str(plan), "--target", str(folder),
                   "--baseline", str(folder / "before.json"), "--output", str(folder / "receipt.json")]
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        receipt = json.loads((folder / "receipt.json").read_text())
    status = "passed" if result.returncode == 0 else "failed"
    return {"case": case["name"], "condition": condition, "expected": case["expected"],
            "observed": status, "exit_code": result.returncode,
            "false_green": status == "passed" and case["expected"] == "failed",
            "plan_sha256": hashlib.sha256(plan.read_bytes()).hexdigest(),
            "notes_preserved": (folder / "notes.md").read_text() == "Unrelated user work\n",
            "receipt": receipt}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional new JSON file")
    args = parser.parse_args()
    rows = []
    with tempfile.TemporaryDirectory(prefix="ae-receipt-demo-") as temp:
        for index, case in enumerate(CASES):
            for condition in ("plain shell sequence", "receipt runner"):
                rows.append(run_case(case, condition, Path(temp) / f"{index}-{condition}"))
    for index in range(len(CASES)):
        assert rows[index * 2]["plan_sha256"] == rows[index * 2 + 1]["plan_sha256"]
    summary = {condition: {"cases": 5,
                          "false_greens": sum(row["false_green"] for row in rows if row["condition"] == condition),
                          "matched_expected": sum(row["observed"] == row["expected"] for row in rows if row["condition"] == condition)}
               for condition in ("plain shell sequence", "receipt runner")}
    data = {"kind": "mechanism_demo", "schema": 1,
            "scope": "Five chosen feature demonstrations, including passing and failing controls. Not a model comparison or representative benchmark.",
            "comparator": "Plain sh sequence using semicolons and only its final exit status. Careful agents, CI runners, and correctly chained commands can already avoid masked failures.",
            "tool_sha256": hashlib.sha256((ROOT / "scripts/verification.py").read_bytes()).hexdigest(),
            "demo_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "summary": summary, "runs": rows}
    if args.output:
        with args.output.open("x") as stream:
            json.dump(data, stream, indent=2)
            stream.write("\n")
    print(json.dumps(summary, indent=2))
    if summary["receipt runner"]["matched_expected"] != len(CASES):
        raise SystemExit("Receipt behavior differed from the demo contract")


if __name__ == "__main__":
    main()
