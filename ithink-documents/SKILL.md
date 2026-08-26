---
name: ithink-documents
description: This skill should be used when producing any client-facing ITHINK document — commercial offers (коммерческое предложение / KP / kommersiya taklifi), product presentations (taqdimot / pitch decks), technical proposals, or one-pager capability sheets. It supplies the ITHINK brand system (Inter, the six-colour palette, logos), the document structures that have already worked with clients, and a build script that inlines fonts and logos so the result publishes as an artifact and exports to PDF. Trigger it whenever a document, offer, proposal, presentation or price quote is being written for an ITHINK client, even if the brand is not mentioned by name.
---

# ITHINK documents

## Purpose

Produce client-facing ITHINK documents without re-deriving the brand or the
document structure each time. The visual system is already decided — do not
invent a palette, pick a font, or design a layout from scratch. Read
`references/brand.md` and follow it.

## When to use

Any document that leaves ITHINK and reaches a client: a commercial offer, a
product presentation, a technical proposal, a capability one-pager, a price
quote. Also use it when updating or re-skinning an existing one of these.

Do not use it for internal notes, code documentation, or README files.

## Workflow

### 1. Ask the language first

Russian and Uzbek are both normal, and the choice depends on the client rather
than the document type. Ask before writing anything; translating a finished
document costs more than asking one question.

Uzbek uses `ʻ` (U+02BB) in *oʻ* and *gʻ*, not a straight apostrophe.

### 2. Gather what only the user knows

ITHINK's own details — legal name, phone, email, website, and which payment
requisites are still missing — are in `references/company.md`. Read it instead
of asking the user for them again.

Never invent client-specific facts. Before writing, establish: client name,
the problem in their words, scope, prices and timeline. Ask for whatever is
missing rather than filling it with plausible text — a placeholder that
survives into a sent document is worse than a gap.

Numbers must be defensible on the spot. Any figure that cannot be sourced gets
cut, not softened.

### 3. Pick the structure

Read `references/document-patterns.md` and follow the structure for the
document type. Each pattern lists its reader, its job, and its section order.
Deviate only for a specific reason.

### 4. Write the document

Copy `assets/template.html` as the starting point. It carries the full brand
system: palette tokens, type scale, cover, tables, callouts, phase list, price
block, footer, print rules and a mobile breakpoint.

Rules the template depends on:

- Write page content only — a `<title>`, a `<style>` block, and the markup.
  No `<!DOCTYPE>`, `<html>`, `<head>` or `<body>` tags; the artifact publisher
  supplies those, and a browser infers them for the PDF path.
- Leave `@@INTER@@` and `@@LOGO:...@@` in place. The build script substitutes
  them.
- Never add a colour outside the palette in `references/brand.md`. Derive from
  the existing tokens instead.
- Never link an external stylesheet, font or image. Published artifacts run
  under a CSP that blocks every external host, so an external reference does
  not fail loudly — it silently degrades to a system font, and the document
  stops looking like ITHINK.

### 5. Build

```bash
python3 scripts/build_document.py <document.html> -o <document.built.html>
```

This inlines the three Inter subsets and any referenced logo as data URIs, and
fails if a placeholder or logo name is unresolved. Output is roughly 350 KB and
makes zero network requests.

### 6. Publish an artifact for review

Publish the built file with the Artifact tool. Give it a stable favicon and a
title matching the document. The user reviews and iterates here — expect
several rounds, and redeploy to the same file path each time so the URL holds.

The design is already settled by `references/brand.md`, so do not load
`artifact-design` and re-derive an aesthetic direction for these documents.

### 7. Export the PDF once approved

The PDF is the deliverable that reaches the client, and it is produced only
after the content is final:

```bash
python3 scripts/build_document.py <document.html> -o <document.built.html> --pdf
```

This prints A4 headlessly through Chrome with backgrounds preserved. Verify
the result before handing it over — check that no table row splits across a
page break and that the price block is intact.

## Bundled resources

| Path | What it is |
|---|---|
| `references/brand.md` | Palette and colour roles, type scale, logo usage, voice. Read before writing |
| `references/company.md` | ITHINK's own legal name, contacts and payment requisites. Read before any document footer or invoice |
| `references/document-patterns.md` | Section structure for each of the four document types |
| `assets/template.html` | Working base document with every component |
| `assets/fonts/` | Inter variable font, three subsets, 152 KB total |
| `assets/logos/` | ITHINK logos referenced as `@@LOGO:<name>@@` |
| `scripts/build_document.py` | Inlines brand assets; `--pdf` also exports A4 PDF |

## Known gaps

`--pdf` needs a local Chrome or Chromium. It is present on a normal desktop
machine but not inside Claude's sandbox on Desktop, web or mobile, where the
script exits with a message instead. Everything else — writing, building and
publishing the artifact — works unchanged there; take the PDF from the browser's
own print dialog (A4, backgrounds on) when Chrome is unreachable.

`assets/logos/` covers every placement except single-colour mono print. If a
document needs a mono lockup, ask for the file — never flatten, recolour,
rotate or distort an existing logo to stand in.
