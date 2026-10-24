# NLP Assignment — Meeting Transcript Analysis for Hindi, Tamil and Marathi

**Course:** 231A042 NLP
**Application assigned:** Meeting Transcript Analysis
**Languages evaluated:** Hindi (`hi`), Tamil (`ta`) and Marathi (`mr`)

This submission investigates whether a meeting-transcription workflow can turn short Indian-language meeting recordings into searchable text and reliable meeting notes. It covers every item in the question sheet:

1. one real-world meeting-transcript workflow, its input/output, successes and failures;
2. a comparison of two speech-recognition tools on the *same* data; and
3. concrete adaptation recommendations for Hindi, Tamil and Marathi.

The folder is deliberately reproducible. It does **not** contain invented model output or screenshots. Run the two tools, save their raw transcripts, and complete the small evidence fields in `REPORT.md` using the checklist in `EVIDENCE_CHECKLIST.md`.

## Selected tools

| Tool | Role in the experiment | Why it is appropriate |
|---|---|---|
| [OpenAI Whisper](https://github.com/openai/whisper) (run locally with `faster-whisper`) | Tool A: multilingual ASR baseline | Handles Hindi, Tamil and Marathi, can transcribe uploaded meeting audio locally, and needs no account. |
| [AI4Bharat IndicConformerASR](https://github.com/AI4Bharat/IndicConformerASR) | Tool B: Indic-language ASR comparison | AI4Bharat provides language-specific ASR models for all 22 scheduled Indian languages, including the three languages in this assignment. |

Both tools perform the speech-to-text stage of a real meeting-transcript system. The subsequent note-taking stage is evaluated with the gold `decision` and `action_items` annotations in `data/meeting_manifest.jsonl`; this prevents an LLM summary from being accepted without checking whether it preserved decisions and responsibilities.

## Folder map

```text
NLP_Assignmnt/
├── README.md
├── REPORT.md                    # submit this after adding genuine results/screenshots
├── EVIDENCE_CHECKLIST.md        # exact evidence needed for Question (i)
├── requirements.txt
├── data/
│   ├── meeting_manifest.jsonl   # six consent-safe scripted meeting references
│   └── README.md                # audio and dataset instructions
├── scripts/
│   ├── transcribe_whisper.py    # Tool A runner
│   ├── make_predictions.py      # imports Tool B transcript files for scoring
│   ├── evaluate_asr.py          # WER/CER + decision/action scoring
│   └── extract_notes.py         # template for recording model-generated notes
├── results/
│   └── .gitkeep
└── screenshots/
    └── .gitkeep
```

## Reproducible experiment

### 1. Prepare matched audio

Record each reference utterance in `data/meeting_manifest.jsonl` once, in a quiet room, as 16-kHz mono WAV files named `<id>.wav` (for example, `hi_01.wav`). Each speaker must consent to the recording. Do not commit private meeting recordings. Keep them in `data/audio/`, which is ignored by Git.

For a public ASR-only benchmark, use the Hindi, Tamil and Marathi portions of [FLEURS](https://huggingface.co/datasets/google/fleurs) or [Mozilla Common Voice](https://commonvoice.mozilla.org/). Those datasets are useful for word-error measurement, but the supplied meeting-style scripts are necessary for decision/action extraction.

### 2. Run Tool A (Whisper)

```powershell
cd NLP_Assignmnt
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/transcribe_whisper.py --audio-dir data/audio --manifest data/meeting_manifest.jsonl --output-dir results/whisper
```

The script saves one UTF-8 transcript per recording and `results/whisper/predictions.jsonl`. Use `--model small` for a CPU-friendly baseline; use `medium` only when sufficient memory is available. Keep the language fixed from the manifest—automatic language detection should be reported separately, not silently used.

### 3. Run Tool B (IndicConformerASR)

Follow AI4Bharat's official [installation and model-download instructions](https://github.com/AI4Bharat/IndicConformerASR). For each audio file, select its matching `hi`, `ta`, or `mr` model and save UTF-8 transcripts as:

```text
results/indicconformer/hi_01.txt
results/indicconformer/hi_02.txt
...
```

Then import those files into the same format as the Whisper output:

```powershell
python scripts/make_predictions.py --manifest data/meeting_manifest.jsonl --transcript-dir results/indicconformer --output results/indicconformer/predictions.jsonl --tool "IndicConformer"
```

### 4. Score both tools and document evidence

```powershell
python scripts/evaluate_asr.py --manifest data/meeting_manifest.jsonl --predictions results/whisper/predictions.jsonl --tool "Whisper"
python scripts/evaluate_asr.py --manifest data/meeting_manifest.jsonl --predictions results/indicconformer/predictions.jsonl --tool "IndicConformer"
```

Copy each tool's macro and language-wise WER/CER into `REPORT.md`, write error examples from the actual output, and add the requested screenshots. This is essential: a score alone does not demonstrate the application output.

## Fair-comparison controls

- Use identical audio files, reference text, decoding language, and output normalisation for both tools.
- Keep original-script transcripts. Do **not** transliterate Tamil into Latin script or translate Hindi/Marathi into English before scoring.
- Report WER and CER separately. WER can be unstable for agglutinative Tamil and punctuation/spacing conventions; CER provides a useful complementary measure.
- Report whether the decision, assignee and due date were retained. Low WER does not guarantee a useful meeting summary.
- Label all code-switched and regional-dialect cases. Do not call a cultural issue an ASR error without identifying the reference and predicted text.

## References

1. Radford et al. (2022), [Whisper: Robust Speech Recognition via Large-Scale Weak Supervision](https://arxiv.org/abs/2212.04356).
2. [OpenAI Whisper source repository](https://github.com/openai/whisper).
3. [AI4Bharat IndicConformerASR source repository](https://github.com/AI4Bharat/IndicConformerASR).
4. Conneau et al. (2023), [FLEURS: Few-shot Learning Evaluation of Universal Representations of Speech](https://arxiv.org/abs/2205.12446).
5. [AI4Bharat Indic NLP Library](https://github.com/AI4Bharat/Indic-NLP-Library), for Indic-language normalisation and tokenisation resources.
