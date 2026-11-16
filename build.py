#!/usr/bin/env python3
"""Build the APT repo + website into _site/. Needs dpkg-scanpackages (dpkg-dev)."""
import bz2, gzip, hashlib, html, json, lzma, os, re, shutil, subprocess, urllib.request
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


def extras(p):
    """Optional per-tweak assets in tweaks/<Package>/: icon.png, banner.png, description.md, screenshots/."""
    d, url = ROOT / "tweaks" / p["Package"], f"{BASE}/tweaks/{p['Package']}"
    shots = sorted((d / "screenshots").glob("*")) if (d / "screenshots").is_dir() else []
    return {
        "icon": f"{url}/icon.png" if (d / "icon.png").is_file() else None,
        "banner": f"{url}/banner.png" if (d / "banner.png").is_file() else None,
        "md": (d / "description.md").read_text() if (d / "description.md").is_file() else p.get("Description", ""),
        "shots": [f"{url}/screenshots/{f.name}" for f in shots if f.suffix.lower() in (".png", ".jpg", ".jpeg")],
    }


def depiction_json(p):
    x = extras(p)
    rows = [("Version", p["Version"]), ("Compatibility", compat(p)), ("Author", p.get("Author", "")),
            ("Section", p.get("Section", ""))]
    views = []
    if x["shots"]:
        views.append({"class": "DepictionScreenshotsView", "itemCornerRadius": 8, "itemSize": "{160, 346}",
                      "screenshots": [{"url": u, "accessibilityText": "Screenshot"} for u in x["shots"]]})
    views += [{"class": "DepictionMarkdownView", "markdown": x["md"]}, {"class": "DepictionSeparatorView"}]
    views += [{"class": "DepictionTableTextView", "title": t, "text": v} for t, v in rows if v]
    if p.get("Homepage"):
        views.append({"class": "DepictionTableButtonView", "title": "Source code", "action": p["Homepage"]})
    dep = {"minVersion": "0.1", "class": "DepictionTabView", "tintColor": TINT,
           "tabs": [{"tabname": "Details", "class": "DepictionStackView", "views": views}]}
    if x["banner"]:
        dep["headerImage"] = x["banner"]
    return dep


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<link rel="icon" href="/CydiaIcon.png"><style>
:root{{--bg:#f5f5f7;--card:#fff;--fg:#1d1d1f;--mut:#6e6e73;--acc:%s}}
@media (prefers-color-scheme:dark){{:root{{--bg:#000;--card:#1c1c1e;--fg:#f5f5f7;--mut:#98989d}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 -apple-system,system-ui,sans-serif}}
main{{max-width:640px;margin:0 auto;padding:32px 16px}}h1{{margin:.2em 0}}p{{color:var(--mut)}}
.btn{{display:inline-block;background:var(--acc);color:#fff;padding:10px 18px;border-radius:10px;text-decoration:none;margin:4px 6px 4px 0}}
dl{{display:grid;grid-template-columns:auto 1fr;gap:6px 16px}}dt{{color:var(--mut)}}dd{{margin:0}}
img.banner{{width:100%%;border-radius:14px}}code{{word-break:break-all}}
.shots{{display:flex;gap:10px;overflow-x:auto}}.shots img{{height:340px;border-radius:8px}}#md table{{border-collapse:collapse}}
#md td,#md th{{border:1px solid var(--mut);padding:4px 8px}}
</style></head><body><main>{body}</main></body></html>""" % TINT


def esc(s):
    return html.escape(s or "")


def depiction_html(p):
    x = extras(p)
    rows = [("Version", p["Version"]), ("Compatibility", compat(p)), ("Author", p.get("Author")),
            ("Depends", p.get("Depends"))]
    dl = "".join(f"<dt>{t}</dt><dd>{esc(v)}</dd>" for t, v in rows if v)
    src = f'<a class="btn" href="{esc(p["Homepage"])}">Source code</a>' if p.get("Homepage") else ""
    banner = f'<img class="banner" src="{x["banner"]}" alt="">' if x["banner"] else ""
    shots = "".join(f'<img src="{u}" alt="Screenshot">' for u in x["shots"])
    md = json.dumps(x["md"]).replace("</", "<\\/")  # markdown is ours; escape only to keep the script tag intact
    body = (f'{banner}<h1>{esc(p.get("Name", p["Package"]))}</h1>'
            f'<div class="shots">{shots}</div><div id="md"><p>{esc(p.get("Description"))}</p></div><dl>{dl}</dl>{src}'
            '<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>'
            f'<script>document.getElementById("md").innerHTML = marked.parse({md});</script>')
    return PAGE.format(title=esc(p.get("Name", p["Package"])), body=body)


def index_html(pkgs):
    cards = "".join(
        f'<a class="card" href="/depictions/{esc(p["Package"])}.html">'
        f'<img src="{extras(p)["icon"] or "/CydiaIcon.png"}" alt=""><b>{esc(p.get("Name", p["Package"]))}</b>'
        f'<span>{esc(p["Version"])} · {esc(compat(p))}</span><br><span>{esc(p.get("Description"))}</span></a>'
        for p in pkgs)
    data = [{"name": p.get("Name", p["Package"]), "meta": f'{p["Version"]} · {compat(p)}',
             "desc": p.get("Description", ""), "url": f'/depictions/{p["Package"]}.html',
             "icon": extras(p)["icon"] or "/CydiaIcon.png"} for p in pkgs]
    tpl = (ROOT / "maze.html").read_text()
    marks = {"/*PKGS*/[]": json.dumps(data).replace("</", "<\\/"),  # "</" would close the <script>
             "<!--CARDS-->": cards, "__BASE__": BASE}
    for mark, val in marks.items():
        assert mark in tpl, f"maze.html lost its {mark} placeholder"
        tpl = tpl.replace(mark, val)
    return tpl


def github(url):
    token = os.environ.get("GITHUB_TOKEN")  # optional; avoids the 60 requests/hour anonymous limit
    hdr = {"Authorization": f"Bearer {token}"} if token else {}
    return urllib.request.urlopen(urllib.request.Request(url, headers=hdr)).read()


def fetch_releases():
    """Download every .deb attached to a published release of the repos listed in sources.txt."""
    repos = [l.split("#")[0].strip() for l in (ROOT / "sources.txt").read_text().splitlines()]
    for repo in filter(None, repos):
        for rel in json.loads(github(f"https://api.github.com/repos/{repo}/releases?per_page=100")):
            for a in rel["assets"]:
                dst = OUT / "debs" / a["name"]
                if rel["draft"] or not a["name"].endswith(".deb") or dst.exists():
                    continue
                blob = github(a["browser_download_url"])
                assert a.get("digest") in (None, "sha256:" + hashlib.sha256(blob).hexdigest()), f"{a['name']}: bad sha256"
                dst.write_bytes(blob)
                print(f"Fetched {repo} {rel['tag_name']}: {a['name']}")


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    (OUT / "depictions").mkdir(parents=True)
    shutil.copytree(ROOT / "debs", OUT / "debs")
    fetch_releases()
    shutil.copy(ROOT / "CydiaIcon.png", OUT)
    shutil.copytree(ROOT / "sfx", OUT / "sfx")
    if (ROOT / "tweaks").is_dir():
        shutil.copytree(ROOT / "tweaks", OUT / "tweaks")

    raw = subprocess.run(["dpkg-scanpackages", "-m", "debs", "/dev/null"], cwd=OUT,
                         capture_output=True, text=True, check=True).stdout
    pkgs = parse(raw)
    for p in pkgs:
        assert (OUT / p["Filename"]).is_file(), p["Filename"]
        p["Depiction"] = f"{BASE}/depictions/{p['Package']}.html"
        p["SileoDepiction"] = f"{BASE}/depictions/{p['Package']}.json"
        p["Icon"] = extras(p)["icon"] or f"{BASE}/CydiaIcon.png"

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
    for d in (ROOT / "tweaks").glob("*/"):  # catch folder names that match no package
        assert d.name in latest, f"tweaks/{d.name} matches no package in debs/ or releases"
    for p in latest.values():
        (OUT / "depictions" / f"{p['Package']}.json").write_text(json.dumps(depiction_json(p), indent=2))
        (OUT / "depictions" / f"{p['Package']}.html").write_text(depiction_html(p))
    (OUT / "index.html").write_text(index_html(sorted(latest.values(), key=lambda p: p.get("Name", ""))))

    # self-check: re-parse what we wrote
    assert len(parse((OUT / "Packages").read_text())) == len(pkgs)
    print(f"Built {len(pkgs)} package(s) into {OUT}")


if __name__ == "__main__":
    main()
