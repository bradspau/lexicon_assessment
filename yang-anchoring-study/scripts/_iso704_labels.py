# Hand/LLM-assigned ISO-704 rubric labels for the 150-node stratified sample
# (data/results/phase1_iso704_sample.csv), in row order. This is annotation
# data, not a heuristic -- each label reflects a reading of the actual
# description text against the 4-way rubric (intensional /
# extensional_example_only / circular_tautological / empty_boilerplate).
#
# LLM_LABELS: full-sample pass (all 150 rows, "llm" annotator)
# MANUAL_LABELS: independent second pass over the first 30 rows only
#   ("manual" annotator), used to compute Cohen's kappa against the llm
#   pass on the overlapping subset per plan step 3.

LLM_LABELS = [
    "intensional", "intensional", "intensional", "circular_tautological", "circular_tautological",
    "intensional", "circular_tautological", "intensional", "circular_tautological", "intensional",
    "circular_tautological", "circular_tautological", "circular_tautological", "extensional_example_only", "circular_tautological",
    "intensional", "extensional_example_only", "intensional", "circular_tautological", "intensional",
    "circular_tautological", "intensional", "circular_tautological", "circular_tautological", "intensional",
    "intensional", "circular_tautological", "circular_tautological", "intensional", "circular_tautological",
    "circular_tautological", "extensional_example_only", "circular_tautological", "intensional", "intensional",
    "circular_tautological", "circular_tautological", "circular_tautological", "circular_tautological", "circular_tautological",
    "intensional", "circular_tautological", "circular_tautological", "intensional", "intensional",
    "circular_tautological", "circular_tautological", "intensional", "intensional", "intensional",
    "intensional", "intensional", "intensional", "circular_tautological", "intensional",
    "circular_tautological", "intensional", "circular_tautological", "circular_tautological", "extensional_example_only",
    "intensional", "circular_tautological", "intensional", "circular_tautological", "circular_tautological",
    "intensional", "intensional", "extensional_example_only", "circular_tautological", "circular_tautological",
    "intensional", "intensional", "circular_tautological", "intensional", "circular_tautological",
    "circular_tautological", "intensional", "circular_tautological", "circular_tautological", "circular_tautological",
    # 75-149 (tapi)
    "intensional", "intensional", "circular_tautological", "intensional", "intensional",
    "empty_boilerplate", "empty_boilerplate", "empty_boilerplate", "intensional", "intensional",
    "intensional", "circular_tautological", "empty_boilerplate", "intensional", "empty_boilerplate",
    "circular_tautological", "intensional", "circular_tautological", "intensional", "circular_tautological",
    "empty_boilerplate", "empty_boilerplate", "empty_boilerplate", "circular_tautological", "intensional",
    "circular_tautological", "empty_boilerplate", "intensional", "intensional", "intensional",
    "intensional", "intensional", "intensional", "intensional", "intensional",
    "circular_tautological", "intensional", "empty_boilerplate", "circular_tautological", "empty_boilerplate",
    "circular_tautological", "intensional", "empty_boilerplate", "intensional", "intensional",
    "intensional", "circular_tautological", "circular_tautological", "empty_boilerplate", "intensional",
    "circular_tautological", "empty_boilerplate", "circular_tautological", "circular_tautological", "empty_boilerplate",
    "circular_tautological", "circular_tautological", "intensional", "circular_tautological", "intensional",
    "empty_boilerplate", "intensional", "intensional", "circular_tautological", "intensional",
    "intensional", "intensional", "intensional", "empty_boilerplate", "circular_tautological",
]

MANUAL_LABELS_FIRST_30 = [
    "intensional", "intensional", "intensional", "circular_tautological", "circular_tautological",
    "circular_tautological", "circular_tautological", "intensional", "circular_tautological", "intensional",
    "circular_tautological", "intensional", "circular_tautological", "extensional_example_only", "circular_tautological",
    "intensional", "extensional_example_only", "intensional", "circular_tautological", "intensional",
    "circular_tautological", "intensional", "circular_tautological", "circular_tautological", "intensional",
    "intensional", "circular_tautological", "circular_tautological", "intensional", "circular_tautological",
]

assert len(LLM_LABELS) == 150, len(LLM_LABELS)
assert len(MANUAL_LABELS_FIRST_30) == 30, len(MANUAL_LABELS_FIRST_30)
