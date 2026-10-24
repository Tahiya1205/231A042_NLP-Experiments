# Evidence checklist

The question specifically asks for input and output snapshots. Use this checklist after performing the runs; save images in `screenshots/` using the suggested names and link them from `REPORT.md`.

## Question (i): one real-world tool

For the selected tool (Whisper workflow):

- [ ] `01_whisper_input.png` — terminal or notebook view showing the selected `.wav` file(s), model name, and explicitly set language code.
- [ ] `02_whisper_output.png` — output view showing the generated native-script transcript for one sample, including the file/record ID.
- [ ] `03_whisper_notes.png` — review sheet or tool output showing the extracted decision and action item(s).
- [ ] Record the input device, noise condition, speakers and date in the report. Do not show a volunteer's identifiable information without consent.

## Question (ii): same data in two tools

- [ ] `04_indicconformer_input.png` — IndicConformer UI/terminal/notebook with the **same** audio identifier.
- [ ] `05_indicconformer_output.png` — its native-script transcript for the same identifier.
- [ ] Save raw files as `results/whisper/<id>.txt` and `results/indicconformer/<id>.txt`.
- [ ] Run `evaluate_asr.py` for both tools and paste the emitted metrics in `REPORT.md`.
- [ ] Quote at least one exact reference/prediction pair for every reported error category. This keeps the error matrix evidence-based.

## Screenshot integrity

Do not crop out a tool/model name, edit transcript text, or substitute translated text for the native-script output. If a tool cannot process one language, capture that failure and report it as a limitation rather than silently excluding it.
