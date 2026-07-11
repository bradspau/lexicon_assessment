import pandas as pd

df = pd.read_csv("data/raw/all_nodes.csv", keep_default_na=False)

DATA_NODE_TYPES = {"container", "leaf", "list", "leaf-list", "choice", "typedef", "grouping", "identity"}
df = df[df["node_type"].isin(DATA_NODE_TYPES)].reset_index(drop=True)

df["desc_len"] = df["description"].str.len()
df["is_empty"] = df["desc_len"] == 0
df["word_count"] = df["description"].str.split().str.len().fillna(0).astype(int)

BOILERPLATE_PATTERNS = ["initial revision", "copyright", r"^\s*$", r"^none$"]
df["is_boilerplate"] = df["description"].str.lower().str.contains(
    "|".join(BOILERPLATE_PATTERNS), regex=True
)


# name-restatement heuristic: description mostly repeats the last path segment
def restates_name(row):
    last_seg = row["path"].split("/")[-1].replace("-", " ").lower()
    return last_seg in row["description"].lower()[:80] if row["description"] else False


df["restates_name"] = df.apply(restates_name, axis=1)

summary = df.groupby("corpus").agg(
    n_nodes=("path", "count"),
    pct_empty=("is_empty", "mean"),
    pct_boilerplate=("is_boilerplate", "mean"),
    pct_restates_name=("restates_name", "mean"),
    mean_word_count=("word_count", "mean"),
    median_word_count=("word_count", "median"),
)
summary.to_csv("data/results/phase1_coverage_summary.csv")
print(summary)

# Duplicate-description detection (common in generated models like TAPI)
dupes = df[(df["description"].str.len() > 10)]
dupe_counts = dupes.groupby(["corpus", "description"]).size().reset_index(name="count")
dupe_counts = dupe_counts[dupe_counts["count"] > 1].sort_values("count", ascending=False)
dupe_counts.to_csv("data/results/phase1_duplicate_descriptions.csv", index=False)

df.to_csv("data/results/phase1_scored_nodes.csv", index=False)
print(f"\nwrote {len(df)} scored data-nodes; {len(dupe_counts)} duplicate-description groups")
