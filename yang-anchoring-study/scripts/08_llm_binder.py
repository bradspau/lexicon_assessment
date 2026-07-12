"""
LLM binder, name-only vs definition-based (plan step 8).

DEVIATION FROM PLAN: no ANTHROPIC_API_KEY is available in this environment,
so this does not call the `anthropic` SDK directly. Instead the binding
judgments in scripts/_phase2_bindings_data.py were collected via 78
independent, isolated subagent tool calls (39 candidates x 2 modes) using
the coding harness's Agent tool -- each a fresh model instance with no
filesystem access and no visibility into this conversation or
data/gold/gold_standard.csv, given only the literal prompt text below. This
is a genuine blind evaluation (see report/FINDINGS.md for the full
breakdown of the results, which matter more than the bare F1 numbers).
"""
import pandas as pd
import yaml
import sys

sys.path.insert(0, "scripts")
from _phase2_bindings_data import NAME_ONLY, DEFINITION_BASED

lexicon = yaml.safe_load(open("data/lexicon/lexicon.yaml"))
gold = pd.read_csv("data/gold/gold_standard.csv")
nodes = pd.read_csv("data/results/phase1_scored_nodes.csv", keep_default_na=False)
# only pull path/description as candidate-set filter keys -- gold's own
# lexicon_id/relation columns are intentionally NOT merged in here (this
# script produces predictions, not answers; scoring against gold happens
# separately in 09_score_binding.py). Merging the full gold frame previously
# caused a silent column collision: gold's "relation" and the predicted
# "relation" both survived the merge, with gold's shadowing the prediction.
candidates = gold[["corpus", "module", "path"]].merge(
    nodes[["corpus", "module", "path", "description"]], on=["corpus", "module", "path"]
)


def lexicon_block(mode):
    if mode == "name_only":
        return "\n".join(f"- {e['id']}: {e['preferred_name']} (synonyms: {', '.join(e['synonyms'])})" for e in lexicon)
    return "\n".join(f"- {e['id']}: {e['preferred_name']}\n  Definition: {e['definition'].strip()}" for e in lexicon)


def node_block(row, mode):
    if mode == "name_only":
        return f"Node path: {row['path']}\nNode name: {row['path'].split('/')[-1]}"
    return f"Node path: {row['path']}\nDescription: {row['description']}"


PROMPT = """You are binding a network-management data-model node to the single best-matching
entry in a reference lexicon, or to "NONE" if no entry fits.

If the node represents an attribute container, property bag, or reusable
template for an entry in the lexicon (rather than being an instance of that
entry itself), classify it as "subsumed_by" that entry rather than "NONE".

Reference lexicon:
{lexicon}

Node to bind:
{node}

Respond ONLY with JSON: {{"lexicon_id": "<id or NONE>", "relation": "equivalent|subsumes|subsumed_by|none", "confidence": <0-1>}}"""

if __name__ == "__main__":
    cols = ["corpus", "module", "path", "lexicon_id", "relation", "confidence"]
    results = []
    for mode, data in [("name_only", NAME_ONLY), ("definition_based", DEFINITION_BASED)]:
        preds = pd.DataFrame(data, columns=cols)
        merged = candidates.merge(preds, on=["corpus", "module", "path"], suffixes=("", "_pred"))
        for _, row in merged.iterrows():
            results.append({
                "corpus": row["corpus"], "module": row["module"], "path": row["path"],
                "node_type": row.get("node_type", ""), "description": row["description"],
                "mode": mode, "lexicon_id": row["lexicon_id"], "relation": row["relation"],
                "confidence": row["confidence"],
            })

    out = pd.DataFrame(results)
    out.to_csv("data/results/phase2_bindings_raw.csv", index=False)
    print(f"wrote {len(out)} bindings ({len(out)//2} candidates x 2 modes) to data/results/phase2_bindings_raw.csv")

    # print the two example prompts once, for documentation/audit purposes
    example = candidates.iloc[3]  # the ietf tunnel-termination-point trap case
    print("\n--- example name_only prompt ---")
    print(PROMPT.format(lexicon=lexicon_block("name_only"), node=node_block(example, "name_only")))
    print("\n--- example definition_based prompt ---")
    print(PROMPT.format(lexicon=lexicon_block("definition_based"), node=node_block(example, "definition_based")))
