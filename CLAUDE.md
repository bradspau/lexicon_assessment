# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

This repository currently contains only a plan document, `CLAUDE_PLAN_yang_anchoring_study.md`. No project dependencies or `requirements.txt` exist yet, and none of the scaffold described below has been created yet. There is no git repo initialized.

When asked to build or continue this project, treat `CLAUDE_PLAN_yang_anchoring_study.md` as the spec and execute it step by step rather than re-deriving the design.

## What this project is

An empirical study testing whether YANG `description` statements in network-management data models (IETF topology/TE modules vs. ONF TAPI modules) support LLM-based "definitional anchoring" — i.e., whether an LLM can correctly bind a data-model node to the right entry in a hand-built reference lexicon using its `description` text, versus using only the node's name. The output is a precision/recall/F1 comparison (name-only vs. definition-based binding) scored against a manually curated gold standard, plus a Phase 1 quality/collision audit of the descriptions themselves.

Full methodology, scripts, and exact commands live in `CLAUDE_PLAN_yang_anchoring_study.md` — read it in full before starting work. Key structure:

- **Phase 1 (steps 1–5):** fetch YANG corpus (IETF + TAPI modules, pinned by revision in `config/modules.yaml`) → extract `(module, path, node-type, description)` tuples via `pyang -f flatten` (with a fallback custom pyang plugin if the flatten flags aren't available) → quality audit (coverage, boilerplate %, name-restatement %, ISO-704 definitional rubric) → semantic-collision analysis (embedding/TF-IDF cosine similarity between same-corpus descriptions) → assemble `report/FINDINGS.md` §1.
- **Phase 2 (steps 6–11):** hand-author a reference lexicon (`data/lexicon/lexicon.yaml`, ~10–15 entries, deliberately including name/definition "trap cases" like `tunnel-termination-point` vs `link-termination-point`) → build a manually-labeled gold standard (`data/gold/gold_standard.csv`) → run an LLM binder (`anthropic` SDK) in `name_only` vs `definition_based` prompt modes → score against gold with precision/recall/F1, including a trap-case-specific breakdown.
- **Step 12:** final write-up in `report/FINDINGS.md`, interpreted against the sanity thresholds in plan §10.

## Working conventions from the plan

- Every numbered step in the plan has an explicit script name (`scripts/01_fetch_corpus.py` … `09_score_binding.py`) and a concrete output artifact under `data/` or `report/` — follow that naming when creating scripts so outputs stay traceable to the step that produced them.
- Steps 7 (gold standard) and part of step 3 (ISO-704 rubric labels) are explicitly manual/expert-judgment steps — only script the scaffolding (candidate filtering, CSV templates, Cohen's κ agreement calc), not the labeling itself.
- pyang needs `-p corpus/ietf:corpus/tapi` on its path even when only extracting descriptions, to resolve imports (`ietf-yang-types`, `ietf-inet-types`, `ietf-te-types`, TAPI's own transitive imports) — otherwise `-f flatten` emits import-resolution warnings. Fetch dependency modules into the corpus dirs, not just the top-level modules listed in `config/modules.yaml`.
- Before trusting `pyang -f flatten --flatten-description`, run `pyang -f flatten --help` once to confirm the installed pyang version's flag names match the plan (drift here is expected across pyang versions).
- The OTN topology draft module has no stable URL yet (see plan §1.2) — resolving it is a one-time manual step (GitHub contents API lookup, or Datatracker HTML extraction as fallback since Datatracker may not be in the sandbox's allowlisted network config).
- When running the LLM binder (step 8), the model string in the plan (`claude-sonnet-5`) may need updating to whatever model the environment actually exposes.
- Validate the LLM as an ISO-704 rubric annotator (step 3) by computing Cohen's κ between LLM labels and a 30-node manually-labeled subset before trusting LLM labels on the full sample.

## Setup

No `requirements.txt` exists yet — create it per plan §"requirements.txt" (`pyang==2.7.1`, `pyyaml`, `requests`, `pandas`, `scikit-learn`, `sentence-transformers` optional, `anthropic`). Install into a local venv (e.g. `.venv`, Python 3.10):

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```
