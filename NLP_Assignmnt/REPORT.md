# Meeting Transcript Analysis in Hindi, Tamil and Marathi

**Student:** Raza Tahiya Ishaque
**Roll no.:** 231A042
**Course:** 231A042 — Natural Language Processing
**Assigned application:** Meeting Transcript Analysis

## Aim and research question

The aim is to assess an Indian-language meeting-transcript workflow. Given a short meeting recording, can it (1) produce searchable text in the speaker's original script, and (2) preserve the decision, assignee and deadline needed for meeting notes?

The comparison uses six matched, consent-safe scripted recordings: two each in Hindi, Tamil and Marathi. In every language, one sample uses native-script speech and one deliberately contains English technical terms such as *sprint*, *login bug*, *GitHub* and *issue*. This makes code-switching observable instead of treating it as a hidden source of error.

> **Evidence status:** This report is submission-ready in structure and methodology. Replace every `PENDING RUN` cell only with the output produced by the documented run, and add the five screenshots named in `EVIDENCE_CHECKLIST.md`. Metrics and screenshots must never be invented.

---

## (i) Real-world tool tried: local Whisper meeting-transcript workflow

### Tool and purpose

[OpenAI Whisper](https://github.com/openai/whisper), executed through the `faster-whisper` implementation, is the selected real-world speech-recognition tool. It converts a meeting recording into a time-ordered, searchable UTF-8 transcript. The transcript is then reviewed using the structured meeting-note template to identify decisions and action items. This is a practical open-source alternative to the transcription stage used by products such as Otter.ai or Fireflies.ai, and it does not require uploading meeting audio to a third-party account.

### Input given

The input is a 16-kHz mono WAV recording named `<id>.wav`; the complete reference scripts and language tags are in `data/meeting_manifest.jsonl`. The run fixes the language code (`hi`, `ta`, or `mr`) and uses `task="transcribe"`, so the result is intended to be a transcription rather than an English translation.

| Input ID | Language | Meeting information embedded in the recording | Evidence |
|---|---|---|---|
| `hi_01`, `hi_02` | Hindi | Decision, two/one action(s), deadline; `hi_02` is Hindi-English code-switched | `screenshots/01_whisper_input.png` |
| `ta_01`, `ta_02` | Tamil | Decision, two/one action(s), deadline; `ta_02` is Tamil-English code-switched | `screenshots/01_whisper_input.png` |
| `mr_01`, `mr_02` | Marathi | Decision, two/one action(s), deadline; `mr_02` is Marathi-English code-switched | `screenshots/01_whisper_input.png` |

**Recording conditions to fill after the run:** microphone/device: `PENDING RUN`; number of speakers: `PENDING RUN`; room/noise condition: `PENDING RUN`; recording date: `PENDING RUN`.

### System response

The runner writes a UTF-8 transcript for every recording to `results/whisper/<id>.txt` and a machine-readable `predictions.jsonl`. The response below must contain copied output, not a paraphrase.

| Example ID | Generated transcript (native script) | Decision retained? | Actions/assignee/deadline retained? | Snapshot |
|---|---|---|---|---|
| `hi_01` | `PENDING RUN` | `PENDING RUN` | `PENDING RUN` | `screenshots/02_whisper_output.png` |
| `ta_01` | `PENDING RUN` | `PENDING RUN` | `PENDING RUN` | `screenshots/02_whisper_output.png` |
| `mr_01` | `PENDING RUN` | `PENDING RUN` | `PENDING RUN` | `screenshots/02_whisper_output.png` |

### Successes and failures to analyse from actual output

Successful behaviour is: native-script output; correctly retained names, English product terms, decisions, action assignments and relative deadlines. Failure is: omitted/substituted words, incorrect script, unintended translation, loss of a named person or deadline, wrong speaker attribution, or a culturally implausible interpretation.

The expected stress points are not results: homophones; Devanagari ambiguity between Hindi and Marathi; Tamil morphology and orthographic word boundaries; regional pronunciation; proper names; and English terms embedded in Indian-language speech. Mark a point as a real failure only after it appears in the saved reference/prediction pair.

---

## (ii) Two-tool comparison and error matrix

### Experimental controls

Both tools receive the exact same WAV file, not separately re-recorded speech. For each sample, the intended language is fixed to the manifest language. Native script is retained for evaluation and no transcript is translated before scoring. WER and CER are reported because word segmentation and agglutination can distort WER, especially for Tamil. The set is a small exploratory classroom test, not a population-level accuracy estimate.

| Tool | Type | Language coverage relevant here | Output location |
|---|---|---|---|
| Whisper via `faster-whisper` | General multilingual ASR baseline | Hindi, Tamil, Marathi | `results/whisper/` |
| AI4Bharat IndicConformerASR | Indic-focused ASR model suite | Hindi, Tamil, Marathi | `results/indicconformer/` |

### Quantitative results

Run `scripts/evaluate_asr.py` for both output files. The script applies NFC normalisation and removes punctuation for scoring; it does not translate or transliterate text.

| Tool | Hindi WER / CER | Tamil WER / CER | Marathi WER / CER | Macro WER / CER | N | Evidence file |
|---|---|---|---|---|---:|---|
| Whisper | `PENDING RUN` | `PENDING RUN` | `PENDING RUN` | `PENDING RUN` | 6 | `results/whisper/evaluation.csv` |
| IndicConformer | `PENDING RUN` | `PENDING RUN` | `PENDING RUN` | `PENDING RUN` | 6 | `results/indicconformer/evaluation.csv` |

### Error matrix

Populate each cell with a short actual example in the form `reference → output (ID)`. A dash means no observed example in this six-item data set; it does not mean the model can never make that error.

| Error category | Whisper | IndicConformer | Interpretation |
|---|---|---|---|
| Grammatical / morphology | `PENDING RUN` | `PENDING RUN` | Wrong inflection, case/postposition, tense, or attached suffix that changes meaning. |
| Semantic / entity | `PENDING RUN` | `PENDING RUN` | Wrong person, product name, number, date, decision or action. |
| Script / transliteration | `PENDING RUN` | `PENDING RUN` | Incorrect Devanagari/Tamil spelling, Latin transliteration, or language-script confusion. |
| Code-switch / context loss | `PENDING RUN` | `PENDING RUN` | Lost, hallucinated or incorrectly segmented terms such as `GitHub`, `sprint`, or `login bug`. |
| Cultural or regional misunderstanding | `PENDING RUN` | `PENDING RUN` | A regional pronunciation, honorific, local expression or relative deadline interpreted incorrectly. |

### Interpretation after scoring

State the outcome in this form after results exist: “On this six-sample, matched set, **[tool]** had lower/higher `[WER/CER]` for `[language]`. The most consequential observed issue was `[evidence]` because it `[changed/preserved]` a meeting decision or responsibility.” Do not generalise from six recordings to all speakers of an Indian language.

---

## (iii) Adapting the tool for Indian languages

The following recommendations apply to a production meeting-transcript system serving **Hindi, Tamil and Marathi**. They directly address the required linguistic resources and sociolinguistic issues.

### A. Required linguistic resources

| Need | Hindi | Tamil | Marathi | Concrete adaptation step |
|---|---|---|---|---|
| Consent-based meeting-speech corpus | Devanagari speech from multiple regions and formal/informal meetings | Tamil-script speech covering formal, colloquial and technical meeting vocabulary | Devanagari speech across regional varieties and professional registers | Collect audio with verbatim original-script transcripts, speaker turns, decisions, action items and a consent/retention policy. Split speakers—not utterances—between train/dev/test. |
| ASR acoustic/language model | Fine-tune and evaluate an Indic ASR checkpoint with Hindi meeting audio | Fine-tune/evaluate a Tamil model; retain grapheme-level scoring | Fine-tune/evaluate a Marathi model separately from Hindi despite shared script | Start from IndicConformer/Whisper, adapt with held-out meeting audio, and publish WER/CER plus entity/action recall per language. |
| Tokenisation and normalisation | Unicode NFC; Devanagari punctuation; Hindi-English term lexicon | Unicode NFC; Tamil tokeniser/normaliser; joined morphology handled without forcing English spacing | Unicode NFC; Marathi morphological forms and Devanagari normalisation | Maintain original text and a separate normalised score version. Use the [Indic NLP Library](https://github.com/AI4Bharat/Indic-NLP-Library) resources where applicable; never normalise away evidence in the raw transcript. |
| Named-entity/term resources | People, organisations, project terms, Hindi/English spellings | Tamil/English technical term aliases and person names | Marathi/English terms and names | Build a project glossary from user-approved names. Use contextual biasing or post-ASR review; log every glossary correction. |
| Meeting-note extraction data | Decision/action/assignee/deadline annotations in Hindi | Equivalent annotations in Tamil | Equivalent annotations in Marathi | Train/evaluate extraction separately from ASR. Use fact-level precision/recall; do not score a fluent summary as correct unless its facts match the transcript. |
| Evaluation benchmark | Balanced speakers, code-switching, noise and dialect conditions | Same, with morphology-aware CER plus WER | Same, including Hindi–Marathi script-confusion checks | Version the test set and report language-wise results, confidence intervals for larger samples, and a human error review. |

### B. Sociolinguistic challenges and mitigations

| Challenge | Why it matters in a meeting | Mitigation |
|---|---|---|
| Code-switching | People naturally say “sprint”, “GitHub issue” or “login bug” within Hindi, Tamil or Marathi clauses. An ASR system may delete, translate or respell those terms. | Include naturally code-switched, consented data; maintain bilingual terminology; preserve the spoken language and script rather than translating automatically. |
| Dialects and regional accents | A model trained on one city/register may fail on another pronunciation, even when the language label is correct. | Recruit diverse speakers; report results by region only with informed consent and sufficient samples; audit accent-specific error rates. |
| Script variation and transliteration | Hindi and Marathi share Devanagari but are different languages; Tamil uses a different script. Users may also type or speak named entities in Latin forms. | Use language ID plus script-aware normalisation; retain original form; offer a reversible transliteration view, not a replacement transcript. |
| Honorifics and names | Dropping an honorific or confusing similar names can change who owns an action item. | Make participant names user-confirmed, add a glossary, and require user review before sending tasks. |
| Relative time phrases | “आज शाम तक”, “வெள்ளிக்கிழமைக்குள்”, and “शुक्रवारपर्यंत” require meeting date and locale to become calendar dates. | Store meeting timezone/date, retain the original phrase, and show any resolved date as a confirmation—not a hidden assumption. |
| Privacy and consent | Meeting speech may contain personal, organisational or sensitive data. | Obtain consent, minimise retention, encrypt stored audio, restrict access, and allow correction/deletion. Never train a model on private meeting audio without explicit permission. |

### Proposed deployment pipeline

```text
consented audio
  → language ID + voice activity detection
  → Hindi/Tamil/Marathi ASR route (original-script transcript)
  → normalisation + glossary suggestions (raw text preserved)
  → speaker/decision/action extraction
  → user review of names, deadlines and decisions
  → searchable transcript and approved meeting notes
```

Human review is required at the action-item stage: a transcription that is mostly correct can still be harmful if it assigns a task to the wrong person or changes a deadline.

---

## Reproducibility and ethical note

The exact reference data, runners, scoring method, model names and report templates are versioned in this folder. Audio is excluded from Git because speech is personal data. Only consented audio should be used; screenshots should not reveal private meeting material. No conclusion in this report should be presented as measured until the corresponding raw transcript, evaluation CSV and screenshot have been saved.

## References

1. Radford, A. et al. (2022). *Robust Speech Recognition via Large-Scale Weak Supervision*. https://arxiv.org/abs/2212.04356
2. OpenAI. *Whisper*. https://github.com/openai/whisper
3. AI4Bharat. *IndicConformerASR*. https://github.com/AI4Bharat/IndicConformerASR
4. Conneau, A. et al. (2023). *FLEURS: Few-shot Learning Evaluation of Universal Representations of Speech*. https://arxiv.org/abs/2205.12446
5. AI4Bharat. *Indic NLP Library*. https://github.com/AI4Bharat/Indic-NLP-Library
