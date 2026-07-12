# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

The study is built and executed. `yang-anchoring-study/` contains the full pipeline (`scripts/`), fetched corpus (`corpus/`), all intermediate and final data (`data/`), and the write-up (`report/FINDINGS.md`). Git is initialized and pushed to `github.com/bradspau/lexicon_assessment` (remote `origin`, branch `main`).

`CLAUDE_PLAN_yang_anchoring_study.md` is still the original spec — useful for understanding *why* a script exists — but it does not reflect what actually happened. For that, read **`yang-anchoring-study/README.md`** first: it documents what's a straight reproducible measurement (Phase 1) versus what required LLM judgment and how blind that judgment actually was (Phase 2), which numbers can be cited and which can't. `yang-anchoring-study/report/FINDINGS.md` has the full results and discussion.

If asked to extend or re-run part of this study, don't re-derive the pipeline from the plan — read the existing scripts and README first; the deviations from the plan (below) were deliberate and re-implementing from the plan text alone will reintroduce bugs that are already fixed.

## What this project is

An empirical study testing whether YANG `description` statements in network-management data models (IETF topology/TE modules vs. ONF TAPI modules) support LLM-based "definitional anchoring" — i.e., whether an LLM can correctly bind a data-model node to the right entry in a hand-built reference lexicon using its `description` text, versus using only the node's name. The output is a precision/recall/F1 comparison (name-only vs. definition-based binding) scored against a manually curated gold standard, plus a Phase 1 quality/collision audit of the descriptions themselves.

- **Phase 1:** fetch YANG corpus (IETF + TAPI modules, pinned by revision in `config/modules.yaml`) → extract `(module, path, node-type, description)` tuples → quality audit (coverage, boilerplate %, name-restatement %, ISO-704 definitional rubric) → semantic-collision analysis (TF-IDF cosine similarity between same-corpus descriptions) → `report/FINDINGS.md` §1.
- **Phase 2:** hand-authored reference lexicon (`data/lexicon/lexicon.yaml`, 12 entries) → hand-authored gold standard (`data/gold/gold_standard.csv`, 39 rows) → LLM binder in `name_only` vs `definition_based` prompt modes → precision/recall/F1 against gold, with a trap-case-specific breakdown.
- Result, real and blind (see "Working conventions" below): name-only F1=0.98, definition-based F1=0.84 — the opposite of the naive hypothesis, and not the whole story. Read `report/FINDINGS.md` §2–3 before citing either number; most of definition-based's errors trace to overlapping lexicon definitions or genuinely tautological source descriptions, not a binder failure.

## Working conventions from the plan and its execution

- Every numbered step in the plan has an explicit script name (`scripts/01_fetch_corpus.py` … `09_score_binding.py`) and a concrete output artifact under `data/` or `report/` — follow that naming when adding scripts so outputs stay traceable to the step that produced them.
- `scripts/07_build_gold_standard.py` only regenerates the candidate pool and the second-annotator κ check. The gold standard itself, plus the ISO-704 rubric labels, are **hand-authored data**, not script output: `scripts/_gold_standard_data.py`, `scripts/_iso704_labels.py`, `scripts/_phase2_bindings_data.py` are `_`-prefixed for exactly this reason — read them as recorded judgments to audit, not pipeline logic to blindly trust or "fix."
- **Extraction deviates from the plan's primary approach.** `scripts/02_extract_descriptions.py` uses the pyang Python API directly instead of the CLI `-f flatten --flatten-description`, because the CLI plugin can't resolve cross-file augments (IETF's TE/OTN topology modules augment the base `ietf-network`/`ietf-network-topology` tree) when modules are passed one file at a time, and gives no way to attribute an augmented node to its true owning module. It uses `i_module.arg` per-statement for correct ownership — verify against a live augmented node before trusting any change here.
- pyang needs `-p corpus/ietf:corpus/tapi` on its path even when only extracting descriptions, to resolve imports. Dependency modules (`ietf-yang-types`, `ietf-inet-types`, `ietf-te-types`, TAPI's transitive imports) live in the corpus dirs alongside the top-level modules for this reason — don't remove them thinking they're unused.
- The OTN topology draft module has no stable pinned URL — it was resolved via a one-time GitHub contents API lookup (see `config/modules.yaml` comments); re-resolve if the corpus needs refreshing.
- **No `ANTHROPIC_API_KEY` is available in this environment.** For Phase 2's LLM binder, this doesn't mean falling back to hand-simulated judgments — that was tried once, found to be contaminated (gold-standard author == the "blind" judge, same conversation), and replaced. The current approach: spawn one isolated `Agent`-tool subagent per binding decision (78 total: 39 candidates × 2 modes), each with no filesystem access and no visibility into this conversation or `data/gold/gold_standard.csv`, given only the literal prompt text. This is a genuinely blind evaluation without needing an API key — reuse this pattern for any future LLM-judgment step in this repo rather than reasoning through prompts by hand.
- **Known fixed bug:** `scripts/08_llm_binder.py` used to merge the *entire* gold-standard frame (including gold's own `relation` column) against predictions. Pandas' `suffixes=("", "_pred")` let gold's `relation` silently shadow the predicted one in the output CSV — didn't affect scoring (which only compares `lexicon_id`) but corrupted the `relation` metadata. Fixed by merging only `[corpus, module, path]` from gold as filter keys. If you touch this script, keep predictions and gold-standard columns from ever having the same name pre-merge.
- Cohen's κ values reported in `FINDINGS.md` (0.880, 0.926) are **self-consistency checks**, not inter-annotator validation — both passes being compared were authored by the same agent in the same session. Only the 78 Phase 2 binder predictions are genuinely independent of the gold standard.
- **Known fixed bug, second instance:** `scripts/09_score_binding.py` used to compute precision via `sklearn.metrics.precision_recall_fscore_support([1]*len(d), y_true, ...)`, an all-1s true-label array that makes precision mathematically pinned at 1.0 no matter how good or bad the binder is (no row can ever produce a false positive). Fixed with direct TP/FP/FN counting. If you touch this script, don't feed sklearn a constant true-label array again.
- **F1 alone won't catch a broken precision/recall computation.** F1 was numerically identical before and after the fix above, a coincidence of the algebra (`F1 = 2×TP/(2×TP+FP+FN)`, invariant to how "wrong" splits between FP and FN), not evidence the old scoring was fine. When auditing metrics code here, check precision and recall individually, not just F1.

## Write-up style

Australian English spelling. No em dashes in prose, use a comma instead. Applies to `FINDINGS.md`, `README.md`, and similar write-ups in this repo — existing em dashes from before this convention was set are not yet swept, don't treat their presence elsewhere as license to add more.

## Setup

```bash
python3 -m venv .venv && .venv/bin/pip install -r yang-anchoring-study/requirements.txt
```

Then see `yang-anchoring-study/README.md` → "Running it" for the pipeline commands (run from within `yang-anchoring-study/`, venv referenced as `../.venv`).
