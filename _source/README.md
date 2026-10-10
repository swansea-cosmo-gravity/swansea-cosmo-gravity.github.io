# Source for swansea-cosmo-gravity.github.io

`index.html` (one folder up) is generated from these files. Folders starting with `_` are not published.

- `data.py` – faculty, people and the seminar programme (edit this to add talks or members)
- `template.html` – page text and layout

The build reuses the stylesheet and photos from Ivonne's site, so it expects a checkout of
`ivonnezca/ivonnezca.github.io` with its `_source` folder available as `../izsite`
(e.g. `ln -s /path/to/ivonnezca.github.io/_source ../izsite`). Then: `python3 build.py && cp index.html ../index.html`
