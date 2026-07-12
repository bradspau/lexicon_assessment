# YANG Description Quality & Definitional Anchoring — Findings

## §1. Phase 1: Description quality audit

**Corpus:** 4 IETF modules (`ietf-network`, `ietf-network-topology`, `ietf-te-topology`, `ietf-otn-topology`) and 3 TAPI v2.5.2 modules (`tapi-topology`, `tapi-connectivity`, `tapi-common`), plus their transitive import dependencies (fetched separately so pyang could resolve augments/imports but excluded from scoring). Node ownership for augmented nodes (e.g. TE/OTN attributes augmented onto the base `ietf-network`/`ietf-network-topology` tree) was attributed via pyang's `i_module`, not the root module of the tree — see `scripts/02_extract_descriptions.py` docstring for why the plan's primary `pyang -f flatten` CLI approach doesn't work here (it can't see cross-file augment targets when modules are extracted one file at a time).

- **2,279** scored IETF data-nodes (container/leaf/list/leaf-list/choice), **3,418** scored TAPI data-nodes. No `typedef`/`grouping`/`identity`/`case` nodes appear because pyang's `i_children` walk only yields data-tree nodes.

### Coverage summary (`phase1_coverage_summary.csv`)

| corpus | n_nodes | pct_empty | pct_boilerplate | pct_restates_name | mean_words | median_words |
|---|---|---|---|---|---|---|
| ietf | 2,279 | 0.0% | 0.0% | 45.4% | 10.2 | 6 |
| tapi | 3,418 | 0.0% | 31.0% | 23.3% | 13.4 | 7 |

`pct_boilerplate` includes the literal string `"none"`, which is not an extraction artifact — it's literal source text in TAPI (confirmed against `corpus/tapi/tapi-topology.yang`), almost certainly a leftover from TAPI's UML→YANG code generation. Neither corpus has any truly *empty* description statements.

### ISO-704 definitional-quality rubric (`phase1_iso704_scores.csv`, `phase1_iso704_distribution.csv`)

150-node stratified sample (75/corpus, `random_state=42`), scored on the 4-way rubric (`intensional` / `extensional_example_only` / `circular_tautological` / `empty_boilerplate`):

| corpus | intensional | circular_tautological | extensional_example_only | empty_boilerplate |
|---|---|---|---|---|
| ietf | 44.0% | 49.3% | 6.7% | 0.0% |
| tapi | 45.3% | 32.0% | 0.0% | 22.7% |

**Annotator agreement caveat:** the plan calls for comparing an independent manual pass against an LLM pass on a 30-node overlap. This run had no `ANTHROPIC_API_KEY`, so both the "manual" and "llm" passes in `phase1_iso704_scores.csv` were produced by the same model (Claude) reading the text directly, in two separate passes. Cohen's κ = **0.880** (93.3% simple agreement, n=30) therefore measures *rubric self-consistency*, not true human-vs-LLM agreement — treat it as a floor on reliability, not a validation of LLM-as-annotator against independent human judgment.

**Headline:** roughly **44–45% of descriptions in both corpora are genuinely intensional** (state a genus + differentiating characteristic per ISO 704), but the failure modes differ by corpus: IETF's problem is tautology (name-restatement, ~49%), TAPI's is literal boilerplate (~23% `"none"`) with a lower tautology rate. This is a more mixed picture than a simple "IETF good / TAPI bad" prior would predict — TAPI's *non-boilerplate* descriptions are if anything slightly more often intensional than IETF's.

### Duplicate descriptions (`phase1_duplicate_descriptions.csv`, 429 groups)

Both corpora show heavy reuse of identical description text across structurally-repeated groupings — e.g. IETF's "Strict or loose hop." appears 136 times (every `hop-type` leaf across all the different route-object types), TAPI's generic "The specific value."/"The specific unit of measurement of the capacity." patterns appear 60–120+ times each (characteristic of TAPI's heavily-templated capacity/characteristic value pattern). This isn't necessarily a defect — the *concept* (e.g. "a name, which carries no semantics") genuinely is identical everywhere it's reused — but it means description text alone often can't disambiguate two different reuse *sites* of the same grouping.

### Same-corpus semantic collisions (`phase1_collisions.csv`, TF-IDF cosine >0.85, 214 pairs after excluding same-named nodes)

All 214 IETF collisions found were between structurally-repeated substructures (`optimizations`, `path-metric`, `connectivity-matrix`) reused at different points in the `te-topology` tree (e.g. under `tunnel-termination-point/local-link-connectivities` vs. under `te-node-attributes/connectivity-matrices`) — same grouping content, different scope. This is a real ambiguity mode: from description text alone, you cannot tell *which* connectivity-matrix's path-metric you're looking at; you need the path.

**This is a fundamentally different limit from anything Phase 2 tests, and worth naming precisely.** Phase 2 asks a *concept-level* question: given a node's description, can you tell **which lexicon concept** it represents? Text often can answer that (§2). This collision finding asks an *instance-level* question: given two nodes that are correctly classified as **the same concept**, can the text tell you **which occurrence** you're looking at? Here, text structurally cannot — not because the descriptions are poorly written, but because they're *byte-for-byte identical by construction*. The cleanest example in the corpus:

```
/networks/network/node/te/te-node-attributes/connectivity-matrices/optimizations
/networks/network/node/te/information-source-entry/connectivity-matrices/optimizations
```

Both carry the exact same description: *"The objective function container that includes attributes to impose when computing a TE path."* One is the `optimizations` container under a node's live, configured connectivity matrix; the other is under an `information-source-entry` — a different provenance/scope for effectively the same schema shape, reused via the same YANG grouping. The two are legitimately different things (different scope, different lifecycle, potentially different values), but the description text was never going to distinguish them, because it's the same string in both places by design.

The implication for "definitional anchoring" as a research question: solving concept-level anchoring (making descriptions intensional, disambiguating a node against a reference lexicon) does not solve instance-level disambiguation. No amount of LLM reasoning over description text recovers positional information the text never encoded — that information lives in the path (or some other structural signal: parent context, containing list key, `when`/`augment` target), not in prose. Any system built on this study's anchoring approach needs both: definitional text to resolve *what kind of thing* a node is, and structural/path context to resolve *which one*. Treating text-only anchoring as sufficient on its own will silently conflate distinct instances that happen to share a grouping.

### Cross-corpus separability (`phase1_cross_corpus_similarity.csv`, TF-IDF cosine >0.3, 536 pairs)

Note this reuses `sentence-transformers`'s declared fallback (TF-IDF) since `sentence-transformers` was not installed in this environment (pure lexical overlap, no semantic embedding). Under TF-IDF, **none** of the plan's headline trap-case nodes (`ietf-te-topology`'s `tunnel-termination-point`, `ietf-network-topology`'s `termination-point`) have *any* TAPI neighbor above the 0.3 threshold — IETF and TAPI use almost entirely disjoint vocabulary for the same concepts (e.g. IETF "termination point... refer to a port or an interface" vs. TAPI "NEPs belonging to / owned by this Node"). This is a negative result for lexical methods specifically, not necessarily for semantic understanding — it's the exact gap an LLM's world knowledge (rather than surface token overlap) would need to bridge, which is what Phase 2 tests directly.

---

## §2. Phase 2: name-only vs. definition-based LLM binding

### Methodology note: this run is genuinely blind

An earlier pass through this study (superseded, see git history) had the same agent that authored the gold standard also produce the "blind" predictions in the same conversation — a real contamination risk. **This version replaces that with 78 real, isolated tool-call invocations** (39 candidates × 2 modes), each a fresh model instance spun up via the `Agent` tool with no filesystem access and no visibility into this conversation or `data/gold/gold_standard.csv`. Each received only the literal prompt text `scripts/08_llm_binder.py` would send (lexicon block + node info) and answered independently — see `data/results/_real_bindings_results.csv` for the raw per-call outputs and `scripts/08_llm_binder.py`'s docstring for exactly how the prompts were constructed. This is a real blind evaluation, not a demonstration.

### Setup

12-entry lexicon (`data/lexicon/lexicon.yaml`), including the plan's two worked trap-case entries (LEX-002 `link-termination-point` vs. LEX-003 `service-anchor`) plus 9 more concepts grounded in terms actually observed in the corpus. 39-row gold standard (`data/gold/gold_standard.csv`, 22 IETF + 17 TAPI). One correction made before running the binder: the lexicon draft initially included `owned-node-edge-point`/`node-edge-point` as extra LEX-002 synonyms beyond the plan's original `[termination-point, port]`, which would have let name-only mode solve the TAPI trap case by trivial synonym lookup — removed before scoring.

(The gold standard itself and its second-annotator κ = 0.926 were still produced by me in-conversation, same as the ISO-704 rubric labels in §1 — that limitation stands. What changed is the *binder*, which is now independent of both.)

### Results (`phase2_scores.csv`), the headline is inverted from the naive hypothesis

| mode | scope | n | precision | recall | F1 |
|---|---|---|---|---|---|
| name_only | equivalence_only | 26 | 0.960 | 1.000 | 0.980 |
| name_only | equivalence_plus_subsumption | 39 | 0.974 | 1.000 | 0.987 |
| name_only | recall_plus_nontrivial | 26 | 0.960 | 1.000 | 0.980 |
| definition_based | equivalence_only | 26 | 0.818 | 0.857 | 0.837 |
| definition_based | equivalence_plus_subsumption | 39 | 0.871 | 0.794 | 0.831 |
| definition_based | recall_plus_nontrivial | 26 | 0.818 | 0.857 | 0.837 |

**How to read this table.** An earlier version of `scripts/09_score_binding.py` computed precision using a degenerate sklearn trick that pinned it at 1.0 regardless of binder quality, see git history for the superseded note that explained that bug. The script has since been fixed to compute proper detection-plus-classification precision and recall, the standard approach for tasks like named-entity recognition, where a system both has to notice something exists and get its label right.

Per row, against gold: TP (true positive) is the binder asserting the exact correct lexicon entry. FP (false positive) is the binder confidently asserting a real lexicon entry that is wrong, whether gold wanted a different entry or no match at all. FN (false negative) is the binder answering `NONE` when gold wanted a real match. The one gold row that genuinely should get `NONE` (`/context/topology-context/topology/node/node-rule-group`) is now included in every scope, since correctly abstaining matters no matter how leniently subsumption is counted. Both modes got it right, so it contributes a true negative and does not move precision or recall either way, it just adds 1 to `n`.

- **Precision** = TP / (TP + FP): of all the times the binder confidently asserted a specific lexicon entry, how often that entry was actually correct. `name_only` sits at 0.96, it made exactly one wrong, confident guess (the `owned-node-edge-point` trap). `definition_based` sits at 0.818 to 0.871 depending on scope, reflecting 4 wrong, confident guesses across the run.
- **Recall** = TP / (TP + FN): of all the gold rows that genuinely needed a real match, how often the binder found it, whether by a confident guess or not. `name_only` hits 1.000 in every scope, it never inappropriately abstained. `definition_based` sits at 0.79 to 0.86, reflecting 7 cases where it answered `NONE` on a row gold expected a real match.
- **F1** is the harmonic mean of the two. Its value is unchanged from the earlier, buggy version of this table, which turns out to be a mathematical coincidence rather than a mistake: F1 reduces algebraically to `2×TP / (2×TP + FP + FN)`, a quantity that does not depend on how "wrong" gets split between FP and FN. So F1 was already correct even while precision and recall, individually, were not.

Across all 39 candidates, **name-only made 1 error, definition-based made 11**, split as 1 FP and 0 FN for name-only versus 4 FP and 7 FN for definition-based. This is the opposite of both the plan's hypothesis and the earlier, contaminated hand-run's result. It would be a mistake to read this as "descriptions actively hurt binding" without understanding why, the error pattern (`data/results/phase2_bindings_raw.csv`, diffed against gold) tells a more specific story than that.

### Why definition-based lost: two distinct, genuine causes

**1. Definition-based mode is measurably more cautious, and forced-choice scoring punishes hedging as harshly as being wrong.** 7 of its 11 errors are `NONE` responses on legitimately ambiguous cases — e.g. `/networks/network/node/te/te-node-template` ("The reference to a TE node template.") was refused at confidence 0.95 rather than force-matched to LEX-001 `forwarding-element` (which the gold standard called `subsumed_by`, my own judgment call at the time). A "reference to a template" genuinely isn't the same genus as "a network element," and the model's refusal to paper over that gap is arguably *more* ISO-704-rigorous than my gold label was. Name-only mode never once returned `NONE` on a wrong-but-refusable case in this run — it always committed to an answer, and its lexical shortcuts (below) mostly happened to be right.

**2. Name-only's accuracy is partly an artifact of how the lexicon was built, not evidence that names are semantically sufficient.** I authored `lexicon.yaml`'s synonym lists by looking at the corpus, so synonyms like `client-svc`, `connection-end-point`, `admin-status`, `risk-characteristic`, `layer-protocol-name` are exact, verbatim matches to real node names — meaning name-only mode can solve most of the gold set by string lookup rather than any semantic reasoning. This is a property of the experimental setup (synonym curation quality), not a general finding that node names alone carry enough meaning. A lexicon built independently of the corpus (e.g. from a standards document, before seeing which YANG modules would be scored) would very likely show a smaller name-only advantage.

**3. Where definition-based genuinely lost on the merits, not just via caution:** several errors cluster on the LEX-002/LEX-003/LEX-007 boundary (`link-termination-point` / `service-anchor` / `client-access-point`) — three "boundary point" concepts whose definitions in my lexicon share overlapping language ("boundary point," "point at which traffic enters or leaves"). `connection-end-point` (gold LEX-007) was bound to LEX-002; `ConnectivityServiceEndPoint` (gold LEX-007) was bound to LEX-003 twice. Name-only solved these instantly via exact synonym string-match (`connection-end-point` is literally listed under LEX-007), while definition-based had to reason from prose across three insufficiently-differentiated definitions and picked wrong more than once. **This is a lexicon construct-validity problem the experiment surfaced, not proof that definition-based reasoning is unreliable in general** — it shows that description-based binding is only as good as how precisely the target lexicon's definitions are written apart from each other.

### Trap-case detail (`phase2_trap_case_detail.csv`) — the mechanism still holds, just not in aggregate

**Plan's original IETF trap** (`ietf-te-topology`'s `tunnel-termination-point`, gold = LEX-003): **both modes got this right**, because LEX-003's synonym list includes `tunnel-termination-point` verbatim (the plan's own worked example) — name-only solves it by exact string match without needing the description.

**The TAPI trap that actually differentiates the two modes** (`tapi-topology`'s `owned-node-edge-point`, gold = LEX-002):
- name-only (real, blind): predicted **LEX-007** (`client-access-point`) — wrong. (An earlier hand-simulated run guessed it would pick LEX-001 via the "node" substring; the real model's actual failure mode was different, which is itself a reminder that hand-simulating model behavior is not a substitute for calling the model.)
- definition-based (real, blind): predicted **LEX-002** — correct, at confidence 0.75. The description ("NEPs belonging to / owned by this Node... 'own' the NEPs") frames NEPs as boundary sub-components *owned by* a node, matching LEX-002's genus rather than any competing entry.

This one row remains the cleanest, fully-uncontaminated evidence for the draft's specific mechanism claim: when a corpus's naming convention (`NodeEdgePoint`) diverges entirely from the lexicon's vocabulary (`termination-point`), description text — not name, not synonym curation — is what recovers the correct binding. It just turns out to be one win against a larger number of losses elsewhere, which is the honest, if less clean, overall picture.

**The `nsrlg` negation case, resolved correctly this time:** IETF's `nsrlg` node describes itself as "List of NSRLGs (**Non**-Shared Risk Link Groups)" — the literal opposite of LEX-009's "shared risk group" definition. The real blind definition-based call answered **NONE** at confidence 0.75, correctly catching the shared/non-shared inversion that the gold standard (my own earlier judgment call) papered over by force-matching to LEX-009 anyway. Scored as a "miss" against gold, but arguably the more rigorous answer — a good illustration of why some of definition-based's "errors" here reflect gold-standard imprecision rather than model failure.

## §3. Verdict against §10 thresholds

The plan's §10 thresholds assume a single F1 number settles the question; this run's actual result resists that framing:

1. **Neither "definition-based clears name-only" nor "descriptions don't help" is the right one-line takeaway.** The real, blind F1s are name-only 0.98 / definition-based 0.84 — definition-based measurably *lost* on raw accuracy in this specific setup. But roughly two-thirds of its errors are appropriately cautious refusals on cases where my own gold labels were arguably too generous, and its genuine errors cluster on a lexicon boundary (LEX-002/003/007) that I wrote with overlapping language — a fixable lexicon problem, not a fundamental limit on definitional binding.
2. **Name-only's strong score is largely an artifact of synonym-list curation quality**, not evidence that bare node names carry sufficient meaning in general. Because the lexicon was authored by reading the corpus, most gold-standard nodes have an exact-string synonym waiting for them. This is worth stating plainly: **the experimental setup, not the underlying phenomenon, is most of why name-only won here.**
3. **The one mechanism the draft specifically predicts — description text recovering a binding that diverges from the lexicon's assumed vocabulary — still held up under a real blind test** (`owned-node-edge-point`). That's real, if narrow, support for the draft's core claim. It just wasn't enough to carry the aggregate numbers, because the aggregate numbers are dominated by lexicon-design artifacts in both directions.
4. **What Phase 1 supports independently of any of this**: IETF descriptions are non-empty but nearly half tautological (49.3%); TAPI is ~23% literal `"none"` boilerplate but comparably-or-more intensional when present (45.3% vs. 44.0%). This half of the study has no blindness confound and is the more trustworthy finding on its own.
5. **To get a cleaner Phase 2 result**, the next iteration should build the lexicon *before* looking at the corpus (e.g. from an independent standards glossary), write definitions with an explicit differentiation pass against neighboring entries, and/or expand the gold standard well past 39 rows so single-case noise (11 errors is a small sample) doesn't dominate the aggregate F1.

## §4. What this execution deviated from in the plan, and why

- **Extraction** used the pyang Python API directly (`scripts/02_extract_descriptions.py`) instead of the CLI `-f flatten --flatten-description`, because the CLI plugin can't resolve cross-file augments (IETF's TE/OTN topology modules augment the base network/network-topology tree) when modules are passed one file at a time, and gives no way to attribute an augmented node to its true owning module. Verified against `i_module.arg` on live augmented nodes before trusting it.
- **Collision analysis** used the TF-IDF fallback, not `sentence-transformers` (not installed in this environment — kept optional per the plan).
- **Phase 2 binder** used 78 isolated `Agent`-tool subagent calls, each given only the literal prompt text (no tool/file access), rather than raw `anthropic` SDK calls against a real API key (none was available) — functionally equivalent for blindness purposes, since each call starts with zero shared context. See `scripts/08_llm_binder.py` and `data/results/_real_bindings_results.csv`.
- ISO-704 rubric annotation (Phase 1) and gold-standard authoring/second-pass (Phase 2 setup) still have a single-agent-does-both-passes limitation; the reported κ values (0.880 and 0.926) should be read as self-consistency checks, not inter-annotator validation. This is now Phase 2's *only* remaining contamination risk — the binder itself is clean.
