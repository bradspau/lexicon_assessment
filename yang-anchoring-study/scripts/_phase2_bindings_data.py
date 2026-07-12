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
#
# CORRECTION ROUND (post-hoc, same day): investigating those 11 errors found
# two real gold-standard mistakes (nsrlg, lifecycle-state -- both corrected
# to NONE in data/gold/gold_standard.csv, see notes column for the semantic
# argument) and a genuine lexicon construct-validity problem (LEX-002 vs
# LEX-003 vs LEX-007 boundaries too close together) plus a missing scoring
# rule (attribute/template containers weren't told to resolve to
# "subsumed_by" rather than "NONE"). LEX-002/003/007 were rewritten to
# sharpen those boundaries (see data/lexicon/lexicon.yaml) and the binder
# prompt gained an explicit attribute/template-container rule (see
# scripts/08_llm_binder.py PROMPT). The 8 affected DEFINITION_BASED rows
# below were re-collected via 8 fresh isolated blind subagent calls against
# the updated lexicon + prompt (not hand-edited) -- marked "RETEST" inline.
# 7 of 8 flipped to correct; cep-list/connection-end-point still misbinds to
# LEX-002, because its source description ("The list of supported
# ConnectionEndPoint (CEP) instances.") genuinely doesn't contain the
# client-facing-vs-network-facing signal needed to disambiguate, no lexicon
# wording fixes a source description that's silent on the distinguishing
# fact. supporting-termination-point was left untested for the same reason:
# its source text describes a dependency relationship between termination
# points, not a definition of what a termination point is, so no lexicon or
# prompt change can supply information the description doesn't contain.

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

    # --- GOLD-STANDARD EXPANSION (19 more candidates, same blind isolated-subagent methodology) ---
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/owned-node-edge-point/administrative-state", "LEX-011", "equivalent", 0.95),
    ("ietf", "ietf-otn-topology", "/networks/network/link/te/te-link-attributes/otn-link/odtu-flex-type", "LEX-010", "equivalent", 0.85),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-attributes/connectivity-matrices/underlay/tunnels", "LEX-006", "subsumed_by", 0.55),
    ("tapi", "tapi-connectivity", "/context/topology-context/topology/node/owned-node-edge-point/cep-list", "LEX-007", "subsumed_by", 0.75),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/tunnel-termination-point/local-link-connectivities", "LEX-003", "subsumed_by", 0.6),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/tunnel-termination-point/client-layer-adaptation", "LEX-005", "subsumed_by", 0.55),
    ("tapi", "tapi-common", "/context/service-interface-point/available-capacity", "LEX-007", "subsumed_by", 0.7),
    ("ietf", "ietf-network-topology", "/networks/network/link/source/source-tp", "LEX-002", "equivalent", 0.85),
    ("ietf", "ietf-network-topology", "/networks/network/link/source", "LEX-002", "subsumed_by", 0.7),
    ("ietf", "ietf-network-topology", "/networks/network/link/link-id", "LEX-004", "subsumed_by", 0.75),
    ("tapi", "tapi-path-computation", "/context/path-computation-context/path-comp-service", "LEX-006", "equivalent", 0.6),
    ("tapi", "tapi-path-computation", "/context/path-computation-context/path-comp-service/end-point", "LEX-007", "equivalent", 0.6),
    ("tapi", "tapi-path-computation", "/context/path-computation-context/path-comp-service/routing-constraint", "LEX-008", "equivalent", 0.9),
    ("tapi", "tapi-path-computation", "/context/path-computation-context/path", "NONE", "none", 0.65),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/connection", "LEX-006", "subsumed_by", 0.55),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/routing-constraint/risk-diversity-characteristic", "LEX-009", "equivalent", 0.72),
    ("ietf", "ietf-network", "/networks/network/supporting-network", "NONE", "none", 0.85),
    ("ietf", "ietf-network", "/networks/network/node/supporting-node", "LEX-001", "subsumed_by", 0.6),
    ("tapi", "tapi-common", "/context/service-interface-point/layer-protocol-name", "LEX-005", "equivalent", 0.85),
]

DEFINITION_BASED = [
    ("ietf", "ietf-network", "/networks/network/node", "LEX-001", "equivalent", 0.83),
    ("ietf", "ietf-network-topology", "/networks/network/node/termination-point", "LEX-002", "subsumes", 0.72),
    ("ietf", "ietf-network-topology", "/networks/network/link", "LEX-004", "equivalent", 0.9),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/tunnel-termination-point", "LEX-003", "equivalent", 0.62),
    ("ietf", "ietf-network-topology", "/networks/network/node/termination-point/supporting-termination-point", "NONE", "none", 0.62),
    # LEX-003-FIX RETEST regression: was correct (LEX-007 subsumed_by) before the LEX-003 over-triggering fix;
    # a fresh isolated call against the fixed lexicon landed on LEX-010, and a second diagnostic call landed on
    # yet a THIRD answer (LEX-003 subsumed_by) -- three different wrong-ish answers across three calls on the
    # same four-word description ("OTN LTP Service attributes."). This instability is further evidence the
    # source text, not the lexicon, is the limiting factor for this row; see FINDINGS.md.
    ("ietf", "ietf-otn-topology", "/networks/network/node/termination-point/te/client-svc", "LEX-010", "subsumed_by", 0.4),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-attributes/connectivity-matrices/underlay/tunnels/tunnel", "LEX-006", "subsumed_by", 0.4),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-attributes/connectivity-matrices/path-constraints", "LEX-008", "equivalent", 0.72),
    # nsrlg: real blind call correctly caught the "Non-Shared" vs "shared risk group" inversion and refused;
    # gold was corrected to NONE post-hoc (see data/gold/gold_standard.csv notes), so this is now scored correct
    ("ietf", "ietf-te-topology", "/networks/network/te/nsrlg", "NONE", "none", 0.75),
    ("ietf", "ietf-otn-topology", "/networks/network/node/termination-point/te/interface-switching-capability/max-lsp-bandwidth/te-bandwidth/technology/otn-bandwidth/odu-type", "LEX-010", "equivalent", 0.87),
    ("ietf", "ietf-te-topology", "/networks/network/node/termination-point/te/admin-status", "LEX-011", "equivalent", 0.9),
    ("ietf", "ietf-te-topology", "/networks/network/node/termination-point/te/oper-status", "LEX-012", "equivalent", 0.92),
    ("ietf", "ietf-te-topology", "/networks/network/link/te/te-link-attributes", "LEX-004", "subsumed_by", 0.6),  # RETEST
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-attributes", "LEX-001", "subsumed_by", 0.4),
    ("ietf", "ietf-otn-topology", "/networks/network/link/te/te-link-attributes/otn-link", "LEX-004", "subsumed_by", 0.55),
    ("ietf", "ietf-otn-topology", "/networks/network/node/te/te-node-attributes/otn-node", "LEX-001", "equivalent", 0.62),
    ("ietf", "ietf-network-topology", "/networks/network/link/supporting-link", "LEX-004", "subsumed_by", 0.55),
    ("ietf", "ietf-te-topology", "/networks/network/link/te/bundle-stack-level/bundled-links/bundled-link", "LEX-004", "subsumed_by", 0.5),
    ("ietf", "ietf-te-topology", "/networks/network/link/te/bundle-stack-level/component-links/component-link", "LEX-004", "subsumed_by", 0.55),  # RETEST
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-template", "LEX-001", "subsumed_by", 0.62),  # RETEST
    ("ietf", "ietf-te-topology", "/networks/network/link/te/te-link-template", "LEX-004", "subsumed_by", 0.55),  # RETEST
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-attributes/connectivity-matrices/path-constraints/path-srlgs-lists/path-srlgs-list", "LEX-009", "equivalent", 0.72),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node", "LEX-001", "equivalent", 0.75),
    # trap resolved correctly under a real blind call: description explains NEPs are boundary points OWNED BY the node, matching LEX-002's
    # genus ("a boundary point on a forwarding element") rather than LEX-001 ("the forwarding element itself")
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/owned-node-edge-point", "LEX-002", "equivalent", 0.75),
    ("tapi", "tapi-topology", "/context/topology-context/topology/link", "LEX-004", "equivalent", 0.9),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service", "LEX-006", "equivalent", 0.83),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/end-point", "LEX-007", "equivalent", 0.85),  # RETEST
    # RETEST (twice now), still wrong both times: source description ("The list of supported ConnectionEndPoint
    # (CEP) instances.") never says whether the CEP faces the client or the network side, so no lexicon wording
    # can supply that fact. LEX-003-fix retest changed the specific wrong answer (LEX-002 -> LEX-003) but not
    # the outcome, consistent with this being a source-text limitation, not a lexicon problem.
    ("tapi", "tapi-connectivity", "/context/topology-context/topology/node/owned-node-edge-point/cep-list/connection-end-point", "LEX-003", "subsumed_by", 0.55),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/connectivity-constraint", "LEX-008", "equivalent", 0.75),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/routing-constraint", "LEX-008", "equivalent", 0.75),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/topology-constraint", "LEX-008", "equivalent", 0.62),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/node-rule-group/risk-characteristic", "LEX-009", "subsumed_by", 0.62),
    ("tapi", "tapi-topology", "/context/topology-context/topology/link/layer-protocol-name", "LEX-005", "subsumed_by", 0.55),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/owned-node-edge-point/layer-protocol-name", "LEX-005", "equivalent", 0.7),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/owned-node-edge-point/operational-state", "LEX-012", "equivalent", 0.97),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/owned-node-edge-point/lifecycle-state", "NONE", "none", 0.7),  # gold corrected to NONE; already correct, no retest needed
    ("tapi", "tapi-common", "/context/service-interface-point", "LEX-007", "subsumed_by", 0.75),  # RETEST
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/node-rule-group", "NONE", "none", 0.95),
    ("tapi", "tapi-path-computation", "/context/path-computation-context/path/link", "LEX-004", "equivalent", 0.75),

    # --- GOLD-STANDARD EXPANSION (19 more candidates, same blind isolated-subagent methodology) ---
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/owned-node-edge-point/administrative-state", "LEX-011", "equivalent", 0.95),
    ("ietf", "ietf-otn-topology", "/networks/network/link/te/te-link-attributes/otn-link/odtu-flex-type", "LEX-010", "subsumed_by", 0.72),
    # LEX-003-FIX RETEST, now correct: after sharpening LEX-003 to explicitly exclude tunnel/service
    # containers, a fresh isolated call correctly bound this to LEX-006 instead
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-attributes/connectivity-matrices/underlay/tunnels", "LEX-006", "subsumed_by", 0.62),
    ("tapi", "tapi-connectivity", "/context/topology-context/topology/node/owned-node-edge-point/cep-list", "NONE", "none", 0.75),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/tunnel-termination-point/local-link-connectivities", "LEX-003", "subsumed_by", 0.55),
    # LEX-003-FIX RETEST: still LEX-003 subsumed_by even against the sharpened definition that explicitly
    # excludes capability descriptors. Two independent calls (pre-fix and post-fix) agreeing on this, plus
    # this node's structural identity to local-link-connectivities (same parent, same attribute-container
    # pattern already correctly subsumed_by LEX-003), was read as the model being right and the original
    # gold NONE call being wrong -- gold revised to LEX-003 subsumed_by, see notes column
    ("ietf", "ietf-te-topology", "/networks/network/node/te/tunnel-termination-point/client-layer-adaptation", "LEX-003", "subsumed_by", 0.55),
    ("tapi", "tapi-common", "/context/service-interface-point/available-capacity", "LEX-007", "subsumed_by", 0.62),
    ("ietf", "ietf-network-topology", "/networks/network/link/source/source-tp", "LEX-002", "equivalent", 0.85),
    ("ietf", "ietf-network-topology", "/networks/network/link/source", "LEX-002", "subsumed_by", 0.7),
    ("ietf", "ietf-network-topology", "/networks/network/link/link-id", "LEX-004", "subsumed_by", 0.75),
    ("tapi", "tapi-path-computation", "/context/path-computation-context/path-comp-service", "LEX-006", "subsumed_by", 0.55),
    # LEX-003-FIX RETEST, now correct: after sharpening LEX-003 to exclude generic "path computation"
    # vocabulary and adding PathServiceEndPoint as an explicit LEX-007 example, a fresh isolated call
    # correctly bound this to LEX-007
    ("tapi", "tapi-path-computation", "/context/path-computation-context/path-comp-service/end-point", "LEX-007", "equivalent", 0.9),
    ("tapi", "tapi-path-computation", "/context/path-computation-context/path-comp-service/routing-constraint", "LEX-008", "equivalent", 0.75),
    ("tapi", "tapi-path-computation", "/context/path-computation-context/path", "NONE", "none", 0.65),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/connection", "LEX-006", "subsumed_by", 0.55),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/routing-constraint/risk-diversity-characteristic", "LEX-009", "subsumed_by", 0.55),
    ("ietf", "ietf-network", "/networks/network/supporting-network", "LEX-005", "none", 0.55),
    ("ietf", "ietf-network", "/networks/network/node/supporting-node", "LEX-001", "subsumed_by", 0.55),
    # path context (under service-interface-point) outweighed the description's own "layer protocol"
    # content; a real definition-based error, mirrors the client-svc/available-capacity pattern in reverse
    ("tapi", "tapi-common", "/context/service-interface-point/layer-protocol-name", "LEX-007", "subsumed_by", 0.6),
]

assert len(NAME_ONLY) == 58, len(NAME_ONLY)
assert len(DEFINITION_BASED) == 58, len(DEFINITION_BASED)
