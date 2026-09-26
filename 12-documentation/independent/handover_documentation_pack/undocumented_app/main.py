import argparse
import base64
import hashlib
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

F = "vault.dat"
K = os.environ.get("VAULT_SECRET_KEY", "default-insecure-key-2026")


def _k():
    return hashlib.sha256(K.encode("utf-8")).digest()


def _enc(d: str) -> str:
    k = _k()
    raw = d.encode("utf-8")
    out = bytearray(len(raw))
    for i in range(len(raw)):
        out[i] = raw[i] ^ k[i % len(k)]
    return base64.b64encode(out).decode("utf-8")


def _dec(d: str) -> str:
    k = _k()
    raw = base64.b64decode(d.encode("utf-8"))
    out = bytearray(len(raw))
    for i in range(len(raw)):
        out[i] = raw[i] ^ k[i % len(k)]
    return out.decode("utf-8")


def _p():
    target = os.environ.get("VAULT_STORAGE_PATH")
    if target:
        return Path(target)
    return Path(F)


def _load():
    p = _p()
    if not p.exists():
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            c = f.read().strip()
            if not c:
                return {}
            return json.loads(_dec(c))
    except Exception:
        return {}


def _save(data):
    p = _p()
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data)
    enc = _enc(payload)
    with open(p, "w", encoding="utf-8") as f:
        f.write(enc)


def set_val(name, val, ttl=0):
    d = _load()
    exp = int(time.time() + ttl) if ttl > 0 else 0
    d[name] = {
        "val": val,
        "created": datetime.utcnow().isoformat() + "Z",
        "expires": exp,
        "rev": d.get(name, {}).get("rev", 0) + 1
    }
    _save(d)
    return d[name]["rev"]


def get_val(name):
    d = _load()
    if name not in d:
        return None
    item = d[name]
    if item["expires"] > 0 and time.time() > item["expires"]:
        del d[name]
        _save(d)
        return None
    return item["val"]


def audit():
    d = _load()
    now = time.time()
    res = []
    for k, v in d.items():
        expired = v["expires"] > 0 and now > v["expires"]
        res.append({
            "name": k,
            "revision": v.get("rev", 1),
            "created": v.get("created"),
            "expired": expired
        })
    return res


def purge():
    d = _load()
    now = time.time()
    active = {}
    purged = 0
    for k, v in d.items():
        if v["expires"] > 0 and now > v["expires"]:
            purged += 1
        else:
            active[k] = v
    if purged > 0:
        _save(active)
    return purged


def main():
    parser = argparse.ArgumentParser(prog="vault")
    sub = parser.add_subparsers(dest="cmd")

    p_set = sub.add_parser("set")
    p_set.add_argument("key")
    p_set.add_argument("value")
    p_set.add_argument("--ttl", type=int, default=0)

    p_get = sub.add_parser("get")
    p_get.add_argument("key")

    sub.add_parser("audit")
    sub.add_parser("purge")

    args = parser.parse_args()

    if args.cmd == "set":
        rev = set_val(args.key, args.value, args.ttl)
        print(f"STORED {args.key} (rev {rev})")
        sys.exit(0)

    elif args.cmd == "get":
        val = get_val(args.key)
        if val is None:
            sys.stderr.write(f"NOT_FOUND {args.key}\n")
            sys.exit(1)
        print(val)
        sys.exit(0)

    elif args.cmd == "audit":
        items = audit()
        if not items:
            print("EMPTY")
            sys.exit(0)
        for it in items:
            st = "EXPIRED" if it["expired"] else "VALID"
            print(f"{it['name']} | rev:{it['revision']} | {it['created']} | {st}")
        sys.exit(0)

    elif args.cmd == "purge":
        n = purge()
        print(f"PURGED {n} expired keys")
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
