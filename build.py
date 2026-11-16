#!/usr/bin/env python3
"""Build the APT repo + website into _site/. Needs dpkg-scanpackages (dpkg-dev)."""
import bz2, gzip, hashlib, html, json, lzma, re, shutil, subprocess
from pathlib import Path

BASE = "https://repo.torinz.it"
ROOT = Path(__file__).parent
OUT = ROOT / "_site"
REPO = {
    "Origin": "Torinz Repo",
    "Label": "Torinz Repo",
    "Suite": "stable",
    "Version": "1.0",
    "Codename": "torinz",
    "Architectures": "iphoneos-arm64",
    "Components": "main",
    "Description": "Rootless tweaks by skfallin",
}
TINT = "#4d5cf2"


def parse(text):
    """Parse a Packages file into a list of dicts (continuation lines kept)."""
    pkgs = []
    for block in text.strip().split("\n\n"):
        d, key = {}, None
        for line in block.splitlines():
            if line[:1] in (" ", "\t") and key:
                d[key] += "\n" + line
            else:
                key, _, val = line.partition(":")
                d[key] = val.strip()
        pkgs.append(d)
    return pkgs


def dump(pkgs):
    return "\n".join("".join(f"{k}: {v}\n" for k, v in p.items()) for p in pkgs)


def compat(p):
    m = re.search(r"firmware \(([^)]+)\)", p.get("Depends", ""))
    return "iOS " + m.group(1).replace("= ", "").strip() if m else "rootless"


def depiction_json(p):
    rows = [("Version", p["Version"]), ("Compatibility", compat(p)), ("Author", p.get("Author", "")),
            ("Section", p.get("Section", ""))]
    views = [{"class": "DepictionMarkdownView", "markdown": p.get("Description", "")},
             {"class": "DepictionSeparatorView"}]
    views += [{"class": "DepictionTableTextView", "title": t, "text": v} for t, v in rows if v]
    if p.get("Homepage"):
        views.append({"class": "DepictionTableButtonView", "title": "Source code", "action": p["Homepage"]})
    return {"minVersion": "0.1", "class": "DepictionTabView", "tintColor": TINT,
            "tabs": [{"tabname": "Details", "class": "DepictionStackView", "views": views}]}


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<link rel="icon" href="/CydiaIcon.png"><style>
:root{{--bg:#f5f5f7;--card:#fff;--fg:#1d1d1f;--mut:#6e6e73;--acc:%s}}
@media (prefers-color-scheme:dark){{:root{{--bg:#000;--card:#1c1c1e;--fg:#f5f5f7;--mut:#98989d}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 -apple-system,system-ui,sans-serif}}
main{{max-width:640px;margin:0 auto;padding:32px 16px}}h1{{margin:.2em 0}}p{{color:var(--mut)}}
.card{{background:var(--card);border-radius:14px;padding:16px;margin:12px 0;display:block;color:inherit;text-decoration:none}}
.card b{{display:block}}.card span{{color:var(--mut);font-size:14px}}
.btn{{display:inline-block;background:var(--acc);color:#fff;padding:10px 18px;border-radius:10px;text-decoration:none;margin:4px 6px 4px 0}}
dl{{display:grid;grid-template-columns:auto 1fr;gap:6px 16px}}dt{{color:var(--mut)}}dd{{margin:0}}
img.icon{{width:72px;height:72px;border-radius:16px}}code{{word-break:break-all}}
</style></head><body><main>{body}</main></body></html>""" % TINT


def esc(s):
    return html.escape(s or "")


def depiction_html(p):
    rows = [("Version", p["Version"]), ("Compatibility", compat(p)), ("Author", p.get("Author")),
            ("Depends", p.get("Depends"))]
    dl = "".join(f"<dt>{t}</dt><dd>{esc(v)}</dd>" for t, v in rows if v)
    src = f'<a class="btn" href="{esc(p["Homepage"])}">Source code</a>' if p.get("Homepage") else ""
    body = f'<h1>{esc(p.get("Name", p["Package"]))}</h1><p>{esc(p.get("Description"))}</p><dl>{dl}</dl>{src}'
    return PAGE.format(title=esc(p.get("Name", p["Package"])), body=body)


def index_html(pkgs):
    cards = "".join(
        f'<a class="card" href="/depictions/{esc(p["Package"])}.html"><b>{esc(p.get("Name", p["Package"]))}</b>'
        f'<span>{esc(p["Version"])} · {esc(compat(p))}</span><br><span>{esc(p.get("Description"))}</span></a>'
        for p in pkgs)
    body = (f'<img class="icon" src="/CydiaIcon.png" alt=""><h1>{REPO["Label"]}</h1><p>{REPO["Description"]}.</p>'
            f'<a class="btn" href="sileo://source/{BASE}/">Add to Sileo</a>'
            f'<a class="btn" href="zbra://sources/add/{BASE}/">Add to Zebra</a>'
            f'<p>Or add this source manually: <code>{BASE}/</code></p><h2>Packages</h2>{cards}')
    return PAGE.format(title=REPO["Label"], body=body)


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    (OUT / "depictions").mkdir(parents=True)
    shutil.copytree(ROOT / "debs", OUT / "debs")
    shutil.copy(ROOT / "CydiaIcon.png", OUT)

    raw = subprocess.run(["dpkg-scanpackages", "-m", "debs", "/dev/null"], cwd=OUT,
                         capture_output=True, text=True, check=True).stdout
    pkgs = parse(raw)
    for p in pkgs:
        assert (OUT / p["Filename"]).is_file(), p["Filename"]
        p["Depiction"] = f"{BASE}/depictions/{p['Package']}.html"
        p["SileoDepiction"] = f"{BASE}/depictions/{p['Package']}.json"
        p["Icon"] = f"{BASE}/CydiaIcon.png"

    data = dump(pkgs).encode()
    files = {"Packages": data, "Packages.gz": gzip.compress(data), "Packages.bz2": bz2.compress(data),
             "Packages.xz": lzma.compress(data)}
    for name, blob in files.items():
        (OUT / name).write_bytes(blob)

    release = "".join(f"{k}: {v}\n" for k, v in REPO.items())
    for label, algo in (("MD5Sum", "md5"), ("SHA256", "sha256")):
        release += f"{label}:\n" + "".join(
            f" {hashlib.new(algo, b).hexdigest()} {len(b)} {n}\n" for n, b in files.items())
    (OUT / "Release").write_text(release)

    latest = {}
    for p in pkgs:  # dpkg-scanpackages -m lists every version; pages show the newest
        cur = latest.get(p["Package"])
        if not cur or subprocess.run(["dpkg", "--compare-versions", p["Version"], "gt", cur["Version"]]).returncode == 0:
            latest[p["Package"]] = p
    for p in latest.values():
        (OUT / "depictions" / f"{p['Package']}.json").write_text(json.dumps(depiction_json(p), indent=2))
        (OUT / "depictions" / f"{p['Package']}.html").write_text(depiction_html(p))
    (OUT / "index.html").write_text(index_html(sorted(latest.values(), key=lambda p: p.get("Name", ""))))

    # self-check: re-parse what we wrote
    assert len(parse((OUT / "Packages").read_text())) == len(pkgs)
    print(f"Built {len(pkgs)} package(s) into {OUT}")


if __name__ == "__main__":
    main()
