#!/usr/bin/env python3
"""
HERMES Result Compiler
======================
Validates annotator exports and generates summary reports.
Runs automatically via GitHub Actions when files land in results/.

Usage:
    python compile_results.py results/*.json
"""

import json, sys, os, glob
from collections import defaultdict
from datetime import datetime

def load_and_validate(path):
    """Load an annotator export and validate its structure."""
    with open(path) as f:
        data = json.load(f)

    errors = []
    for key in ["reviewer", "dataset_fingerprint", "responses", "total_items", "total_reviewed"]:
        if key not in data:
            errors.append(f"Missing required key: {key}")

    if not isinstance(data.get("responses"), list):
        errors.append("'responses' must be a list")

    if errors:
        return None, errors

    # Validate responses
    for i, r in enumerate(data["responses"][:5]):
        for field in ["feature", "index", "human_verdict"]:
            if field not in r:
                errors.append(f"Response {i} missing '{field}'")
                break

    return data, errors


def annotator_summary(data, path):
    """Generate per-annotator stats."""
    responses = [r for r in data["responses"] if not r.get("is_probe")]
    verdicts = defaultdict(int)
    features = defaultdict(lambda: defaultdict(int))
    times = []

    for r in responses:
        verdicts[r["human_verdict"]] += 1
        features[r["feature"]][r["human_verdict"]] += 1
        if r.get("response_time_ms") and r["response_time_ms"] > 0:
            times.append(r["response_time_ms"])

    total = len(responses)
    correct = verdicts.get("correct", 0)
    wrong = verdicts.get("wrong", 0)
    unsure = verdicts.get("unsure", 0)
    agreement = round(correct / total * 100, 1) if total > 0 else 0
    median_ms = sorted(times)[len(times) // 2] if times else 0

    # Rubber-stamp check
    rubber_stamp = agreement > 95

    # Self-consistency from probes
    probes = data.get("self_consistency", {})
    probe_rate = probes.get("agreement_rate", "N/A")

    return {
        "file": os.path.basename(path),
        "reviewer": data.get("reviewer", "unknown"),
        "fingerprint": data.get("dataset_fingerprint", "unknown"),
        "total": total,
        "correct": correct,
        "wrong": wrong,
        "unsure": unsure,
        "agreement": agreement,
        "median_ms": median_ms,
        "rubber_stamp": rubber_stamp,
        "probe_rate": probe_rate,
        "features": dict(features),
        "tool_version": data.get("tool_version", "unknown"),
    }


def format_report(summaries, fingerprints_match):
    """Format a markdown report."""
    lines = []
    lines.append("# HERMES Annotation Results")
    lines.append(f"_Compiled: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}_\n")

    # Dataset integrity
    fps = list(set(s["fingerprint"] for s in summaries))
    if len(fps) == 1:
        lines.append(f"**Dataset fingerprint:** `{fps[0]}` (all annotators match)\n")
    else:
        lines.append(f"**⚠ FINGERPRINT MISMATCH** — annotators used different datasets: {fps}\n")

    lines.append(f"**Annotators:** {len(summaries)}\n")

    # Per-annotator table
    lines.append("## Per-Annotator Summary\n")
    lines.append("| File | Reviewer | Items | Correct | Wrong | Unsure | Agreement | Median RT | Self-consistency | Flags |")
    lines.append("|------|----------|-------|---------|-------|--------|-----------|-----------|-----------------|-------|")

    for s in summaries:
        flags = []
        if s["rubber_stamp"]:
            flags.append("⚠ RUBBER-STAMP")
        if s["total"] < 1000:
            flags.append("⚠ INCOMPLETE")
        flag_str = ", ".join(flags) if flags else "—"

        lines.append(
            f"| {s['file']} | {s['reviewer'][:12]} | {s['total']} | "
            f"{s['correct']} ({s['agreement']}%) | {s['wrong']} | {s['unsure']} | "
            f"{s['agreement']}% | {s['median_ms']}ms | {s['probe_rate']}% | {flag_str} |"
        )

    # Per-feature breakdown
    all_features = sorted(set(f for s in summaries for f in s["features"]))
    if all_features:
        lines.append("\n## Per-Feature Agreement\n")
        header = "| Feature |" + " | ".join(s["file"][:15] for s in summaries) + " |"
        sep = "|---------|" + " | ".join("---" for _ in summaries) + " |"
        lines.append(header)
        lines.append(sep)
        for feat in all_features:
            row = f"| {feat} |"
            for s in summaries:
                fd = s["features"].get(feat, {})
                total = sum(fd.values())
                correct = fd.get("correct", 0)
                rate = round(correct / total * 100) if total > 0 else 0
                row += f" {rate}% ({correct}/{total}) |"
            lines.append(row)

    # Status
    lines.append("\n## Status\n")
    if len(summaries) < 2:
        lines.append("**Waiting for more annotators.** Need 2+ to compute inter-rater agreement (Cohen's κ).\n")
        lines.append(f"Current: {len(summaries)} of 2 required.\n")
    else:
        lines.append(f"**{len(summaries)} annotators submitted.** Run kappa pipeline for inter-rater agreement:\n")
        files = " ".join(s["file"] for s in summaries)
        lines.append(f"```\npython sfrp_kappa_pipeline.py results/{files.replace(' ', ' results/')}\n```\n")

    # Warnings
    warnings = []
    for s in summaries:
        if s["rubber_stamp"]:
            warnings.append(f"{s['file']}: {s['agreement']}% correct — possible rubber-stamping")
        if s["total"] < 1000:
            warnings.append(f"{s['file']}: only {s['total']}/{1114} items reviewed")
    if not fingerprints_match:
        warnings.append("Dataset fingerprints don't match across annotators")

    if warnings:
        lines.append("## ⚠ Warnings\n")
        for w in warnings:
            lines.append(f"- {w}")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        # Auto-discover from results/
        paths = sorted(glob.glob("results/*.json"))
        if not paths:
            print("No JSON files found in results/")
            sys.exit(1)
    else:
        paths = sys.argv[1:]

    summaries = []
    for path in paths:
        data, errors = load_and_validate(path)
        if errors:
            print(f"ERROR in {path}: {'; '.join(errors)}")
            continue
        summaries.append(annotator_summary(data, path))

    if not summaries:
        print("No valid annotator exports found.")
        sys.exit(1)

    fps = list(set(s["fingerprint"] for s in summaries))
    fingerprints_match = len(fps) == 1

    report = format_report(summaries, fingerprints_match)
    print(report)

    # Also write to file if results/ dir exists
    if os.path.isdir("results"):
        with open("results/REPORT.md", "w") as f:
            f.write(report)
        print(f"\nReport written to results/REPORT.md")


if __name__ == "__main__":
    main()
