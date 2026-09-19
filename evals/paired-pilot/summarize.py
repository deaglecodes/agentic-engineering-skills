"""Summarize observed paired runs without treating repeated tasks as independent evidence."""
import argparse
import json
from pathlib import Path
import statistics


def summarize(data):
    groups = {}
    for condition in ["without-pack", "with-pack"]:
        rows = [row for row in data["runs"] if row["condition"] == condition]
        times = [row["seconds"] for row in rows]
        usages = [row["usage"] for row in rows if row["usage"] is not None]
        groups[condition] = {
            "runs": len(rows), "strict_successes": sum(row["strict_success"] for row in rows),
            "heldout_passed": sum(row["heldout"]["passed"] for row in rows),
            "heldout_total": sum(row["heldout"]["total"] for row in rows),
            "visible_passes": sum(row["visible_pass"] for row in rows),
            "notes_preserved": sum(row["notes_preserved"] for row in rows),
            "median_seconds": round(statistics.median(times), 2) if times else None,
            "usage_records": len(usages),
            "input_tokens": sum(usage.get("input_tokens", 0) for usage in usages),
            "cached_input_tokens": sum(usage.get("cached_input_tokens", 0) for usage in usages),
            "output_tokens": sum(usage.get("output_tokens", 0) for usage in usages),
            "reasoning_output_tokens": sum(usage.get("reasoning_output_tokens", 0) for usage in usages),
        }
    return groups


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(json.loads(args.results.read_text())), indent=2))
