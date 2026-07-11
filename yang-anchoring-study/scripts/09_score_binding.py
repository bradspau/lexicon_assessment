import pandas as pd
from sklearn.metrics import precision_recall_fscore_support

pred = pd.read_csv("data/results/phase2_bindings_raw.csv")
gold = pd.read_csv("data/gold/gold_standard.csv")

merged = pred.merge(gold, on=["corpus", "module", "path"], suffixes=("_pred", "_gold"))


def score(df, relation_filter=None, exclude_trivial_name_match=False):
    d = df.copy()
    if relation_filter:
        d = d[d["relation_gold"].isin(relation_filter)]
    if exclude_trivial_name_match:
        d = d[~d.apply(lambda r: r["path"].split("/")[-1].replace("-", "") in str(r.get("lexicon_id", "")).lower(), axis=1)]
    y_true = (d["gold_lexicon_id"] == d["lexicon_id"]).astype(int)
    p, r, f1, _ = precision_recall_fscore_support(
        [1] * len(d), y_true, average="binary", zero_division=0
    )
    return {"n": len(d), "precision": p, "recall": r, "f1": f1}


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
