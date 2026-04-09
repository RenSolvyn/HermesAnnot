# HERMES — Human Evaluation of Research Model Embedded Semantics

A single-file, zero-dependency annotation tool for validating auto-generated linguistic labels. Runs entirely in your browser — nothing is uploaded, nothing leaves your device.

## Quick Start

**Option A — Online (recommended):**
Open the tool directly:  
👉 [**Launch HERMES**](https://RenSolvyn.github.io/HermesAnnot/sfrp_audit_v5.html)

**Option B — Offline:**
1. Download `sfrp_audit_v5.html` and `audit_set.json`
2. Open `sfrp_audit_v5.html` in Chrome, Safari, or Firefox
3. Load `audit_set.json` when prompted

## How It Works

1. **Enter your name** → used to identify your export (hashed, not stored raw)
2. **Load the audit set** → tap the drop zone and select `audit_set.json`
3. **Review items** → for each sentence, the algorithm's label is shown. Tap:
   - ✅ **Correct** — label is right
   - ❌ **Wrong** — pick the correct label, then a reason
   - ❓ **Not sure** — genuinely ambiguous
4. **Export results** → when done, download your validation JSON

## Features

- 📱 Works on desktop and mobile (Safari, Chrome, Firefox)
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
- Total time: **60–90 minutes** with breaks

## Files

| File | What it is |
|------|-----------|
| `sfrp_audit_v5.html` | The annotation tool |
| `audit_set.json` | 1,114 items across 9 linguistic features |
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

- Single HTML file, ~2,400 lines, zero external dependencies
- Uses `localStorage` for auto-save + optional file-based save/restore
- FNV-1a checksums + SHA-256 integrity hashes on all exports
- Canvas-based animated UI on the load screen (degrades gracefully without JS)
- 40 automated tests (Playwright) covering desktop, mobile touch, and edge cases

---

*Part of the SFRP (Structured Feature Research Program) — investigating semantic geometry in transformer embedding spaces.*

*Part of the SFRP (Structured Feature Research Program) — investigating semantic geometry in transformer embedding spaces.*
