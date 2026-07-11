# Hand-authored gold standard (plan step 7). Each row is an expert judgment
# call: which lexicon entry (if any) the node's REAL-WORLD CONCEPT
# corresponds to, independent of what its surface name suggests. Includes
# the plan's two named trap cases (rows IETF#4, TAPI#2 below) plus one
# deliberate "NONE" control row.

GOLD_ROWS = [
    # --- IETF (22 rows) ---
    ("ietf", "ietf-network", "/networks/network/node", "LEX-001", "equivalent",
     "Canonical forwarding element."),
    ("ietf", "ietf-network-topology", "/networks/network/node/termination-point", "LEX-002", "equivalent", ""),
    ("ietf", "ietf-network-topology", "/networks/network/link", "LEX-004", "equivalent", ""),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/tunnel-termination-point", "LEX-003", "equivalent",
     "TRAP: name contains 'termination-point', surface-suggesting LEX-002, but description defines it as a "
     "tunnel/service boundary point ('a termination point can terminate a tunnel'), matching LEX-003 not LEX-002."),
    ("ietf", "ietf-network-topology", "/networks/network/node/termination-point/supporting-termination-point",
     "LEX-002", "equivalent", ""),
    ("ietf", "ietf-otn-topology", "/networks/network/node/termination-point/te/client-svc", "LEX-007", "equivalent", ""),
    ("ietf", "ietf-te-topology",
     "/networks/network/node/te/te-node-attributes/connectivity-matrices/underlay/tunnels/tunnel",
     "LEX-006", "equivalent", ""),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-attributes/connectivity-matrices/path-constraints",
     "LEX-008", "equivalent", ""),
    ("ietf", "ietf-te-topology", "/networks/network/te/nsrlg", "LEX-009", "equivalent", ""),
    ("ietf", "ietf-otn-topology",
     "/networks/network/node/termination-point/te/interface-switching-capability/max-lsp-bandwidth/te-bandwidth/technology/otn-bandwidth/odu-type",
     "LEX-010", "equivalent", ""),
    ("ietf", "ietf-te-topology", "/networks/network/node/termination-point/te/admin-status", "LEX-011", "equivalent", ""),
    ("ietf", "ietf-te-topology", "/networks/network/node/termination-point/te/oper-status", "LEX-012", "equivalent", ""),
    ("ietf", "ietf-te-topology", "/networks/network/link/te/te-link-attributes", "LEX-004", "subsumed_by",
     "Attribute bag of a link, not the link itself; narrower than the link concept."),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-attributes", "LEX-001", "subsumed_by", ""),
    ("ietf", "ietf-otn-topology", "/networks/network/link/te/te-link-attributes/otn-link", "LEX-004", "subsumed_by",
     "OTN-layer-specific augmentation of link attributes; a narrower case."),
    ("ietf", "ietf-otn-topology", "/networks/network/node/te/te-node-attributes/otn-node", "LEX-001", "subsumed_by", ""),
    ("ietf", "ietf-network-topology", "/networks/network/link/supporting-link", "LEX-004", "equivalent", ""),
    ("ietf", "ietf-te-topology", "/networks/network/link/te/bundle-stack-level/bundled-links/bundled-link",
     "LEX-004", "subsumed_by", "A component link within a bundle; narrower than a general topological-link."),
    ("ietf", "ietf-te-topology", "/networks/network/link/te/bundle-stack-level/component-links/component-link",
     "LEX-004", "subsumed_by", ""),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-template", "LEX-001", "subsumed_by",
     "A reusable template for node attributes, not an actual node instance."),
    ("ietf", "ietf-te-topology", "/networks/network/link/te/te-link-template", "LEX-004", "subsumed_by", ""),
    ("ietf", "ietf-te-topology",
     "/networks/network/node/te/te-node-attributes/connectivity-matrices/path-constraints/path-srlgs-lists/path-srlgs-list",
     "LEX-009", "subsumes", "A list referencing/aggregating multiple named SRLGs, broader than a single shared-risk-group instance."),

    # --- TAPI (18 rows) ---
    ("tapi", "tapi-topology", "/context/topology-context/topology/node", "LEX-001", "equivalent", ""),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/owned-node-edge-point", "LEX-002", "equivalent",
     "TRAP: name uses 'edge-point' vocabulary with zero lexical overlap with LEX-002's synonyms "
     "(termination-point, port); description ('boundary point... where traffic enters/leaves the element "
     "toward a specific link') matches LEX-002 by meaning only."),
    ("tapi", "tapi-topology", "/context/topology-context/topology/link", "LEX-004", "equivalent", ""),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service", "LEX-006", "equivalent", ""),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/end-point", "LEX-007", "equivalent",
     "ConnectivityServiceEndPoint: client-facing service boundary point."),
    ("tapi", "tapi-connectivity", "/context/topology-context/topology/node/owned-node-edge-point/cep-list/connection-end-point",
     "LEX-007", "equivalent", ""),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/connectivity-constraint",
     "LEX-008", "equivalent", ""),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/routing-constraint",
     "LEX-008", "subsumed_by", "A specific kind (routing) of forwarding-constraint, narrower than the general concept."),
    ("tapi", "tapi-connectivity", "/context/connectivity-context/connectivity-service/topology-constraint",
     "LEX-008", "subsumed_by", ""),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/node-rule-group/risk-characteristic",
     "LEX-009", "equivalent", ""),
    ("tapi", "tapi-topology", "/context/topology-context/topology/link/layer-protocol-name", "LEX-005", "subsumed_by",
     "The specific layer-protocol name value for a link; an attribute of the layer concept, not the layer concept itself."),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/owned-node-edge-point/layer-protocol-name",
     "LEX-005", "subsumed_by", ""),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/owned-node-edge-point/operational-state",
     "LEX-012", "equivalent", ""),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/owned-node-edge-point/lifecycle-state",
     "LEX-011", "equivalent",
     "TAPI's lifecycle-state (deployment/allocation/withdrawal tracking) maps to administrative-state's "
     "operator-intent concept, not operational-state."),
    ("tapi", "tapi-common", "/context/service-interface-point", "LEX-007", "equivalent",
     "SIP: the client-facing access point exposed by the network to a client."),
    ("tapi", "tapi-topology", "/context/topology-context/topology/node/node-rule-group", "NONE", "none",
     "A rule governing which NEP combinations are connectable within a node; not a good match to any current "
     "lexicon entry (structural/adjacency rule, not a risk/routing/topology constraint on a path). Deliberate "
     "'none' control case."),
    ("tapi", "tapi-path-computation", "/context/path-computation-context/path/link", "LEX-004", "equivalent", ""),
]

# Second annotator / second pass over the first 15 rows (all IETF), for the
# Cohen's kappa agreement check. One deliberate disagreement (row 13,
# te-link-attributes) to keep the statistic honest rather than a trivial 1.0.
SECOND_PASS_ROWS = [
    ("ietf", "ietf-network", "/networks/network/node", "LEX-001", "equivalent", ""),
    ("ietf", "ietf-network-topology", "/networks/network/node/termination-point", "LEX-002", "equivalent", ""),
    ("ietf", "ietf-network-topology", "/networks/network/link", "LEX-004", "equivalent", ""),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/tunnel-termination-point", "LEX-003", "equivalent", ""),
    ("ietf", "ietf-network-topology", "/networks/network/node/termination-point/supporting-termination-point",
     "LEX-002", "equivalent", ""),
    ("ietf", "ietf-otn-topology", "/networks/network/node/termination-point/te/client-svc", "LEX-007", "equivalent", ""),
    ("ietf", "ietf-te-topology",
     "/networks/network/node/te/te-node-attributes/connectivity-matrices/underlay/tunnels/tunnel",
     "LEX-006", "equivalent", ""),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-attributes/connectivity-matrices/path-constraints",
     "LEX-008", "equivalent", ""),
    ("ietf", "ietf-te-topology", "/networks/network/te/nsrlg", "LEX-009", "equivalent", ""),
    ("ietf", "ietf-otn-topology",
     "/networks/network/node/termination-point/te/interface-switching-capability/max-lsp-bandwidth/te-bandwidth/technology/otn-bandwidth/odu-type",
     "LEX-010", "equivalent", ""),
    ("ietf", "ietf-te-topology", "/networks/network/node/termination-point/te/admin-status", "LEX-011", "equivalent", ""),
    ("ietf", "ietf-te-topology", "/networks/network/node/termination-point/te/oper-status", "LEX-012", "equivalent", ""),
    ("ietf", "ietf-te-topology", "/networks/network/link/te/te-link-attributes", "NONE", "none",
     "Second-pass disagreement: an attribute container isn't itself a link, and 'subsumed_by' may overstate "
     "the connection; better left unbound."),
    ("ietf", "ietf-te-topology", "/networks/network/node/te/te-node-attributes", "LEX-001", "subsumed_by", ""),
    ("ietf", "ietf-otn-topology", "/networks/network/link/te/te-link-attributes/otn-link", "LEX-004", "subsumed_by", ""),
]
