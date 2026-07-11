"""
Scaffolding only, per plan step 7: filter candidate topology/forwarding
nodes from both corpora. The actual lexicon_id/relation/notes assignment is
inherently manual/expert judgment and is NOT done here -- it's hand-authored
directly into data/gold/gold_standard.csv (see that file's provenance note).

This script just regenerates the candidate pool for reference/audit, and
computes Cohen's kappa for the second-annotator agreement check on the
15-row subset once both label sets exist.
"""
import pandas as pd
from sklearn.metrics import cohen_kappa_score

CANDIDATE_SUBSTRINGS = ["node", "termination-point", "link", "service", "tunnel", "layer", "risk", "constraint"]

df = pd.read_csv("data/results/phase1_scored_nodes.csv", keep_default_na=False)
mask = df["path"].str.lower().str.contains("|".join(CANDIDATE_SUBSTRINGS))
candidates = df[mask].reset_index(drop=True)
candidates.to_csv("data/gold/candidate_pool.csv", index=False)
print(f"{len(candidates)} candidate nodes written to data/gold/candidate_pool.csv")

# --- second-annotator agreement check (run only once gold_standard.csv and
# gold_standard_second_pass.csv both exist) ---
try:
    gold = pd.read_csv("data/gold/gold_standard.csv")
    second = pd.read_csv("data/gold/gold_standard_second_pass.csv")
    merged = gold.merge(second, on=["corpus", "module", "path"], suffixes=("_1", "_2"))
    kappa = cohen_kappa_score(merged["gold_lexicon_id_1"], merged["gold_lexicon_id_2"])
    agree = (merged["gold_lexicon_id_1"] == merged["gold_lexicon_id_2"]).mean()
    print(f"\nSecond-annotator check (n={len(merged)}): kappa={kappa:.3f}, agreement={agree:.1%}")
except FileNotFoundError as e:
    print(f"\n(second-annotator check skipped: {e})")
