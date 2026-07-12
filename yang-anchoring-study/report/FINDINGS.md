# YANG Description Quality & Definitional Anchoring, Findings

## §1. Phase 1: Description quality audit

**Corpus:** 4 IETF modules (`ietf-network`, `ietf-network-topology`, `ietf-te-topology`, `ietf-otn-topology`) and 3 TAPI v2.5.2 modules (`tapi-topology`, `tapi-connectivity`, `tapi-common`), plus their transitive import dependencies (fetched separately so pyang could resolve augments/imports but excluded from scoring). Node ownership for augmented nodes (e.g. TE/OTN attributes augmented onto the base `ietf-network`/`ietf-network-topology` tree) was attributed via pyang's `i_module`, not the root module of the tree, see `scripts/02_extract_descriptions.py` docstring for why the plan's primary `pyang -f flatten` CLI approach doesn't work here (it can't see cross-file augment targets when modules are extracted one file at a time).

- **2,279** scored IETF data-nodes (container/leaf/list/leaf-list/choice), **3,418** scored TAPI data-nodes. No `typedef`/`grouping`/`identity`/`case` nodes appear because pyang's `i_children` walk only yields data-tree nodes.

### Coverage summary (`phase1_coverage_summary.csv`)

| corpus | n_nodes | pct_empty | pct_boilerplate | pct_restates_name | mean_words | median_words |
|---|---|---|---|---|---|---|
| ietf | 2,279 | 0.0% | 0.0% | 45.4% | 10.2 | 6 |
| tapi | 3,418 | 0.0% | 31.0% | 23.3% | 13.4 | 7 |

`pct_boilerplate` includes the literal string `"none"`, which is not an extraction artifact, it's literal source text in TAPI (confirmed against `corpus/tapi/tapi-topology.yang`), almost certainly a leftover from TAPI's UML→YANG code generation. Neither corpus has any truly *empty* description statements.

### ISO-704 definitional-quality rubric (`phase1_iso704_scores.csv`, `phase1_iso704_distribution.csv`)

150-node stratified sample (75/corpus, `random_state=42`), scored on the 4-way rubric (`intensional` / `extensional_example_only` / `circular_tautological` / `empty_boilerplate`):

| corpus | intensional | circular_tautological | extensional_example_only | empty_boilerplate |
|---|---|---|---|---|
| ietf | 44.0% | 49.3% | 6.7% | 0.0% |
| tapi | 45.3% | 32.0% | 0.0% | 22.7% |

**Annotator agreement caveat:** the plan calls for comparing an independent manual pass against an LLM pass on a 30-node overlap. This run had no `ANTHROPIC_API_KEY`, so both the "manual" and "llm" passes in `phase1_iso704_scores.csv` were produced by the same model (Claude) reading the text directly, in two separate passes. Cohen's κ = **0.880** (93.3% simple agreement, n=30) therefore measures *rubric self-consistency*, not true human-vs-LLM agreement, treat it as a floor on reliability, not a validation of LLM-as-annotator against independent human judgment.

**Headline:** roughly **44–45% of descriptions in both corpora are genuinely intensional** (state a genus + differentiating characteristic per ISO 704), but the failure modes differ by corpus: IETF's problem is tautology (name-restatement, ~49%), TAPI's is literal boilerplate (~23% `"none"`) with a lower tautology rate. This is a more mixed picture than a simple "IETF good / TAPI bad" prior would predict, TAPI's *non-boilerplate* descriptions are if anything slightly more often intensional than IETF's.

### Duplicate descriptions (`phase1_duplicate_descriptions.csv`, 429 groups)

Both corpora show heavy reuse of identical description text across structurally-repeated groupings, e.g. IETF's "Strict or loose hop." appears 136 times (every `hop-type` leaf across all the different route-object types), TAPI's generic "The specific value."/"The specific unit of measurement of the capacity." patterns appear 60–120+ times each (characteristic of TAPI's heavily-templated capacity/characteristic value pattern). This isn't necessarily a defect, the *concept* (e.g. "a name, which carries no semantics") genuinely is identical everywhere it's reused, but it means description text alone often can't disambiguate two different reuse *sites* of the same grouping.

### Same-corpus semantic collisions (`phase1_collisions.csv`, TF-IDF cosine >0.85, 214 pairs after excluding same-named nodes)

All 214 IETF collisions found were between structurally-repeated substructures (`optimizations`, `path-metric`, `connectivity-matrix`) reused at different points in the `te-topology` tree (e.g. under `tunnel-termination-point/local-link-connectivities` vs. under `te-node-attributes/connectivity-matrices`), same grouping content, different scope. This is a real ambiguity mode: from description text alone, you cannot tell *which* connectivity-matrix's path-metric you're looking at; you need the path.

**This is a fundamentally different limit from anything Phase 2 tests, and worth naming precisely.** Phase 2 asks a *concept-level* question: given a node's description, can you tell **which lexicon concept** it represents? Text often can answer that (§2). This collision finding asks an *instance-level* question: given two nodes that are correctly classified as **the same concept**, can the text tell you **which occurrence** you're looking at? Here, text structurally cannot, not because the descriptions are poorly written, but because they're *byte-for-byte identical by construction*. The cleanest example in the corpus:

```
/networks/network/node/te/te-node-attributes/connectivity-matrices/optimizations
/networks/network/node/te/information-source-entry/connectivity-matrices/optimizations
```

Both carry the exact same description: *"The objective function container that includes attributes to impose when computing a TE path."* One is the `optimizations` container under a node's live, configured connectivity matrix; the other is under an `information-source-entry`, a different provenance/scope for effectively the same schema shape, reused via the same YANG grouping. The two are legitimately different things (different scope, different lifecycle, potentially different values), but the description text was never going to distinguish them, because it's the same string in both places by design.

The implication for "definitional anchoring" as a research question: solving concept-level anchoring (making descriptions intensional, disambiguating a node against a reference lexicon) does not solve instance-level disambiguation. No amount of LLM reasoning over description text recovers positional information the text never encoded, that information lives in the path (or some other structural signal: parent context, containing list key, `when`/`augment` target), not in prose. Any system built on this study's anchoring approach needs both: definitional text to resolve *what kind of thing* a node is, and structural/path context to resolve *which one*. Treating text-only anchoring as sufficient on its own will silently conflate distinct instances that happen to share a grouping.

### Cross-corpus separability (`phase1_cross_corpus_similarity.csv`, TF-IDF cosine >0.3, 536 pairs)

Note this reuses `sentence-transformers`'s declared fallback (TF-IDF) since `sentence-transformers` was not installed in this environment (pure lexical overlap, no semantic embedding). Under TF-IDF, **none** of the plan's headline trap-case nodes (`ietf-te-topology`'s `tunnel-termination-point`, `ietf-network-topology`'s `termination-point`) have *any* TAPI neighbor above the 0.3 threshold, IETF and TAPI use almost entirely disjoint vocabulary for the same concepts (e.g. IETF "termination point... refer to a port or an interface" vs. TAPI "NEPs belonging to / owned by this Node"). This is a negative result for lexical methods specifically, not necessarily for semantic understanding, it's the exact gap an LLM's world knowledge (rather than surface token overlap) would need to bridge, which is what Phase 2 tests directly.

---

## §2. Phase 2: name-only vs. definition-based LLM binding

### Methodology note: this run is genuinely blind

An earlier pass through this study (superseded, see git history) had the same agent that authored the gold standard also produce the "blind" predictions in the same conversation, a real contamination risk. **This version replaces that with 78 real, isolated tool-call invocations** (39 candidates × 2 modes), each a fresh model instance spun up via the `Agent` tool with no filesystem access and no visibility into this conversation or `data/gold/gold_standard.csv`. Each received only the literal prompt text `scripts/08_llm_binder.py` would send (lexicon block + node info) and answered independently, see `data/results/_real_bindings_results.csv` for the raw per-call outputs and `scripts/08_llm_binder.py`'s docstring for exactly how the prompts were constructed. This is a real blind evaluation, not a demonstration.

### Setup

12-entry lexicon (`data/lexicon/lexicon.yaml`), including the plan's two worked trap-case entries (LEX-002 `link-termination-point` vs. LEX-003 `service-anchor`) plus 9 more concepts grounded in terms actually observed in the corpus. 39-row gold standard (`data/gold/gold_standard.csv`, 22 IETF + 17 TAPI). One correction made before running the binder: the lexicon draft initially included `owned-node-edge-point`/`node-edge-point` as extra LEX-002 synonyms beyond the plan's original `[termination-point, port]`, which would have let name-only mode solve the TAPI trap case by trivial synonym lookup, removed before scoring.

(The gold standard itself and its second-annotator κ = 0.926 were still produced by me in-conversation, same as the ISO-704 rubric labels in §1, that limitation stands. What changed is the *binder*, which is now independent of both.)

### Correction round: two gold-standard errors and a lexicon boundary problem

The first blind run above scored name-only F1=0.98 against definition-based F1=0.84, eleven definition-based errors against name-only's one. Investigating *why* each of those eleven disagreed with gold (not just tallying them) surfaced three distinct, fixable problems, each addressed and re-tested via fresh isolated blind subagent calls (same methodology as the original 78, never hand-reasoned):

1. **Two gold-standard rows were wrong, not the binder.** `nsrlg`'s own source text says NSRLGs are groups underlay paths must be kept mutually *disjoint* across, the operational opposite of LEX-009's "shared risk, avoid double-use" definition; the lexical similarity ("risk group") masked an opposite semantic relationship. TAPI's `lifecycle-state` ("tracks planned deployment, allocation to clients, and withdrawal") is a provisioning-lifecycle concept, not LEX-011's in-service/out-of-service operator intent, a resource can be administratively in-service while its lifecycle-state is still planned. Both gold rows were corrected to `NONE` (full reasoning in `data/gold/gold_standard.csv`'s notes column); the original blind definition-based calls had already answered `NONE` on both, so this converts two definition-based "errors" into correct answers without any re-test needed.
2. **LEX-002/LEX-003/LEX-007 genuinely overlapped.** `link-termination-point`, `service-anchor`, and `client-access-point` all used variations of "boundary point... where traffic enters or leaves" with no explicit differentiator, close enough to confuse a careful blind reader. Rewritten in `data/lexicon/lexicon.yaml` with explicit cross-references (LEX-002 now states it's never client-facing and never tunnel/LSP-defined; LEX-003 is now scoped specifically to TE tunnel/LSP provisioning; LEX-007 is now scoped to the network's external client demarcation, contrasted against both).
3. **The binder prompt had no rule for attribute/template containers.** Four errors were `NONE` answers on nodes like `te-link-attributes` ("Link attributes in a TE topology") that are property bags for a lexicon entry, not instances of it, gold called these `subsumed_by`, but nothing in the prompt said containers of an entity should resolve that way rather than `NONE`. Added one explicit sentence to `scripts/08_llm_binder.py`'s `PROMPT`.

The 8 candidate rows affected by fixes 2 and 3 were re-sent to 8 fresh, independent, isolated subagents (no shared context with each other, gold, or this conversation) against the corrected lexicon and prompt. **7 of 8 flipped to correct.** The one that didn't, `cep-list/connection-end-point` ("The list of supported ConnectionEndPoint (CEP) instances."), still binds to LEX-002 rather than gold's LEX-007, because its source text never states whether the CEP faces the client or the network side of an adaptation; no lexicon wording can supply a fact the description doesn't contain. A ninth row, `supporting-termination-point`, was left untested for the same underlying reason: its description explains a *dependency relationship* between termination points, not what a termination point *is*, so neither the lexicon rewrite nor the prompt fix addresses its root cause. Both remain open errors, discussed below as **not correctable** within this study's scope.

**Caveat on this correction methodology:** the eleven rows re-investigated here were specifically the ones where the binder disagreed with gold, that's a real selection effect. Rows where both modes already agreed with gold were not symmetrically re-audited, so it's possible other gold rows carry similar errors that happened not to surface because the binder agreed with them anyway (right label, wrong reason, or gold and binder sharing the same unstated assumption). Treat the corrected results below as a cleaner run of the same experiment, not as proof the gold standard is now error-free.

### Results (`phase2_scores.csv`), post-correction

| mode | scope | n | precision | recall | F1 |
|---|---|---|---|---|---|
| name_only | equivalence_only | 26 | 0.880 | 0.957 | 0.917 |
| name_only | equivalence_plus_subsumption | 39 | 0.921 | 0.972 | 0.946 |
| name_only | recall_plus_nontrivial | 26 | 0.880 | 0.957 | 0.917 |
| definition_based | equivalence_only | 26 | 0.955 | 0.913 | 0.933 |
| definition_based | equivalence_plus_subsumption | 39 | 0.971 | 0.944 | 0.958 |
| definition_based | recall_plus_nontrivial | 26 | 0.955 | 0.913 | 0.933 |

**How to read this table.** `scripts/09_score_binding.py` computes proper detection-plus-classification precision and recall, the standard approach for tasks like named-entity recognition, where a system both has to notice something exists and get its label right. A wrong non-`NONE` guess is double-counted as both a false positive (a wrong answer was confidently asserted) and a false negative (the correct answer was missed), the standard NER/IE convention, rather than only counting against precision.

Per row, against gold: TP is the binder asserting the exact correct lexicon entry. FP is the binder confidently asserting a real lexicon entry that is wrong, whether gold wanted a different entry or no match at all. FN is gold wanting a real match and the binder not producing it, whether it said `NONE` or asserted a different wrong entry. TN is the binder correctly saying `NONE` when gold agrees. The three gold rows that genuinely should get `NONE` (`node-rule-group`, and, post-correction, `nsrlg` and `lifecycle-state`) are included in every scope, since correctly abstaining matters no matter how leniently subsumption is counted.

On the full 39-row set: **name-only made 3 errors (TP 35, FP 3, FN 1, TN 1); definition-based made 2 (TP 34, FP 1, FN 2, TN 3).** Definition-based now edges out name-only on F1 (0.958 vs. 0.946), a genuine but narrow result, not a landslide, and it only emerges after fixing two errors in *our own* gold standard and one construct-validity problem in *our own* lexicon. This is the opposite of the first run's inverted headline, but it should be read as "the study's instruments needed calibrating," not as "the model got better."

### What the remaining errors show

**Name-only's 3 remaining errors are now genuinely informative, not just curation noise.** All three are cases where a literal name/synonym match actively misleads: `nsrlg` matches the `LEX-009` synonym list verbatim but means the semantic opposite of shared-risk-group; `lifecycle-state` matches the `LEX-011` synonym list verbatim but names a different (provisioning-lifecycle) concept than administrative-state; `owned-node-edge-point` has no lexical overlap with LEX-002's synonyms at all and gets pulled toward LEX-007 by a different surface cue. In all three, definition-based mode (or gold, once corrected) got the semantics right precisely because it wasn't relying on string matching. That is a small but clean piece of positive evidence for the study's original thesis: name-only's genuine failure mode is trusting a name/synonym match that turns out to be a false friend.

**Definition-based's 2 remaining errors are genuinely not correctable within this study.** Both trace to source descriptions that are silent on the exact fact needed to disambiguate, `cep-list/connection-end-point`'s four-word description never says client-facing vs. network-facing; `supporting-termination-point`'s description explains a dependency relationship, not an identity. No lexicon rewrite or prompt change can supply information the YANG description itself doesn't contain, this is the clearest evidence in the whole study that *some* binding failures are a genuine property of the source text's semantic content, not of the binder or the reference lexicon.

### Trap-case detail (`phase2_trap_case_detail.csv`), the mechanism still holds, just not in aggregate

**Plan's original IETF trap** (`ietf-te-topology`'s `tunnel-termination-point`, gold = LEX-003): **both modes got this right**, because LEX-003's synonym list includes `tunnel-termination-point` verbatim (the plan's own worked example), name-only solves it by exact string match without needing the description.

**The TAPI trap that actually differentiates the two modes** (`tapi-topology`'s `owned-node-edge-point`, gold = LEX-002):
- name-only (real, blind): predicted **LEX-007** (`client-access-point`), wrong. (An earlier hand-simulated run guessed it would pick LEX-001 via the "node" substring; the real model's actual failure mode was different, which is itself a reminder that hand-simulating model behavior is not a substitute for calling the model.)
- definition-based (real, blind): predicted **LEX-002**, correct, at confidence 0.75. The description ("NEPs belonging to / owned by this Node... 'own' the NEPs") frames NEPs as boundary sub-components *owned by* a node, matching LEX-002's genus rather than any competing entry.

This one row remains the cleanest, fully-uncontaminated evidence for the draft's specific mechanism claim: when a corpus's naming convention (`NodeEdgePoint`) diverges entirely from the lexicon's vocabulary (`termination-point`), description text, not name, not synonym curation, is what recovers the correct binding. Post-correction, it is joined by two more cases with the same shape (`nsrlg`, `lifecycle-state`, both below), so it's no longer a single lucky win against a sea of losses, it's one instance of a pattern that shows up three times in 39 rows.

**The `nsrlg` and `lifecycle-state` negation cases, now scored correctly:** IETF's `nsrlg` node describes itself as "List of NSRLGs (**Non**-Shared Risk Link Groups)", the literal opposite of LEX-009's "shared risk group" definition. TAPI's `lifecycle-state` describes deployment-stage tracking, not administrative in/out-of-service intent. The real blind definition-based calls answered **NONE** on both at the time, correctly catching subtleties that the original gold standard (my own earlier judgment calls) papered over by force-matching anyway. Both gold rows are now corrected to `NONE`, converting what were scored as definition-based "misses" into correct answers, and turning name-only's confident, literal synonym match on both into name-only's own errors instead.

## §3. Verdict against §10 thresholds

The plan's §10 thresholds assume a single F1 number settles the question; the post-correction result still resists that framing, just less dramatically than the first pass did:

1. **Definition-based edges out name-only on F1 (0.958 vs. 0.946), but only after fixing instrumentation, not because the model changed.** Two of the original eleven "errors" were gold-standard mistakes (`nsrlg`, `lifecycle-state`); most of the rest traced to a lexicon boundary (LEX-002/003/007) written with overlapping language. Once both were corrected, seven of the eight retested rows flipped to correct. The remaining two errors (`cep-list/connection-end-point`, `supporting-termination-point`) are genuinely not fixable by lexicon or prompt changes, their source descriptions are silent on the fact needed to disambiguate.
2. **Name-only's remaining errors are now the more interesting result.** All three trace to a literal name or synonym match that turned out to be a false friend (`nsrlg`, `lifecycle-state`, `owned-node-edge-point`), cases where trusting the surface string actively produced the wrong answer. This is real, if narrow, support for the draft's core claim: a name can look like a match and mean something else, and description text is what catches that.
3. **What Phase 1 supports independently of any of this**: IETF descriptions are non-empty but nearly half tautological (49.3%); TAPI is ~23% literal `"none"` boilerplate but comparably-or-more intensional when present (45.3% vs. 44.0%). This half of the study has no blindness confound and is the more trustworthy finding on its own.
4. **What would make this result more robust**: build the lexicon *before* looking at the corpus (e.g. from an independent standards glossary) rather than sharpening it in response to observed errors, since the correction round here specifically targeted rows the binder disagreed with gold on and did not symmetrically re-audit rows where they agreed; and expand the gold standard well past 39 rows so a 2-to-5-error margin doesn't swing the aggregate F1 as much as it currently does.

## §4. What this execution deviated from in the plan, and why

- **Extraction** used the pyang Python API directly (`scripts/02_extract_descriptions.py`) instead of the CLI `-f flatten --flatten-description`, because the CLI plugin can't resolve cross-file augments (IETF's TE/OTN topology modules augment the base network/network-topology tree) when modules are passed one file at a time, and gives no way to attribute an augmented node to its true owning module. Verified against `i_module.arg` on live augmented nodes before trusting it.
- **Collision analysis** used the TF-IDF fallback, not `sentence-transformers` (not installed in this environment, kept optional per the plan).
- **Phase 2 binder** used 78 isolated `Agent`-tool subagent calls, each given only the literal prompt text (no tool/file access), rather than raw `anthropic` SDK calls against a real API key (none was available), functionally equivalent for blindness purposes, since each call starts with zero shared context. See `scripts/08_llm_binder.py` and `data/results/_real_bindings_results.csv`.
- ISO-704 rubric annotation (Phase 1) and gold-standard authoring/second-pass (Phase 2 setup) still have a single-agent-does-both-passes limitation; the reported κ values (0.880 and 0.926) should be read as self-consistency checks, not inter-annotator validation. This is now Phase 2's *only* remaining contamination risk, the binder itself is clean.
- **Post-hoc correction round**: after the first blind run, `data/gold/gold_standard.csv` was hand-edited to fix two rows (`nsrlg`, `lifecycle-state`) found to be semantically wrong on inspection, and `data/lexicon/lexicon.yaml`'s LEX-002/003/007 definitions were rewritten to sharpen an overlapping boundary. The 8 affected `DEFINITION_BASED` rows in `scripts/_phase2_bindings_data.py` were re-collected via 8 more isolated blind subagent calls against the corrected lexicon and prompt (marked `# RETEST` inline), not hand-edited. `scripts/09_score_binding.py`'s false-negative counting was also changed to double-count a wrong non-`NONE` guess as both FP and FN (the standard NER/IE convention), which it did not do before. All three changes are why the numbers in §2 differ from the first blind run's; see §2's "Correction round" subsection for the full reasoning and its selection-effect caveat.
