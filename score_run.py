#!/usr/bin/env python3
"""
Run run_eval.py and mark each try PASS/FAIL against criteria.md.

    python score_run.py --label before

run_eval.py writes the run log (results/run_*.md) but leaves the verdicts
blank. This wraps it, keeps every session, and applies each criterion exactly
as written, so the PASS/FAIL cells come from a rule rather than a mood.
Scores go to results/scores_<label>.json and are printed as a README table.
"""
import json
import re
import sys

import agent
import config
import run_eval
import scenarios

TARGETS = {1: 4, 2: 5, 3: 5, 4: 4, 5: 5}
NAMES = {
    1: "Matching query completes all three tools",
    2: "Impossible query stops before suggest_outfit",
    3: "selected_item is the dict passed to suggest_outfit",
    4: "Fit card mentions item title and price",
    5: "No returned listing over max_price",
}

records = []         # (scenario, record) for every try
_passed_items = []   # what suggest_outfit received during the current try

_real_run_once = run_eval.run_once
_real_suggest = agent.suggest_outfit


def _spy_suggest(new_item, wardrobe):
    _passed_items.append(new_item)
    return _real_suggest(new_item, wardrobe)


def _run_once(scenario, use_trace=True):
    _passed_items.clear()
    record = _real_run_once(scenario, use_trace)
    record["passed_items"] = list(_passed_items)
    records.append((scenario, record))
    return record


def _norm(text):
    return re.sub(r"[\s\-—–,]+", " ", str(text).lower()).strip()


def score(criterion, record):
    """Return (passed, reason) for one try."""
    if record["crashed"]:
        return False, f"crashed: {record['crashed']}"
    s = record["session"]
    ok = not s["error"] and bool(s["fit_card"])

    if criterion == 1:
        return ok, "fit card returned" if ok else f"no fit card: {s['error']}"
    if criterion == 2:
        stopped = bool(s["error"]) and not record["passed_items"] and s["outfit_suggestion"] is None
        names_fix = "try changing" in (s["error"] or "").lower()
        return stopped and names_fix, f"suggest_outfit calls={len(record['passed_items'])}, error={s['error']!r}"
    if criterion == 3:
        if not ok:
            return False, f"run not successful: {s['error']}"
        same = len(record["passed_items"]) == 1 and record["passed_items"][0] is s["selected_item"]
        return same, "same object" if same else "different object passed"
    if criterion == 4:
        if not ok:
            return False, f"run not successful: {s['error']}"
        card, item = s["fit_card"], s["selected_item"]
        has_title = _norm(item["title"]) in _norm(card)
        price = re.escape(f"{float(item['price']):g}")
        has_price = re.search(rf"\$\s*{price}(\.0+)?\b", card) is not None
        return has_title and has_price, f"title={'yes' if has_title else 'NO'}, price={'yes' if has_price else 'NO'}"
    if criterion == 5:
        ceiling = s["parsed"].get("max_price")
        over = [r for r in s["search_results"] if ceiling is None or r["price"] > ceiling]
        return bool(s["search_results"]) and not over and ceiling is not None, \
            f"{len(s['search_results'])} results, max ${ceiling}, over ceiling: {len(over)}"
    return None, "diagnostic"


def main():
    label = sys.argv[sys.argv.index("--label") + 1] if "--label" in sys.argv else "run"
    run_eval.run_once = _run_once
    agent.suggest_outfit = _spy_suggest
    run_eval.main()

    rows, detail = [], []
    for sc in scenarios.SCENARIOS:
        n = sc.get("criterion")
        tries = [r for s, r in records if s is sc]
        results = [score(n, r) for r in tries]
        detail.append({"scenario": sc["name"], "criterion": n, "query": sc["query"],
                       "tries": [{"pass": p, "why": why,
                                  "fit_card": (r["session"] or {}).get("fit_card")}
                                 for (p, why), r in zip(results, tries)]})
        if not n:
            continue
        passes = sum(bool(p) for p, _ in results)
        verdict = "MET" if passes >= TARGETS[n] else "MISSED"
        cells = " | ".join("PASS" if p else "FAIL" for p, _ in results)
        rows.append(f"| {n}. {NAMES[n]} | {TARGETS[n]} of 5 | {cells} | {verdict} ({passes}/5) |")
        for i, (p, why) in enumerate(results, 1):
            print(f"  c{n} try {i}: {'PASS' if p else 'FAIL'} — {why}")

    print("\n| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |")
    print("|---|---|---|---|---|---|---|---|")
    print("\n".join(sorted(rows)))

    out = config.RESULTS_DIR / f"scores_{label}.json"
    out.write_text(json.dumps(detail, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
