"""Create a review sheet for extracting decisions and actions from a transcript.

This is intentionally human-verifiable: a meeting-note model can fill the values,
but the evaluator must compare them with the gold annotations before claiming success.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an auditable meeting-notes review sheet.")
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    records = [json.loads(line) for line in args.predictions.read_text(encoding="utf-8").splitlines() if line.strip()]
    lines = ["# Meeting-note review sheet", "", "For each transcript, extract only explicitly stated information. Use `Not stated` for a missing assignee or due date.", ""]
    for record in records:
        lines.extend([
            f"## {record['id']} ({record['language']})",
            "", f"**Transcript:** {record['transcript']}", "",
            "- Decision: `TO BE EXTRACTED`",
            "- Action 1 — assignee: `TO BE EXTRACTED`; task: `TO BE EXTRACTED`; due date: `TO BE EXTRACTED`",
            "- Action 2 — assignee: `TO BE EXTRACTED`; task: `TO BE EXTRACTED`; due date: `TO BE EXTRACTED`",
            "",
        ])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
