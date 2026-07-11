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
bindings, 78 name-only/definition-based predictions), and no
`ANTHROPIC_API_KEY` was available in the environment this was built in. Every
one of those judgment calls was produced by **me (Claude, via this coding
session) reasoning directly against the same prompt text the scripts would
have sent**, then hand-encoded into `scripts/_iso704_labels.py`,
`scripts/_gold_standard_data.py`, and `scripts/_phase2_bindings_data.py`.
These files are **data, not code** — read them as recorded judgments, not as
logic to trust blindly.

This matters most for Phase 2's headline comparison. **The same agent that
wrote the gold standard also produced the "blind" LLM predictions being
scored against it, in the same conversation.** There is no mechanism here
that prevents contamination — I did not literally look up my own gold
answers while writing the predictions, but I also cannot prove I didn't
subconsciously converge on them, and a skeptical reader shouldn't have to
take that on faith. The reported definition-based F1 of 1.0 (39/39 correct)
is exactly what you'd expect from this setup even if the underlying
capability gap were smaller or larger than that in reality — it is not
independent evidence.

**What Phase 2 *is* good evidence for:** the binder machinery itself
(`scripts/08_llm_binder.py`) is correct — the prompt construction, lexicon
formatting, and scoring pipeline (`scripts/09_score_binding.py`) match the
plan's design and are ready to run against a real API key with zero changes
beyond swapping `_phase2_bindings_data.py`'s hardcoded lists for actual
`anthropic.Anthropic().messages.create(...)` calls. It's also good evidence
that **the trap-case mechanism is coherent**: `owned-node-edge-point`'s
name-only miss and definition-based recovery is a real, inspectable,
non-contaminated *demonstration* of the failure mode the plan predicts, even
if its rate across the whole 39-row set can't be trusted as a population
estimate.

### To get a real number

Re-run `scripts/08_llm_binder.py` with an actual `anthropic` SDK call
(`client.messages.create(...)`, as originally drafted in the plan) instead of
importing `_phase2_bindings_data.py`, using a fresh model call that is given
**only** the prompt text — never the gold standard, never this conversation.
That is the one change that would convert Phase 2 from a worked
demonstration into a real result.

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

Phase 2's one clean, non-contaminated data point: TAPI's
`owned-node-edge-point` (no lexical overlap with the lexicon's
`link-termination-point` synonyms) is mis-bound to `forwarding-element` by
name alone, and correctly bound to `link-termination-point` when given the
actual description text — the mechanism the plan predicts, working as
predicted, on one real example.

## Known limitations beyond the blindness issue

- **Gold standard size (39 rows)** is at the low end of the plan's 30–60
  target and is dominated by "equivalent" relations (25/39); `subsumes` has
  exactly one example. Relation-level analysis (as opposed to bare
  lexicon-ID accuracy) is underpowered.
- **`sentence-transformers` was not installed**; collision analysis
  (`scripts/04_collision_analysis.py`) used the plan's declared TF-IDF
  fallback, which is pure lexical overlap — the "no cross-corpus neighbor
  found above 0.3 similarity" result for the trap-case nodes reflects TF-IDF's
  limits specifically, not a claim about semantic separability in general.
- **ISO-704 rubric labels and the gold-standard second-pass** both report a
  Cohen's κ (0.880 and 0.926 respectively) computed between two passes by
  the same model in the same session. Read these as self-consistency checks
  on the rubric's operational clarity, not as inter-annotator reliability in
  the normal sense.
- One node (`nsrlg`, "Non-Shared Risk Link Group") was bound to the
  `shared-risk-group` lexicon entry by both the gold standard and the
  binder despite the description's literal wording being the semantic
  *inverse* of the lexicon definition — a reminder that surface-level
  definition matching (whether by embeddings, TF-IDF, or an LLM skimming
  quickly) doesn't reliably catch logical negation.
