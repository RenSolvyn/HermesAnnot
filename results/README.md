# Annotation Results
 
Drop annotator JSON exports into this folder and push to main.
 
GitHub Actions will automatically:
1. Validate each export (structure, fingerprint, completeness)
2. Generate per-annotator summary stats
3. Flag rubber-stamping (>95% correct) and incomplete reviews
4. Run Cohen's κ when 2+ annotators are present
5. Commit `REPORT.md` with compiled results
 
## How to add results
 
1. Annotator finishes in HERMES, downloads their JSON
2. They send it to you (email, Teams, etc.)
3. Rename to something clear: `reviewer_a.json`, `reviewer_b.json`
4. Drop into this folder, commit, push
5. Check Actions tab for the compiled report
 
## Threshold
 
κ ≥ 0.80 on negation, sentiment, and cause_effect = **validated**.
 
