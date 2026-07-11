# YANG Description Text & Definitional Anchoring — Study

Empirical test of whether YANG `description` statements support LLM-based
"definitional anchoring": binding a data-model node to the right concept in
a reference lexicon using its description text, versus using only its name.
Full methodology: [`../CLAUDE_PLAN_yang_anchoring_study.md`](../CLAUDE_PLAN_yang_anchoring_study.md).
Full findings and discussion: [`report/FINDINGS.md`](report/FINDINGS.md). This
README is an analysis of what was actually built and how much weight the
results can bear — read it before citing any number from this study.

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
the second-annotator κ check — the gold standard itself
(`data/gold/gold_standard.csv`) is hand-authored data, not a script output.

## What's real vs. what's a stand-in

This is the single most important thing to understand about this repo. The
pipeline has two structurally different halves:

**Phase 1 (corpus fetch → extraction → quality audit → collision analysis)
is a straight, reproducible measurement.** Every number in
`data/results/phase1_*` comes from mechanically processing the actual fetched
YANG files — pyang parsing, string/regex heuristics, TF-IDF cosine
similarity. Re-running the scripts against the same corpus reproduces the
same numbers. No model judgment is involved except in the ISO-704 rubric
sample (below).

**Phase 2 (lexicon → gold standard → LLM binder → scoring) required an LLM
to make ~150 individual judgment calls** (150 rubric labels, 39 gold-standard
bindings, 78 name-only/definition-based predictions). No `ANTHROPIC_API_KEY`
was available in this environment, so these were not raw `anthropic` SDK
calls — but the 78 binder predictions **were** produced independently: each
of the 39 candidates × 2 modes was sent to a *separate, freshly-spawned
subagent* (via the coding harness's `Agent` tool) with no filesystem access
and no visibility into this conversation or the gold standard, given only the
literal prompt text `scripts/08_llm_binder.py` constructs. That's a real
blind evaluation — see `data/results/_real_bindings_results.csv` for the raw
per-call outputs.

The 150 ISO-704 rubric labels and the 39 gold-standard bindings themselves
are **not** independent — both were authored by me (Claude, in this same
conversation), hand-encoded into `scripts/_iso704_labels.py` and
`scripts/_gold_standard_data.py`. Read those two files as recorded
judgments, not as logic to trust blindly; the reported κ values (0.880,
0.926) are self-consistency checks on those judgments, not inter-annotator
validation.

**The headline result is genuinely surprising, and inverts the naive
hypothesis:** real, blind name-only binding scored F1=0.98 (1 error / 39);
real, blind definition-based binding scored F1=0.84 (11 errors / 39).
Don't stop at that headline, though — `report/FINDINGS.md` §2 breaks down
*why*: roughly two-thirds of definition-based's errors are appropriately
cautious `NONE` refusals on cases where my own gold labels were arguably too
generous, and most of its genuine errors cluster on three lexicon entries
(LEX-002/003/007) whose definitions I wrote with overlapping "boundary
point" language — a lexicon-design artifact the experiment surfaced, not
proof that description text doesn't help. Meanwhile name-only's strong score
is largely because the lexicon's synonym lists were curated *from the
corpus*, so most nodes have an exact string match waiting for them — that's
an artifact of experimental setup, not evidence names alone carry enough
meaning in general. The one designed trap case that isolates the actual
mechanism (`owned-node-edge-point`) still resolves exactly as the plan
predicts: name-only wrong, definition-based right, under a real blind call.

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

Phase 2, real blind result: name-only F1=0.98 (1/39 wrong), definition-based
F1=0.84 (11/39 wrong) — see `report/FINDINGS.md` §2–§3 for the full breakdown
of why before drawing a "descriptions don't help" conclusion from the raw
numbers alone. The one designed trap case (`owned-node-edge-point`, no
lexical overlap with the lexicon's `link-termination-point` synonyms) still
resolves exactly as the plan predicts: mis-bound to `client-access-point` by
name alone, correctly bound to `link-termination-point` given the actual
description text.

## Known limitations beyond the blindness issue

- **Gold standard size (39 rows)** is at the low end of the plan's 30–60
  target and is dominated by "equivalent" relations (25/39); `subsumes` has
  exactly one example. With only 39 rows, 11 definition-based errors is a
  small enough sample that a handful of lexicon rewrites could plausibly flip
  the aggregate F1 comparison — the *pattern* in §2/§3 of FINDINGS.md is more
  trustworthy than the specific F1 numbers.
- **`sentence-transformers` was not installed**; collision analysis
  (`scripts/04_collision_analysis.py`) used the plan's declared TF-IDF
  fallback, which is pure lexical overlap — the "no cross-corpus neighbor
  found above 0.3 similarity" result for the trap-case nodes reflects TF-IDF's
  limits specifically, not a claim about semantic separability in general.
- **ISO-704 rubric labels and the gold standard itself** (as opposed to the
  binder predictions scored against it) were authored by me in this
  conversation; the reported κ values (0.880, 0.926) are self-consistency
  checks on those judgments, not inter-annotator validation. Several of
  definition-based's "errors" in §2 are cases where a rigorous reading
  suggests my gold label, not the blind model call, was the less careful
  judgment (see the `te-node-template` and `nsrlg` discussions in
  `report/FINDINGS.md`).
- **The lexicon's LEX-002/LEX-003/LEX-007 definitions overlap** ("boundary
  point... where traffic enters or leaves") enough that even a careful blind
  reader confuses them from prose alone; name-only mode sidesteps this
  entirely via exact synonym-string matches that happen to exist because the
  lexicon was authored by reading the corpus. Both of these are lexicon
  construction issues, not evidence about the underlying question.
- One node (`nsrlg`, "Non-Shared Risk Link Group") was correctly flagged
  `NONE` by the real blind definition-based call, catching a shared/vs-non-shared
  inversion between the description text and the lexicon definition that the
  gold standard (my earlier judgment) had papered over — a good illustration
  that not every definition-based "miss" in this run is actually a model
  error.
