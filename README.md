# Torinz Repo

APT repo for my jailbreak tweaks, served at **https://repo.torinz.it**.

Add it in Sileo or Zebra: `https://repo.torinz.it/`

## Publishing a tweak

1. Put the `.deb` in `debs/` (old versions can stay or go).
2. Commit and push to `main`.

The GitHub Action runs `build.py`, which generates `Packages`, `Release`, the depictions and the landing page, then deploys to GitHub Pages.

The landing page is the maze game in `maze.html`; `build.py` fills in the packages.

Sounds in `sfx/` are CC0 (public domain) from Freesound, found via Openverse, trimmed and normalized:

- `music.mp3`: [Happy](https://freesound.org/s/395244/) by Hoshi_Hana
- `pickup.mp3`: [Retro, Coin 05](https://freesound.org/s/443258/) by MATRIXXX_
- `win.mp3`: [Powerup01](https://freesound.org/s/341242/) by jeremysykes
- `step.mp3`: one step from [8-bit footsteps](https://freesound.org/s/501102/) by EVRetro

Build locally (needs `brew install dpkg`): `python3 build.py`, output in `_site/`.

## Tweak page extras

Optional, per tweak, in `tweaks/<Package>/` (folder name = the `Package` field):

- `icon.png`: square, shown in the package list
- `banner.png`: wide header (content in the middle ~60%, Sileo crops the sides)
- `description.md`: long description in Markdown
- `screenshots/`: PNG/JPG, shown in file-name order

Anything missing is simply left out.
