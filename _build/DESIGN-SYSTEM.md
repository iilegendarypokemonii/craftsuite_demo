# Showcase design system (extracted from adobe.com, 11 Oct 2026)

## Source
- adobe.com runs on Adobe's open-source "Milo" framework. The homepage declares `foundation: c2`
  (the 2026 site redesign). The C2 tokens come from github.com/adobecom/milo, `libs/c2/styles/`:
  `deps/tokens.primitives.css`, `deps/tokens.semantic*.css`, `deps/tokens.responsive.*.css`,
  `s2a-tokens.css`, `styles.css`, and the block styles (base-card, explore-card, hover-list, marquee).
- Visual check: headless screenshots of adobe.com and adobe.com/products/photoshop.html.
- Token prefix on adobe.com: `--s2a-` ("Spectrum 2 for Adobe.com").

## Tokens used (values copied from the C2 token files)
| Group | Token | Value |
|---|---|---|
| Neutrals | gray-25 / 50 / 75 / 100 / 300 / 600 / 800 / 900 / 1000 | #fff / #f8f8f8 / #f3f3f3 / #e9e9e9 / #dadada / #717171 / #292929 / #131313 / #000 |
| Accent | blue-900 (button, focus ring) / 1000 hover / 1100 active | #3b63fb / #274dea / #1d3ecf |
| Text subtle | transparent-black-64 | rgb(0 0 0 / 64%) |
| Eyebrow on dark | transparent-white-48 | rgb(255 255 255 / 48%) |
| Radius | xs 8 / sm 12 / md 16 / lg 22 / xl 32 / round 999 | px |
| Spacing | 4 8 12 16 24 32 40 48 64 | px |
| Layout | sm 80 / md 96 / lg 128 / xl 160 | px (section padding) |
| Type scale (lg) | heading-1 80/76 −3.2px · heading-2 56/56 −1.68px · heading-3 48/48 −1.44px · heading-4 36/32 −1px · heading-5 24/24 −0.96px | size/line-height letter-spacing |
| Body | body-lg 20/24 · body-md 16/20 · body-sm 14/18 · label 14/18 bold · caption 12/16 bold · eyebrow 16/20 bold | |
| Weights | heading 900 (Display Black) · body 400 · label/eyebrow/caption 700 | |
| Shadow | level-1 0 1px 6px black-12 · level-3 0 4px 12px black-16 | |
| Motion | parallax easing cubic-bezier(0.42, 0, 0, 1); card image hover scale 1.03 over 0.75s | |
| Grid | margin 24px, gutter 8px, nav height 80px | |

## Components seen on adobe.com
- **Global nav**: white or transparent, bold 14px links, pill "Sign in" button.
- **Buttons** (`.con-button`): pill, 40px high, 2px border, 14px bold label, padding 0 24px.
  Variants: outline (black border), fill (black), blue (#3b63fb), white solid on dark.
- **Marquee / hero**: full-bleed media with dark scrim, bold eyebrow, display headline with tight tracking,
  body-lg paragraph, 1–2 pill buttons.
- **Product hero**: text left, media right. Product icon + product name label above the H1.
- **Feature rows**: media on one side; eyebrow (14px) + heading-4 + body on the other.
- **Card grid**: 3-up; media first with 16px radius (clip), heading 20px bold, body in subtle gray.
- **Centered section title** at heading-4 to heading-3 size, "Explore … features."
- Large white space; white and #f8f8f8 sections; black sections for drama.

## Adaptations for this page
- **Font**: Adobe Clean / Adobe Clean Display are licensed through Adobe Fonts and cannot be bundled.
  The page uses Adobe's open-source **Source Sans 3** (SIL OFL 1.1, file in assets/_site/) at weight 900
  for display and 400/700 for text. Fallbacks follow C2: "Adobe Clean" (if installed), then
  Source Sans 3, Trebuchet MS, Arial.
- **Product icons**: each Craft app's own icon (from `<app>/assets/app-icon/<app>.ico`), shown like
  Adobe's product tiles. Each app accent colour is sampled from its icon background.
- **Brand red (#eb1000)** is not used: this page is not an Adobe page.
- **Text**: ASD-STE100 Simplified Technical English (max 20 words per sentence, active voice).
