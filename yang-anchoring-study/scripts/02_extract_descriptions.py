"""
Extract (corpus, module, path, node_type, description) tuples from the YANG corpus.

Deviates from the plan's primary approach (pyang CLI `-f flatten
--flatten-description`) because that plugin, invoked one file at a time,
cannot see augment targets defined in other files, so augmenting modules
(ietf-te-topology, ietf-otn-topology, all of which augment ietf-network /
ietf-network-topology) yield zero rows. It also has no way to attribute an
augmented node to the module that actually defines it (as opposed to the
module whose tree it lives in).

Instead this uses the pyang Context/Repository API directly (the same
machinery the flatten plugin sits on top of) and walks i_children, reading
each statement's `i_module.arg` for true ownership -- this is exactly the
mechanism the plan's fallback flatten_desc_plugin.py relies on, just run
in-process instead of via `--plugindir`. IETF modules are loaded together
(network + network-topology + te-topology + otn-topology) so augments
resolve; TAPI modules are self-contained (no augments across the top-level
tapi-topology/tapi-connectivity/tapi-common trio) so they're walked the
same way for consistency.
"""
import csv
import pathlib

from pyang import context, repository, statements

DATA_NODE_TYPES = {
    "container", "leaf", "list", "leaf-list", "choice", "case",
    "typedef", "grouping", "identity",
}

IETF_TOP_MODULES = [
    "corpus/ietf/ietf-network.yang",
    "corpus/ietf/ietf-network-topology.yang",
    "corpus/ietf/ietf-te-topology.yang",
    "corpus/ietf/ietf-otn-topology.yang",
]
TAPI_TOP_MODULES = [
    "corpus/tapi/tapi-topology.yang",
    "corpus/tapi/tapi-connectivity.yang",
    "corpus/tapi/tapi-common.yang",
]


def load_modules(files, search_path="corpus/ietf:corpus/tapi"):
    repo = repository.FileRepository(search_path, use_env=False)
    ctx = context.Context(repo)
    mods = []
    for fn in files:
        text = pathlib.Path(fn).read_text()
        m = ctx.add_module(fn, text)
        if m is None:
            raise RuntimeError(f"pyang failed to parse {fn}")
        mods.append(m)
    ctx.validate()
    errors = [e for e in ctx.errors if e[1].is_error]
    if errors:
        for pos, err in errors:
            print("PYANG ERROR:", pos, err)
        raise RuntimeError(f"pyang reported {len(errors)} error(s) while loading {files}")
    return mods


def walk(stmt, rows, corpus, seen):
    for ch in getattr(stmt, "i_children", []):
        path = statements.mk_path_str(ch, with_prefixes=False)
        if path not in seen:
            seen.add(path)
            owner = ch.i_module.arg if getattr(ch, "i_module", None) else ""
            desc_stmt = ch.search_one("description")
            desc = desc_stmt.arg.strip().replace("\n", " ") if desc_stmt else ""
            desc = " ".join(desc.split())  # collapse whitespace
            rows.append({
                "corpus": corpus,
                "module": owner,
                "path": path,
                "node_type": ch.keyword,
                "description": desc,
            })
        walk(ch, rows, corpus, seen)


def extract_corpus(top_modules, corpus_name):
    mods = load_modules(top_modules)
    rows = []
    seen = set()
    # walk every top-level module's tree; augmented nodes get discovered
    # via i_children of the module they augment, and de-duped via `seen`
    for m in mods:
        walk(m, rows, corpus_name, seen)
    return rows


if __name__ == "__main__":
    all_rows = []
    all_rows += extract_corpus(IETF_TOP_MODULES, "ietf")
    all_rows += extract_corpus(TAPI_TOP_MODULES, "tapi")

    out_dir = pathlib.Path("data/raw")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "all_nodes.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["corpus", "module", "path", "node_type", "description"])
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"wrote {len(all_rows)} rows to {out_path}")
    for corpus in ("ietf", "tapi"):
        n = sum(1 for r in all_rows if r["corpus"] == corpus)
        print(f"  {corpus}: {n} nodes")
