"""Evaluate transcript and meeting-note fields against the assignment reference set.

The prediction file must be JSONL with `id`, `language`, and `transcript` fields.
Optional `decision` and `action_items` fields can be included after a tool generates
meeting notes.  `action_items` must be a list of {assignee, task, due_date} objects.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

from jiwer import wer


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def normalise(text: str) -> str:
    """Normalise formatting only; never transliterate or translate a transcript."""
    text = unicodedata.normalize("NFC", text).lower()
    text = re.sub(r"[\u0964\u0965.,!?;:\"'()\[\]{}…—–-]", " ", text)
    return " ".join(text.split())


def levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for index, source_char in enumerate(left, start=1):
        current = [index]
        for target_index, target_char in enumerate(right, start=1):
            current.append(min(
                current[-1] + 1,
                previous[target_index] + 1,
                previous[target_index - 1] + (source_char != target_char),
            ))
        previous = current
    return previous[-1]


def character_error_rate(reference: str, hypothesis: str) -> float:
    reference_chars = reference.replace(" ", "")
    hypothesis_chars = hypothesis.replace(" ", "")
    return levenshtein(reference_chars, hypothesis_chars) / max(1, len(reference_chars))


def fact_score(reference: dict[str, Any], prediction: dict[str, Any]) -> tuple[str, str]:
    """Conservative exact-normalised scoring for generated meeting notes."""
    if "decision" not in prediction and "action_items" not in prediction:
        return "not evaluated", "not evaluated"

    decision_ok = normalise(str(reference["decision"])) == normalise(str(prediction.get("decision", "")))
    reference_actions = {
        (normalise(str(action.get("assignee", ""))), normalise(str(action.get("task", ""))), normalise(str(action.get("due_date") or "")))
        for action in reference["action_items"]
    }
    predicted_actions = {
        (normalise(str(action.get("assignee", ""))), normalise(str(action.get("task", ""))), normalise(str(action.get("due_date") or "")))
        for action in prediction.get("action_items", [])
    }
    action_score = len(reference_actions & predicted_actions) / max(1, len(reference_actions))
    return ("correct" if decision_ok else "incorrect", f"{action_score:.0%}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Score one ASR/meeting-notes tool.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--tool", required=True)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    reference = {record["id"]: record for record in read_jsonl(args.manifest)}
    predictions = {record["id"]: record for record in read_jsonl(args.predictions)}
    rows: list[dict[str, Any]] = []
    for item_id, gold in reference.items():
        predicted = predictions.get(item_id)
        if predicted is None:
            rows.append({"id": item_id, "language": gold["language"], "status": "missing", "wer": "", "cer": "", "decision": "", "action_recall": ""})
            continue
        gold_text = normalise(gold["reference_text"])
        predicted_text = normalise(str(predicted.get("transcript", "")))
        decision, action_recall = fact_score(gold, predicted)
        rows.append(
            {
                "id": item_id,
                "language": gold["language"],
                "status": "scored",
                "wer": round(wer(gold_text, predicted_text), 4),
                "cer": round(character_error_rate(gold_text, predicted_text), 4),
                "decision": decision,
                "action_recall": action_recall,
            }
        )

    output = args.output or args.predictions.with_name("evaluation.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["status"] == "scored":
            grouped[row["language"]].append(row)
    print(f"{args.tool} — results saved to {output}")
    for language, language_rows in sorted(grouped.items()):
        mean_wer = sum(float(row["wer"]) for row in language_rows) / len(language_rows)
        mean_cer = sum(float(row["cer"]) for row in language_rows) / len(language_rows)
        print(f"{language}: WER={mean_wer:.2%}, CER={mean_cer:.2%}, n={len(language_rows)}")


if __name__ == "__main__":
    main()
