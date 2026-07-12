# YANG Description Text & Definitional Anchoring: Study

Empirical test of whether YANG `description` statements support LLM-based
"definitional anchoring": binding a data-model node to the right concept in
a reference lexicon using its description text, versus using only its name.
Full methodology: [`../CLAUDE_PLAN_yang_anchoring_study.md`](../CLAUDE_PLAN_yang_anchoring_study.md).
Full findings and discussion: [`report/FINDINGS.md`](report/FINDINGS.md). This
README is an analysis of what was actually built and how much weight the
results can bear, read it before citing any number from this study.

## Running it

```bash
python3 -m venv ../.venv && ../.venv/bin/pip install -r requirements.txt
../.venv/bin/python scripts/01_fetch_corpus.py       # network access required
../.venv/bin/python scripts/02_extract_descriptions.py
../.venv/bin/python scripts/03_quality_audit.py
../.venv/bin/python scripts/04_collision_analysis.py
../.venv/bin/python scripts/08_llm_binder.py         # see caveat below
../.venv/bin/python scripts/09_score_binding.py
```

`scripts/07_build_gold_standard.py` only regenerates the candidate pool and
the second-annotator κ check, the gold standard itself
(`data/gold/gold_standard.csv`) is hand-authored data, not a script output.

## What's real vs. what's a stand-in

This is the single most important thing to understand about this repo. The
pipeline has two structurally different halves:

**Phase 1 (corpus fetch → extraction → quality audit → collision analysis)
is a straight, reproducible measurement.** Every number in
`data/results/phase1_*` comes from mechanically processing the actual fetched
YANG files, pyang parsing, string/regex heuristics, TF-IDF cosine
similarity. Re-running the scripts against the same corpus reproduces the
same numbers. No model judgment is involved except in the ISO-704 rubric
sample (below).

**Phase 2 (lexicon → gold standard → LLM binder → scoring) required an LLM
to make ~150 individual judgment calls** (150 rubric labels, 39 gold-standard
bindings, 78 name-only/definition-based predictions). No `ANTHROPIC_API_KEY`
was available in this environment, so these were not raw `anthropic` SDK
calls, but the 78 binder predictions **were** produced independently: each
of the 39 candidates × 2 modes was sent to a *separate, freshly-spawned
subagent* (via the coding harness's `Agent` tool) with no filesystem access
and no visibility into this conversation or the gold standard, given only the
literal prompt text `scripts/08_llm_binder.py` constructs. That's a real
blind evaluation, see `data/results/_real_bindings_results.csv` for the raw
per-call outputs.

The 150 ISO-704 rubric labels and the 39 gold-standard bindings themselves
are **not** independent, both were authored by me (Claude, in this same
conversation), hand-encoded into `scripts/_iso704_labels.py` and
`scripts/_gold_standard_data.py`. Read those two files as recorded
judgments, not as logic to trust blindly; the reported κ values (0.880,
0.926) are self-consistency checks on those judgments, not inter-annotator
validation.

**The first blind run inverted the naive hypothesis** (name-only F1=0.98 vs.
definition-based F1=0.84), but investigating *why* found that two of
definition-based's eleven "errors" were actually mistakes in the
hand-authored gold standard, and most of the rest traced to three lexicon
entries (LEX-002/003/007) written with overlapping "boundary point"
language. Both were fixed, the two gold rows corrected, the lexicon boundary
sharpened, and the 8 affected candidates re-tested via 8 more isolated blind
subagent calls against the corrected material. **Post-correction, the two
modes are close and definition-based edges ahead: name-only F1=0.946 (3
errors/39), definition-based F1=0.958 (2 errors/39).** See
`report/FINDINGS.md` §2's "Correction round" for the full reasoning,
including the selection-effect caveat (only rows the binder disagreed with
gold on were re-investigated, not a symmetric re-audit of everything).
Name-only's 3 remaining errors are now the more interesting result: each is
a literal name/synonym match that turned out to mean something different
(`nsrlg`, `lifecycle-state`, `owned-node-edge-point`), real evidence for the
study's core claim that surface names can mislead where description text
doesn't. Definition-based's 2 remaining errors are genuinely uncorrectable,
their source descriptions are silent on the fact needed to disambiguate, no
lexicon or prompt fix can supply information the YANG text doesn't contain.

## Findings summary (see `report/FINDINGS.md` for full detail)

| | IETF | TAPI |
|---|---|---|
| nodes scored | 2,279 | 3,418 |
| empty descriptions | 0% | 0% |
| boilerplate (incl. literal `"none"`) | 0.0% | 31.0% |
| name-restatement | 45.4% | 23.3% |
| ISO-704 intensional (sampled) | 44.0% | 45.3% |
| ISO-704 tautological (sampled) | 49.3% | 32.0% |

Neither corpus fits a simple "IETF good / TAPI bad" prior. IETF's failure
mode is near-universal tautology; TAPI's is a large minority of literal
generated-model placeholders (`"none"`, confirmed against source, not an
extraction bug), with non-boilerplate TAPI text scoring *as well or better*
than IETF's on genuine intensional-definition quality.

Phase 2, real blind result post-correction: name-only F1=0.946 (3/39 wrong),
definition-based F1=0.958 (2/39 wrong), see `report/FINDINGS.md` §2–§3 for
the full breakdown, including the first (pre-correction) run's inverted
numbers and why two of its eleven definition-based "errors" turned out to be
gold-standard mistakes. The one designed trap case (`owned-node-edge-point`,
no lexical overlap with the lexicon's `link-termination-point` synonyms)
still resolves exactly as the plan predicts: mis-bound to
`client-access-point` by name alone, correctly bound to
`link-termination-point` given the actual description text.

## Known limitations beyond the blindness issue

- **Gold standard size (39 rows)** is at the low end of the plan's 30–60
  target and is dominated by "equivalent" relations (25/39); `subsumes` has
  exactly one example. With only 39 rows, a 2-to-5-error swing is enough to
  move the aggregate F1 comparison, the *pattern* in §2/§3 of FINDINGS.md is
  more trustworthy than the specific F1 numbers.
- **`sentence-transformers` was not installed**; collision analysis
  (`scripts/04_collision_analysis.py`) used the plan's declared TF-IDF
  fallback, which is pure lexical overlap, the "no cross-corpus neighbor
  found above 0.3 similarity" result for the trap-case nodes reflects TF-IDF's
  limits specifically, not a claim about semantic separability in general.
- **ISO-704 rubric labels were authored by me in this conversation**; the
  reported κ = 0.880 is a self-consistency check on those judgments, not
  inter-annotator validation.
- **The gold standard had two confirmed errors**, found post-hoc by
  investigating definition-based's disagreements with it: `nsrlg` ("Non-Shared
  Risk Link Group") was gold-labelled as LEX-009 shared-risk-group despite the
  source text describing the semantic opposite (mandatory disjointness, not
  shared risk); `lifecycle-state` was gold-labelled as LEX-011
  administrative-state despite describing a distinct provisioning-lifecycle
  concept. Both are now corrected to `NONE` in `data/gold/gold_standard.csv`
  (see its notes column). The reported second-annotator κ = 0.926 predates
  this correction and is a self-consistency check, not inter-annotator
  validation, and this correction methodology only re-examined rows the
  binder disagreed with gold on, not a symmetric re-audit of every row.
- **The lexicon's LEX-002/LEX-003/LEX-007 definitions originally overlapped**
  ("boundary point... where traffic enters or leaves") enough that even a
  careful blind reader confused them from prose alone. Rewritten with
  explicit cross-references (see `data/lexicon/lexicon.yaml`); 6 of 7 rows in
  this boundary flipped to correct on retest, one (`cep-list/connection-end-point`)
  remains wrong because its four-word source description doesn't state the
  fact needed to disambiguate, no lexicon wording can fix that.
