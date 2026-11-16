# Torinz Repo

APT repo for my jailbreak tweaks, served at **https://repo.torinz.it**.

Add it in Sileo or Zebra: `https://repo.torinz.it/`

## Publishing a tweak

1. Put the `.deb` in `debs/` (old versions can stay or go).
2. Commit and push to `main`.

The GitHub Action runs `build.py`, which generates `Packages`, `Release`, the depictions and the landing page, then deploys to GitHub Pages.

Build locally (needs `brew install dpkg`): `python3 build.py`, output in `_site/`.
