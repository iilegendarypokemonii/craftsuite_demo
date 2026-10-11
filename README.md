# Craft suite showcase

**Live page: https://iilegendarypokemonii.github.io/craftsuite_demo/**

12 free Craft apps, 1 example project. The apps made a complete research project, "Signal & Noise 2026",
about how social media talked about AI language models from January to September 2026. The project has
a dataset, charts, a poster, a report, a PDF, slides, images, a photo, a tune, an animation, a video and a
floor plan. Each app made its files from typed commands, through its command-line tool. No app window opened.

- 75 files are on the page. 66 came directly from the apps. A small Python script helped with the other 9,
  for example to join app frames into a GIF. The "Sources" table on the page lists each file.
- All data is invented: the posts, the accounts and the research team. No quote comes from a real person.
- Get the apps (free, open source, Windows, macOS and Linux): https://getartcraft.com/apps

## Files

| Path | Content |
|---|---|
| `index.html` | The page (static HTML, no external requests) |
| `assets/<app>/` | The files that each app made, and `manifest.json` with the captions and the exact commands |
| `assets/_site/` | App icons, the Source Sans 3 font and its license |
| `data/` | The invented dataset (CSV) and the summary numbers (JSON) |
| `_build/` | `build_page.py` makes `index.html` from the manifests; `DESIGN-SYSTEM.md` lists the design tokens |

Rebuild the page: `python _build/build_page.py` (needs Python 3 and Pillow).

## Credits

- Design: the layout follows the public design system of adobe.com (Adobe Milo, C2 tokens). Adobe did not
  make this page and has no connection to it.
- Font: Source Sans 3 by Adobe, SIL Open Font License 1.1 (`assets/_site/OFL-SourceSans3.txt`).
- App icons: the Craft apps.
