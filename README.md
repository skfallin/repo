# Torinz Repo

APT repo for my jailbreak tweaks, served at **https://repo.torinz.it**.

Add it in Sileo or Zebra: `https://repo.torinz.it/`

## Publishing a tweak

Automatic: in the tweak's own repo, publish a GitHub release with the `.deb` attached. Within about 15 minutes it is live here. Every `.deb` of every release (pre-releases included, drafts excluded) of the repos in `sources.txt` is served, and the pages show the newest version.

- New tweak: add its `owner/repo` line to `sources.txt` and push.
- Don't want to wait: `gh workflow run deploy.yml -R skfallin/repo`.
- A `.deb` without a release can still go in `debs/` and be pushed by hand.

The GitHub Action runs `build.py`, which downloads the release `.deb` files, generates `Packages`, `Release`, the depictions and the landing page, then deploys to GitHub Pages. Pushes always deploy; the 15-minute scheduled run deploys only when the package list changed.

The landing page is the maze game in `maze.html`; `build.py` fills in the packages.

Sounds in `sfx/` are CC0 (public domain) from Freesound, found via Openverse, trimmed and normalized:

- `music.mp3`: [Aesthetic Lofi Loop](https://freesound.org/s/679187/) by Seth_Makes_Sounds
- `pickup.mp3`: [Kalimba A4](https://freesound.org/s/441135/) by nemaavla
- `win.mp3`: [Soft Short App Melody](https://freesound.org/s/619837/) by CogFireStudios
- `step.mp3`: [cartoon pop or drip](https://freesound.org/s/221091/) by AlaskaRobotics

Build locally (needs `brew install dpkg`): `python3 build.py`, output in `_site/`.

## Tweak page extras

Optional, per tweak, in `tweaks/<Package>/` (folder name = the `Package` field):

- `icon.png`: square, shown in the package list
- `banner.png`: wide header (content in the middle ~60%, Sileo crops the sides)
- `description.md`: long description in Markdown
- `screenshots/`: PNG/JPG, shown in file-name order

Anything missing is simply left out.
