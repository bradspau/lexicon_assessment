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
to make ~150 individual judgment calls**, plus 116 name-only/definition-based
binder predictions (58 gold-standard candidates × 2 modes, grown from an
initial 39). No `ANTHROPIC_API_KEY` was available in this environment, so
these were not raw `anthropic` SDK calls, but the binder predictions **were**
produced independently: each candidate × mode was sent to a *separate,
freshly-spawned subagent* (via the coding harness's `Agent` tool) with no
filesystem access and no visibility into this conversation or the gold
standard, given only the literal prompt text `scripts/08_llm_binder.py`
constructs. That's a real blind evaluation, see
`data/results/_real_bindings_results.csv` for the raw per-call outputs.

The 150 ISO-704 rubric labels and the gold-standard bindings themselves are
**not** independent, both were authored by me (Claude, in this same
conversation), hand-encoded into `scripts/_iso704_labels.py` and
`data/gold/gold_standard.csv`. Read those as recorded judgments, not as logic
to trust blindly; the reported κ values (0.880, 0.926) are self-consistency
checks on those judgments, not inter-annotator validation. A handful of gold
labels were revised post-hoc when investigation or convergent independent
blind evidence contradicted the original hand-authored guess, see
`report/FINDINGS.md` §2 for the full history.

**The result moved with every round, converging as real problems got fixed.**
First blind run (39 rows, uncorrected): name-only F1=0.98, definition-based
F1=0.84, inverting the naive hypothesis. After fixing two gold-standard
errors and an overlapping lexicon boundary (39 rows, corrected): name-only
F1=0.946, definition-based F1=0.958, a narrow definition-based lead. After
expanding to 58 rows: name-only F1=0.943, definition-based F1=0.893,
name-only back in front by a real margin, tracing to a newly-found lexicon
over-triggering problem (LEX-003's definition text pulling in unrelated
"tunnel"/"path computation" nodes). After fixing that: name-only F1=0.935,
definition-based F1=0.923, both modes down to 5 errors out of 58, the
closest result of any round. Four runs, four different numbers, from the
same lexicon and corpus, see `report/FINDINGS.md` §2–§3 for the full
reasoning behind each round.

**What is stable across every round is the *shape* of each mode's errors,
not the count, and definition-based's errors got measurably cleaner once
the fixable problems were actually fixed.** Name-only's errors are
consistently name/synonym matches that turn out to mean something different
in context (`nsrlg`, `lifecycle-state`, `owned-node-edge-point`, `cep-list`,
`client-layer-adaptation`, all 5 of name-only's current errors fit this
pattern, and always have). Definition-based's errors, once the LEX-002/003/007
boundary and the LEX-003 over-triggering were both fixed, collapsed to
essentially one category: source descriptions too terse to disambiguate
regardless of lexicon wording (3 of 5 current errors), plus two still-open,
not-yet-investigated issues. Name-only fails when a name misleads;
definition-based fails when there's nothing left to reason from, or on a
lexicon construct-validity problem, and lexicon problems are fixable in a way
terse source text is not.

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

Phase 2, real blind result on the current 58-row gold standard, post-LEX-003-fix:
name-only F1=0.935 (5/58 wrong), definition-based F1=0.923 (5/58 wrong), see
`report/FINDINGS.md` §2–§3 for the full breakdown across all four rounds
(inverted at 39 rows, corrected at 39 rows, expanded to 58, LEX-003 fixed),
and for why the aggregate comparison kept changing while the per-mode error
*patterns* didn't. The one designed trap case (`owned-node-edge-point`, no lexical
overlap with the lexicon's `link-termination-point` synonyms) still resolves
exactly as the plan predicts: mis-bound to `client-access-point` by name
alone, correctly bound to `link-termination-point` given the actual
description text.

## Known limitations beyond the blindness issue

- **Gold standard size (58 rows, grown from 39)** is now near the top of the
  plan's 30–60 target, expanded specifically to test whether the 39-row
  near-tie between modes would hold up. It didn't, name-only regained a real
  lead at 58 rows, demonstrating that even a 48% size increase is enough to
  flip the aggregate F1 comparison a second time. `subsumes` grew from one
  example to two; still dominated by "equivalent" relations. The *pattern* in
  §2/§3 of FINDINGS.md (what each mode's errors have in common) is more
  trustworthy than the specific F1 number from any single round.
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
  validation. A follow-up symmetric re-audit of all 37 rows where the binder
  already agreed with gold found no further `lexicon_id` errors, one relation
  label softened (`client-svc`, `equivalent` → `subsumed_by`, no scoring
  impact), and 3 rows (`odu-type`, `admin-status`, `oper-status`) whose source
  descriptions are near-total name restatements, correctly bound but barely
  testing definitional anchoring at all. See `report/FINDINGS.md` §2's
  "Symmetric re-audit" subsection.
- **The lexicon's LEX-002/LEX-003/LEX-007 definitions originally overlapped**
  ("boundary point... where traffic enters or leaves") enough that even a
  careful blind reader confused them from prose alone. Rewritten with
  explicit cross-references (see `data/lexicon/lexicon.yaml`); 6 of 7 rows in
  this boundary flipped to correct on retest, one (`cep-list/connection-end-point`)
  remains wrong because its four-word source description doesn't state the
  fact needed to disambiguate, no lexicon wording can fix that.
- **A second, distinct lexicon problem surfaced during the 58-row expansion,
  since fixed**: LEX-003's definition text literally contained the strings
  "TE tunnel" and "path computation", so any node whose own description or
  module name shared that vocabulary got pulled toward LEX-003 even when
  it wasn't a tunnel/LSP endpoint, causing 3 of definition-based's 5 new
  errors (`underlay/tunnels`, `path-comp-service/end-point`,
  `client-layer-adaptation`). Rewritten to explicitly exclude containers and
  abstract capability descriptions (see `data/lexicon/lexicon.yaml`); 2 of the
  3 flipped to correct on retest, the third turned out to be a gold-labelling
  error on the same evidence standard as below, revised to match. One
  regression surfaced during retesting (`client-svc`), reported rather than
  quietly re-rolled away, see `report/FINDINGS.md` §2's "LEX-003 correction
  round" for the full accounting.
- **4 gold labels were revised on convergent independent evidence rather
  than source-text verification**: for `/networks/network/link/source`,
  `path-comp-service`, `connectivity-service/connection`, and (after the
  LEX-003 fix) `client-layer-adaptation`, both blind modes independently
  disagreed with the original hand-authored label and converged on the same
  alternative, so the label was revised to match. This is a different,
  weaker standard of evidence than the nsrlg/lifecycle-state corrections
  above (which were verified against the actual RFC/TAPI source text), it
  reflects a genuine modelling judgment call rather than a checkable fact,
  see `data/gold/gold_standard.csv`'s notes column.
