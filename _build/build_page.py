"""Builds showcase/index.html from assets/<app>/manifest.json files.

Design: tokens extracted from adobe.com (Milo C2 foundation), see _build/DESIGN-SYSTEM.md.
Text: ASD-STE100 Simplified Technical English (short sentences, active voice, one term per thing).
Run: python -I _build/build_page.py   (paths resolve from this file)
"""
import csv, html, json, pathlib

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DATA = ROOT / "data"
e = html.escape
SITE = "https://getartcraft.com/apps"

# key: name, category, familiar equivalent, icon colour, section headline
APPS = {
    "gridcraft":   ("GridCraft",   "Spreadsheets",      "Microsoft Excel",      "#1f9d55", "Turn raw posts into clear numbers."),
    "vectorcraft": ("VectorCraft", "Vector graphics",   "Adobe Illustrator",    "#e8573f", "Draw charts and logos that stay sharp."),
    "designcraft": ("DesignCraft", "Page layout",       "Adobe InDesign",       "#7bb51c", "Put text, charts and images on a page."),
    "wordcraft":   ("WordCraft",   "Documents",         "Microsoft Word",       "#3b5bdb", "Write the report, with tables and figures."),
    "pdfcraft":    ("PdfCraft",    "PDF editing",       "Adobe Acrobat",        "#12a58a", "Combine, edit and check PDF files."),
    "deckcraft":   ("DeckCraft",   "Presentations",     "Microsoft PowerPoint", "#f26b1d", "Turn the findings into a slide deck."),
    "photocraft":  ("PhotoCraft",  "Image editing",     "Adobe Photoshop",      "#2f7bf5", "Make social images with editable layers."),
    "lightcraft":  ("LightCraft",  "Photo library",     "Adobe Lightroom",      "#f2a516", "Improve photos. Combine 3 shots into 1."),
    "soundcraft":  ("SoundCraft",  "Audio",             "Adobe Audition",       "#14a9c4", "Make the data audible."),
    "effectcraft": ("EffectCraft", "Motion graphics",   "Adobe After Effects",  "#e0368f", "Animate the key numbers."),
    "filmcraft":   ("FilmCraft",   "Video editing",     "Adobe Premiere Pro",   "#8b5cf6", "Edit all parts into 1 short video."),
    "cadcraft":    ("CADCraft",    "Technical drawing", "Autodesk AutoCAD",     "#14a2c5", "Draw exact plans of rooms and buildings."),
}
ACTS = [
    ("Analyse", ["gridcraft"]),
    ("Visualise", ["vectorcraft", "designcraft"]),
    ("Publish", ["wordcraft", "pdfcraft", "deckcraft"]),
    ("Images", ["photocraft", "lightcraft"]),
    ("Sound and film", ["soundcraft", "effectcraft", "filmcraft"]),
    ("Plan", ["cadcraft"]),
]
ORDER = [a for _, apps in ACTS for a in apps]

# A plain request that gives the same result when an AI assistant writes the commands (STE, imperative).
ASK = {
    "gridcraft": "Open posts.csv in GridCraft. Calculate each theme's share of the posts per month. Add 3 charts and save an Excel file.",
    "vectorcraft": "Make a line chart of these monthly shares in VectorCraft. Show 2 themes in colour and the others in grey. Export PNG and PDF.",
    "designcraft": "Make a 2-page poster in DesignCraft, 1080 × 1350 pixels. Use these charts and these 4 key numbers. Export PNG and PDF.",
    "wordcraft": "Write a 4-page report in WordCraft from these findings. Add a table, 2 figures and page numbers. Save it as Word and PDF.",
    "pdfcraft": "Combine the report and the spreadsheet PDF with PdfCraft. Add a cover page and bookmarks. Make a short version with the key pages.",
    "deckcraft": "Make 7 slides in DeckCraft from the report: title, method, 3 findings, conclusion and a data note. Save it as PowerPoint.",
    "photocraft": "Make a 1600 × 900 header in PhotoCraft with the title and a small bar chart. Then make a square version for Instagram.",
    "lightcraft": "Join these 3 photos (dark, normal and bright) into 1 photo in LightCraft. Give it a warm look and export a JPEG.",
    "soundcraft": "Make a 20-second tune in SoundCraft from the monthly shares. Use more notes for a bigger share. Export a WAV file.",
    "effectcraft": "Make a 7-second animated card in EffectCraft. Grow the bars month by month and show the final values: 20% and 6%.",
    "filmcraft": "Edit a 20-second video in FilmCraft from the header, the animated card and the tune. Add captions and export an MP4.",
    "cadcraft": "Draw a 14 × 9 m computer room plan in CADCraft. Show 20 server cabinets, the cooling units and the dimensions. Export a PDF.",
}
# Before/after pairs shown with a comparison slider.
PAIRS = {
    "lightcraft": ("cover-before.jpg", "cover-after-graded.jpg", "Drag to compare the photo before and after LightCraft."),
    "photocraft": ("before-lake.jpg", "after-lake-brand-duotone.jpg", "Drag to compare the photo before and after PhotoCraft."),
}
# Visible in Files, but not as a gallery card (duplicates of other media on the page).
NOT_IN_GALLERY = {"signal_noise_card.gif", "signal_noise_card_still.png", "signal_noise_teaser.gif",
                  "signal_noise_teaser_program_10s.png", "hdr-merge-preview.png",
                  "signal-noise-2026-slideshow.gif", "noise-steps.gif", "signal_noise_teaser_frame_mix.png", "signal_noise_teaser_frame_2s.png"}
POSTERS = {"signal_noise_card.mp4": "signal_noise_card_still.png",
           "signal_noise_teaser.mp4": "signal_noise_teaser_frame_2s.png"}
# Files not made by their own app: (other app that made it, or None, label)
OTHER = {
    "before-lake.jpg": ("lightcraft", None),
    "sting_waveform.png": (None, "Drawn with a Python script"),
    "gridcraft-charts.png": (None, "App output, cropped with a Python script"),
}
# One output per app for the hero mosaic.
MOSAIC = [("photocraft", "signal-noise-header-1600x900.png"), ("vectorcraft", "vc_badge.png"),
          ("deckcraft", "slide-01.png"), ("filmcraft", "signal_noise_teaser.mp4"),
          ("designcraft", "signal-noise-poster-p1.png"), ("lightcraft", "cover-after-graded.jpg"),
          ("gridcraft", "gridcraft-summary-sheet.png"), ("effectcraft", "signal_noise_card_still.png"),
          ("cadcraft", "gpu-row-floorplan.png"), ("wordcraft", "wordcraft-page-1.png"),
          ("soundcraft", "sting_waveform.png"), ("pdfcraft", "pdfcraft-page-1.png")]
CENTER_CROP = {"vc_badge.png", "cover-after-graded.jpg", "gpu-row-floorplan.png", "sting_waveform.png"}
TOP_CROP = {"signal-noise-poster-p1.png", "wordcraft-page-1.png", "pdfcraft-page-1.png", "gridcraft-summary-sheet.png"}
GLOSSARY = [
    ("Agentic coding", "AI that writes, tests and fixes code on its own."),
    ("Open-weight models", "AI models that anyone can download and run."),
    ("Reasoning & test-time compute", "AI that “thinks” for longer before it answers."),
    ("Prices & tokens", "What AI costs. A token is a small piece of text."),
    ("On-device AI", "AI that runs on a phone or laptop, not in the cloud."),
    ("Regulation & policy", "Laws and rules for AI."),
    ("Benchmarks & evals", "Tests that compare AI models."),
    ("Compute & energy", "The computers and electricity that AI needs."),
    ("Multimodal & voice", "AI that uses images, sound and speech, not only text."),
    ("Safety & trust", "How to make AI reliable and safe."),
]
SAMPLE_IDS = ["P0057", "P0152", "P0007", "P0277", "P0104", "P0066"]
IDEAS = [
    ("A class project", "Collect survey answers, chart them, write the report and present it.",
     ["gridcraft", "vectorcraft", "wordcraft", "deckcraft"],
     "Chart the answers in survey.csv. Write a 2-page report and make 5 slides for the class."),
    ("A product launch kit", "Make the product photos, a flyer, an animated banner and a short video.",
     ["photocraft", "designcraft", "effectcraft", "filmcraft"],
     "Use these 6 product photos. Make a 1-page flyer, a 5-second banner and a 15-second video."),
    ("A podcast or an event", "Make the intro music, the cover art and a printable programme.",
     ["soundcraft", "photocraft", "designcraft"],
     "Make a 10-second intro tune, a square cover image and a 2-page PDF programme."),
    ("A shop or studio plan", "Draw the floor plan, improve the photos and make a 1-page brochure.",
     ["cadcraft", "lightcraft", "designcraft"],
     "Draw a 6 × 4 m shop plan. Make my 10 photos brighter. Put both in a 1-page brochure."),
]
OUTPUTS = [("gridcraft", "a workbook with formulas and 3 charts"), ("vectorcraft", "3 charts and a badge"),
           ("designcraft", "a 2-page poster"), ("wordcraft", "a 4-page report"), ("pdfcraft", "a 6-page PDF with a cover"),
           ("deckcraft", "7 slides for PowerPoint"), ("photocraft", "a header and social images"),
           ("lightcraft", "1 photo from 3 shots"), ("soundcraft", "a 20-second tune from the data"),
           ("effectcraft", "a 7-second animated card"), ("filmcraft", "a 20-second video"), ("cadcraft", "a computer room plan")]
FRIENDLY = {"XLSX": "Excel file", "DOCX": "Word file", "PPTX": "PowerPoint file", "PDF": "PDF", "PNG": "Image",
            "JPG": "Image", "GIF": "Animation", "SVG": "SVG image", "ZIP": "ZIP file", "DXF": "CAD drawing",
            "DWG": "CAD drawing", "HTML": "Web page", "PCRAFT": "PhotoCraft file", "SCRAFT": "SoundCraft file",
            "ECPROJ": "EffectCraft file", "FCPROJ": "FilmCraft file", "DECKCRAFT": "DeckCraft file",
            "DESIGNCRAFT": "DesignCraft file", "VECTORCRAFT": "VectorCraft file", "WAV": "Sound", "FLAC": "Sound"}


def clean(s):
    return (s or "").replace("�", "…").strip()


def sentence(s):
    s = clean(s)
    return s if not s or s[-1] in ".!?…" else s + "."


def load(app):
    p = ASSETS / app / "manifest.json"
    if not p.exists():
        return None
    m = json.loads(p.read_text(encoding="utf-8"))
    m["_key"] = app
    return m


def kind_of(a):
    ext = pathlib.Path(a["file"]).suffix.lower()
    name = a["file"].lower()
    if ext in (".mp4", ".webm"):
        return "video"
    if ext == ".gif":
        return "gif"
    if ext in (".png", ".jpg", ".jpeg", ".webp"):
        return "image"
    if ext in (".wav", ".mp3", ".ogg", ".m4a"):
        return "audio"
    if ext == ".txt" and ("eval" in name or "extract" in name):
        return "text"
    return "file"


def ext_of(f):
    return "ZIP" if f.endswith(".zip") else pathlib.Path(f).suffix.lstrip(".").upper()


def size_of(app, f):
    n = (ASSETS / app / f).stat().st_size
    return f"{n / 1024:.0f} KB" if n < 1024 * 1024 else f"{n / 1048576:.1f} MB"


def dims(app, f):
    try:
        with Image.open(ASSETS / app / f) as im:
            return im.size
    except Exception:
        return None


def visible(m):
    return [a for a in m.get("assets", []) if not a.get("hidden") and (ASSETS / m["_key"] / a["file"]).exists()]


def by_app(a, app):
    """Which app made this file (None = a script helped)."""
    if a.get("made_with_app"):
        return app
    return OTHER.get(a["file"], (None, None))[0]


def icon(app, size=40, cls="icon"):
    return f'<img class="{cls}" src="assets/_site/icon-{app}.png" width="{size}" height="{size}" alt="">'


def made_tag(app, a):
    maker = by_app(a, app)
    if maker:
        return f'<span class="tag made" style="--c:{APPS[maker][3]}">{icon(maker, 16, "ticon")}Made with {APPS[maker][0]}</span>'
    label = OTHER.get(a["file"], (None, None))[1]
    return f'<span class="tag other">{label or "App output, joined with a Python script"}</span>'


def img_html(app, a, eager=False):
    rel = f"assets/{app}/{a['file']}"
    d = dims(app, a["file"])
    wh = f' width="{d[0]}" height="{d[1]}"' if d else ""
    lazy = "" if eager else ' loading="lazy"'
    cap = e(sentence(a.get("caption", "")))
    return (f'<button class="zoom" data-src="{e(rel)}" data-cap="{cap}" aria-label="Enlarge: {cap}">'
            f'<img src="{e(rel)}" alt="{cap}"{wh}{lazy}><span class="zi" aria-hidden="true">⤢</span></button>')


def video_html(app, a, autoplay=False, controls=True):
    rel = f"assets/{app}/{a['file']}"
    poster = a.get("poster") or POSTERS.get(a["file"])
    pa = f' poster="assets/{app}/{e(poster)}"' if poster and (ASSETS / app / poster).exists() else ""
    ctrl = ""
    auto = " autoplay" if autoplay else ""
    vid = f'<video src="{e(rel)}"{ctrl} muted loop playsinline preload="metadata"{auto}{pa}></video>'
    if not controls:
        return vid
    return f'<div class="vwrap">{vid}<button class="play" aria-label="Play the video">▶</button></div>'


def audio_html(app, a):
    return (f'<div class="player"><span class="pl-ico" aria-hidden="true">♪</span>'
            f'<audio src="assets/{app}/{e(a["file"])}" controls preload="metadata"></audio></div>')


def compare_html(app, before, after, hint):
    b, a = f"assets/{app}/{before['file']}", f"assets/{app}/{after['file']}"
    d = dims(app, after["file"]) or (16, 10)
    return (f'<div class="compare" style="aspect-ratio:{d[0]}/{d[1]}">'
            f'<img src="{e(a)}" alt="{e(sentence(after.get("caption", "")))}" loading="lazy">'
            f'<img class="before" src="{e(b)}" alt="{e(sentence(before.get("caption", "")))}" loading="lazy">'
            f'<span class="cl l">Before</span><span class="cl r">After</span><span class="divider" aria-hidden="true"></span>'
            f'<input type="range" min="0" max="100" value="50" aria-label="{e(hint)}"></div>')


def caption_block(app, a):
    return (f'<figcaption><b>{e(sentence(a.get("caption", "")))}</b> {e(clean(a.get("description", "")))} '
            f'{made_tag(app, a)}</figcaption>')


def card(app, a, wide=False):
    k = kind_of(a)
    cap = e(sentence(a.get("caption", "")))
    desc = e(clean(a.get("description", "")))
    cls = "card wide" if wide else "card"
    if k in ("image", "gif"):
        d = dims(app, a["file"]) or (16, 10)
        style = f' style="aspect-ratio:{d[0]}/{d[1]}"' if d[0] / d[1] > 2.2 else ""
        media = f'<div class="cmedia"{style}>{img_html(app, a)}</div>'
    elif k == "video":
        media = f'<div class="cmedia vid">{video_html(app, a)}</div>'
    elif k == "text":
        txt = (ASSETS / app / a["file"]).read_text(encoding="utf-8", errors="replace")
        if "eval" in a["file"]:
            outs = [ln.strip() for ln in txt.splitlines()
                    if ln.strip() and not ln.lstrip().startswith(("$", "(", "--", "#", '"', "'")) and "cli" not in ln]
            media = '<ul class="answers">' + "".join(f"<li>{e(o)}</li>" for o in outs[:6]) + "</ul>"
        else:
            lines = [ln for ln in txt.splitlines() if ln.strip() and not ln.startswith("#")][:9]
            media = '<blockquote class="extract">' + "".join(f"<p>{e(ln)}</p>" for ln in lines) + "<p>…</p></blockquote>"
        cls = "card wide"
    else:
        return ""
    return (f'<article class="{cls}">{media}<div class="cbody"><h4>{cap}</h4>'
            f'{f"<p>{desc}</p>" if desc else ""}{made_tag(app, a)}</div></article>')


def cards_grid(app, items, pair=None):
    """Pair (full row), then images (2 or 3 per row, no lone card), then text cards (full row)."""
    imgs = [a for a in items if kind_of(a) != "text"]
    texts = [a for a in items if kind_of(a) == "text"]
    out = []
    if pair:
        before, after, hint = pair
        out.append(f'<article class="card full">{compare_html(app, before, after, hint)}<div class="cbody">'
                   f'<h4>{e(hint)}</h4><p>{e(clean(after.get("description", "")))}</p>{made_tag(app, after)}</div></article>')
    n = len(imgs)
    cols = 2 if n in (1, 2, 4) else 3
    for i, x in enumerate(imgs):
        lone = cols == 3 and i == n - 1 and n % 3 == 1
        out.append(card(app, x, wide=lone))
    out += [card(app, x, wide=True) for x in texts]
    if not out:
        return ""
    return f'<div class="cards c{cols}">{"".join(out)}</div>'


def app_section(app, num):
    name, cat, equiv, color, headline = APPS[app]
    m = load(app)
    if not m:
        return ""
    vis = visible(m)
    by_file = {a["file"]: a for a in vis}
    pair = None
    if app in PAIRS and PAIRS[app][0] in by_file and PAIRS[app][1] in by_file:
        pair = (by_file[PAIRS[app][0]], by_file[PAIRS[app][1]], PAIRS[app][2])
    pair_files = {PAIRS[app][0], PAIRS[app][1]} if pair else set()
    gallery = [a for a in vis if a["file"] not in pair_files and a["file"] not in NOT_IN_GALLERY
               and kind_of(a) in ("image", "gif", "video", "text")]
    audio = [a for a in vis if kind_of(a) == "audio"]
    files = [a for a in vis if kind_of(a) == "file" or a["file"] in NOT_IN_GALLERY]
    made = sum(1 for a in vis if by_app(a, app))
    uses = "".join(f"<li>{e(sentence(u))}</li>" for u in m.get("use_cases", []))

    # featured: the pair (LightCraft), a video, or the first image
    feat_html, feat = "", None
    if pair and app == "lightcraft":
        feat_html = (f'<figure class="feature">{compare_html(app, *pair)}<figcaption><b>{e(pair[2])}</b> '
                     f'{e(clean(pair[1].get("description", "")))} {made_tag(app, pair[1])}</figcaption></figure>')
        pair_for_grid = None
    else:
        pair_for_grid = pair
        for k in ("video", "image", "gif"):
            feat = next((a for a in gallery if kind_of(a) == k), None)
            if feat:
                break
        if feat:
            body = video_html(app, feat) if kind_of(feat) == "video" else img_html(app, feat, eager=False)
            feat_html = f'<figure class="feature">{body}{caption_block(app, feat)}</figure>'
    for a in audio:
        feat_html += f'<figure class="feature audio">{audio_html(app, a)}{caption_block(app, a)}</figure>'
    rest = [a for a in gallery if a is not feat]
    side = None
    if len(rest) == 1 and not pair_for_grid and kind_of(rest[0]) in ("image", "gif"):
        side, rest = rest[0], []
    grid = cards_grid(app, rest, pair_for_grid)

    recipe = "\n".join(clean(r) for r in m.get("recipe", [])[:2])
    chips = "".join(
        f'<a class="pill sm" href="assets/{app}/{e(a["file"])}" '
        f'{"target=\"_blank\" rel=\"noopener\"" if a["file"].lower().endswith((".pdf", ".html", ".svg", ".png", ".gif", ".jpg")) else "download"} '
        f'title="{e(clean(a.get("description") or a.get("caption", "")))}">'
        f'<b>{e(FRIENDLY.get(ext_of(a["file"]), ext_of(a["file"])))}</b>'
        f'<span>{e(sentence(a.get("caption", "")))}{"" if by_app(a, app) else " <i>App output, joined with a Python script.</i>"}</span><small>{size_of(app, a["file"])}</small></a>'
        for a in files)
    files_html = (f'<div class="try-files"><p class="eyebrow on-dark">Files from this project</p><div class="pills">{chips}</div></div>'
                  if chips else "")
    twocol_inner = (f'<div><h3 class="mini">In this project</h3><p>{e(clean(m.get("story", "")))}</p></div>'
                    f'<div><h3 class="mini">Ideas for your own work</h3><ul class="uses">{uses}</ul></div>')
    if side:
        twocol = f'<div class="twocol side">{card(app, side)}<div class="stack">{twocol_inner}</div></div>'
    else:
        twocol = f'<div class="twocol">{twocol_inner}</div>'
    return f'''
<section class="app" id="{app}" style="--c:{color}">
  <div class="wrap">
    <div class="app-hero">
      <div class="app-text">
        <div class="product">{icon(app, 48)}<span><b>{name}</b><small>{e(cat)} · like {e(equiv)}</small></span></div>
        <p class="eyebrow">{num:02d} of 12 · {made} of {len(vis)} files made by the apps</p>
        <h2>{e(headline)}</h2>
        <p class="lead">{e(clean(m.get("summary", "")))}</p>
        <a class="btn sm" href="{SITE}/{app}" target="_blank" rel="noopener">Get {name}, free</a>
      </div>
      <div class="app-media">{feat_html}</div>
    </div>
    {twocol}
    {grid}
    <div class="try">
      <div class="try-l">
        <p class="eyebrow on-dark">Try it: describe the result</p>
        <p class="ask">“{e(ASK[app])}”</p>
      </div>
      <div class="try-c">
        <p class="try-sub">The app runs commands such as these. A script or an AI assistant can write them for you.</p>
        <pre class="code">{e(recipe)}</pre>
      </div>
      {files_html}
    </div>
  </div>
</section>'''


def dataset_rows():
    with open(DATA / "llm_posts_2026.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    pick = sorted((r for r in rows if r["post_id"] in SAMPLE_IDS), key=lambda r: r["date"])
    cols = [("date", "Date"), ("platform", "Platform"), ("theme", "Theme"), ("sentiment", "Tone"), ("text", "Post (invented)")]
    head = "".join(f"<th>{t}</th>" for _, t in cols)
    body = "".join("<tr>" + "".join(f'<td class="c-{c}">{e(r[c])}</td>' for c, _ in cols) + "</tr>" for r in pick)
    return len(rows), f'<div class="table"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def share_chart():
    """Small inline SVG of the 2 key themes (drawn by this page, from summary.json)."""
    s = json.loads((DATA / "summary.json").read_text(encoding="utf-8"))
    sh = s["share_pct_by_month_theme"]
    series = [("Agentic coding", "#3b63fb", ["Agentic coding"]), ("Reasoning & test-time compute", "#8f8f8f", ["Reasoning &", "test-time compute"])]
    W, H, L, R, T, B = 540, 210, 34, 140, 12, 26
    ymax = 25
    x = lambda i: L + i * (W - L - R) / (len(sh) - 1)
    y = lambda v: T + (H - T - B) * (1 - v / ymax)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Share of the conversation per month. Agentic coding increases from 9% to 20%. Reasoning and test-time compute decreases from 18% to 6%.">']
    for v in (0, 10, 20):
        out.append(f'<line x1="{L}" x2="{W - R}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="gl"/><text x="{L - 6}" y="{y(v) + 4:.1f}" class="ax" text-anchor="end">{v}%</text>')
    for i, lab in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]):
        out.append(f'<text x="{x(i):.1f}" y="{H - 6}" class="ax" text-anchor="middle">{lab}</text>')
    for th, col, short in series:
        v = [r[th] for r in sh]
        pts = " ".join(f"{x(i):.1f},{y(t):.1f}" for i, t in enumerate(v))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
        for i in (0, len(v) - 1):
            out.append(f'<circle cx="{x(i):.1f}" cy="{y(v[i]):.1f}" r="4" fill="{col}"/>')
        lx, ly = x(len(v) - 1) + 9, y(v[-1]) + 4 - 8 * (len(short) - 1)
        spans = "".join(f'<tspan x="{lx:.1f}" dy="{0 if j == 0 else 15}">{e(t)}{(" " + format(v[-1], ".0f") + "%") if j == len(short) - 1 else ""}</tspan>'
                        for j, t in enumerate(short))
        out.append(f'<text x="{lx:.1f}" y="{ly:.1f}" class="lab" fill="{col}">{spans}</text>')
    out.append("</svg>")
    return "".join(out)


def mosaic():
    tiles = []
    for app, f in MOSAIC:
        if not (ASSETS / app / f).exists():
            continue
        rel = f"assets/{app}/{f}"
        if app == "soundcraft":
            tiles.append(f'<a class="mt sound" href="#{app}" aria-label="SoundCraft: listen to the data as music">'
                         f'<b aria-hidden="true">♪</b><em>Listen: the data as a 20-second tune</em>'
                         f'<span>{icon(app, 24, "ticon")}{APPS[app][0]}</span></a>')
            continue
        media = (video_html(app, {"file": f}, autoplay=True, controls=False) if f.endswith(".mp4")
                 else f'<img src="{e(rel)}" alt="" style="object-position:{"0 0" if f in TOP_CROP else ("50% 50%" if f in CENTER_CROP else "0 50%")}">')
        tiles.append(f'<a class="mt" href="#{app}" aria-label="{APPS[app][0]}: see what it made">{media}'
                     f'<span>{icon(app, 24, "ticon")}{APPS[app][0]}</span></a>')
    return f'<div class="mosaic">{"".join(tiles)}</div>'


def provenance(manifests):
    rows = []
    for app in ORDER:
        m = manifests.get(app)
        if not m:
            continue
        for a in visible(m):
            maker = by_app(a, app)
            rows.append(
                f'<tr><td class="pa">{icon(app, 20, "ticon")}{APPS[app][0]}</td>'
                f'<td class="pf"><a href="assets/{app}/{e(a["file"])}">{e(a["file"])}</a></td>'
                f'<td class="{"y" if maker else "n"}">{APPS[maker][0] if maker else "App + script"}</td>'
                f'<td>{e(clean(a.get("description") or a.get("caption", "")))}</td></tr>')
    return ('<div class="table"><table class="prov"><thead><tr><th>Section</th><th>File</th><th>Made by</th>'
            '<th>How it was made</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")


def builder_notes(manifests):
    items = []
    for app in ORDER:
        m = manifests.get(app)
        if m and m.get("headless_notes"):
            items.append(f'<div class="bn">{icon(app, 24, "ticon")}<p><b>{APPS[app][0]}.</b> {e(clean(m["headless_notes"]))}</p></div>')
    return f'<div class="bnotes">{"".join(items)}</div>'


CSS = r"""
@font-face{font-family:"Source Sans 3";src:url(assets/_site/SourceSans3VF-Upright.woff2) format("woff2");font-weight:200 900;font-display:swap}
:root{
 /* adobe.com C2 tokens (s2a) */
 --gray-25:#fff;--gray-50:#f8f8f8;--gray-75:#f3f3f3;--gray-100:#e9e9e9;--gray-300:#dadada;--gray-600:#717171;--gray-800:#292929;--gray-900:#131313;--gray-1000:#000;
 --blue-900:#3b63fb;--blue-1000:#274dea;--blue-1100:#1d3ecf;
 --subtle:rgb(0 0 0/64%);--subtle-dark:rgb(255 255 255/64%);--eyebrow-dark:rgb(255 255 255/48%);
 --r-xs:8px;--r-sm:12px;--r-md:16px;--r-lg:22px;--r-xl:32px;
 --s4:4px;--s8:8px;--s12:12px;--s16:16px;--s24:24px;--s32:32px;--s40:40px;--s48:48px;--s64:64px;
 --layout-sm:80px;--layout-md:96px;--layout-lg:128px;
 --ease:cubic-bezier(.42,0,0,1);
 --shadow-1:0 1px 6px rgb(0 0 0/12%);--shadow-3:0 4px 12px rgb(0 0 0/16%);
 --body:"Adobe Clean","Source Sans 3",adobe-clean,"Trebuchet MS",sans-serif;
 --display:"Adobe Clean Display","Source Sans 3",adobe-clean-display,"Arial Black",sans-serif;
 --mono:ui-monospace,"Cascadia Mono",Consolas,monospace;
 --nav-h:64px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:calc(var(--nav-h) + 8px)}
body{margin:0;font:400 16px/20px var(--body);color:var(--gray-1000);background:var(--gray-25);-webkit-font-smoothing:antialiased;overflow-wrap:break-word}
img{max-width:100%;height:auto}
a{color:inherit}
h1,h2,h3,h4{margin:0;font-family:var(--display);font-weight:900}
.wrap{max-width:1280px;margin:0 auto;padding:0 var(--s32)}
.eyebrow{font:700 16px/20px var(--body);color:var(--subtle);margin:0 0 var(--s12)}
.eyebrow.on-dark{color:var(--eyebrow-dark)}
.lead{font-size:20px;line-height:28px}
/* nav */
nav.gnav{position:sticky;top:0;z-index:30;height:var(--nav-h);background:rgb(255 255 255/94%);backdrop-filter:blur(16px);border-bottom:1px solid var(--gray-100)}
nav.gnav .wrap{display:flex;align-items:center;gap:var(--s24);height:100%}
.brand{font:900 20px/1 var(--display);letter-spacing:-.4px;text-decoration:none;display:flex;align-items:center;gap:10px}
.brand i{display:inline-grid;grid-template-columns:repeat(2,8px);gap:2px}.brand i b{width:8px;height:8px;border-radius:2px}
.navlinks{display:flex;gap:var(--s24);font:700 14px/18px var(--body)}
.navlinks a{text-decoration:none;color:var(--gray-800)}.navlinks a:hover{color:var(--gray-1000);text-decoration:underline;text-underline-offset:4px}
.navend{margin-left:auto;display:flex;gap:var(--s8)}
/* buttons (con-button) */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;height:40px;padding:0 24px;border-radius:999px;border:2px solid var(--gray-1000);font:700 14px/18px var(--body);text-decoration:none;color:var(--gray-1000);background:transparent;transition:background-color .3s var(--ease),color .3s var(--ease),border-color .3s var(--ease);cursor:pointer;white-space:nowrap}
.btn:hover{background:rgb(0 0 0/8%)}
.btn.sm{height:32px;padding:0 16px;font-size:13px}
.btn.fill{background:var(--gray-1000);color:#fff}.btn.fill:hover{background:rgb(0 0 0/64%);border-color:transparent}
.btn.blue{background:var(--blue-900);border-color:var(--blue-900);color:#fff}.btn.blue:hover{background:var(--blue-1000);border-color:var(--blue-1000)}
.btn.white{background:#fff;border-color:#fff;color:#000}.btn.white:hover{background:rgb(255 255 255/64%)}
.btn.ghost{border-color:#fff;color:#fff}.btn.ghost:hover{background:rgb(255 255 255/12%)}
.btn:focus-visible,.zoom:focus-visible,a:focus-visible,input:focus-visible{outline:2px solid var(--blue-900);outline-offset:2px}
/* hero */
.hero{background:var(--gray-1000);color:#fff;padding:var(--layout-sm) 0 var(--s64);overflow:hidden}
.hero-grid{display:grid;grid-template-columns:5fr 6fr;gap:var(--s64);align-items:center}
.hero h1{font-size:80px;line-height:76px;letter-spacing:-3.2px;margin-bottom:var(--s24)}
.hero h1 span{color:var(--blue-900)}
.hero .lead{color:rgb(255 255 255/88%);max-width:560px;margin:0 0 var(--s32)}
.actions{display:flex;flex-wrap:wrap;gap:var(--s8)}
.mosaic{display:grid;grid-template-columns:repeat(4,1fr);gap:var(--s8)}
.mt{position:relative;display:block;aspect-ratio:1/1;border-radius:var(--r-sm);overflow:hidden;background:#1a1a1a}
.mt img,.mt video{width:100%;height:100%;object-fit:cover;object-position:0 50%;display:block;transition:transform .75s ease}
.mt:hover img,.mt:hover video{transform:scale(1.05)}
.mt.sound{background:linear-gradient(160deg,#0f4c57,#14a9c4);display:grid;place-items:center;text-decoration:none;color:#fff;padding:12px;text-align:center}
.mt.sound b{font-size:44px;line-height:1}.mt.sound em{font:700 12px/15px var(--body);font-style:normal;margin-top:-30px}
.mt span{position:absolute;left:6px;bottom:6px;display:inline-flex;align-items:center;gap:5px;font:700 11px/14px var(--body);color:#fff;background:rgb(0 0 0/72%);backdrop-filter:blur(8px);padding:3px 8px 3px 3px;border-radius:999px}
.facts{display:grid;grid-template-columns:repeat(4,1fr);gap:var(--s24);margin-top:var(--s64);padding-top:var(--s24);border-top:1px solid rgb(255 255 255/16%)}
.facts div{font:900 40px/40px var(--display);letter-spacing:-1px}.facts small{display:block;font:400 14px/18px var(--body);letter-spacing:0;color:var(--subtle-dark);margin-top:8px}
/* sections */
.sec{padding:var(--layout-md) 0}
.sec.subtle{background:var(--gray-50)}
.sec.dark{background:var(--gray-1000);color:#fff}
.sec-title{max-width:840px;margin-bottom:var(--s48)}
.sec-title h2{font-size:56px;line-height:56px;letter-spacing:-1.68px;margin-bottom:var(--s16)}
/* how it works */
.request{background:var(--gray-1000);color:#fff;border-radius:var(--r-lg);padding:var(--s40);display:grid;grid-template-columns:7fr 5fr;gap:var(--s48);margin-bottom:var(--s16)}
.msg{max-width:92%;border-radius:var(--r-md);padding:var(--s16) var(--s24);margin-bottom:var(--s12);font-size:17px;line-height:24px}
.msg p{margin:0}.msg .who{display:block;font:700 12px/16px var(--body);color:var(--eyebrow-dark);margin-bottom:4px}
.msg.you{background:var(--blue-900);margin-left:auto;border-bottom-right-radius:4px}.msg.you .who{color:rgb(255 255 255/72%)}
.msg.ai{background:rgb(255 255 255/10%);border-bottom-left-radius:4px}
.facts-list{list-style:none;margin:var(--s24) 0 0;padding:0}.facts-list li{padding:var(--s12) 0;border-top:1px solid rgb(255 255 255/12%);font-size:15px;line-height:21px;color:var(--subtle-dark)}.facts-list b{color:#fff;display:block}
.pause{text-align:center;font-size:13px;color:var(--eyebrow-dark);margin:var(--s16) 0}
.outputs ul{list-style:none;margin:0;padding:0}
.outputs li a{display:grid;grid-template-columns:24px 104px 1fr;gap:10px;align-items:center;padding:7px 0;border-top:1px solid rgb(255 255 255/12%);text-decoration:none;font-size:14px;line-height:18px}
.outputs li:first-child a{border-top:0}.outputs li b{font-weight:700}.outputs li span{color:var(--subtle-dark)}
.outputs li a:hover span{color:#fff}
.outputs img.ticon{width:24px;height:24px;border-radius:6px}
.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:var(--s16)}
.step{background:var(--gray-25);border-radius:var(--r-md);padding:var(--s32);box-shadow:var(--shadow-1)}
.step .k{font:900 48px/48px var(--display);color:var(--blue-900);letter-spacing:-1.44px}
.step h3{font-size:24px;line-height:28px;letter-spacing:-.96px;margin:var(--s16) 0 var(--s8)}
.step p{margin:0;color:var(--subtle);font-size:16px;line-height:24px}
.step a{font-weight:700}
/* app tiles by act */
.acts{display:grid;grid-template-columns:1fr 2fr 3fr;gap:var(--s16)}
.acts2{display:grid;grid-template-columns:2fr 3fr 1fr;gap:var(--s16);margin-top:var(--s16)}
.act{background:var(--gray-25);border-radius:var(--r-md);padding:var(--s24);box-shadow:var(--shadow-1)}
.act h3{font:700 14px/18px var(--body);color:var(--subtle);margin-bottom:var(--s16)}
.act h3 b{color:var(--gray-1000);margin-right:6px}
.tiles{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:var(--s16)}
.tile{display:flex;flex-direction:column;gap:10px;text-decoration:none;padding:var(--s8);margin:calc(-1*var(--s8));border-radius:var(--r-sm);transition:background-color .3s var(--ease)}
.tile:hover{background:var(--gray-75)}
.tile img{border-radius:14px;transition:transform .75s ease}.tile:hover img{transform:scale(1.04)}
.tile b{font:900 20px/24px var(--display);letter-spacing:-.4px}
.tile small{font-size:14px;line-height:18px;color:var(--subtle)}
/* project */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:var(--s16);margin-bottom:var(--s48)}
.stat{background:var(--gray-25);border-radius:var(--r-md);padding:var(--s24) var(--s24) var(--s32);box-shadow:var(--shadow-1)}
.stat .n{font:900 48px/48px var(--display);letter-spacing:-1.44px;color:var(--blue-900);white-space:nowrap}
.stat .n.neutral{color:var(--gray-1000)}
.stat p{margin:var(--s12) 0 0;font-size:16px;line-height:22px}
.stat small{display:block;margin-top:var(--s8);color:var(--subtle);font-size:13px;line-height:18px}
.split{display:grid;grid-template-columns:5fr 7fr;gap:var(--s48);align-items:start}
.chartcard{background:#fff;border-radius:var(--r-md);padding:var(--s24);box-shadow:var(--shadow-1)}
.chartcard h3{font:900 24px/24px var(--display);letter-spacing:-.96px;margin-bottom:6px}
.chartcard p{margin:0 0 var(--s12);color:var(--subtle);font-size:14px;line-height:18px}
svg .gl{stroke:var(--gray-100)}svg .ax{font:12px var(--body);fill:var(--gray-600)}svg .lab{font:700 13px var(--body)}
.method{font-size:16px;line-height:24px}
.method p{margin:0 0 var(--s16)}
.links{display:flex;flex-wrap:wrap;gap:var(--s8);margin-top:var(--s24)}
.gloss{display:grid;grid-template-columns:repeat(2,1fr);gap:0 var(--s48);margin:0}
.gloss div{display:grid;grid-template-columns:220px 1fr;gap:var(--s16);padding:var(--s12) 0;border-top:1px solid var(--gray-100);font-size:15px;line-height:20px}
.gloss dt{font-weight:700}.gloss dd{margin:0;color:var(--subtle)}
.table{overflow-x:auto;border-radius:var(--r-md);background:#fff;box-shadow:var(--shadow-1)}
table{border-collapse:collapse;width:100%;font-size:14px;line-height:18px}
th,td{padding:12px 16px;text-align:left;vertical-align:top;border-bottom:1px solid var(--gray-100)}
th{font-weight:700;color:var(--subtle);background:var(--gray-75)}
tr:last-child td{border-bottom:0}
td.c-date,td.c-platform,td.c-sentiment{white-space:nowrap}
/* app sections */
section.app{padding:var(--layout-md) 0;border-top:1px solid var(--gray-100)}
section.app:nth-of-type(even){background:var(--gray-50)}
.app-hero{display:grid;grid-template-columns:5fr 7fr;gap:var(--s64);align-items:center}
.product{display:flex;align-items:center;gap:var(--s12);margin-bottom:var(--s32)}
.product img{border-radius:12px}
.product span{display:flex;flex-direction:column}
.product b{font:900 20px/24px var(--display);letter-spacing:-.4px}
.product small{font-size:14px;line-height:18px;color:var(--subtle)}
.app h2{font-size:48px;line-height:48px;letter-spacing:-1.44px;margin-bottom:var(--s24)}
.app-text .lead{margin:0 0 var(--s24)}
.twocol{display:grid;grid-template-columns:1fr 1fr;gap:var(--s64);margin-top:var(--s48)}
.twocol p{margin:0;font-size:16px;line-height:24px}
.mini{font:700 14px/18px var(--body);margin:0 0 var(--s8);padding-top:var(--s16);border-top:2px solid var(--c)}
.uses{margin:0;padding-left:20px;font-size:16px;line-height:24px}.uses li{margin:4px 0}
.feature{margin:0}
.feature>button.zoom img,.feature>video{width:100%;display:block;border-radius:var(--r-md);background:var(--gray-75);box-shadow:var(--shadow-1)}
.feature>video{background:#111}
.feature figcaption,.cbody{font-size:14px;line-height:20px;color:var(--subtle)}
.feature figcaption{margin-top:var(--s12)}
.feature figcaption b{color:var(--gray-1000)}
.feature.audio{margin-top:var(--s24)}
.tag{display:inline-flex;align-items:center;gap:6px;font:700 12px/16px var(--body);padding:3px 10px 3px 4px;border-radius:999px;vertical-align:middle;margin-top:6px;white-space:nowrap}
.tag.made{background:color-mix(in srgb,var(--c) 14%,#fff);color:var(--gray-1000)}
.tag.other{background:var(--gray-100);color:var(--gray-800);padding-left:10px}
.tag img.ticon,td img.ticon,.mt img.ticon{width:16px;height:16px;display:inline-block;border-radius:4px;vertical-align:middle;background:none;transform:none!important}
td img.ticon{width:20px;height:20px}.mt img.ticon{width:18px;height:18px;object-fit:contain}
.cards{display:grid;gap:var(--s32) var(--s24);margin-top:var(--s48)}
.cards.c3{grid-template-columns:repeat(3,1fr)}.cards.c2{grid-template-columns:repeat(2,1fr)}
.card{display:flex;flex-direction:column;gap:var(--s16);min-width:0}
.cards.c3 .card.wide{grid-column:span 2}.cards.c2 .card.wide{grid-column:1/-1}
.cards.c3 .card.wide:last-child{grid-column:1/-1}
.card.full{grid-column:1/-1;display:grid;grid-template-columns:7fr 5fr;gap:var(--s32);align-items:center}
.twocol.side{grid-template-columns:5fr 6fr;align-items:start}.stack{display:flex;flex-direction:column;gap:var(--s32)}
ul.answers{list-style:none;margin:0;padding:var(--s24);background:var(--gray-75);border-radius:var(--r-md);display:grid;grid-template-columns:1fr 1fr;gap:var(--s16) var(--s32)}
ul.answers li{font:900 22px/26px var(--display);letter-spacing:-.4px;padding-left:var(--s16);border-left:3px solid var(--c)}
blockquote.extract{margin:0;padding:var(--s24) var(--s32);background:var(--gray-75);border-radius:var(--r-md);font-size:15px;line-height:22px;color:var(--gray-800)}
blockquote.extract p{margin:0 0 6px}blockquote.extract p:first-child{font:900 20px/24px var(--display)}
.cmedia{position:relative;border-radius:var(--r-md);overflow:hidden;background:var(--gray-75);aspect-ratio:16/10}
.card.wide .cmedia{aspect-ratio:21/9}
.cmedia>button.zoom{position:absolute;inset:0}
.cmedia img{width:100%;height:100%;object-fit:contain;display:block;transition:transform .75s ease}
.card:hover .cmedia img{transform:scale(1.03)}
.cmedia.vid{aspect-ratio:auto;background:#111}.cmedia video{width:100%;display:block}
.card h4{font:700 18px/22px var(--body);color:var(--gray-1000);margin-bottom:6px}
.card p{margin:0}
button.zoom{all:unset;cursor:zoom-in;display:block;position:relative}
.zi{position:absolute;right:10px;top:10px;width:30px;height:30px;border-radius:999px;background:rgb(0 0 0/56%);color:#fff;display:grid;place-items:center;font-size:15px;opacity:.75;transition:opacity .3s var(--ease)}
button.zoom:hover .zi,button.zoom:focus-visible .zi{opacity:1}
.vwrap{position:relative}.vwrap video{width:100%;display:block;border-radius:var(--r-md);background:#111;box-shadow:var(--shadow-1)}
.play{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:72px;height:72px;border-radius:999px;border:0;background:rgb(255 255 255/92%);color:#000;font-size:26px;padding-left:6px;cursor:pointer;box-shadow:var(--shadow-3);transition:transform .3s var(--ease)}
.play:hover{transform:translate(-50%,-50%) scale(1.06)}.vwrap.on .play{display:none}
.compare{position:relative;border-radius:var(--r-md);overflow:hidden;background:var(--gray-75);--pos:50%}
.compare img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}
.compare img.before{clip-path:inset(0 calc(100% - var(--pos)) 0 0)}
.compare .divider{position:absolute;top:0;bottom:0;left:var(--pos);width:3px;margin-left:-1.5px;background:#fff;box-shadow:0 0 8px rgb(0 0 0/40%);pointer-events:none}
.compare .divider::after{content:"⇆";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:40px;height:40px;border-radius:999px;background:#fff;color:#000;display:grid;place-items:center;font-size:18px;box-shadow:var(--shadow-3)}
.compare input{position:absolute;inset:0;width:100%;height:100%;opacity:0;cursor:ew-resize;margin:0}
.compare .cl{position:absolute;top:12px;font:700 12px/16px var(--body);color:#fff;background:rgb(0 0 0/56%);padding:4px 10px;border-radius:999px;pointer-events:none}
.compare .cl.l{left:12px}.compare .cl.r{right:12px}
.player{display:flex;align-items:center;gap:var(--s16);background:var(--gray-1000);border-radius:var(--r-md);padding:var(--s16) var(--s24)}
.pl-ico{color:var(--c);font-size:28px}.player audio{flex:1;min-width:0}
pre.code{margin:0;font:13px/20px var(--mono);background:var(--gray-900);color:#e8e8e8;border-radius:var(--r-sm);padding:var(--s16) var(--s24);overflow:auto;white-space:pre-wrap;word-break:break-word;max-height:360px}
pre.code.light{background:var(--gray-75);color:var(--gray-900)}
.try{display:grid;grid-template-columns:5fr 6fr;gap:var(--s24) var(--s48);margin-top:var(--s64);background:var(--gray-1000);color:#fff;border-radius:var(--r-lg);padding:var(--s40)}
.try-files{grid-column:1/-1;border-top:1px solid rgb(255 255 255/16%);padding-top:var(--s24)}
.try-files .pills{flex-direction:row;flex-wrap:wrap}.try-files .pill.sm{flex:1 1 300px;max-width:520px}
.ask{font:900 28px/34px var(--display);letter-spacing:-.6px;margin:0 0 var(--s24)}
.try-sub{font-size:14px;line-height:20px;color:var(--subtle-dark);margin:0 0 var(--s12)}
.try pre.code{background:rgb(255 255 255/8%);color:rgb(255 255 255/72%);font-size:12px;line-height:18px}
.pills{display:flex;flex-direction:column;gap:var(--s8)}
.pill.sm{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:var(--s12);text-decoration:none;border:2px solid rgb(255 255 255/24%);border-radius:var(--r-sm);padding:10px 16px;font:400 13px/18px var(--body);color:#fff;transition:background-color .3s var(--ease),border-color .3s var(--ease)}
.pill.sm:hover{background:rgb(255 255 255/12%);border-color:#fff}
.pill.sm b{font-weight:700;font-size:12px}
.pill.sm span{color:rgb(255 255 255/80%)}.pill.sm i{font-style:normal;color:#ffc15e}
.pill.sm small{color:var(--eyebrow-dark);white-space:nowrap}
/* ideas */
.ideas{display:grid;grid-template-columns:repeat(4,1fr);gap:var(--s16)}
.idea{border:1px solid rgb(255 255 255/16%);border-radius:var(--r-md);padding:var(--s24)}
.idea h3{font-size:20px;line-height:24px;letter-spacing:-.4px;margin-bottom:var(--s8)}
.idea p{margin:0 0 var(--s16);color:var(--subtle-dark);line-height:22px}
.idea .req{font:700 15px/21px var(--body);color:#fff;border-left:3px solid var(--blue-900);padding-left:12px}
.idea .row{display:flex;flex-wrap:wrap;gap:6px 12px}.idea .row span{display:inline-flex;align-items:center;gap:6px;font-size:13px;color:var(--subtle-dark)}.idea .row img{border-radius:6px}
.sec.dark .sec-title .lead{color:var(--subtle-dark)}
.prov td.y{color:#05834e;font-weight:700;white-space:nowrap}.prov td.n{color:var(--gray-800);font-weight:700;white-space:nowrap}
.prov td.pa{white-space:nowrap;font-weight:700}.prov td.pa img{margin-right:8px}
.prov td.pf{min-width:230px}
details.builders{margin-top:var(--s64);border-top:1px solid var(--gray-100);padding-top:var(--s24)}
details.builders summary{cursor:pointer;font:900 24px/28px var(--display);letter-spacing:-.6px}
details.builders summary small{display:block;font:400 16px/22px var(--body);letter-spacing:0;color:var(--subtle);margin-top:4px}
.bnotes{columns:2;column-gap:var(--s48);margin-top:var(--s32)}
.bn{display:flex;gap:var(--s12);break-inside:avoid;margin-bottom:var(--s24);font-size:14px;line-height:20px;color:var(--subtle)}.bn p{margin:0}.bn b{color:var(--gray-1000)}.bn img.ticon{width:24px;height:24px;flex:none;margin-top:2px}
footer{background:var(--gray-1000);color:var(--subtle-dark);padding:var(--s64) 0;font-size:14px;line-height:20px}
footer p{margin:0 0 var(--s8);max-width:900px}footer b{color:#fff}
#lb{position:fixed;inset:0;background:rgb(0 0 0/92%);display:none;align-items:center;justify-content:center;flex-direction:column;gap:var(--s16);z-index:60;padding:var(--s24)}
#lb.on{display:flex}#lb img{max-width:94vw;max-height:84vh;border-radius:var(--r-sm);background:#fff}
#lb p{color:#fff;margin:0;max-width:900px;text-align:center}
#lb .x{position:absolute;top:var(--s16);right:var(--s16)}
@media (max-width:1100px){.acts,.acts2{grid-template-columns:1fr 1fr}.ideas{grid-template-columns:1fr 1fr}.stats{grid-template-columns:1fr 1fr}.gloss{grid-template-columns:1fr}}
@media (max-width:900px){
 .wrap{padding:0 var(--s24)}
 .hero-grid,.split,.app-hero,.try,.twocol,.twocol.side,.request{grid-template-columns:1fr}ul.answers{grid-template-columns:1fr}
 .hero h1{font-size:56px;line-height:54px;letter-spacing:-1.68px}
 .sec-title h2{font-size:40px;line-height:40px;letter-spacing:-1px}
 .app h2{font-size:36px;line-height:36px;letter-spacing:-1px}
 .cards.c3{grid-template-columns:1fr 1fr}.steps{grid-template-columns:1fr 1fr}.facts{grid-template-columns:1fr 1fr}
 .navlinks{display:none}.bnotes{columns:1}.gloss div{grid-template-columns:1fr;gap:2px}
}
@media (max-width:600px){.steps,.acts,.acts2,.ideas,.stats,.cards.c3,.cards.c2{grid-template-columns:1fr}.card.wide,.cards.c3 .card.wide{grid-column:auto}.tiles{grid-auto-flow:row;grid-template-columns:1fr 1fr}.mosaic{grid-template-columns:repeat(3,1fr)}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}
"""

JS = r"""
const lb=document.getElementById('lb'),li=lb.querySelector('img'),lp=lb.querySelector('p'),lx=lb.querySelector('.x');let last=null;
document.querySelectorAll('button.zoom').forEach(b=>b.addEventListener('click',()=>{last=b;li.src=b.dataset.src;li.alt=b.dataset.cap;lp.textContent=b.dataset.cap;lb.classList.add('on');lx.focus();}));
function closeLb(){lb.classList.remove('on');li.removeAttribute('src');if(last)last.focus();}
lb.addEventListener('click',ev=>{if(ev.target!==li)closeLb();});
document.addEventListener('keydown',ev=>{if(ev.key==='Escape'&&lb.classList.contains('on'))closeLb();});
document.querySelectorAll('.compare input').forEach(r=>{const c=r.closest('.compare');const f=()=>c.style.setProperty('--pos',r.value+'%');r.addEventListener('input',f);f();});
document.querySelectorAll('.vwrap').forEach(w=>{const v=w.querySelector('video'),b=w.querySelector('.play');b.addEventListener('click',()=>{w.classList.add('on');v.controls=true;v.muted=false;v.play();v.focus();});});
if(matchMedia('(prefers-reduced-motion: reduce)').matches)document.querySelectorAll('video[autoplay]').forEach(v=>{v.removeAttribute('autoplay');v.pause();});
"""


def main():
    manifests = {a: m for a in ORDER if (m := load(a))}
    vis_all = [(a, x) for a, m in manifests.items() for x in visible(m)]
    total = len(vis_all)
    made = sum(1 for a, x in vis_all if by_app(x, a))
    n_rows, table = dataset_rows()

    def tiles(apps):
        return "".join(f'<a class="tile" href="#{a}">{icon(a, 64)}<b>{APPS[a][0]}</b><small>like {e(APPS[a][2])}</small></a>' for a in apps)
    act_html = [f'<div class="act"><h3><b>{i + 1}</b>{e(t)}</h3><div class="tiles">{tiles(apps)}</div></div>'
                for i, (t, apps) in enumerate(ACTS)]
    sections = "".join(app_section(a, i + 1) for i, a in enumerate(ORDER))
    ideas = "".join(
        f'<div class="idea"><h3>{e(t)}</h3><p>{e(d)}</p><p class="req">“{e(r)}”</p>'
        f'<div class="row">{"".join(f"<span>{icon(a, 24)}{APPS[a][0]}</span>" for a in apps)}</div></div>'
        for t, d, apps, r in IDEAS)
    outputs = "".join(f'<li><a href="#{a}">{icon(a, 24, "ticon")}<b>{APPS[a][0]}</b><span>{e(t)}</span></a></li>' for a, t in OUTPUTS)
    gloss = "".join(f"<div><dt>{e(t)}</dt><dd>{e(d)}</dd></div>" for t, d in GLOSSARY)
    brand_dots = "".join(f'<b style="background:{APPS[a][3]}"></b>' for a in ("gridcraft", "vectorcraft", "photocraft", "filmcraft"))

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Craft suite showcase: 12 free apps, 1 project</title>
<meta name="description" content="The 12 free Craft apps made 1 research project: data, charts, report, slides, images, sound and video, all from typed commands.">
<style>{CSS}</style></head><body>
<nav class="gnav" aria-label="Main"><div class="wrap">
  <a class="brand" href="#top"><i aria-hidden="true">{brand_dots}</i>Craft suite</a>
  <div class="navlinks"><a href="#how">How it works</a><a href="#apps">The apps</a><a href="#project">The project</a><a href="#ideas">Ideas</a><a href="#sources">Sources</a></div>
  <div class="navend"><a class="btn blue" href="{SITE}" target="_blank" rel="noopener">Get the apps, free</a></div>
</div></nav>

<header class="hero" id="top"><div class="wrap">
  <div class="hero-grid">
    <div>
      <p class="eyebrow on-dark">Craft suite showcase</p>
      <h1>12 apps.<br>1 project.<br><span>All scripted.</span></h1>
      <p class="lead">The 12 free Craft apps made a complete research project: the data, charts, report, slides, photos, sound and video. Each app also works from typed commands. A script or an AI assistant can run the full chain, and no app window opens.</p>
      <div class="actions"><a class="btn white" href="#how">See how it works</a><a class="btn ghost" href="#apps">Meet the 12 apps</a></div>
    </div>
    {mosaic()}
  </div>
  <div class="facts">
    <div>{total}<small>files on this page. {made} came directly from the apps.</small></div>
    <div>12<small>apps. Each one has a command-line tool for typed commands.</small></div>
    <div>Free<small>All 12 apps are open source. They run on Windows, macOS and Linux.</small></div>
    <div>0<small>app windows opened. All work ran in the background while a person used the same PC.</small></div>
  </div>
</div></header>

<section class="sec subtle" id="how"><div class="wrap">
  <div class="sec-title">
    <p class="eyebrow">How it works</p>
    <h2>Every app works from typed commands.</h2>
    <p class="lead">Each Craft app has a command-line tool: a way to control the app with typed commands. A script can run these commands. An AI assistant can also write them for you. The result is normal files that you can open and change.</p>
  </div>
  <div class="request">
    <div class="chat">
      <p class="eyebrow on-dark">The request for this page, shortened</p>
      <div class="msg you"><span class="who">Request</span><p>Make a showcase page for all 12 Craft apps. Use 1 example: social media research on how AI language models developed in 2026. Make the media with the apps themselves. Run everything in the background.</p></div>
      <ul class="facts-list">
        <li><b>Each app ran its own list of steps.</b> It read the files of the step before, then saved normal files: Excel, Word, PowerPoint, PDF, PSD, MP4 and more.</li>
        <li><b>4 groups of 3 apps ran at the same time.</b> Each group made its first files in about 15 minutes.</li>
        <li><b>No app window opened.</b> All work ran in the background while a person used the same PC.</li>
        <li><b>The tools have limits.</b> The notes at the end of the page list more than 40 workarounds.</li>
      </ul>
    </div>
    <div class="outputs">
      <p class="eyebrow on-dark">What each app made</p>
      <ul>{outputs}</ul>
    </div>
  </div>
  <div class="steps">
    <div class="step"><div class="k">1</div><h3>Get the apps.</h3><p>Download the apps that you need from <a href="{SITE}" target="_blank" rel="noopener">getartcraft.com/apps</a>. They are free and open source. They run on Windows, macOS and Linux. The command-line tools come with the desktop versions.</p></div>
    <div class="step"><div class="k">2</div><h3>Script it, or let an assistant do it.</h3><p>Write the commands yourself, or use an AI assistant that can run programs on your computer, for example <a href="https://claude.com/claude-code" target="_blank" rel="noopener">Claude Code</a> or <a href="https://openai.com/codex/" target="_blank" rel="noopener">OpenAI Codex</a>. A chat in a web browser cannot do this. These assistants usually need a paid plan.</p></div>
    <div class="step"><div class="k">3</div><h3>Describe the result.</h3><p>Write down the topic, the audience and the formats. For example: a 4-page report, 7 slides and a 20-second video.</p></div>
    <div class="step"><div class="k">4</div><h3>Review and edit.</h3><p>The apps make the files in the background. Then you check the result. You can open each file in its app and change it.</p></div>
  </div>
</div></section>

<section class="sec" id="apps"><div class="wrap">
  <div class="sec-title">
    <p class="eyebrow">The apps</p>
    <h2>12 apps, 1 chain of work.</h2>
    <p class="lead">Each Craft app does the work of a familiar tool, such as Excel, Photoshop or Premiere Pro. Most apps use files from other apps. For example, DeckCraft uses the VectorCraft charts. Select an app to see what it made.</p>
  </div>
  <div class="acts">{"".join(act_html[:3])}</div>
  <div class="acts2">{"".join(act_html[3:])}</div>
</div></section>

<section class="sec subtle" id="project"><div class="wrap">
  <div class="sec-title">
    <p class="eyebrow">The example project</p>
    <h2>Signal &amp; Noise 2026</h2>
    <p class="lead">A small research team asks: how did social media talk about AI language models from January to September 2026? The team gives each post 1 of 10 themes. Then it measures each theme's share of the conversation.</p>
  </div>
  <div class="stats">
    <div class="stat"><div class="n">9% → 20%</div><p><b>AI that writes code</b> became the biggest theme.</p><small>Theme: Agentic coding</small></div>
    <div class="stat"><div class="n neutral">18% → 6%</div><p><b>AI that “thinks” longer</b> fell from the top theme to one of the smallest.</p><small>Theme: Reasoning &amp; test-time compute</small></div>
    <div class="stat"><div class="n">53%</div><p>of posts about <b>AI prices</b> are negative. The average for all themes is 23%.</p><small>Theme: Prices &amp; tokens</small></div>
    <div class="stat"><div class="n neutral">12%</div><p>was the peak for <b>AI laws and rules</b>, in July.</p><small>Theme: Regulation &amp; policy</small></div>
  </div>
  <div class="split">
    <div class="method">
      <h3 class="mini" style="--c:var(--blue-900)">How the team measured</h3>
      <p><b>Share of the conversation</b> is the number of posts about a theme, divided by all AI posts in that month.</p>
      <p>The sample has {n_rows} posts from 6 platforms. In this invented study, a person reads each post and gives it a theme and a tone. A real study takes a sample like this from a much larger stream of posts.</p>
      <p><b>All data on this page is invented:</b> the posts, the accounts and the research team. In the images, "hand-coded" means that a person of the invented team gave each post a theme. The {n_rows} posts reuse 30 example texts. No quote comes from a real person.</p>
      <div class="links"><a class="btn fill" href="data/llm_posts_2026.csv" download>Download the posts (CSV)</a><a class="btn" href="data/summary.json">Summary numbers (JSON)</a></div>
    </div>
    <div class="chartcard"><h3>2 themes changed places</h3><p>Share of the conversation per month, January to September 2026</p>{share_chart()}</div>
  </div>
  <div style="margin-top:var(--s48)">
    <h3 class="mini" style="--c:var(--blue-900)">The 10 themes in plain words</h3>
    <dl class="gloss">{gloss}</dl>
    <p style="color:var(--subtle);font-size:14px;margin:var(--s16) 0 0"><b>LLM</b> means large language model: the type of AI behind chat assistants such as ChatGPT and Claude. The images use this short form.</p>
  </div>
  <div style="margin-top:var(--s48)"><h3 class="mini" style="--c:var(--blue-900)">6 posts from the sample</h3>{table}</div>
</div></section>

<div id="walkthrough">{sections}</div>

<section class="sec dark" id="ideas"><div class="wrap">
  <div class="sec-title">
    <p class="eyebrow on-dark">Your next project</p>
    <h2>Start with 1 idea and 3 or 4 apps.</h2>
    <p class="lead">You do not need all 12 apps. Pick a project, get the apps for it and write the steps, or describe the result to an assistant.</p>
  </div>
  <div class="ideas">{ideas}</div>
  <div class="actions" style="margin-top:var(--s48)"><a class="btn white" href="{SITE}" target="_blank" rel="noopener">Get the apps, free</a><a class="btn ghost" href="#how">Read how it works</a></div>
</div></section>

<section class="sec" id="sources"><div class="wrap">
  <div class="sec-title">
    <p class="eyebrow">Sources</p>
    <h2>Which files did the apps make?</h2>
    <p class="lead">{made} of {total} files came directly from the apps. For the other {total - made}, a short Python script joined app output or drew a picture. An example is frames joined into a GIF.</p>
  </div>
  {provenance(manifests)}
  <details class="builders"><summary>Notes for people who write their own commands<small>Technical details for each command-line tool: what worked and what needed a workaround.</small></summary>{builder_notes(manifests)}</details>
</div></section>

<footer><div class="wrap">
  <p><b>Craft suite showcase.</b> Made on 11 October 2026 with the current versions of the 12 Craft apps. Every file came from the command-line tools of the apps, run in the background.</p>
  <p><b>Data.</b> All posts, accounts and numbers are invented, only for this example.</p>
  <p><b>Design.</b> The layout follows the public design system of adobe.com. Adobe did not make this page and has no connection to it. Font: Source Sans 3 by Adobe, free under the SIL Open Font License (<a href="assets/_site/OFL-SourceSans3.txt">license</a>). App icons: the Craft apps. Get the apps at <a href="{SITE}" target="_blank" rel="noopener">getartcraft.com/apps</a>.</p>
</div></footer>
<div id="lb" role="dialog" aria-modal="true" aria-label="Enlarged image"><button class="btn ghost x" aria-label="Close">Close</button><img alt=""><p></p></div>
<script>{JS}</script>
</body></html>"""
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print("wrote", ROOT / "index.html", f"{made}/{total} made by apps (visible)")


if __name__ == "__main__":
    main()
