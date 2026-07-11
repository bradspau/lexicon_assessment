# Real LLM binder output (plan step 8), collected via 78 independent,
# isolated subagent tool calls (39 candidates x 2 modes) -- NOT hand-reasoned.
#
# Each call was a fresh model instance with no filesystem access and no
# visibility into this conversation or data/gold/gold_standard.csv, given
# only the literal prompt text scripts/08_llm_binder.py constructs (lexicon
# block + node info). This is a genuine blind evaluation: the model that
# produced these predictions never saw the gold labels. Raw per-call outputs
# (with agent task IDs implicit in collection order) are preserved in
# data/results/_real_bindings_results.csv.
#
# NAME_ONLY: given only "Node path" + "Node name" + lexicon (id,
#   preferred_name, synonyms) -- no description, no lexicon definitions.
# DEFINITION_BASED: given "Node path" + full description + lexicon (id,
#   preferred_name, definition) -- no synonyms shown.
#
# Headline (see report/FINDINGS.md §2-3 for the full breakdown, which
# matters more than these two numbers): name_only 38/39 correct (F1=0.98),
# definition_based 28/39 correct (F1=0.84). Definition-based's errors are
# NOT random noise -- 7 of 11 are appropriately cautious NONE refusals on
# cases where the hand-authored gold label was arguably too generous, and
# most of the rest cluster on three lexicon entries (LEX-002/003/007) whose
# definitions overlap enough to confuse a careful blind reader. Name-only's
# high score is largely an artifact of synonym lists having been curated
# from the corpus itself. Don't cite the bare F1 numbers without that context.

NAME_ONLY = [
    ("ietf", "ietf-network", "/networks/network/node", "LEX-001", "equivalent", 0.95),
    ("ietf", "ietf-network-topology", "/networks/network/node/termination-point", "LEX-002", "equivalent", 0.95),
    ("ietf", "ietf-network-topology", "/networks/network/link", "LEX-004", "equivalent", 0.95),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/tunnel-termination-point", "LEX-003", "equivalent", 0.95),
    ("ietf", "ietf-network-topology", "/networks/network/node/termination-point/supporting-termination-point", "LEX-002", "equivalent", 0.75),
    ("ietf", "ietf-otn-topology", "/networks/network/node/termination-point/te/client-svc", "LEX-007", "equivalent", 0.9),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-attributes/connectivity-matrices/underlay/tunnels/tunnel", "LEX-006", "equivalent", 0.85),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-attributes/connectivity-matrices/path-constraints", "LEX-008", "equivalent", 0.85),
    ("ietf", "ietf-te-topology", "/networks/network/te/nsrlg", "LEX-009", "equivalent", 0.97),
    ("ietf", "ietf-otn-topology", "/networks/network/node/termination-point/te/interface-switching-capability/max-lsp-bandwidth/te-bandwidth/technology/otn-bandwidth/odu-type", "LEX-010", "equivalent", 0.97),
    ("ietf", "ietf-te-topology", "/networks/network/node/termination-point/te/admin-status", "LEX-011", "equivalent", 0.95),
    ("ietf", "ietf-te-topology", "/networks/network/node/termination-point/te/oper-status", "LEX-012", "equivalent", 0.95),
    ("ietf", "ietf-te-topology", "/networks/network/link/te/te-link-attributes", "LEX-004", "subsumed_by", 0.62),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-attributes", "LEX-001", "subsumed_by", 0.75),
    ("ietf", "ietf-otn-topology", "/networks/network/link/te/te-link-attributes/otn-link", "LEX-004", "subsumed_by", 0.6),
    ("ietf", "ietf-otn-topology", "/networks/network/node/te/te-node-attributes/otn-node", "LEX-001", "subsumed_by", 0.65),
    ("ietf", "ietf-network-topology", "/networks/network/link/supporting-link", "LEX-004", "subsumed_by", 0.7),
    ("ietf", "ietf-te-topology", "/networks/network/link/te/bundle-stack-level/bundled-links/bundled-link", "LEX-004", "subsumed_by", 0.6),
    ("ietf", "ietf-te-topology", "/networks/network/link/te/bundle-stack-level/component-links/component-link", "LEX-004", "subsumed_by", 0.55),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-template", "LEX-001", "subsumed_by", 0.62),
    ("ietf", "ietf-te-topology", "/networks/network/link/te/te-link-template", "LEX-004", "subsumed_by", 0.6),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-attributes/connectivity-matrices/path-constraints/path-srlgs-lists/path-srlgs-list", "LEX-009", "equivalent", 0.95),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node", "LEX-001", "equivalent", 0.9),
    # TRAP: name-only has no synonym overlap with LEX-002; real blind failure mode was LEX-007, not the "node"-substring guess a hand simulation might expect
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/owned-node-edge-point", "LEX-007", "equivalent", 0.65),
    ("tapi", "tapi-topology", "/context/topology-context/topology/link", "LEX-004", "equivalent", 0.97),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service", "LEX-006", "equivalent", 0.95),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/end-point", "LEX-007", "equivalent", 0.72),
    ("tapi", "tapi-connectivity", "/context/topology-context/topology/node/owned-node-edge-point/cep-list/connection-end-point", "LEX-007", "equivalent", 0.95),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/connectivity-constraint", "LEX-008", "equivalent", 0.75),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/routing-constraint", "LEX-008", "equivalent", 0.95),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/topology-constraint", "LEX-008", "equivalent", 0.95),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/node-rule-group/risk-characteristic", "LEX-009", "equivalent", 0.9),
    ("tapi", "tapi-topology", "/context/topology-context/topology/link/layer-protocol-name", "LEX-005", "equivalent", 0.95),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/owned-node-edge-point/layer-protocol-name", "LEX-005", "equivalent", 0.95),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/owned-node-edge-point/operational-state", "LEX-012", "equivalent", 0.98),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/owned-node-edge-point/lifecycle-state", "LEX-011", "equivalent", 0.85),
    ("tapi", "tapi-common", "/context/service-interface-point", "LEX-007", "equivalent", 0.62),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/node-rule-group", "NONE", "none", 0.85),
    ("tapi", "tapi-path-computation", "/context/path-computation-context/path/link", "LEX-004", "equivalent", 0.95),
]

DEFINITION_BASED = [
    ("ietf", "ietf-network", "/networks/network/node", "LEX-001", "equivalent", 0.83),
    ("ietf", "ietf-network-topology", "/networks/network/node/termination-point", "LEX-002", "subsumes", 0.72),
    ("ietf", "ietf-network-topology", "/networks/network/link", "LEX-004", "equivalent", 0.9),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/tunnel-termination-point", "LEX-003", "equivalent", 0.62),
    ("ietf", "ietf-network-topology", "/networks/network/node/termination-point/supporting-termination-point", "NONE", "none", 0.62),
    ("ietf", "ietf-otn-topology", "/networks/network/node/termination-point/te/client-svc", "LEX-002", "subsumed_by", 0.45),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-attributes/connectivity-matrices/underlay/tunnels/tunnel", "LEX-006", "subsumed_by", 0.4),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-attributes/connectivity-matrices/path-constraints", "LEX-008", "equivalent", 0.72),
    # nsrlg: real blind call correctly caught the "Non-Shared" vs "shared risk group" inversion and refused, rather than force-matching like gold did
    ("ietf", "ietf-te-topology", "/networks/network/te/nsrlg", "NONE", "none", 0.75),
    ("ietf", "ietf-otn-topology", "/networks/network/node/termination-point/te/interface-switching-capability/max-lsp-bandwidth/te-bandwidth/technology/otn-bandwidth/odu-type", "LEX-010", "equivalent", 0.87),
    ("ietf", "ietf-te-topology", "/networks/network/node/termination-point/te/admin-status", "LEX-011", "equivalent", 0.9),
    ("ietf", "ietf-te-topology", "/networks/network/node/termination-point/te/oper-status", "LEX-012", "equivalent", 0.92),
    ("ietf", "ietf-te-topology", "/networks/network/link/te/te-link-attributes", "NONE", "none", 0.85),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-attributes", "LEX-001", "subsumed_by", 0.4),
    ("ietf", "ietf-otn-topology", "/networks/network/link/te/te-link-attributes/otn-link", "LEX-004", "subsumed_by", 0.55),
    ("ietf", "ietf-otn-topology", "/networks/network/node/te/te-node-attributes/otn-node", "LEX-001", "equivalent", 0.62),
    ("ietf", "ietf-network-topology", "/networks/network/link/supporting-link", "LEX-004", "subsumed_by", 0.55),
    ("ietf", "ietf-te-topology", "/networks/network/link/te/bundle-stack-level/bundled-links/bundled-link", "LEX-004", "subsumed_by", 0.5),
    ("ietf", "ietf-te-topology", "/networks/network/link/te/bundle-stack-level/component-links/component-link", "NONE", "none", 0.6),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-template", "NONE", "none", 0.95),
    ("ietf", "ietf-te-topology", "/networks/network/link/te/te-link-template", "NONE", "none", 0.95),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-attributes/connectivity-matrices/path-constraints/path-srlgs-lists/path-srlgs-list", "LEX-009", "equivalent", 0.72),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node", "LEX-001", "equivalent", 0.75),
    # trap resolved correctly under a real blind call: description explains NEPs are boundary points OWNED BY the node, matching LEX-002's
    # genus ("a boundary point on a forwarding element") rather than LEX-001 ("the forwarding element itself")
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/owned-node-edge-point", "LEX-002", "equivalent", 0.75),
    ("tapi", "tapi-topology", "/context/topology-context/topology/link", "LEX-004", "equivalent", 0.9),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service", "LEX-006", "equivalent", 0.83),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/end-point", "LEX-003", "equivalent", 0.78),
    ("tapi", "tapi-connectivity", "/context/topology-context/topology/node/owned-node-edge-point/cep-list/connection-end-point", "LEX-002", "subsumed_by", 0.45),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/connectivity-constraint", "LEX-008", "equivalent", 0.75),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/routing-constraint", "LEX-008", "equivalent", 0.75),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/topology-constraint", "LEX-008", "equivalent", 0.62),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/node-rule-group/risk-characteristic", "LEX-009", "subsumed_by", 0.62),
    ("tapi", "tapi-topology", "/context/topology-context/topology/link/layer-protocol-name", "LEX-005", "subsumed_by", 0.55),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/owned-node-edge-point/layer-protocol-name", "LEX-005", "equivalent", 0.7),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/owned-node-edge-point/operational-state", "LEX-012", "equivalent", 0.97),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/owned-node-edge-point/lifecycle-state", "NONE", "none", 0.7),
    ("tapi", "tapi-common", "/context/service-interface-point", "LEX-003", "equivalent", 0.75),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/node-rule-group", "NONE", "none", 0.95),
    ("tapi", "tapi-path-computation", "/context/path-computation-context/path/link", "LEX-004", "equivalent", 0.75),
]

assert len(NAME_ONLY) == 39, len(NAME_ONLY)
assert len(DEFINITION_BASED) == 39, len(DEFINITION_BASED)
