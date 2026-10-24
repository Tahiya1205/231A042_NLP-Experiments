# Meeting Transcript Analysis for Hindi, Tamil and Marathi

**Student:** Raza Tahiya Ishaque
**Roll no.:** 231A042
**Course:** 231A042 — Natural Language Processing
**Assigned application:** Meeting Transcript Analysis

## Aim and experimental design

This project evaluates a meeting-transcript workflow in Hindi (`hi`), Tamil (`ta`) and Marathi (`mr`). Every recording states a decision and action items; the second item in each language additionally uses English technical terms such as *sprint*, *login bug*, *GitHub*, and *issue*.

The same six MP3 recordings were supplied to both tools. They are consent-safe neural-TTS renderings of the scripts in `data/meeting_manifest.jsonl`; audio is deliberately excluded from Git. The results are therefore a **synthetic-speech reproducibility smoke test**, not a claim about diverse human speakers. Raw tool output and score files are committed in `results/`.

| Control | Value |
|---|---|
| Samples | Six: two Hindi, two Tamil, two Marathi |
| Input | Exactly one shared recording per ID for both tools |
| Language setting | Fixed from manifest (`hi`, `ta`, `mr`) |
| Script | Hindi/Marathi: Devanagari; Tamil: Tamil script |
| Metrics | Punctuation-insensitive NFC-normalised WER and CER |

---

## (i) Real-world tool tried: Whisper Tiny

**Tool:** OpenAI Whisper Tiny, run locally through `faster-whisper`. It converts a meeting recording into searchable UTF-8 text. Input was a synthetic MP3 with an explicitly fixed language code. The command and dependencies are in `README.md`; raw responses are in `results/whisper_tiny_synthetic/`.

| ID | Language/input | Actual Whisper output excerpt | Result |
|---|---|---|---|
| `hi_01` | Hindi | `Kalki bedhak... Neha data slide... Rohan...` | Language detected as Hindi, but output is largely Latin transliteration with word substitutions. |
| `ta_01` | Tamil | `நாட்ட்டுக்காக கன்பதில்...` | Tamil script is retained but multiple content words and action details are corrupted. |
| `mr_01` | Marathi | `Kalcha Baitkit... Sneha, Daita...` | Marathi becomes Latin transliteration, not the expected Devanagari transcript. |

Whisper detected the intended language for all six items with reported probability `1.000`, and retained a few names/terms such as *Neha*, *data*, and *login*. It failed the core usability requirement for a native-language meeting archive: Hindi/Marathi were often Romanised, Tamil had severe word errors, and code-switching was distorted. Examples: `sprint` → `aglis print` in `hi_02`, and `GitHub issue` → `Github Tishu` in `mr_02`. These errors can damage search, task extraction, and accountability.

---

## (ii) Same-data comparison with two tools

| Tool | Implementation | Why it is distinct |
|---|---|---|
| Whisper Tiny | Local `faster-whisper` model | Open-weight multilingual ASR, processed locally. |
| Google Web Speech | `SpeechRecognition` client using `hi-IN`, `ta-IN`, `mr-IN` locale tags | Independently served ASR; only synthetic/consented audio should be sent to it. |

### Quantitative results

| Tool | Hindi WER / CER | Tamil WER / CER | Marathi WER / CER | Macro WER / CER | N |
|---|---:|---:|---:|---:|---:|
| Whisper Tiny | 99.75% / 104.54% | 84.97% / 52.88% | 88.89% / 99.94% | **91.20% / 85.79%** | 6 |
| Google Web Speech | 16.38% / 11.97% | 44.94% / 19.95% | 32.50% / 16.28% | **31.28% / 16.06%** | 6 |

Google Web Speech had lower WER and CER in all three languages on this six-item synthetic test. Tamil remained its weakest language by WER. This must not be generalised to spontaneous human meetings: the test has a synthetic voice, no noise, no overlap, and no regional-accent diversity.

### Error matrix from actual outputs

| Error category | Whisper Tiny | Google Web Speech | Meeting-analysis impact |
|---|---|---|---|
| Script/transliteration | `कालच्या बैठकीत` → `Kalcha Baitkit` (`mr_01`) | Native script retained for all outputs | Romanisation weakens native-script search and review. |
| Grammar/morphology | `संदर्भ तपासेल` → `Sundar Bhatapase` (`mr_01`) | `संदर्भ तपासेल` → `संदर्भ तपासे` (`mr_01`) | The action is lost or grammatically weakened. |
| Semantic/entity | `GitHub issue` → `Github Tishu` (`mr_02`) | `login bug` → `लोगों बुक` (`hi_02`) | A technical issue becomes unrelated text. |
| Code-switch/context | `sprint` → `aglis print` (`hi_02`) | `GitHub` → `गिटार` (`hi_02`); `GitHub` → `கஜாப்` (`ta_02`) | Platform/product terms need a glossary and confirmation. |
| Deadline/context | `शुक्रवार तक` appears only in an inaccurate Romanised sentence (`hi_01`) | `வெள்ளிக்கிழமைக்குள்` → `வெள்ளிக்கிழமை போல்` (`ta_01`) | A deadline can be altered. |

Neither ASR output is safe for automatic task creation without review. Google preserved much of clean `hi_01` and `mr_01`, but technical-term errors make code-switched cases unsafe. Whisper Tiny's script changes and substitutions make automatic decision/action extraction unsafe across the set.

---

## (iii) Concrete adaptation for Hindi, Tamil and Marathi

### Required linguistic resources and implementation

| Resource | Hindi | Tamil | Marathi | Concrete step |
|---|---|---|---|---|
| Meeting-speech corpus | Devanagari meetings across regions/registers | Tamil-script formal/colloquial meetings | Marathi meetings, distinct from Hindi despite shared script | Collect consented audio with original-script transcripts, speaker turns, decisions, action items and deadlines. Split train/test by speaker. |
| ASR adaptation | Hindi + Hindi-English code-switching | Tamil acoustic/morphological coverage | Marathi acoustic/language model | Fine-tune and evaluate separate language routes from an Indic model suite such as [IndicConformerASR](https://github.com/AI4Bharat/IndicConformerASR). Report WER/CER and entity/action recall per language. |
| Normalisation/tokenisation | Unicode NFC; Devanagari rules | Tamil normalisation and morphology-aware segmentation | Unicode NFC; Marathi morphology | Preserve raw text and make a separate normalised scoring copy using the [Indic NLP Library](https://github.com/AI4Bharat/Indic-NLP-Library). Never replace raw evidence with translation. |
| Names and technical terms | Hindi/English aliases | Tamil/English aliases | Marathi/English aliases | Maintain a user-approved project glossary; apply contextual biasing and show all corrections for review. |
| Note-extraction labels | Decisions, tasks, assignees, deadlines | Same labels in Tamil | Same labels in Marathi | Train/evaluate note extraction separately from ASR; score factual correctness, not summary fluency. |

### Sociolinguistic challenges

| Challenge | Why it matters | Mitigation |
|---|---|---|
| Code-switching | The test shows repeated errors in *sprint*, *GitHub issue*, and *login bug*. | Include naturally code-switched data; retain spoken terms and use bilingual terminology lists. |
| Dialects/accents | A model trained on one region/register can fail elsewhere. | Recruit diverse consented speakers and audit errors by dialect/region with adequate samples. |
| Script variation | Hindi/Marathi share Devanagari; Tamil uses another script; outputs may be Romanised. | Use language ID and script-aware normalisation; make transliteration reversible, never the stored transcript. |
| Names/honorifics | A name error can assign work to the wrong person. | Confirm participant names and require review before task distribution. |
| Relative time | `आज शाम तक`, `வெள்ளிக்கிழமைக்குள்`, and `शुक्रवारपर्यंत` need meeting date/timezone. | Store meeting time/timezone; show both original phrase and resolved date for confirmation. |
| Privacy/consent | Meetings can contain sensitive information. | Obtain consent, minimise retention, encrypt storage, restrict access, and permit correction/deletion. |

### Recommended production pipeline

```text
consented meeting audio
  → language ID + voice activity detection
  → Hindi / Tamil / Marathi ASR route (original-script text)
  → normalisation + approved glossary suggestions (raw text retained)
  → decision/action/assignee/deadline extraction
  → human confirmation of names, deadlines and decisions
  → searchable transcript and approved meeting notes
```

Human confirmation is necessary: a low average error rate is still unacceptable when it changes a task owner, technical term, or deadline.

## Reproducibility and references

The manifest, runners, exact raw transcripts and evaluations are versioned in this folder. Audio is excluded because it is derived media; its text and language labels are in the manifest.

1. Radford et al. (2022), [Whisper: Robust Speech Recognition via Large-Scale Weak Supervision](https://arxiv.org/abs/2212.04356).
2. [OpenAI Whisper](https://github.com/openai/whisper).
3. [AI4Bharat IndicConformerASR](https://github.com/AI4Bharat/IndicConformerASR).
4. [AI4Bharat Indic NLP Library](https://github.com/AI4Bharat/Indic-NLP-Library).
