# ITHINK brand

## Company

**ITHINK** — always set in capitals in body copy and headings. Not "iThink",
not "Ithink".

Tagline: *Think beyond limits with ITHINK.* It appears inside the horizontal
logo lockup, so do not repeat it as a separate line next to that logo.

## Palette

Six colours. Nothing outside this list belongs in a document; if a new colour
seems necessary, derive it from one of these instead.

| Token | Hex | Role |
|---|---|---|
| `--blue` | `#377dff` | Primary. The mark, links, CTAs, accents, active states, chart series 1 |
| `--navy` | `#1a2138` | Headings, dark surfaces, footer bands, table headers |
| `--ink` | `#1e2022` | Body text |
| `--paper` | `#f7faff` | Page background |
| `--surface` | `#eeeeef` | Fills — table stripes, muted panels, disabled states, callout backgrounds |
| `--white` | `#ffffff` | Cards and content blocks sitting on `--paper` |

### Derived values — do not add new brand colours for these

```css
--line:        rgba(26, 33, 56, 0.12);  /* hairlines, dividers, card borders */
--line-strong: rgba(26, 33, 56, 0.24);  /* table rules, section breaks */
--ink-soft:    rgba(30, 32, 34, 0.64);  /* secondary text, captions, labels */
--ink-faint:   rgba(30, 32, 34, 0.44);  /* metadata, footnotes, page numbers */
--blue-soft:   rgba(55, 125, 255, 0.08); /* highlighted rows, quiet callouts */
```

`--surface` (`#eeeeef`) is a **fill, never a border**. Against `--paper` it is
roughly a 3% luminance step: invisible as a line on screen and gone entirely
on a laser printer. Borders always come from `--line`.

### Applying colour

- Blue carries meaning. Use it for the one thing on a page that matters most —
  the price, the CTA, the recommended option. A page where five things are
  blue has no emphasis at all.
- Navy is for structure: headings, the cover, table headers, the footer band.
- Never put `--ink` body text on `--navy`. On dark surfaces use white at 100%
  for headings and white at 72% for supporting copy.
- Semantic colours are not in the brand palette. When a document genuinely
  needs positive/negative signalling (savings versus cost, included versus
  excluded), use `#2e7d5b` and `#b0472f` sparingly, and never near the price.

## Typography

**Inter**, bundled in `assets/fonts/` as a variable font (weights 100–900),
three subsets: latin, latin-ext, cyrillic. Together 152 KB.

Never link Google Fonts from a document. Published artifacts run under a CSP
that blocks external hosts, so a linked font silently falls back to a system
font, and the document then looks like every other document. Inline the fonts
with `scripts/build_document.py`.

### Scale

| Role | Size / weight / tracking |
|---|---|
| Cover title | 44px / 700 / -0.02em |
| Section heading (h2) | 26px / 600 / -0.01em |
| Sub-heading (h3) | 18px / 600 |
| Body | 15px / 400 / 1.6 line-height |
| Table and dense copy | 14px / 400 |
| Label / eyebrow | 12px / 600 / uppercase / 0.08em |
| Figures and prices | tabular numerals, 600 |

Set `font-variant-numeric: tabular-nums` on every price, quantity and total.
Proportional digits make a column of numbers look ragged, which reads as
carelessness in a document about money.

Inter's default apostrophe is typographically wrong for Uzbek. Use `ʻ` (U+02BB)
in *oʻ* and *gʻ*, not `'` — the correct character is in the bundled latin
subset.

## Logos

Files live in `assets/logos/`, referenced from a document as
`@@LOGO:<filename-without-extension>@@`.

| File | When to use |
|---|---|
| `ithink-horizontal-color` | Default. Cover and document header, on light backgrounds |
| `ithink-horizontal-white` | On `--navy` and photography |
| `ithink-horizontal-mono` | Single-colour printing, faxable documents, stamps |
| `ithink-mark-color` | Favicon, avatar, tight corners, page-footer repeat |
| `ithink-mark-white` | The same on dark |
| `ithink-stacked` | Square or narrow placements, title slides |

**Only `ithink-horizontal-color` is present so far** (recovered from the ASLZAR
proposal, 1939×542, ratio 3.58). The other five names are reserved. If a
document calls for one that is missing, use the horizontal colour version and
say so, rather than distorting or recolouring an existing file.

### Rules

- Clear space on all sides: at least the height of the diamond mark.
- Minimum width 120px on screen, 32mm in print — below that the tagline inside
  the lockup stops being legible.
- Never recolour, rotate, add effects to, or place the colour logo on a
  mid-tone background.
- One logo per page. On a multi-page document it belongs on the cover and in
  the running footer, nowhere else.

## Voice

Documents go to Uzbek business owners and their technical staff. They are
being asked to spend real money.

- Lead with what the client gets, not with what ITHINK builds.
- Concrete over abstract: "orders reach the kitchen in 4 seconds" beats
  "streamlined operational workflow".
- No superlatives, no "innovative", no "cutting-edge". A specific number is
  more persuasive than any adjective and cannot be argued with.
- Every figure in a document must be defensible on the spot. If a number
  cannot be sourced, cut it — a made-up statistic in front of a procurement
  committee costs more than a weaker-looking page.
- Prices in soʻm, grouped with thin spaces: `145 000 soʻm`. Never round a
  quoted price to look cheaper.
- Uzbek and Russian both use formal register (Вы / Siz).
