# Data protocol

`meeting_manifest.jsonl` is a **small, scripted, consent-safe reference set**. It has two examples for each required language:

- `*_01`: native-script meeting statement with a decision and two actions;
- `*_02`: a realistic code-switched statement containing product and platform terms.

The reference strings are the gold transcripts. The structured `decision` and `action_items` fields are the gold meeting-note facts. They are not claims about a model's output.

## Recording protocol

1. Ask the speaker's permission; use only a volunteer or your own voice.
2. Record every script once in a quiet setting, with a normal speaking rate.
3. Convert to 16-kHz, mono WAV and use the exact filename `<id>.wav` in `data/audio/`.
4. Do not publish the audio without speaker consent. `data/audio/` is excluded from version control.
5. In the report, state the microphone/device, number of speakers, approximate duration, and noise condition. These affect ASR results.

## Limits

Six short recordings are enough for a transparent classroom demonstration, not for a statistical performance claim. The report therefore describes results as an **exploratory comparison**. A stronger study should add many independent speakers, dialect regions, acoustic conditions, and naturally occurring (consented) meetings.
