"""Transcribe assignment recordings with Google Web Speech via SpeechRecognition."""

from __future__ import annotations

import argparse
import json
import tempfile
import wave
from pathlib import Path
from typing import Any

import av
import speech_recognition as sr


LANGUAGE_TAGS = {"hi": "hi-IN", "ta": "ta-IN", "mr": "mr-IN"}
AUDIO_SUFFIXES = (".wav", ".mp3", ".m4a", ".flac")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def locate_audio(audio_dir: Path, item_id: str) -> Path | None:
    return next((audio_dir / f"{item_id}{suffix}" for suffix in AUDIO_SUFFIXES if (audio_dir / f"{item_id}{suffix}").exists()), None)


def make_wav(source: Path, destination: Path, sample_rate: int = 16_000) -> None:
    """Decode common audio formats to mono 16-bit WAV for SpeechRecognition."""
    pcm_chunks: list[bytes] = []
    with av.open(str(source)) as container:
        stream = container.streams.audio[0]
        resampler = av.audio.resampler.AudioResampler(format="s16", layout="mono", rate=sample_rate)
        for frame in container.decode(stream):
            converted = resampler.resample(frame)
            for output_frame in converted if isinstance(converted, list) else [converted]:
                pcm_chunks.append(output_frame.to_ndarray().tobytes())
    with wave.open(str(destination), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(b"".join(pcm_chunks))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Google Web Speech on meeting audio.")
    parser.add_argument("--audio-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    recognizer = sr.Recognizer()
    predictions: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    with tempfile.TemporaryDirectory(prefix="nlp-assignment-") as temp_dir:
        for item in read_jsonl(args.manifest):
            audio_path = locate_audio(args.audio_dir, item["id"])
            if audio_path is None:
                errors.append({"id": item["id"], "error": "audio file missing"})
                continue
            wav_path = Path(temp_dir) / f"{item['id']}.wav"
            try:
                make_wav(audio_path, wav_path)
                with sr.AudioFile(str(wav_path)) as source:
                    audio = recognizer.record(source)
                transcript = recognizer.recognize_google(audio, language=LANGUAGE_TAGS[item["language"]])
                (args.output_dir / f"{item['id']}.txt").write_text(transcript + "\n", encoding="utf-8")
                predictions.append({"id": item["id"], "language": item["language"], "transcript": transcript, "tool": "Google Web Speech"})
                print(f"DONE {item['id']}")
            except (sr.UnknownValueError, sr.RequestError, OSError, av.FFmpegError) as error:
                errors.append({"id": item["id"], "error": str(error)})
                print(f"ERROR {item['id']}: {error}")

    with (args.output_dir / "predictions.jsonl").open("w", encoding="utf-8") as handle:
        for record in predictions:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    with (args.output_dir / "errors.json").open("w", encoding="utf-8") as handle:
        json.dump(errors, handle, ensure_ascii=False, indent=2)
    print(f"Saved {len(predictions)} transcripts and {len(errors)} errors to {args.output_dir}")


if __name__ == "__main__":
    main()
