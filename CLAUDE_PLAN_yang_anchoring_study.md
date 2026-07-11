# Implementation Plan: Testing YANG Description Text for Definitional Anchoring

**Purpose of this file:** a self-contained plan that Claude (or a developer) can execute step-by-step in Python to empirically test whether YANG `description` statements support LLM-based definitional anchoring, per the two-phase methodology (quality audit + name-only vs. definition-based binding experiment, scored with precision/recall/F1 against a hand-built gold standard).

**How to use this file:** treat each numbered step as a unit of work. Run steps in order. Each step names its inputs, its script, and its concrete output artifact. Steps 1–5 are Phase 1 (description quality audit). Steps 6–11 are Phase 2 (LLM binding experiment). Step 12 is the write-up.

---

## 0. Project scaffold

```
yang-anchoring-study/
├── requirements.txt
├── config/
│   └── modules.yaml          # pinned source URLs + revisions
├── corpus/
│   ├── ietf/                 # fetched .yang files
│   └── tapi/
├── scripts/
│   ├── 01_fetch_corpus.py
│   ├── 02_extract_descriptions.py
│   ├── 03_quality_audit.py
│   ├── 04_collision_analysis.py
│   ├── 05_report_phase1.py
│   ├── 06_build_lexicon.py
│   ├── 07_build_gold_standard.py
│   ├── 08_llm_binder.py
│   ├── 09_score_binding.py
│   └── flatten_desc_plugin.py  # fallback pyang plugin
├── data/
│   ├── raw/                  # extracted CSV/JSON tuples
│   ├── lexicon/              # reference lexicon entries
│   ├── gold/                 # gold-standard correspondences
│   └── results/              # scored outputs
└── report/
    └── FINDINGS.md
```

Run once:
```bash
mkdir -p yang-anchoring-study/{config,corpus/ietf,corpus/tapi,scripts,data/{raw,lexicon,gold,results},report}
cd yang-anchoring-study
```

---

## requirements.txt

```
pyang==2.7.1
pyyaml
requests
pandas
scikit-learn
sentence-transformers   # optional, for collision analysis; fallback = TF-IDF if unavailable
anthropic               # for the LLM binder (steps 8)
```

Install with `pip install -r requirements.txt --break-system-packages` (sandbox convention) or a venv locally.

---

## 1. Pin and fetch the corpus

### config/modules.yaml
```yaml
ietf:
  - name: ietf-network
    revision: "2018-02-26"
    url: https://raw.githubusercontent.com/YangModels/yang/main/standard/ietf/RFC/ietf-network@2018-02-26.yang
  - name: ietf-network-topology
    revision: "2018-02-26"
    url: https://raw.githubusercontent.com/YangModels/yang/main/standard/ietf/RFC/ietf-network-topology@2018-02-26.yang
  - name: ietf-te-topology
    revision: "2020-08-06"
    url: https://raw.githubusercontent.com/YangModels/yang/main/standard/ietf/RFC/ietf-te-topology@2020-08-06.yang
  - name: ietf-otn-topology
    revision: "TBD-confirm-latest-draft"
    url: "TBD"   # resolve via GitHub contents API, see 1.2 below; else pull from Datatracker HTML

tapi:
  tag: v2.5.2
  base: https://raw.githubusercontent.com/OpenNetworkingFoundation/TAPI/v2.5.2/YANG
  modules:
    - tapi-topology.yang
    - tapi-connectivity.yang
    - tapi-common.yang
```

### scripts/01_fetch_corpus.py
```python
import yaml, requests, pathlib

CFG = yaml.safe_load(open("config/modules.yaml"))

def fetch(url, dest):
    dest = pathlib.Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    dest.write_text(r.text)
    print(f"fetched {dest} ({len(r.text)} bytes)")

if __name__ == "__main__":
    for m in CFG["ietf"]:
        if m["url"] != "TBD":
            fetch(m["url"], f"corpus/ietf/{m['name']}.yang")

    tapi = CFG["tapi"]
    for mod in tapi["modules"]:
        fetch(f"{tapi['base']}/{mod}", f"corpus/tapi/{mod}")
```

### 1.2 Resolving the OTN draft module (one-time manual step)
```bash
curl -s https://api.github.com/repos/YangModels/yang/contents/experimental/ietf-extracted-YANG-modules \
  | python3 -c "import sys,json; [print(f['name']) for f in json.load(sys.stdin) if 'otn-topology' in f['name']]"
```
Take the highest-dated match, update `modules.yaml`'s `url` field, re-run `01_fetch_corpus.py`. If unreachable, fall back to extracting the `<CODE BEGINS>` block from the Datatracker HTML of the current draft (`draft-ietf-ccamp-otn-topo-yang-<latest>`) with a small regex script — note this file is NOT allowlisted in Claude's sandbox network config, so this sub-step may need to run outside the sandbox or be supplied as an uploaded file.

**Also fetch dependency modules** referenced by `import` statements so pyang can resolve them (ietf-yang-types, ietf-inet-types, ietf-te-types, tapi-common's own transitive imports) into the same corpus directories — pyang needs `-p corpus/ietf:corpus/tapi` on its path even if you only care about descriptions, to avoid import-resolution warnings breaking `-f flatten`.

---

## 2. Extract `(module, path, node-type, description)` tuples

### scripts/02_extract_descriptions.py
Primary path — pyang's built-in flatten plugin:
```python
import subprocess, pathlib, csv

def extract(yang_file, out_csv, path_dirs):
    p = "-p " + ":".join(path_dirs)
    cmd = f"pyang {p} -f flatten --flatten-description --flatten-csv-dialect excel {yang_file}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("WARN pyang stderr:", result.stderr)
    pathlib.Path(out_csv).write_text(result.stdout)

if __name__ == "__main__":
    path_dirs = ["corpus/ietf", "corpus/tapi"]
    for f in pathlib.Path("corpus/ietf").glob("*.yang"):
        extract(f, f"data/raw/{f.stem}.csv", path_dirs)
    for f in pathlib.Path("corpus/tapi").glob("*.yang"):
        extract(f, f"data/raw/{f.stem}.csv", path_dirs)
```

**Before trusting this:** run `pyang -f flatten --help` once and confirm the description field flag name matches (`--flatten-description` per current docs; adjust if your installed version differs).

**Fallback** if the flag isn't present or output is malformed — use the custom plugin:

### scripts/flatten_desc_plugin.py
```python
from pyang import plugin, statements

def pyang_plugin_init():
    plugin.register_plugin(FlattenDescPlugin())

class FlattenDescPlugin(plugin.PyangPlugin):
    def add_output_format(self, fmts):
        self.multiple_modules = True
        fmts['flatten-desc'] = self

    def emit(self, ctx, modules, fd):
        fd.write("module;path;keyword;description\n")
        for m in modules:
            for ch in getattr(m, 'i_children', []):
                _walk(m, ch, fd)

def _walk(module, stmt, fd):
    path = statements.mk_path_str(stmt, with_prefixes=False)
    desc = stmt.search_one('description')
    text = (desc.arg.replace('\n', ' ').replace(';', ',') if desc else '')
    fd.write(f'{module.arg};{path};{stmt.keyword};"{text}"\n')
    for ch in getattr(stmt, 'i_children', []):
        _walk(module, ch, fd)
```
Run with: `pyang --plugindir scripts -f flatten-desc -p corpus/ietf:corpus/tapi corpus/ietf/ietf-network-topology.yang > data/raw/ietf-network-topology.csv`

**Output of this step:** one CSV per module in `data/raw/`, union them (pandas `pd.concat`) into `data/raw/all_nodes.csv` with columns `[corpus, module, path, node_type, description]` (add a `corpus` column = "ietf"/"tapi" manually or by source directory when concatenating).

---

## 3. Quality audit (Phase 1 core)

### scripts/03_quality_audit.py
```python
import pandas as pd

df = pd.read_csv("data/raw/all_nodes.csv", sep=";")

DATA_NODE_TYPES = {"container","leaf","list","leaf-list","choice","typedef","grouping","identity"}
df = df[df["node_type"].isin(DATA_NODE_TYPES)]

df["desc_len"] = df["description"].fillna("").str.len()
df["is_empty"] = df["desc_len"] == 0
df["word_count"] = df["description"].fillna("").str.split().str.len()

BOILERPLATE_PATTERNS = ["initial revision", "copyright", r"^\s*$"]
df["is_boilerplate"] = df["description"].fillna("").str.lower().str.contains(
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
dupes = df[df["description"].notna() & (df["description"].str.len() > 10)]
dupe_counts = dupes.groupby(["corpus", "description"]).size().reset_index(name="count")
dupe_counts = dupe_counts[dupe_counts["count"] > 1].sort_values("count", ascending=False)
dupe_counts.to_csv("data/results/phase1_duplicate_descriptions.csv", index=False)

df.to_csv("data/results/phase1_scored_nodes.csv", index=False)
```

**Output:** `phase1_coverage_summary.csv` (coverage %, boilerplate %, name-restatement %, verbosity, broken out by corpus — this is the headline IETF-vs-TAPI contrast), plus `phase1_duplicate_descriptions.csv`.

### ISO-704 style definitional-quality sample (manual + LLM-assisted)
- Sample ~100–150 nodes stratified by corpus and node-type from `phase1_scored_nodes.csv` (`df.groupby("corpus").sample(n=75, random_state=42)` or similar).
- Score each on a 4-way rubric: `intensional` (states genus + differentiating characteristic) / `extensional_example_only` / `circular_tautological` / `empty_boilerplate`.
- Do this two ways and compare: (a) your own manual labels on a 30-node subset, (b) an LLM classifier (via `anthropic` SDK, one call per node, fixed rubric prompt) on the full sample. Report agreement (Cohen's κ) between (a) and (b) on the overlapping 30 to validate the LLM as an annotator before trusting its labels on the rest.
- Save to `data/results/phase1_iso704_scores.csv` with columns `[corpus, module, path, rubric_label, annotator]`.

---

## 4. Semantic-collision analysis

### scripts/04_collision_analysis.py
```python
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

df = pd.read_csv("data/results/phase1_scored_nodes.csv")
df = df[df["description"].fillna("").str.len() > 5].reset_index(drop=True)

# Prefer sentence-transformers if available/offline-capable; else TF-IDF fallback.
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")  # confirm offline availability first
    emb = model.encode(df["description"].tolist())
except Exception as e:
    print("Falling back to TF-IDF:", e)
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
            records.append({
                "corpus": df.loc[i, "corpus"],
                "node_a": df.loc[i, "path"], "node_b": df.loc[j, "path"],
                "similarity": sims[i, j],
            })
pd.DataFrame(records).drop_duplicates().to_csv("data/results/phase1_collisions.csv", index=False)
```

**Output:** `phase1_collisions.csv` — pairs of same-corpus nodes whose descriptions are near-duplicate despite being different concepts (an anchoring-failure mode). Cross-corpus separability (can TAPI `link` find IETF `link` via embedding nearest-neighbor?) can be checked with the same similarity matrix restricted to cross-corpus pairs — add this as a second query if useful.

---

## 5. Phase 1 report

### scripts/05_report_phase1.py
Assemble `phase1_coverage_summary.csv`, `phase1_iso704_scores.csv`, `phase1_collisions.csv`, `phase1_duplicate_descriptions.csv` into `report/FINDINGS.md` §1 with the actual numbers filled in. This is the point at which your original gut-feeling prior gets its first quantitative check — write the coverage %, intensional-definition %, and collision-rate numbers directly against your threshold from the earlier discussion (~80% intensional coverage + high separability → prior likely wrong; <40% + high collisions → prior vindicated).

---

## 6. Build the reference lexicon (Phase 2 setup)

### data/lexicon/lexicon.yaml
Hand-author ~10–15 entries per the draft's own list. Example:
```yaml
- id: LEX-001
  preferred_name: forwarding-element
  synonyms: [node, te-node, network-element]
  entity_class: node-like
  definition: >
    A network element that switches or forwards traffic between its
    termination points, considered as a single addressable unit within
    a topology, irrespective of internal implementation.

- id: LEX-002
  preferred_name: link-termination-point
  synonyms: [termination-point, port]
  entity_class: termination-point-like
  definition: >
    A boundary point on a forwarding element where a topological link
    attaches; the point at which traffic enters or leaves the element
    toward a specific link.

- id: LEX-003
  preferred_name: service-anchor
  synonyms: [tunnel-termination-point, tunnel-endpoint]
  entity_class: service-boundary
  definition: >
    The head or tail point of an end-to-end service or tunnel, as
    distinct from a physical link-attachment point; it identifies
    where a service begins or ends, not where a link is physically
    attached.

# ... continue for: topological-link, layer, service, client-access-point,
#     forwarding-constraint, shared-risk-group, layer-1-signal-type
```
Load this with a small `load_lexicon.py` helper (`yaml.safe_load` → list of dicts) reused by steps 7–9.

---

## 7. Build the gold standard

### scripts/07_build_gold_standard.py (semi-manual)
1. From `phase1_scored_nodes.csv`, filter to candidate topology/forwarding nodes in both corpora (grep on path substrings: `node`, `termination-point`, `link`, `service`, `tunnel`, `layer`, `risk`, `constraint`).
2. For each candidate node, manually assign: `lexicon_id` (equivalence), `relation` (`equivalent` / `subsumes` / `subsumed_by` / `none`), and a free-text justification. Deliberately include trap cases:
   - `ietf-te-topology: .../tunnel-termination-point` → gold = `LEX-003 service-anchor`, relation=`equivalent` (NOT `LEX-002`, despite the name).
   - `tapi-topology: .../owned-node-edge-point` → gold = `LEX-002 link-termination-point`.
3. Target 30–60 rows. Use a second annotator (or a second manual pass a day later) on a subset (~15 rows) and compute agreement (simple % agreement or Cohen's κ via `sklearn.metrics.cohen_kappa_score`).
4. Save as `data/gold/gold_standard.csv` with columns `[corpus, module, path, gold_lexicon_id, relation, notes]`.

This step is inherently manual/expert judgment — script only the scaffolding (candidate filtering, CSV template generation, kappa calculation), not the labeling itself.

---

## 8. LLM binder — name-only vs. definition-based

### scripts/08_llm_binder.py
```python
import pandas as pd, yaml, json
from anthropic import Anthropic

client = Anthropic()
lexicon = yaml.safe_load(open("data/lexicon/lexicon.yaml"))
gold = pd.read_csv("data/gold/gold_standard.csv")
nodes = pd.read_csv("data/results/phase1_scored_nodes.csv")
candidates = nodes.merge(gold[["corpus","module","path"]], on=["corpus","module","path"])

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

Reference lexicon:
{lexicon}

Node to bind:
{node}

Respond ONLY with JSON: {{"lexicon_id": "<id or NONE>", "relation": "equivalent|subsumes|subsumed_by|none", "confidence": <0-1>}}"""

def bind(row, mode):
    prompt = PROMPT.format(lexicon=lexicon_block(mode), node=node_block(row, mode))
    resp = client.messages.create(
        model="claude-sonnet-5", max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    text = resp.content[0].text.strip().strip("`").replace("json", "", 1).strip()
    try:
        return json.loads(text)
    except Exception:
        return {"lexicon_id": "PARSE_ERROR", "relation": "none", "confidence": 0.0}

results = []
for mode in ["name_only", "definition_based"]:
    for _, row in candidates.iterrows():
        out = bind(row, mode)
        results.append({**row.to_dict(), "mode": mode, **out})

pd.DataFrame(results).to_csv("data/results/phase2_bindings_raw.csv", index=False)
```

**Note:** update the model string if a different Claude model is preferred/available at run time; use whatever endpoint your environment actually exposes. Consider batching or rate-limiting if the candidate set is large. Optionally add a third `mode="genom_style"` that first asks the LLM to *generate* a one-sentence definition for empty/boilerplate descriptions, then binds on that generated definition — directly testing the GenOM-style remedy from the research.

---

## 9. Score against the gold standard

### scripts/09_score_binding.py
```python
import pandas as pd
from sklearn.metrics import precision_recall_fscore_support

pred = pd.read_csv("data/results/phase2_bindings_raw.csv")
gold = pd.read_csv("data/gold/gold_standard.csv")

merged = pred.merge(gold, on=["corpus","module","path"], suffixes=("_pred","_gold"))

def score(df, relation_filter=None, exclude_trivial_name_match=False):
    d = df.copy()
    if relation_filter:
        d = d[d["relation_gold"].isin(relation_filter)]
    if exclude_trivial_name_match:
        # recall+ : drop cases where predicted lexicon preferred_name == node's last path segment
        d = d[~d.apply(lambda r: r["path"].split("/")[-1].replace("-","") in str(r.get("lexicon_id_pred","")).lower(), axis=1)]
    y_true = (d["lexicon_id_gold"] == d["lexicon_id_pred"]).astype(int)
    p, r, f1, _ = precision_recall_fscore_support(
        [1]*len(d), y_true, average="binary", zero_division=0
    )
    return {"n": len(d), "precision": p, "recall": r, "f1": f1}

rows = []
for mode in ["name_only", "definition_based"]:
    sub = merged[merged["mode"] == mode]
    rows.append({"mode": mode, "scope": "equivalence_only",
                 **score(sub, relation_filter=["equivalent"])})
    rows.append({"mode": mode, "scope": "equivalence_plus_subsumption",
                 **score(sub, relation_filter=["equivalent","subsumes","subsumed_by"])})
    rows.append({"mode": mode, "scope": "recall_plus_nontrivial",
                 **score(sub, relation_filter=["equivalent"], exclude_trivial_name_match=True)})

pd.DataFrame(rows).to_csv("data/results/phase2_scores.csv", index=False)
print(pd.DataFrame(rows))

# Confusion detail on the trap cases specifically
traps = merged[merged["path"].str.contains("tunnel-termination-point", na=False)]
traps.to_csv("data/results/phase2_trap_case_detail.csv", index=False)
```

**Output:** `phase2_scores.csv` — the headline table: precision/recall/F1 for name-only vs. definition-based, at equivalence-only and equivalence+subsumption scope, plus the `recall+` (non-trivial-match) variant that isolates the draft's real claim. `phase2_trap_case_detail.csv` shows exactly whether the tunnel-termination-point trap was caught by the definition-based run and missed by the name-only run — this single row is the most legible piece of evidence in the whole study.

---

## 10. Sanity thresholds to interpret the numbers

- **Definition-based F1 clears ~0.6–0.7** (OAEI Conference-track LogMap ≈0.67 / BERTMap ≈0.71 as reference bands) **and** materially beats name-only → draft's binding approach is empirically supported even on real, imperfect YANG text.
- **Definition-based F1 ≈ name-only F1** → descriptions add little beyond names in this corpus; your original prior gains support, and the fix is either better-curated definitions or a GenOM-style generation pre-pass (test as `mode="genom_style"` from step 8).
- **Both conditions score poorly (<0.4)** on the trap cases specifically → the "settle by definition, not name" mechanism the draft leans on isn't yet reliable on this corpus, regardless of overall F1 — check `phase2_trap_case_detail.csv` directly rather than only the aggregate.

## 11. What this plan does NOT cover (explicitly out of scope)
- Step 5.5's "reconcile the residual by conversation" (structural reconciliation) — this plan tests binding/identity (§5.3–5.4 of the draft) only, since that's the piece your original question was about. A follow-on study would need a separate multi-turn agent-to-agent conversation harness and its own gold standard for structural transforms (e.g., single-multi-layer vs stacked-layer topology mapping), which is a materially different and harder evaluation.
- Full-scale yangcatalog.org metadata integration — treated as optional/out-of-band per the earlier research.

## 12. Final write-up
`report/FINDINGS.md` should present, in order: Phase 1 coverage/quality/collision tables (with the ISO-704 rubric breakdown and IETF-vs-TAPI contrast), the gold standard (size, agreement statistic, trap cases included), Phase 2's precision/recall/F1 table (name-only vs. definition-based, both scope variants), the trap-case confusion detail, and a one-paragraph verdict against the thresholds in §10. Keep raw CSVs in `data/results/` as backing evidence/appendices.
