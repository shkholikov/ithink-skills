---
name: system-diagram
description: Use when the user asks to draw, create, explain or animate a system, architecture, pipeline or flow diagram — how a service works end to end, what an agent loop does, where a request travels, what guards a step. Produces a self-contained SVG in the ITHINK style, a looping animated SVG, and optionally a real GIF in which the icons move on a seamless loop. Triggers on "architecture diagram", "system design", "flow diagram", "pipeline diagram", "how it works diagram", "схема системы", "архитектура", "diagram this flow", "explainer graphic", or when a user describes stages of a process and asks to picture it. Not for network topology — use topology-creator for devices, ports and VLANs.
---

# System diagram

Turns a described system into `diagram.svg` — a vertical flow of stages, a zone
frame around the part that matters, sidecar cards for the things that watch or
constrain the flow, and dashed feedback loops routed clear of everything else.

Output is publication-ready rather than editable. It is meant to be published
as an artifact, dropped in a deck, or posted as a GIF.

## When to use

A diagram that explains **how something works**: a request path, an agent loop,
a data pipeline, a deployment flow, a decision process.

Do not use it for physical networks — `topology-creator` owns devices, ports,
VLANs and cabling, and produces an editable draw.io file instead.

## Workflow

### 1. Get the stages in order

The whole layout is one vertical column, so the first question is always: what
are the stages, in the order they run? Ask for them rather than inferring, and
ask what each one *does* in three or four words — that becomes the `sub` line
and is what makes a diagram explain rather than decorate.

Then ask what is **not** a stage: the things that watch the flow (observability,
logging) or bound it (policy, quotas, permissions). Those are sidecars, not
steps, and putting them in the column is the most common way these diagrams go
wrong.

### 2. Write the spec

Full schema in `references/spec-schema.md`, worked example in
`examples/harness.json`. The shape:

```json
{
  "title": "What is X?", "highlight": "X", "subtitle": "one line", "brand": "ITHINK",
  "nodes":    [{"id": "a", "label": "Stage", "sub": "what it does", "step": 1,
                "tone": "blue", "shape": "box", "icon": "database",
                "tiles": [{"icon": "file-text", "label": "Docs"}]}],
  "zone":     {"label": "THE SYSTEM", "from": "a", "to": "e"},
  "sidecars": [{"id": "obs", "anchor": "b", "label": "Observability", "icon": "activity"}],
  "flow":     [{"from": "a", "to": "b", "label": "what moves"}],
  "links":    [{"from": "e", "to": "a", "style": "dashed", "route": "gutter",
                "label": "feedback"}]
}
```

`flow` is the column and must connect flow nodes. `links` is everything else —
sidecar tethers and feedback loops. A feedback edge takes `"route": "gutter"`
so it runs up the left channel instead of across the diagram.

Lanes are assigned automatically: two edges whose vertical spans overlap are
given separate tracks, so they cannot share a column. Set `lane` by hand only
to override that.

### 3. Build

```bash
python3 scripts/build_diagram.py spec.json -o diagram.svg            # static
python3 scripts/build_diagram.py spec.json -o diagram.svg --animate  # + looping SVG
python3 scripts/build_diagram.py spec.json -o diagram.svg --gif      # + real GIF
```

Two kinds of motion, and picking the wrong one is the most likely mistake:

- **Default — living diagram.** Everything is visible from the first frame and
  stays visible; the icons drift, swing and pulse, and dashed links flow along
  their path. Nothing appears or disappears. This is what an explainer GIF
  looks like on social media, and it is the one to use unless asked otherwise.
- **`--reveal`** — the diagram builds up one stage at a time and rests on the
  finished picture. Use it when the *order* is the point, such as walking
  through a pipeline in a talk.

`--frames` (default 30) sets the smoothness of the motion loop and `--scale`
its pixel size; both trade against file size. Each icon can override its motion
with `"motion": "swing" | "bob" | "pulse" | "none"`.

Stdlib only. Inter and every icon are embedded, so the SVG renders identically
offline and inside a published artifact under CSP.

Validation is strict and fails on the first problem with the id or field that
caused it. An unknown icon, a dangling edge or a backwards zone stops the
build — none of them degrade into a diagram that is quietly wrong about a
system.

### 4. Read the collision report

The build prints what it had to move and what it could not:

```
diagram.svg  102 KB  932x1506
  resolved 4 collisions (4 edge/edge)
  warning: label 'feedback signals' overlaps edge tools->llm; no free slot
```

`resolved` is routine — it means the rules worked. A **warning is not**: it
names two things drawn on top of each other, and the fix is in the spec, not
in the renderer. Usually it means the diagram is asking for more links than the
layout has room for; cut one, or move a sidecar to a different anchor.

### 5. Look at it before showing it

Render it and actually look:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless \
  --disable-gpu --hide-scrollbars --window-size=W,H \
  --screenshot=check.png "file://$PWD/diagram.svg"
```

Text width is approximated rather than measured — there is no font metrics
library in the stdlib — so a long label can wrap a word early or a tight one
can sit closer than intended. The failure mode is cosmetic and always visible.

### 6. Publish

Publish the SVG with the Artifact tool, or embed it in a page. For the animated
version, the `.anim.svg` loops on its own with no script.

## Layout rules

Three rules the renderer enforces, rather than hoping the spec happens to
avoid trouble:

1. **A line never passes through a box.** Boxes claim their rectangles first;
   links are then routed as orthogonal paths through the free channels — up the
   left gutter, or down the corridor between the column and the sidecars.
2. **Two lines never share a track.** Overlapping vertical spans get separate
   lanes. Where lines must cross they do so at a right angle, which reads.
3. **Nothing is drawn over anything.** Every label searches a list of candidate
   positions and takes the first that touches no box, no line — including its
   own — and no other label. If none is free, it is placed and reported.

Longest links route first, since they have the fewest options.

## Icons

98 icons from Lucide, in `assets/icons.json`, listed in `references/icons.md`.
Reference one by name (`"icon": "database"`). An unknown name fails the build
and prints what is available — it never renders a blank box.

## Known gaps

`--gif` needs local Chrome or Chromium to rasterise each frame. It is present
on a normal desktop and absent from Claude's sandbox on Desktop, web and
mobile, where the flag exits with a message. Everything else — the static SVG
and the animated SVG — is pure stdlib and works everywhere. When a GIF is
wanted and Chrome is unreachable, hand over the animated SVG and say so; never
claim a GIF that was not produced.

A 30-frame motion GIF of a full-size diagram runs about 300 KB. Frames after
the first store only the pixels that changed, which is what keeps a smooth loop
from reaching several megabytes. If it must be smaller still, drop `--frames`
or render at `--scale 0.6`.

Rendering a GIF takes roughly three seconds per frame, since each one is a
separate Chrome launch. A 30-frame loop is about 90 seconds — say so before
starting rather than leaving the user watching a silent terminal.

The layout is one vertical column by design. A diagram that genuinely needs
parallel branches or a matrix is the wrong shape for this skill — say so rather
than forcing it.

## Bundled resources

| Path | What it is |
|---|---|
| `references/spec-schema.md` | Every field, with what happens when it is wrong |
| `references/icons.md` | The 98 icon names, grouped by what they depict |
| `references/palette.md` | The tone ramp, and how it derives from the ITHINK palette |
| `examples/harness.json` | Worked example — the diagram in the README |
| `scripts/build_diagram.py` | Validate, lay out, render, animate, encode |
| `scripts/layout.py` | Geometry and text metrics |
| `scripts/collide.py` | Overlap detection, lane assignment, label placement |
| `scripts/render.py` | SVG drawing, the motion model and the reveal order |
| `scripts/gifenc.py` | PNG reader, colour quantiser, frame differencing, GIF89a encoder |
| `tests/` | `python3 tests/test_system_diagram.py` — 46 tests, no dependencies |
