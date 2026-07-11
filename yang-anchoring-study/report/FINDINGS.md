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

### Cross-corpus separability (`phase1_cross_corpus_similarity.csv`, TF-IDF cosine >0.3, 536 pairs)

Note this reuses `sentence-transformers`'s declared fallback (TF-IDF) since `sentence-transformers` was not installed in this environment (pure lexical overlap, no semantic embedding). Under TF-IDF, **none** of the plan's headline trap-case nodes (`ietf-te-topology`'s `tunnel-termination-point`, `ietf-network-topology`'s `termination-point`) have *any* TAPI neighbor above the 0.3 threshold — IETF and TAPI use almost entirely disjoint vocabulary for the same concepts (e.g. IETF "termination point... refer to a port or an interface" vs. TAPI "NEPs belonging to / owned by this Node"). This is a negative result for lexical methods specifically, not necessarily for semantic understanding — it's the exact gap an LLM's world knowledge (rather than surface token overlap) would need to bridge, which is what Phase 2 tests directly.

---

## §2. Phase 2: name-only vs. definition-based LLM binding

### Methodology caveat (read this first)

**This is not a blind evaluation.** The plan's step 8 calls for an `anthropic` API call per binding decision; no `ANTHROPIC_API_KEY` was available in this environment, so the binding judgments in `data/results/phase2_bindings_raw.csv` were produced by direct reasoning (by me, Claude) against the exact same prompts the script would have sent — see `scripts/08_llm_binder.py` for the byte-for-byte prompt construction and a printed example of both prompt variants. Critically, **the same agent that hand-authored the gold standard** (`data/gold/gold_standard.csv`, step 7) **also produced these bindings, in the same conversation**, minutes apart. There is no way to guarantee the binding judgments weren't influenced by already having written the "correct" answers. Treat the numbers below as a **worked demonstration of the pipeline and mechanism**, not as an unbiased capability estimate of "LLMs binding via description text" in general — a genuine test of that claim requires a fresh model instance (or a separate API-key-driven run) that never saw the gold standard.

### Setup

12-entry lexicon (`data/lexicon/lexicon.yaml`), including the plan's two worked trap-case entries (LEX-002 `link-termination-point` vs. LEX-003 `service-anchor`) plus 9 more concepts grounded in terms actually observed in the corpus. 39-row gold standard (`data/gold/gold_standard.csv`, 22 IETF + 17 TAPI), second-annotator κ = **0.926** (93.3% agreement, n=15) — again same-agent self-consistency, not independent validation (see same caveat above).

One correction made before running the binder: the lexicon draft initially included `owned-node-edge-point`/`node-edge-point` as extra LEX-002 synonyms beyond the plan's original `[termination-point, port]`. That would have let name-only mode solve the TAPI trap case by trivial synonym lookup, defeating its purpose — removed before scoring (`data/lexicon/lexicon.yaml` now matches the plan's original synonym list for LEX-002).

### Results (`phase2_scores.csv`)

| mode | scope | n | precision | recall | F1 |
|---|---|---|---|---|---|
| name_only | equivalence_only | 25 | 1.0 | 0.920 | 0.958 |
| name_only | equivalence_plus_subsumption | 38 | 1.0 | 0.947 | 0.973 |
| name_only | recall_plus_nontrivial | 25 | 1.0 | 0.920 | 0.958 |
| definition_based | equivalence_only | 25 | 1.0 | 1.000 | 1.000 |
| definition_based | equivalence_plus_subsumption | 38 | 1.0 | 1.000 | 1.000 |
| definition_based | recall_plus_nontrivial | 25 | 1.0 | 1.000 | 1.000 |

Both modes score far above the OAEI reference band (§10 threshold: 0.6–0.7 clears "empirically supported"). This is expected and not very informative on its own given the non-blindness caveat above — what's more informative is *where* name-only fails and *whether the definition text is what fixes it*, which the trap-case detail speaks to directly.

### Trap-case detail (`phase2_trap_case_detail.csv`)

**Plan's original IETF trap** (`ietf-te-topology`'s `tunnel-termination-point`, expected gold = LEX-003 not LEX-002): **both modes got this right.** On inspection, this is because the lexicon's own synonym list for LEX-003 includes `tunnel-termination-point` verbatim (per the plan's original worked example) — so even name-only mode, given the full synonym list, can resolve it by exact string match without needing the description at all. This is a real, useful negative finding: **a well-curated synonym list can close the gap that description text was supposed to fill**, at least for single-token trap cases. It suggests the draft's "definitions matter" claim is strongest specifically when synonym curation *can't* anticipate every real-world name variant.

**The TAPI trap that actually differentiates the two modes** (`tapi-topology`'s `owned-node-edge-point`, gold = LEX-002 `link-termination-point`):
- name-only: predicted **LEX-001** (`forwarding-element`) — wrong. With no synonym overlap with LEX-002 at all (`owned-node-edge-point` shares no token with `termination-point`/`port`), the dominant lexical signal is the substring `node`, pulling the guess toward LEX-001.
- definition-based: predicted **LEX-002** — correct. The actual description ("The NEPs belonging to / owned by this Node... only Node instances... 'own' the NEPs") explicitly frames NEPs as boundary sub-components *owned by* a node, matching LEX-002's genus ("a boundary point *on* a forwarding element") rather than LEX-001's genus (the forwarding element itself).

This single row is the cleanest evidence in the study for the draft's mechanism: not "any description helps" but specifically that **when a corpus's naming convention diverges from the lexicon's (TAPI's "NodeEdgePoint" vs. IETF-style "termination-point"), description text is what recovers the correct binding, and synonym curation alone cannot be relied on to anticipate every naming convention.**

A secondary miss appeared outside the two designed traps: `tapi-common`'s `/context/service-interface-point` (gold = LEX-007 `client-access-point`) was bound to LEX-006 (`service`) under name-only (no exact synonym for "service-interface-point"; the dominant token "service" pulled toward LEX-006) but correctly to LEX-007 under definition-based. This wasn't planned as a trap — it emerged from the real corpus — and reinforces the same pattern.

One near-miss worth flagging even though it *did* score correct: IETF's `nsrlg` node describes itself as "List of NSRLGs (**Non**-Shared Risk Link Groups)" — the literal opposite framing from LEX-009's definition of a *shared* risk group. Both the gold standard and the binder judgment call this LEX-009 (the only risk-grouping concept available), but a maximally rigorous ISO-704 comparison would flag the shared/non-shared inversion as a definitional mismatch rather than a clean equivalence. This is a real limit on how far surface-level definition matching can go — it doesn't catch logical negation.

## §3. Verdict against §10 thresholds

Per the plan's own framing, this is not a case where the raw F1 numbers (both ≥0.92, one at 1.0) can be taken as "clears 0.6–0.7 → draft supported" in the way a genuinely blind study would license — the non-blindness caveat in §2 means these numbers overstate confidence. What the study **does** support, at the level of a worked mechanism demonstration:

1. **Phase 1** is the more trustworthy half of this run (no blindness issue — it's a direct measurement of the corpus, not a judgment call graded against the same judge's own key). Real, contrasting quality profiles: IETF descriptions are non-empty but nearly half tautological (49.3%); TAPI descriptions are ~23% literal boilerplate (`"none"`) but comparably or more often genuinely intensional when present (45.3% vs. IETF's 44.0%). Neither corpus supports a simple "coverage is fine, don't worry about it" prior, nor a simple "descriptions are all boilerplate" prior — the failure mode differs by corpus and needs corpus-specific remediation (TAPI: fill in the `"none"` placeholders; IETF: rewrite tautological name-echoes into real definitions).
2. **Phase 2's mechanism, row by row, is real and legible**: the one case in this run where name-only and definition-based genuinely diverge (`owned-node-edge-point`) diverges for exactly the reason the draft predicts — description text carries the boundary-point-owned-by-node relationship that the bare name doesn't. But this run only produced *two* such naturally-occurring divergences out of 39 candidates (one designed, one emergent), which is a thin evidence base for a population-level F1 claim, independent of the blindness problem.
3. **To actually validate or refute the draft's claim with the rigor step 10 calls for**, this study needs to be re-run with real `anthropic` API calls (or at minimum a fresh model instance with no visibility into the gold standard) — ideally with a larger gold standard (the plan's 30–60 row target was met at the low end, 39) so the trap-case rate is estimated from more than one or two naturally-occurring examples rather than mostly-designed cases.

## §4. What this execution deviated from in the plan, and why

- **Extraction** used the pyang Python API directly (`scripts/02_extract_descriptions.py`) instead of the CLI `-f flatten --flatten-description`, because the CLI plugin can't resolve cross-file augments (IETF's TE/OTN topology modules augment the base network/network-topology tree) when modules are passed one file at a time, and gives no way to attribute an augmented node to its true owning module. Verified against `i_module.arg` on live augmented nodes before trusting it.
- **Collision analysis** used the TF-IDF fallback, not `sentence-transformers` (not installed in this environment — kept optional per the plan).
- **Phase 2 binder** used direct reasoning instead of `anthropic` API calls (no key available) — see the methodology caveat in §2, which is the single most important thing to read before citing this study's Phase 2 numbers.
- Both ISO-704 rubric annotation (Phase 1) and gold-standard second-pass annotation (Phase 2 setup) have the same single-agent-does-both-passes limitation; the reported κ values (0.880 and 0.926) should be read as self-consistency checks, not inter-annotator validation.
