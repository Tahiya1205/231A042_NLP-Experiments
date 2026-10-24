"""Convert one-folder-per-tool transcript files into evaluator JSONL format."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build JSONL predictions from transcript text files.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--transcript-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tool", required=True)
    args = parser.parse_args()

    manifest = [json.loads(line) for line in args.manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    records = []
    for item in manifest:
        transcript_path = args.transcript_dir / f"{item['id']}.txt"
        if not transcript_path.exists():
            print(f"SKIP {item['id']}: missing {transcript_path}")
            continue
        records.append(
            {
                "id": item["id"],
                "language": item["language"],
                "transcript": transcript_path.read_text(encoding="utf-8").strip(),
                "tool": args.tool,
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Saved {len(records)} predictions to {args.output}")


if __name__ == "__main__":
    main()
