"""Transcribe the assignment recordings with OpenAI Whisper via faster-whisper.

Example:
    python scripts/transcribe_whisper.py --audio-dir data/audio \
        --manifest data/meeting_manifest.jsonl --output-dir results/whisper
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from faster_whisper import WhisperModel


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run multilingual Whisper on meeting audio.")
    parser.add_argument("--audio-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model", default="small", help="Whisper model size or model identifier.")
    parser.add_argument("--device", default="cpu", choices=("cpu", "cuda", "auto"))
    parser.add_argument("--compute-type", default="int8", help="Use float16 on a compatible CUDA GPU.")
    parser.add_argument("--beam-size", default=5, type=int)
    args = parser.parse_args()

    device = "cuda" if args.device == "auto" else args.device
    model = WhisperModel(args.model, device=device, compute_type=args.compute_type)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    for item in read_jsonl(args.manifest):
        audio_path = next(
            (args.audio_dir / f"{item['id']}{suffix}" for suffix in (".wav", ".mp3", ".m4a", ".flac") if (args.audio_dir / f"{item['id']}{suffix}").exists()),
            None,
        )
        if audio_path is None:
            print(f"SKIP {item['id']}: no .wav, .mp3, .m4a, or .flac file found")
            continue

        segments, info = model.transcribe(
            str(audio_path),
            language=item["language"],
            task="transcribe",
            beam_size=args.beam_size,
            vad_filter=True,
            condition_on_previous_text=False,
        )
        transcript = " ".join(segment.text.strip() for segment in segments).strip()
        (args.output_dir / f"{item['id']}.txt").write_text(transcript + "\n", encoding="utf-8")
        records.append(
            {
                "id": item["id"],
                "language": item["language"],
                "transcript": transcript,
                "detected_language": info.language,
                "language_probability": round(info.language_probability, 4),
                "tool": "Whisper/faster-whisper",
                "model": args.model,
            }
        )
        print(f"DONE {item['id']} ({info.language}, p={info.language_probability:.3f})")

    with (args.output_dir / "predictions.jsonl").open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Saved {len(records)} transcripts to {args.output_dir}")


if __name__ == "__main__":
    main()
