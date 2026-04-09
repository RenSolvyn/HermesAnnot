# HERMES — Human Evaluation of Research Model Embedded Semantics
 
A single-file, zero-dependency annotation tool for validating auto-generated linguistic labels. Runs entirely in your browser — nothing is uploaded, nothing leaves your device.
 
## Quick Start
 
**Option A — Online (recommended):**
Open the tool directly:
👉 [**Launch HERMES**](https://RenSolvyn.github.io/HermesAnnot/sfrp_audit_v5.html)
 
**Option B — Offline:**
1. Download `sfrp_audit_v5.html`
2. Open it in Chrome, Safari, or Firefox
3. That's it — the 1,114-item audit set is embedded in the file
 
## How It Works
 
1. **Enter your reviewer name** → hashed into an anonymous ID (e.g., `R-a1b2c3d4`)
2. **Tap Begin** → the embedded audit set loads automatically
3. **Review items in chunks of 25** → for each sentence, the algorithm's label is shown. Tap:
   - ✅ **Correct** — label is right
   - ❌ **Wrong** — pick the correct label, then a reason
   - ❓ **Not sure** — genuinely ambiguous
4. **Take micro-breaks** → every 25 items, a celebration screen shows your chunk stats and estimated time remaining
5. **Export results** → when done, download your validation JSON
 
> **Power users:** To load a custom audit set instead of the embedded one, expand the *Advanced* section on the load screen.
 
## Features
 
- 📱 Works on desktop and mobile (Safari, Chrome, Firefox)
- 🧩 **Chunked progress** — see "3 / 25" not "47 / 1114"; overall progress shown as a subtle secondary bar
- 🎉 **Chunk breaks** every 25 items with stats, encouragement, and estimated time remaining
- 🏆 **Milestones** at 25%, 50%, 75%, and 90% with special celebrations
- 🔥 **Streak counter** after 5+ consecutive reviews
- 🌙 Automatic dark/light mode
- 💾 Auto-saves progress in your browser
- 📂 Save/restore progress to file (survives browser data clears)
- 🔄 Consistency probes (blind re-tests ~5% of items)
- ⏱️ Per-item response timing and fatigue detection
- 🔐 Tamper-evident hash chains on all responses
- ⌨️ Keyboard shortcuts: → correct · ← wrong · ↓ unsure · backspace undo
 
## For Annotators
 
Read the **[Annotation Guidelines](SFRP_Annotation_Guidelines.docx)** before starting. Key rules:
 
- For **negation, tense, number, voice**: judge the **main clause only** — ignore subordinate clauses and quoted speech
- For **sentiment, register, complexity, cause/effect, comparison**: judge the **whole sentence**
- The algorithm makes real mistakes (~10–20%). If you're marking >95% correct, slow down
- Speed target: **5–10 seconds per item**. Use your gut
- Total time: **60–90 minutes** with breaks every 25 items
 
## Files
 
| File | What it is |
|------|-----------|
| `sfrp_audit_v5.html` | The annotation tool (1,114 items embedded) |
| `audit_set_mini.json` | 18-item test set for trying the tool |
| `SFRP_Annotation_Guidelines.docx` | Detailed guide for annotators |
 
## After You Finish
 
1. Tap **Stats** → review your numbers
2. Tap **Download validation results** → saves a JSON file
3. Send the JSON file back
 
Your results are compared with other reviewers using Cohen's κ to measure inter-rater agreement. κ ≥ 0.80 = validated.
 
## Privacy
 
- Everything runs locally in your browser
- No data is sent anywhere — no server, no analytics, no tracking
- Your name is SHA-256 hashed before export (e.g., `R-a1b2c3d4e5f6`)
- The tool works fully offline after the page loads
 
## Technical Details
 
- Single HTML file, ~2,700 lines, zero external dependencies
- 1,114 items across 9 linguistic features + ~50 blind consistency probes embedded directly
- Chunked progress UI: main bar scoped to current 25-item batch, secondary bar for overall
- Uses `localStorage` for auto-save + optional file-based save/restore
- FNV-1a checksums + SHA-256 integrity hashes on all exports
- Canvas-based animated UI on the load screen (degrades gracefully)
- 44 automated Playwright tests covering desktop, mobile, gamification, and a full 1,114-item end-to-end workflow
 
---
