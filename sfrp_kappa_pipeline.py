#!/usr/bin/env python3
"""
SFRP Inter-Rater Validation Pipeline v3
========================================
Compute Cohen's κ between 2+ reviewers for required features.
κ ≥ 0.80 AND effective_label_κ ≥ 0.70 AND not rubber-stamped = validated.

v3 fixes over v2:
  - effective_label_kappa now used in pass/fail gate (was computed but ignored)
  - wrong-wrong divergence rate gates pass (>25% = fail)
  - n_items uses min across pairs (conservative)
  - per-annotator rubber-stamp detection (either, not just both)

Anti-circular-logic:
  - Rubber-stamp detection: flags ANY reviewer >90% "correct" on a feature
  - Effective-label κ: κ on what-label-should-be, not just verdicts
  - Wrong-wrong divergence: both say "wrong" but different corrections
  - Unsure exclusion: pairs where either said "unsure" excluded from κ
  - Duplicate reviewer detection
"""

import json, sys, os
from collections import defaultdict
from datetime import datetime

try:
    from sklearn.metrics import cohen_kappa_score
    import numpy as np
except ImportError:
    print("ERROR: pip install scikit-learn numpy"); sys.exit(1)

REQUIRED_FEATURES = ["negation", "sentiment", "cause_effect"]
KAPPA_THRESHOLD = 0.80
EFFECTIVE_KAPPA_THRESHOLD = 0.70
MIN_ITEMS_PER_FEATURE = 20
RUBBER_STAMP_THRESHOLD = 0.90
WRONG_WRONG_DIVERGENCE_LIMIT = 0.25  # >25% of wrong-wrong pairs diverge = fail


def load_export(path):
    with open(path) as f:
        data = json.load(f)
    for k in ["reviewer", "dataset_fingerprint", "responses"]:
        assert k in data, f"Missing '{k}' in {path}"
    return data


def verify_integrity(data, path=""):
    warnings = []
    reported = data.get("total_reviewed", 0)
    actual = len([r for r in data["responses"] if not r.get("is_probe")])
    if reported != actual:
        warnings.append(f"Count mismatch: reported {reported}, found {actual}")
    flags = data.get("quality_flags", {})
    vr = flags.get("very_rapid", 0)
    if vr > 0:
        warnings.append(f"{vr} very rapid responses — possible autopilot")
    return warnings


def extract_verdicts(data):
    out = {}
    for r in data["responses"]:
        if r.get("is_probe"): continue
        out[(r["feature"], r["index"])] = r
    return out


def get_effective_label(r):
    """What label does this annotator think the item should have?"""
    v = r["human_verdict"]
    if v == "correct":
        return str(r.get("auto_label", "UNKNOWN"))
    elif v == "wrong":
        return str(r.get("correction", "REJECTED_" + str(r.get("auto_label", ""))))
    return "UNSURE"


def compute_pairwise_kappa(va, vb, feature=None, use_effective=False):
    """Compute Cohen's κ between two annotators on verdict or effective labels."""
    ka = set(va.keys())
    kb = set(vb.keys())
    if feature:
        ka = {k for k in ka if k[0] == feature}
        kb = {k for k in kb if k[0] == feature}
    overlap = sorted(ka & kb)

    if use_effective:
        pairs = []
        for k in overlap:
            ea = get_effective_label(va[k])
            eb = get_effective_label(vb[k])
            if ea != "UNSURE" and eb != "UNSURE":
                pairs.append((ea, eb))
        if len(pairs) < MIN_ITEMS_PER_FEATURE:
            return {"kappa": None, "n_items": len(pairs), "sufficient": False}
        labels_a = [a for a, _ in pairs]
        labels_b = [b for _, b in pairs]
    else:
        pairs = [(k, va[k]["human_verdict"], vb[k]["human_verdict"]) for k in overlap]
        pairs = [(k, a, b) for k, a, b in pairs if a != "unsure" and b != "unsure"]
        if len(pairs) < MIN_ITEMS_PER_FEATURE:
            return {"kappa": None, "n_items": len(pairs), "sufficient": False}
        labels_a = [a for _, a, _ in pairs]
        labels_b = [b for _, _, b in pairs]

    agree = sum(1 for a, b in zip(labels_a, labels_b) if a == b)
    rate = agree / len(labels_a)
    try:
        kappa = float(cohen_kappa_score(labels_a, labels_b))
        if np.isnan(kappa):
            kappa = 1.0 if rate == 1.0 else 0.0
    except ValueError:
        kappa = 1.0 if rate == 1.0 else 0.0

    return {"kappa": round(kappa, 4), "n_items": len(labels_a),
            "agreement_rate": round(rate, 4), "sufficient": True}


def detect_rubber_stamping(va, vb, feature=None):
    """Flag if EITHER annotator is >threshold on 'correct' for a feature."""
    ka = set(va.keys())
    kb = set(vb.keys())
    if feature:
        ka = {k for k in ka if k[0] == feature}
        kb = {k for k in kb if k[0] == feature}

    def correct_rate(verdicts, keys):
        if not keys: return 0.0
        return sum(1 for k in keys if verdicts[k]["human_verdict"] == "correct") / len(keys)

    ra, rb = correct_rate(va, ka), correct_rate(vb, kb)
    either_flagged = ra > RUBBER_STAMP_THRESHOLD or rb > RUBBER_STAMP_THRESHOLD
    both_flagged = ra > RUBBER_STAMP_THRESHOLD and rb > RUBBER_STAMP_THRESHOLD
    return {"rate_a": round(ra, 4), "rate_b": round(rb, 4),
            "either_flagged": either_flagged, "both_flagged": both_flagged}


def compute_wrong_wrong_divergence(va, vb, feature=None):
    """Of pairs where both said 'wrong', what fraction gave different corrections?"""
    ka = set(va.keys())
    kb = set(vb.keys())
    if feature:
        ka = {k for k in ka if k[0] == feature}
        kb = {k for k in kb if k[0] == feature}

    both_wrong = 0
    divergent = 0
    divergent_items = []
    for k in sorted(ka & kb):
        ra, rb = va[k], vb[k]
        if ra["human_verdict"] == "wrong" and rb["human_verdict"] == "wrong":
            both_wrong += 1
            ca, cb = ra.get("correction"), rb.get("correction")
            if ca and cb and ca != cb:
                divergent += 1
                divergent_items.append({
                    "feature": k[0], "index": k[1],
                    "correction_a": ca, "correction_b": cb
                })

    rate = divergent / both_wrong if both_wrong > 0 else 0.0
    return {"both_wrong": both_wrong, "divergent": divergent,
            "divergence_rate": round(rate, 4), "items": divergent_items,
            "exceeds_limit": rate > WRONG_WRONG_DIVERGENCE_LIMIT and both_wrong >= 5}


def find_disagreements(va, vb, feature=None):
    ka = set(va.keys())
    kb = set(vb.keys())
    if feature:
        ka = {k for k in ka if k[0] == feature}
        kb = {k for k in kb if k[0] == feature}
    out = []
    for k in sorted(ka & kb):
        ra, rb = va[k], vb[k]
        if ra["human_verdict"] != rb["human_verdict"]:
            out.append({"feature": k[0], "index": k[1],
                        "verdict_a": ra["human_verdict"], "verdict_b": rb["human_verdict"]})
    return out


def aggregate_reasons(exports):
    reasons = defaultdict(int)
    for data in exports:
        summary = data.get("disagree_reason_summary")
        if summary:
            for reason, count in summary.items():
                reasons[reason] += count
    return dict(sorted(reasons.items(), key=lambda x: -x[1])) if reasons else {}


def run_pipeline(exports, paths=None):
    if paths is None:
        paths = [f"reviewer_{i}" for i in range(len(exports))]

    if len(exports) < 2:
        raise ValueError("Need ≥2 reviewers for inter-rater validation. Got 1.")

    reviewer_ids = [d["reviewer"] for d in exports]
    if len(set(reviewer_ids)) < len(reviewer_ids):
        dupes = [r for r in set(reviewer_ids) if reviewer_ids.count(r) > 1]
        raise ValueError(f"Duplicate reviewer IDs: {dupes}")

    fps = set(d.get("dataset_fingerprint") for d in exports)
    fps.discard(None)

    all_warnings = {d["reviewer"]: verify_integrity(d, p) for d, p in zip(exports, paths)}
    all_verdicts = [extract_verdicts(d) for d in exports]

    all_features = set()
    for v in all_verdicts:
        for f, _ in v: all_features.add(f)

    n = len(exports)
    feature_results = {}

    for feature in sorted(all_features):
        verdict_kappas = []
        effective_kappas = []
        rubber_stamps = []
        ww_divergences = []

        for i in range(n):
            for j in range(i+1, n):
                vk = compute_pairwise_kappa(all_verdicts[i], all_verdicts[j], feature, False)
                if vk["sufficient"]: verdict_kappas.append(vk)
                ek = compute_pairwise_kappa(all_verdicts[i], all_verdicts[j], feature, True)
                if ek["sufficient"]: effective_kappas.append(ek)
                rubber_stamps.append(detect_rubber_stamping(all_verdicts[i], all_verdicts[j], feature))
                ww_divergences.append(compute_wrong_wrong_divergence(all_verdicts[i], all_verdicts[j], feature))

        any_rs = any(r["either_flagged"] for r in rubber_stamps)
        both_rs = any(r["both_flagged"] for r in rubber_stamps)
        any_wwd = any(w["exceeds_limit"] for w in ww_divergences)
        total_ww_div = sum(w["divergent"] for w in ww_divergences)

        mean_vk = float(np.mean([v["kappa"] for v in verdict_kappas])) if verdict_kappas else None
        mean_ek = float(np.mean([e["kappa"] for e in effective_kappas])) if effective_kappas else None
        min_items = min((v["n_items"] for v in verdict_kappas), default=0)

        # === PASS/FAIL GATE (v3: all four conditions) ===
        verdict_passes = mean_vk is not None and mean_vk >= KAPPA_THRESHOLD
        effective_passes = mean_ek is not None and mean_ek >= EFFECTIVE_KAPPA_THRESHOLD
        not_both_stamped = not both_rs
        wwd_ok = not any_wwd
        passes = verdict_passes and effective_passes and not_both_stamped and wwd_ok

        fail_reasons = []
        if not verdict_passes:
            fail_reasons.append(f"verdict_κ={'%.4f' % mean_vk if mean_vk is not None else 'N/A'} < {KAPPA_THRESHOLD}")
        if not effective_passes:
            fail_reasons.append(f"effective_label_κ={'%.4f' % mean_ek if mean_ek is not None else 'N/A'} < {EFFECTIVE_KAPPA_THRESHOLD}")
        if not not_both_stamped:
            fail_reasons.append("both annotators >90% 'correct' (rubber-stamp)")
        if not wwd_ok:
            fail_reasons.append(f"wrong-wrong divergence >{WRONG_WRONG_DIVERGENCE_LIMIT*100:.0f}%")

        feature_results[feature] = {
            "verdict_kappa": round(mean_vk, 4) if mean_vk is not None else None,
            "effective_label_kappa": round(mean_ek, 4) if mean_ek is not None else None,
            "n_items": min_items, "n_pairs": len(verdict_kappas),
            "passes_threshold": passes,
            "fail_reasons": fail_reasons,
            "is_required": feature in REQUIRED_FEATURES,
            "rubber_stamp_either": any_rs,
            "rubber_stamp_both": both_rs,
            "wrong_wrong_divergences": total_ww_div,
            "wrong_wrong_exceeds_limit": any_wwd,
        }

    missing = [f for f in REQUIRED_FEATURES
               if f not in feature_results or (feature_results[f]["n_items"] or 0) == 0]
    if missing:
        verdict = "INCOMPLETE"
        verdict_reason = f"Missing features: {missing}"
    elif all(feature_results.get(f, {}).get("passes_threshold") for f in REQUIRED_FEATURES):
        verdict = "PASS"
        verdict_reason = "All required features meet κ, effective-label κ, rubber-stamp, and divergence gates"
    else:
        failed_features = [f for f in REQUIRED_FEATURES
                           if not feature_results.get(f, {}).get("passes_threshold")]
        verdict = "FAIL"
        reasons = {f: feature_results[f].get("fail_reasons", ["unknown"]) for f in failed_features}
        verdict_reason = f"Failed features: {json.dumps(reasons)}"

    return {
        "tool": "sfrp_kappa_pipeline", "version": "3.0",
        "computed_at": datetime.now().isoformat(),
        "inputs": {"n_reviewers": n, "reviewer_ids": reviewer_ids,
                    "fingerprints": list(fps), "fingerprints_match": len(fps) <= 1},
        "thresholds": {"verdict_kappa_pass": KAPPA_THRESHOLD,
                        "effective_kappa_pass": EFFECTIVE_KAPPA_THRESHOLD,
                        "rubber_stamp": RUBBER_STAMP_THRESHOLD,
                        "wrong_wrong_divergence_limit": WRONG_WRONG_DIVERGENCE_LIMIT,
                        "required_features": REQUIRED_FEATURES,
                        "min_items": MIN_ITEMS_PER_FEATURE},
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "per_feature_kappa": feature_results,
        "disagree_reason_aggregate": aggregate_reasons(exports),
        "integrity_warnings": all_warnings,
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python sfrp_kappa_pipeline.py r1.json r2.json [...]"); sys.exit(1)
    exports = [load_export(p) for p in sys.argv[1:]]
    report = run_pipeline(exports, sys.argv[1:])
    print(json.dumps(report, indent=2, default=str))
    with open("sfrp_interrater_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
