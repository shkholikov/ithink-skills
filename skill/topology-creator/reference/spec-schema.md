# Spec schema

A spec is one JSON object with four top-level keys: `pages`, `nodes`, `links`,
`legend`. Only `pages` and `nodes` are required.

## `nodes` — the device catalogue

Flat list. Declaration order does not matter; placement is decided by `pages`.

| Field | Type | Required | Meaning |
|---|---|---|---|
| `id` | string | yes | Unique. Referenced by zones and links. |
| `icon` | string | yes | Icon name — see *Icon names* in SKILL.md. |
| `label` | string | yes | Bold caption under the icon. |
| `sub` | string | no | Small grey second line. Model, speed, VLAN role. |
| `count` | number | no | Renders as `× N`. Use for "12 laptops". |
| `badges` | string[] | no | Small violet lines under the caption, e.g. `VLAN 20`. |

## `pages` — what goes where

One entry per draw.io page.

| Field | Type | Meaning |
|---|---|---|
| `name` | string | Page tab name. |
| `header` | object | `{title, subtitle}` drawn top-left. Optional. |
| `nodes` | string[] | Node ids placed loose in a row across the top, above all zones. Use for internet clouds and ISP routers. |
| `zones` | object[] | Zone boxes. |

### Zone

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Only used in error messages. |
| `label` | string | Header text drawn inside the box, top-left. |
| `color` | hex | Border and header colour. Default `#8C9AAE`. |
| `fill` | hex | Background. Default `none`. |
| `dash` | `solid` \| `dashed` \| `dotted` | Border style. Default `solid`. |
| `row` | number | Top-level zones sharing a `row` sit side by side. Default `0`. |
| `cols` | number | Icons per row inside this zone. Default `min(count, 4)`. |
| `width` | number | Force a width in px. Rarely needed. |
| `nodes` | string[] | Node ids placed in this zone's grid. |
| `zones` | object[] | Nested zones, stacked below this zone's own nodes. |

`row` only applies to top-level zones. Nested zones always stack vertically.

## `links` — the cabling

| Field | Type | Meaning |
|---|---|---|
| `from`, `to` | string | Node ids. Unknown ids are a hard error. |
| `fromPort`, `toPort` | string | Interface labels pinned near each end — `Gi1`, `p48`, `Lan2`. |
| `label` | string | Text at the middle of the line — `Trunk`, `UpLink`, `Fiber`. |
| `color` | hex | Line colour. Default `#5A6472`. |
| `width` | number | Stroke width. `3` for trunks and uplinks, `2` otherwise. |
| `dashed` | bool | Wireless links, unmanaged cascades. |
| `meaning` | string | Legend entry for this colour. Only needed on one link per colour. |
| `exitX`/`exitY`/`entryX`/`entryY` | 0–1 | Override which side the line attaches to. Omit unless the automatic choice is wrong. |

A link whose endpoints sit on different pages is silently skipped on both — draw.io
cannot draw an edge across pages. Put cross-floor links on one page and note the
continuation in `legend.assumptions`.

## `legend` — the last page

Omit the whole key to skip the legend page.

| Field | Type | Meaning |
|---|---|---|
| `pageName` | string | Page tab name. Default `Legend`. |
| `title` | string | Heading. Default `Legend`. |
| `ports` | object | `{"Core switch": "VLAN 10: 1-8 · Trunk: 48"}` — rendered as a table. |
| `portsTitle` | string | Default `PORT ASSIGNMENT`. |
| `assumptions` | string[] | Numbered notes about anything you guessed. |
| `assumptionsTitle` | string | Default `ASSUMPTIONS`. |

The colour key is generated automatically from every distinct
`(color, dashed, meaning)` used in `links`.

## Layout constants

Set at the top of `scripts/build_topology.py` if a diagram needs different
proportions: `ICON_BOX_W/H` (icon size), `CELL_W/H` (grid pitch), `ZONE_PAD_*`,
`ZONE_GAP`, `PAGE_MARGIN`.

## Validation rules

Hard errors, which stop the build:

- a node id declared twice
- a node never placed on a page or in a zone
- a node placed in more than one zone
- a zone or page listing a node id that does not exist
- a link referencing a node id that does not exist

Warnings, which do not stop the build:

- an icon name that matches nothing — the node renders as a dashed grey box and
  the name is printed to stderr
