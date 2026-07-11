import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

df = pd.read_csv("data/results/phase1_scored_nodes.csv", keep_default_na=False)
df = df[df["description"].str.len() > 5].reset_index(drop=True)

# sentence-transformers is not installed in this environment (kept optional
# per plan); TF-IDF is the declared fallback.
print("Using TF-IDF (sentence-transformers not installed in this environment)")
vec = TfidfVectorizer(max_features=2000)
emb = vec.fit_transform(df["description"]).toarray()

sims = cosine_similarity(emb)
np.fill_diagonal(sims, 0)

# Intra-corpus collisions: high similarity between nodes with different last-path-segment names
# (i.e., descriptions too similar to distinguish semantically distinct nodes)
records = []
threshold = 0.85
for i in range(len(df)):
    for j in np.argsort(-sims[i])[:3]:
        if sims[i, j] > threshold and df.loc[i, "corpus"] == df.loc[j, "corpus"] and i != j:
            name_i = df.loc[i, "path"].split("/")[-1]
            name_j = df.loc[j, "path"].split("/")[-1]
            if name_i == name_j:
                continue  # same field name repeated at different paths isn't a collision, it's the same concept
            records.append({
                "corpus": df.loc[i, "corpus"],
                "node_a": df.loc[i, "path"], "node_b": df.loc[j, "path"],
                "similarity": sims[i, j],
            })
collisions = pd.DataFrame(records).drop_duplicates()
collisions.to_csv("data/results/phase1_collisions.csv", index=False)
print(f"same-corpus, different-name collisions (sim>{threshold}): {len(collisions)}")

# Cross-corpus separability check: for each ietf node, is its TF-IDF nearest
# neighbor a genuinely-related tapi node? (sanity signal for whether the
# embedding space could support cross-corpus binding at all)
ietf_idx = df.index[df["corpus"] == "ietf"].tolist()
tapi_idx = df.index[df["corpus"] == "tapi"].tolist()
cross_records = []
for i in ietf_idx:
    j_best = max(tapi_idx, key=lambda j: sims[i, j])
    if sims[i, j_best] > 0.3:
        cross_records.append({
            "ietf_node": df.loc[i, "path"], "tapi_node": df.loc[j_best, "path"],
            "similarity": sims[i, j_best],
        })
cross = pd.DataFrame(cross_records).sort_values("similarity", ascending=False)
cross.to_csv("data/results/phase1_cross_corpus_similarity.csv", index=False)
print(f"cross-corpus candidate pairs (sim>0.3): {len(cross)}")
