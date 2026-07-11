import yaml, requests, pathlib

CFG = yaml.safe_load(open("config/modules.yaml"))


def fetch(url, dest):
    dest = pathlib.Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    dest.write_text(r.text)
    print(f"fetched {dest} ({len(r.text)} bytes)")


if __name__ == "__main__":
    # top-level IETF modules (the ones we actually score)
    for m in CFG["ietf"]:
        fetch(m["url"], f"corpus/ietf/{m['name']}.yang")

    # IETF dependency modules (needed for pyang import resolution only)
    for m in CFG.get("ietf_deps", []):
        fetch(m["url"], f"corpus/ietf/{m['name']}.yang")

    # top-level TAPI modules (the ones we actually score)
    tapi = CFG["tapi"]
    for mod in tapi["modules"]:
        fetch(f"{tapi['base']}/{mod}", f"corpus/tapi/{mod}")

    # TAPI dependency modules
    for mod in tapi.get("deps", []):
        fetch(f"{tapi['base']}/{mod}", f"corpus/tapi/{mod}")
