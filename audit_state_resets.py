#!/usr/bin/env python3
"""
HERMES State Audit — checks that all mutable globals are properly
reset in every session entry point (processInput, resumeSession, resetAll).

Run this after any code change to catch the class of bug where a new
session inherits stale state from a previous session.

Usage:
    python audit_state_resets.py sfrp_audit_v5.html
"""

import re
import sys

def extract_fn(html, name):
    """Extract function body by balanced brace counting."""
    idx = html.index(f"function {name}(")
    depth = 0
    start = html.index("{", idx)
    i = start
    while i < len(html):
        if html[i] == "{":
            depth += 1
        elif html[i] == "}":
            depth -= 1
            if depth == 0:
                return html[start:i+1]
        i += 1
    return ""

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "sfrp_audit_v5.html"
    html = open(path).read()

    # All mutable globals that represent session state
    mutable_globals = [
        "dataset", "responses", "currentIndex", "shuffledOrder", "probeSet",
        "originalItemCount", "sessionStartMs", "priorTimeMs", "itemShownAtMs",
        "labelsPerFeature", "datasetFingerprint", "saveDegraded", "fatigueAcked",
        "awaitingCorrection", "pendingWrongKey", "hasGroundTruth",
        "awaitingReason", "pendingReasonKey", "selectedReasons",
        "reviewerName", "sessionNonce", "hashChainHead",
        "originalResponseCount", "processingResponse",
        "chunkItemCount", "currentStreak", "longestStreak", "totalSessionItems",
    ]

    # Variables that are intentionally NOT reset in certain entry points
    # Each tuple: (function_name, variable, reason)
    known_exceptions = [
        ("processInput", "sessionStartMs", "Set in startReview(), not processInput"),
        ("processInput", "itemShownAtMs", "Set in renderCurrentItem()"),
        ("processInput", "reviewerName", "Set from input field in startReview()"),
        ("resumeSession", "sessionStartMs", "Set in startReview()"),
        ("resumeSession", "itemShownAtMs", "Set in renderCurrentItem()"),
        ("resumeSession", "labelsPerFeature", "Loaded from stored dataset"),
        ("resumeSession", "datasetFingerprint", "Loaded from stored dataset"),
        ("resetAll", "labelsPerFeature", "Cleared implicitly when dataset=null"),
        ("resetAll", "datasetFingerprint", "Cleared implicitly when dataset=null"),
        ("resetAll", "itemShownAtMs", "Explicitly reset"),
    ]
    exception_set = {(fn, var) for fn, var, _ in known_exceptions}

    entry_points = ["processInput", "resumeSession", "resetAll"]
    fns = {name: extract_fn(html, name) for name in entry_points}

    print(f"Auditing {len(mutable_globals)} mutable globals across {len(entry_points)} entry points\n")
    print(f"{'Variable':<28} {'processInput':<15} {'resumeSession':<15} {'resetAll':<15}")
    print("=" * 73)

    gaps = []
    for v in mutable_globals:
        row = f"{v:<28}"
        for name in entry_points:
            pattern = rf'\b{re.escape(v)}\s*='
            found = bool(re.search(pattern, fns[name]))
            is_exception = (name, v) in exception_set
            if found:
                row += f" {'✓':<14}"
            elif is_exception:
                row += f" {'(ok)':<14}"
            else:
                row += f" {'MISSING':<14}"
                gaps.append((name, v))
        print(row)

    print(f"\n{'='*73}")
    if gaps:
        print(f"\n⚠ FOUND {len(gaps)} UNRESOLVED GAPS:")
        for fn, var in gaps:
            print(f"  {fn}() does NOT reset: {var}")
        print(f"\nEach gap means: if a user triggers {fn}() after a previous session,")
        print(f"the variable '{var}' will carry over stale state.")
        sys.exit(1)
    else:
        print("\n✓ ALL MUTABLE STATE PROPERLY RESET IN ALL ENTRY POINTS")
        print(f"  ({len([e for e in known_exceptions])} known exceptions documented)")
        sys.exit(0)

if __name__ == "__main__":
    main()
