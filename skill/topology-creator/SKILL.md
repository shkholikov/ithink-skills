---
name: topology-creator
description: Use when the user asks to draw, create, redraw, or update a network topology diagram — office/enterprise networks, VLAN maps, floor-by-floor layouts, rack or ISP diagrams. Produces an editable draw.io file with Cisco network icons, zone boxes, port labels and a legend. Triggers on "network topology", "network diagram", "топология сети", "схема сети", "draw my network", "diagram this network", or when a user describes devices and how they are cabled together.
---

# Topology Creator

Turns a described network into `topology.drawio` — a real draw.io file with Cisco
icons, zone boxes, interface labels on both ends of every link, colour-coded VLAN
links, and a generated legend page.

Output is editable: the user opens it in draw.io and drags anything they dislike.
Do not try to make the generated layout perfect. Make it correct and readable.

## Workflow

1. **Collect the network.** Ask for whatever is missing (see *What to ask* below).
   Do not invent devices, ports, VLANs or IP ranges — a wrong port number in a
   network diagram is worse than a missing one.
2. **Write a spec JSON.** Schema below; full reference in
   `reference/spec-schema.md`, worked example in `reference/examples/small-office.json`.
3. **Generate:**
   ```bash
   python3 scripts/build_topology.py spec.json -o topology.drawio
   ```
   Stdlib only — works on macOS, Linux, and inside Claude's sandbox.
4. **Read the warnings.** Any icon it could not match is listed on stderr and
   drawn as a dashed grey placeholder box. Fix the icon name and re-run.
5. **Export an image** if the user wants one, and if `drawio` is on PATH:
   ```bash
   drawio -x -f png -s 2 -o topology.png topology.drawio
   drawio -x -f pdf -o topology.pdf topology.drawio
   ```
   If it is not installed, hand over the `.drawio` and say it exports via
   *File › Export as* in draw.io. Never claim you produced a PNG you did not.

## Spec format

```json
{
  "pages": [
    {
      "name": "Floor 1",
      "header": {"title": "...", "subtitle": "..."},
      "nodes": ["internet", "isp1"],
      "zones": [
        {"id": "srv", "label": "Server room", "color": "#DC2626",
         "dash": "dashed", "row": 0, "cols": 3,
         "nodes": ["fw", "core"],
         "zones": [ {"...nested zone..."} ]}
      ]
    }
  ],
  "nodes": [
    {"id": "fw", "icon": "firewall", "label": "Kerio Control",
     "sub": "VLAN 10 gateway", "count": 2, "badges": ["VLAN 20"]}
  ],
  "links": [
    {"from": "fw", "to": "core", "fromPort": "p2", "toPort": "p1",
     "color": "#111827", "width": 3, "label": "Trunk", "dashed": false,
     "meaning": "Trunk — 802.1Q, all VLANs"}
  ],
  "legend": {"title": "...", "ports": {"Core": "VLAN 10: 1-8"},
             "assumptions": ["1 — ..."]}
}
```

Key rules:

- Every node **must** be placed exactly once — in a page's `nodes` (top-level,
  for internet clouds and ISP routers) or in exactly one zone's `nodes`.
  Unplaced or twice-placed nodes are hard errors.
- `row` puts top-level zones side by side: same `row` = same horizontal band.
- `cols` sets how many icons per row inside a zone. Default is min(count, 4).
- `count` renders as `× N` — use it for "12 laptops", never 12 separate nodes.
- `meaning` on a link is what makes it appear in the legend. Links sharing a
  colour only need it once.

## Icon names

Use plain vocabulary — `switch`, `firewall`, `l3-switch`, `poe-switch`, `ap`,
`server`, `active-directory`, `database`, `nas`, `ip-camera`, `nvr`, `laptop`,
`workstation`, `printer`, `patch-panel`, `ups`, `internet`, `isp-router`.
These resolve via `assets/aliases.json`. Anything in `assets/icons.json` also
works by its own slug (294 Cisco icons). Unmatched names fall back to token
matching, then to a placeholder box plus a warning.

## Link colour convention

Follow the user's own scheme if they have one. Otherwise:

| Purpose | Colour |
|---|---|
| UpLink / WAN | `#DC2626` red |
| Trunk (802.1Q) | `#111827` black |
| LAN / workstations | `#2563EB` blue |
| Server farm | `#7C3AED` violet |
| CCTV / access control | `#059669` green |
| Guest wi-fi | `#D97706` amber |
| End-device runs | `#9CA3AF` grey |

Use `width: 3` for trunks and uplinks, `2` for everything else, and `dashed`
for wireless or unmanaged-switch cascades.

## What to ask

Only what you actually need, and only if it is not already given:

- Floors / rooms / departments → these become zones.
- Devices per zone, with model names if the user knows them.
- What connects to what, and the interface on each end (`Gi1`, `p48`, `Fa8`).
- VLANs and which links carry them.
- Whether device counts should collapse (`× 10`) or be drawn individually.

If the user says "just draw it", pick sensible defaults and state the
assumptions in `legend.assumptions` rather than stopping to ask.
