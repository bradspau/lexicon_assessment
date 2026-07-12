import pandas as pd

pred = pd.read_csv("data/results/phase2_bindings_raw.csv")
gold = pd.read_csv("data/gold/gold_standard.csv")

merged = pred.merge(gold, on=["corpus", "module", "path"], suffixes=("_pred", "_gold"))


def score(df, relation_filter=None, exclude_trivial_name_match=False):
    """
    Detection + classification scoring (standard for tasks like NER/relation
    extraction, not the degenerate sklearn-on-all-1s trick this replaces --
    see report/FINDINGS.md's "how to read this table" note for why the old
    version made precision mathematically pinned at 1.0 regardless of binder
    quality).

    A gold row's "NONE" case is always included in every scope, since
    correctly abstaining is relevant no matter how leniently we're counting
    subsumption -- it's the only source of a genuine false positive in this
    dataset (a real error where the binder asserts a match that doesn't
    exist), without it precision can never differ from 1.0 by construction.

    Per row: TP = binder asserted the exact correct lexicon_id (gold isn't
    NONE). FP = binder asserted *some* real lexicon_id but it's wrong
    (whether gold wanted a different id or no match at all). FN = gold
    wanted a real match and the binder didn't produce it, whether it said
    NONE or asserted a different (wrong) lexicon_id -- a wrong guess is
    double-counted as both FP and FN, the standard detection+classification
    convention (as in NER/IE scoring), since it is simultaneously a false
    assertion and a missed correct answer. TN = binder said NONE and gold
    is NONE (contributes to neither precision nor recall, same as always).
    """
    d = df.copy()
    if relation_filter:
        d = d[d["relation_gold"].isin(relation_filter) | (d["gold_lexicon_id"] == "NONE")]
    if exclude_trivial_name_match:
        d = d[~d.apply(lambda r: r["path"].split("/")[-1].replace("-", "") in str(r.get("lexicon_id", "")).lower(), axis=1)]

    is_none_gold = d["gold_lexicon_id"] == "NONE"
    is_none_pred = d["lexicon_id"] == "NONE"
    tp = ((~is_none_gold) & (d["lexicon_id"] == d["gold_lexicon_id"])).sum()
    fp = ((~is_none_pred) & (d["lexicon_id"] != d["gold_lexicon_id"])).sum()
    fn = ((~is_none_gold) & (d["lexicon_id"] != d["gold_lexicon_id"])).sum()

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {"n": len(d), "precision": precision, "recall": recall, "f1": f1}


rows = []
for mode in ["name_only", "definition_based"]:
    sub = merged[merged["mode"] == mode]
    rows.append({"mode": mode, "scope": "equivalence_only",
                 **score(sub, relation_filter=["equivalent"])})
    rows.append({"mode": mode, "scope": "equivalence_plus_subsumption",
                 **score(sub, relation_filter=["equivalent", "subsumes", "subsumed_by"])})
    rows.append({"mode": mode, "scope": "recall_plus_nontrivial",
                 **score(sub, relation_filter=["equivalent"], exclude_trivial_name_match=True)})

scores = pd.DataFrame(rows)
scores.to_csv("data/results/phase2_scores.csv", index=False)
print(scores.to_string(index=False))

# Confusion detail on the trap cases specifically
traps = merged[merged["path"].str.contains("tunnel-termination-point|owned-node-edge-point", na=False, regex=True)]
traps = traps[["mode", "corpus", "path", "gold_lexicon_id", "relation_gold", "lexicon_id", "relation_pred", "confidence"]]
traps.to_csv("data/results/phase2_trap_case_detail.csv", index=False)
print("\n--- trap case detail ---")
print(traps.sort_values(["path", "mode"]).to_string(index=False))
