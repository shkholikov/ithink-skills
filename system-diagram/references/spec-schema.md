# Spec schema

One JSON object. Only `nodes` is required; everything else is optional and
absent means "do not draw it".

Every rule below is enforced by `build_diagram.py` and fails the build with the
offending id or field named. Nothing degrades silently — a diagram that is
quietly wrong about a system is worse than no diagram.

## Top level

| Field | Type | What it does |
|---|---|---|
| `title` | string | Headline. Omit for a bare diagram with no title band |
| `highlight` | string | A substring of `title` set in a blue box, ByteByteGo style. Ignored if it is not in the title |
| `subtitle` | string | One line under the title |
| `brand` | string | Set top right. `"ITHINK"` |
| `nodes` | list | **Required.** The vertical column, in order |
| `zone` | object | A frame drawn around a run of nodes |
| `sidecars` | list | Cards in the right margin |
| `flow` | list | Arrows down the column |
| `links` | list | Everything else — tethers and feedback loops |

## nodes

The column, drawn top to bottom in the order given.

| Field | Type | Default | Notes |
|---|---|---|---|
| `id` | string | — | Required, unique across nodes *and* sidecars |
| `label` | string | — | Required |
| `sub` | string | — | The three-or-four-word line under the label. This is what makes the diagram explain |
| `step` | int | — | Draws a numbered navy badge on the top-left corner |
| `shape` | enum | `box` | `box`, `pill`, `ellipse`, `diamond` |
| `tone` | enum | `neutral` | See `palette.md` |
| `icon` | string | — | Drawn left of the label. Ignored when `tiles` is set |
| `tiles` | list | — | `{"icon", "label"}` pairs in a strip along the bottom |

`shape` carries meaning worth keeping consistent: `pill` for something entering
or leaving the system, `ellipse` for a model or black box, `diamond` for a
decision, `box` for everything that does work.

`tiles` are for showing what a stage is made of — three data sources, three
runtimes. More than four gets cramped at the default width.

## zone

```json
{"label": "THE HARNESS", "from": "ctx", "to": "verify"}
```

Frames the nodes from `from` to `to` inclusive, with a navy tab. `from` must
come before `to` in the node order. One zone per diagram.

## sidecars

Cards in the right margin for things that observe or constrain the flow rather
than sit in it.

| Field | Type | Notes |
|---|---|---|
| `id` | string | Required, unique |
| `anchor` | string | Required. The flow node it sits beside |
| `label` | string | Required |
| `sub` | string | Wraps; the card grows to fit |
| `icon` | string | Centred under the text |
| `note` | string | Small line at the bottom, e.g. "watches every stage" |
| `tone` | enum | Default `slate` |

Two sidecars anchored to the same node stack downwards instead of overlapping.

## flow

Arrows down the column. Both ends must be flow nodes — an edge to a sidecar is
an error telling you to use `links`.

| Field | Notes |
|---|---|
| `from`, `to` | Required node ids |
| `label` | Sits beside the arrow on a paper-coloured chip |
| `color` | Overrides navy. Use for a meaningful edge, like a green success path |

## links

Everything not in the column.

| Field | Default | Notes |
|---|---|---|
| `from`, `to` | — | Any node or sidecar id |
| `style` | `dotted` | `dotted` (observation), `dashed` (enforcement, feedback), `solid` |
| `tone` | — | `accent` blue, `green`, or omit for the style's default |
| `label` | — | |
| `arrow` | `true` | `false` for a tether that is not directional |
| `route` | — | `"gutter"` routes it up the left channel |
| `lane` | `0` | Which gutter channel. Give each feedback loop its own |

Without `route`, a link is a short curve between the two boxes — right for a
sidecar tether. With `"route": "gutter"` it leaves the source on its left, runs
up the left channel and comes back into the target, which is the only way a
long feedback loop avoids crossing the column.

Two gutter links on the same `lane` will overlap. This is not validated,
because a diagram can legitimately want two edges sharing a channel; look at
the render.

## Failure messages

| Message | Cause |
|---|---|
| `"nodes" must be a non-empty list` | No column |
| `nodes[2] (gate) has no label` | Missing required field, with the index and id |
| `duplicate ids: ctx` | An id reused between nodes and sidecars |
| `nodes[1] shape 'hexagon' unknown` | With the list of valid shapes |
| `flow[3] to='ghost' is not a known id` | Dangling edge |
| `flow[0] must connect two flow nodes; use "links" for sidecars` | Sidecar in the column |
| `sidecar obs anchors to 'nope', which is not a flow node` | Bad anchor |
| `zone "from" must come before "to" in the node order` | Reversed zone |
| `unknown icon 'unicorn' on node llm` | Typo, with a pointer to `icons.md` |
