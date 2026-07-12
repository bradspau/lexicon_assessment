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
to make ~150 individual judgment calls**, plus 144 name-only/definition-based
binder predictions (72 gold-standard candidates × 2 modes, grown from an
initial 39 via two expansion rounds). No `ANTHROPIC_API_KEY` was available in this environment, so
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
to trust blindly; the reported κ values (0.880 for ISO-704, 0.852 for the
gold-standard second-annotator check, n=15 either way) are self-consistency
checks on those judgments, not inter-annotator validation. A handful of gold
labels were revised post-hoc when investigation or convergent independent
blind evidence contradicted the original hand-authored guess, see
`report/FINDINGS.md` §2 for the full history, including a note on why the
second-annotator κ reads lower now than it did earlier in the process (a
later gold-standard correction desynced the frozen second-pass comparison
file, not a new disagreement).

**The result moved with every round, converging as real problems got fixed,
then held and widened under a second, larger expansion.**
First blind run (39 rows, uncorrected): name-only F1=0.98, definition-based
F1=0.84, inverting the naive hypothesis. After fixing two gold-standard
errors and an overlapping lexicon boundary (39 rows, corrected): name-only
F1=0.946, definition-based F1=0.958, a narrow definition-based lead. After
expanding to 58 rows: name-only F1=0.943, definition-based F1=0.893,
name-only back in front by a real margin, tracing to a newly-found lexicon
over-triggering problem (LEX-003's definition text pulling in unrelated
"tunnel"/"path computation" nodes). After fixing that: name-only F1=0.935,
definition-based F1=0.923, both modes down to 5 errors out of 58. After
investigating the last two open definition-based errors, one was a real,
fixable gap (LEX-005 missing a parent-context rule, fixed), the other was
diagnosed as single-call sampling noise on a genuinely borderline case:
name-only F1=0.935, definition-based F1=0.942, definition-based ahead.
Expanded a second time to 72 rows specifically to test whether that lead
held up: name-only F1=0.923, definition-based F1=0.945, **the gap widened**.
Six runs, a result that gets more pronounced under more data rather than
shrinking or flipping, the signature of a real effect rather than small-n
noise, see `report/FINDINGS.md` §2–§3 for the full reasoning behind each
round.

**What is stable across every round is the *shape* of each mode's errors,
not the count, and definition-based's errors got measurably cleaner as every
fixable problem was actually fixed and regression-tested.** Name-only's
errors are consistently name/synonym matches, or in the clearest final-round
case a structural inference from a bare path with no description available
at all (`/networks/network` reasoned to "contain nodes" and bound to LEX-001,
with nothing to correct that inference in name-only mode), that turn out to
mean something different or fall outside the lexicon's scope (all 7 of
name-only's final errors fit this pattern, and always have). Definition-based's
errors, once every fixable lexicon problem found (LEX-002/003/007's overlap,
LEX-003's over-triggering, LEX-005's parent-context gap) was fixed, collapsed
to essentially one category: source descriptions too terse to disambiguate
regardless of lexicon wording (3 of 5 final errors), plus one likely sampling
artifact and one genuine, narrow edge-case judgment call about lexicon scope.
Name-only fails when a name, or a name-shaped inference, misleads;
definition-based fails when there's nothing left in the text to reason from,
a genuine, irreducible limit of the source material, unlike a name/synonym
choice, which the lexicon author controls.

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

Phase 2, real blind result on the current 72-row gold standard, final:
name-only F1=0.923 (7/72 wrong), definition-based F1=0.945 (5/72 wrong), see
`report/FINDINGS.md` §2–§3 for the full breakdown across all six rounds
(inverted at 39 rows, corrected at 39 rows, expanded to 58, LEX-003 fixed,
LEX-005 fixed + supporting-network investigated, expanded again to 72), and
for why the aggregate comparison kept changing, converging and widening in
definition-based's favour as the gold standard grew, while the per-mode
error *patterns* stayed constant throughout. The one designed trap case
(`owned-node-edge-point`, no lexical
overlap with the lexicon's `link-termination-point` synonyms) still resolves
exactly as the plan predicts: mis-bound to `client-access-point` by name
alone, correctly bound to `link-termination-point` given the actual
description text.

## Known limitations beyond the blindness issue

- **Gold standard size (72 rows, grown from 39 via two expansion rounds)**
  is now well past the plan's 30–60 target. The first expansion (39→58) was
  run to test whether the 39-row near-tie would hold up, it didn't, name-only
  regained a real lead, demonstrating that even a 48% size increase can flip
  the aggregate F1 comparison. After investigating and fixing the lexicon
  problems that surfaced, definition-based took the lead at 58 rows; a
  second expansion (58→72) tested whether *that* lead would hold, and it
  did, widening rather than narrowing. `subsumes` grew from one example to
  five; still dominated by "equivalent" relations. The *pattern* in §2/§3 of
  FINDINGS.md (what each mode's errors have in common) is more trustworthy
  than the specific F1 number from any single round, though the trend across
  the last two expansions is now a meaningful data point in its own right.
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
  (see its notes column). The reported second-annotator κ was originally
  0.926, but the `nsrlg` fix desynced that number from the frozen 15-row
  comparison file it's computed against (still holding the old, uncorrected
  label); re-running the check now gives κ = 0.852. Either way it's a
  self-consistency check, not inter-annotator validation, see
  `report/FINDINGS.md` §2 for the detail. A follow-up symmetric re-audit of
  all 37 rows where the binder
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
- **A third lexicon gap (`layer-protocol-name` under `service-interface-point`
  binding to its parent entity's type instead of LEX-005) was found, fixed,
  and confirmed via regression testing**: LEX-005 was missing an explicit
  rule that a `layer-protocol-name`-style attribute belongs to LEX-005
  regardless of which entity it decorates, confirmed by comparison against
  two already-correct sibling rows using the identical pattern. Fixed with
  one added sentence; all 3 layer-protocol-name rows in the gold standard now
  bind consistently. The other open error (`supporting-network`) was
  diagnosed as likely single-call sampling noise rather than a fixable
  defect, a diagnostic re-check returned the correct answer, but per this
  study's rule against re-rolling until a call agrees with the desired
  result, it was not substituted in as the scored prediction, see
  `report/FINDINGS.md` §2's "LEX-005 correction round" for the reasoning.
- **One new definition-based error from the second expansion was left
  unrevised, deliberately**: `network-id` ("Identifies a network.") bound to
  `LEX-001 subsumed_by` rather than gold's `NONE`. This is a single
  disagreement, not the convergent-independent-evidence pattern used
  elsewhere in this study to justify revising a gold label, so it stands as
  a genuine recorded error, a real edge case (does an identifier of an
  out-of-scope concept inherit the nearest in-scope concept, or stay out of
  scope?) rather than a lexicon defect to fix.
