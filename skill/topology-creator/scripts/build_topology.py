#!/usr/bin/env python3
"""Network topology spec (JSON) -> draw.io .drawio file with Cisco icons.

Stdlib only, on purpose: the skill has to run unchanged inside Claude's
sandbox on Desktop and mobile, where nothing can be installed.

Layout is a zone grid. Zones are boxes placed in rows; nodes flow left to
right inside their zone; nested zones stack under their parent's nodes.
Links are *declarative* -- draw.io routes them orthogonally when the file is
opened, so this script never computes a path.

Usage:
    build_topology.py spec.json -o out.drawio
    cat spec.json | build_topology.py -o out.drawio
"""

import argparse
import base64
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

ASSETS = Path(__file__).resolve().parent.parent / "assets"

# --- geometry -------------------------------------------------------------
ICON_BOX_W = 78          # icon is fitted inside this box, aspect preserved
ICON_BOX_H = 62
CELL_W = 150             # horizontal pitch between nodes
CELL_H = 152             # vertical pitch; the gap under the icon holds labels
ZONE_PAD_X = 26
ZONE_PAD_TOP = 40        # room for the zone's own header label
ZONE_PAD_BOTTOM = 22
ZONE_GAP = 34            # between sibling zones
PAGE_MARGIN = 40

DEFAULT_LINK_COLOR = "#5A6472"


class SpecError(Exception):
    """Raised for problems in the input spec that must not be papered over."""


# --- icons ----------------------------------------------------------------

class IconLibrary:
    """Resolves icon names to base64 data URIs, embedding only what is used."""

    def __init__(self) -> None:
        index_path = ASSETS / "icons.json"
        if not index_path.exists():
            raise SpecError(f"icon index missing: {index_path}")
        self.index = json.loads(index_path.read_text())
        self.aliases = json.loads((ASSETS / "aliases.json").read_text())
        self._cache: dict[str, str] = {}
        self.missing: list[str] = []

    def resolve(self, name: str) -> str | None:
        """Return the canonical icon slug, or None if nothing matches."""
        slug = name.strip().lower().replace(" ", "-").replace("_", "-")
        if slug in self.index:
            return slug
        if slug in self.aliases:
            target = self.aliases[slug]
            if target in self.index:
                return target
        # Last resort: every word of the query must appear in the slug.
        words = [w for w in slug.split("-") if w]
        hits = [
            key for key in self.index
            if all(w in key for w in words)
        ]
        if hits:
            return min(hits, key=len)
        return None

    def data_uri(self, slug: str) -> str:
        if slug not in self._cache:
            raw = (ASSETS / "icons" / self.index[slug]["file"]).read_bytes()
            self._cache[slug] = "data:image/png," + base64.b64encode(raw).decode()
        return self._cache[slug]

    def aspect(self, slug: str) -> float:
        meta = self.index[slug]
        return meta["w"] / meta["h"]


def fit_icon(aspect: float) -> tuple[int, int]:
    """Fit an icon of the given aspect ratio inside the standard icon box."""
    if aspect >= ICON_BOX_W / ICON_BOX_H:
        return ICON_BOX_W, max(18, round(ICON_BOX_W / aspect))
    return max(18, round(ICON_BOX_H * aspect)), ICON_BOX_H


# --- layout ---------------------------------------------------------------

class Box:
    """A laid-out rectangle in page coordinates."""

    def __init__(self, x: float = 0, y: float = 0, w: float = 0, h: float = 0):
        self.x, self.y, self.w, self.h = x, y, w, h


def layout_zone(zone: dict, nodes_by_id: dict, icons: IconLibrary) -> Box:
    """Measure a zone bottom-up. Returns its size; children get local coords."""
    node_ids = zone.get("nodes", [])
    cols = zone.get("cols") or max(1, min(len(node_ids), 4))

    inner_w = 0.0
    cursor_y = ZONE_PAD_TOP

    if node_ids:
        rows = (len(node_ids) + cols - 1) // cols
        for i, nid in enumerate(node_ids):
            node = nodes_by_id.get(nid)
            if node is None:
                raise SpecError(
                    f"zone {zone.get('id', zone.get('label'))!r} lists unknown node {nid!r}"
                )
            col, row = i % cols, i // cols
            iw, ih = fit_icon(node["_aspect"])
            node["_box"] = Box(
                ZONE_PAD_X + col * CELL_W + (CELL_W - iw) / 2,
                cursor_y + row * CELL_H,
                iw, ih,
            )
        inner_w = max(inner_w, cols * CELL_W)
        cursor_y += rows * CELL_H

    for child in zone.get("zones", []):
        child_box = layout_zone(child, nodes_by_id, icons)
        child_box.x = ZONE_PAD_X
        child_box.y = cursor_y
        child["_box"] = child_box
        inner_w = max(inner_w, child_box.w)
        cursor_y += child_box.h + ZONE_GAP

    if zone.get("zones"):
        cursor_y -= ZONE_GAP

    width = zone.get("width") or (inner_w + 2 * ZONE_PAD_X)
    height = cursor_y + ZONE_PAD_BOTTOM
    return Box(0, 0, width, height)


def layout_page(page: dict, nodes_by_id: dict, icons: IconLibrary) -> None:
    """Place page-level nodes in a row across the top, then zones in rows below.

    draw.io child geometry is relative to its parent, so only these top-level
    cells need absolute page coordinates. Nodes inside a zone, and zones inside
    zones, are already measured in parent-local space by layout_zone().
    """
    cursor_y = PAGE_MARGIN + (70 if page.get("header") else 0)

    loose = page.get("nodes", [])
    if loose:
        cursor_x = PAGE_MARGIN
        tallest = 0.0
        for nid in loose:
            node = nodes_by_id.get(nid)
            if node is None:
                raise SpecError(f"page {page.get('name')!r} lists unknown node {nid!r}")
            iw, ih = fit_icon(node["_aspect"])
            node["_box"] = Box(cursor_x + (CELL_W - iw) / 2, cursor_y, iw, ih)
            cursor_x += CELL_W
            tallest = max(tallest, ih)
        cursor_y += max(tallest, CELL_H - 40) + ZONE_GAP + 30

    rows: dict[int, list[dict]] = {}
    for zone in page.get("zones", []):
        rows.setdefault(zone.get("row", 0), []).append(zone)

    for row_index in sorted(rows):
        cursor_x = PAGE_MARGIN
        tallest = 0.0
        for zone in rows[row_index]:
            box = layout_zone(zone, nodes_by_id, icons)
            box.x, box.y = cursor_x, cursor_y
            zone["_box"] = box
            cursor_x += box.w + ZONE_GAP
            tallest = max(tallest, box.h)
        cursor_y += tallest + ZONE_GAP

    # Emitted geometry stays parent-relative, but link routing needs to compare
    # endpoints across different zones, so record absolute centres too.
    for nid in loose:
        b = nodes_by_id[nid]["_box"]
        nodes_by_id[nid]["_abs"] = Box(b.x, b.y, b.w, b.h)
    for zone in page.get("zones", []):
        assign_absolute(zone, 0, 0, nodes_by_id)


def assign_absolute(zone: dict, ox: float, oy: float, nodes_by_id: dict) -> None:
    box = zone["_box"]
    zx, zy = ox + box.x, oy + box.y
    for nid in zone.get("nodes", []):
        b = nodes_by_id[nid]["_box"]
        nodes_by_id[nid]["_abs"] = Box(zx + b.x, zy + b.y, b.w, b.h)
    for child in zone.get("zones", []):
        assign_absolute(child, zx, zy, nodes_by_id)


def auto_anchors(src: dict, dst: dict) -> dict:
    """Pick which side of each icon a link leaves and enters.

    Without this every edge attaches at the node centre and draw.io bundles
    them into the same channel, which is what makes generated diagrams look
    like a knot. Comparing absolute centres costs nothing and fixes most of it.
    """
    a, b = src.get("_abs"), dst.get("_abs")
    if a is None or b is None:
        return {}
    dx = (b.x + b.w / 2) - (a.x + a.w / 2)
    dy = (b.y + b.h / 2) - (a.y + a.h / 2)

    # Bias towards horizontal: icons carry their caption underneath, so leaving
    # from the bottom edge draws the line straight through the text.
    if abs(dy) > abs(dx) * 1.6:
        if dy > 0:
            return {"exitX": 0.5, "exitY": 1, "entryX": 0.5, "entryY": 0}
        return {"exitX": 0.5, "exitY": 0, "entryX": 0.5, "entryY": 1}
    if dx > 0:
        return {"exitX": 1, "exitY": 0.5, "entryX": 0, "entryY": 0.5}
    return {"exitX": 0, "exitY": 0.5, "entryX": 1, "entryY": 0.5}


# --- drawio emission ------------------------------------------------------

def zone_style(zone: dict) -> str:
    color = zone.get("color", "#8C9AAE")
    fill = zone.get("fill", "none")
    dash = zone.get("dash", "solid")
    parts = [
        "rounded=0",
        "whiteSpace=wrap",
        "html=1",
        f"fillColor={fill}",
        f"strokeColor={color}",
        "strokeWidth=2",
        "verticalAlign=top",
        "align=left",
        "spacingLeft=10",
        "spacingTop=6",
        f"fontColor={color}",
        "fontSize=13",
        "fontStyle=1",
        "container=1",
        "collapsible=0",
        "expand=0",
        "recursiveResize=0",
    ]
    if dash == "dashed":
        parts += ["dashed=1", "dashPattern=8 4"]
    elif dash == "dotted":
        parts += ["dashed=1", "dashPattern=1 4"]
    else:
        parts.append("dashed=0")
    return ";".join(parts)


def node_label(node: dict) -> str:
    """Icon caption: bold title, optional grey subtitle, optional xN."""
    title = escape(str(node["label"]))
    if node.get("count"):
        title += f" &#215;&#160;{escape(str(node['count']))}"
    html = f"<b>{title}</b>"
    if node.get("sub"):
        html += f"<br/><font style='font-size:10px' color='#6B7280'>{escape(str(node['sub']))}</font>"
    for badge in node.get("badges", []):
        html += (
            "<br/><font style='font-size:9px' color='#7C3AED'>"
            f"{escape(str(badge))}</font>"
        )
    return html


def node_style(node: dict, icons: IconLibrary) -> str:
    uri = icons.data_uri(node["_icon"]) if node.get("_icon") else None
    if uri is None:
        return (
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#F3F4F6;"
            "strokeColor=#9CA3AF;dashed=1;fontSize=11;verticalAlign=middle"
        )
    return (
        "shape=image;html=1;imageAspect=0;aspect=fixed;labelBackgroundColor=none;"
        "verticalLabelPosition=bottom;verticalAlign=top;align=center;"
        f"fontSize=11;fontColor=#111827;image={uri}"
    )


def port_label_offset(side_x, side_y, index: int = 0) -> tuple[int, int]:
    """Pixel nudge for a port label, given which side of the icon it sits on.

    Captions hang below every icon, so a label on the bottom edge has to clear
    roughly a caption's height or it lands in the middle of the device name.
    `index` fans out labels when several links share one side of one device:
    sideways for vertical links, downwards for horizontal ones.
    """
    if side_y == 1:      # link leaves/enters the bottom edge
        return 22 + index * 30, 46
    if side_y == 0:      # top edge
        return 22 + index * 30, -20
    if side_x == 1:      # right edge
        return 20, -13 + index * 15
    if side_x == 0:      # left edge
        return -20, -13 + index * 15
    return 0, -13 + index * 15


def edge_style(link: dict) -> str:
    parts = [
        "edgeStyle=orthogonalEdgeStyle",
        "rounded=1",
        "html=1",
        "jettySize=auto",
        "orthogonalLoop=1",
        "endArrow=none",
        "startArrow=none",
        f"strokeColor={link.get('color', DEFAULT_LINK_COLOR)}",
        f"strokeWidth={link.get('width', 2)}",
    ]
    if link.get("dashed"):
        parts += ["dashed=1", "dashPattern=6 4"]
    else:
        parts.append("dashed=0")
    if link.get("exitX") is not None:
        parts += [f"exitX={link['exitX']}", f"exitY={link['exitY']}",
                  "exitDx=0", "exitDy=0"]
    if link.get("entryX") is not None:
        parts += [f"entryX={link['entryX']}", f"entryY={link['entryY']}",
                  "entryDx=0", "entryDy=0"]
    return ";".join(parts)


class XmlBuilder:
    def __init__(self) -> None:
        self.parts: list[str] = []
        self.counter = 0

    def next_id(self, prefix: str = "c") -> str:
        self.counter += 1
        return f"{prefix}{self.counter}"

    def cell(self, cid: str, value: str, style: str, parent: str,
             box: Box, vertex: bool = True) -> None:
        self.parts.append(
            f'        <mxCell id={quoteattr(cid)} value={quoteattr(value)} '
            f'style={quoteattr(style)} vertex="1" parent={quoteattr(parent)}>\n'
            f'          <mxGeometry x="{box.x:.0f}" y="{box.y:.0f}" '
            f'width="{box.w:.0f}" height="{box.h:.0f}" as="geometry" />\n'
            f'        </mxCell>\n'
        )

    def edge(self, cid: str, value: str, style: str, parent: str,
             source: str, target: str) -> None:
        self.parts.append(
            f'        <mxCell id={quoteattr(cid)} value={quoteattr(value)} '
            f'style={quoteattr(style)} edge="1" parent={quoteattr(parent)} '
            f'source={quoteattr(source)} target={quoteattr(target)}>\n'
            f'          <mxGeometry relative="1" as="geometry" />\n'
            f'        </mxCell>\n'
        )

    def edge_label(self, cid: str, value: str, parent: str,
                   position: float, dx: int = 0, dy: int = 0) -> None:
        style = (
            "edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;"
            "points=[];fontSize=10;fontColor=#374151;labelBackgroundColor=#FFFFFF;"
            "spacing=2"
        )
        self.parts.append(
            f'        <mxCell id={quoteattr(cid)} value={quoteattr(value)} '
            f'style={quoteattr(style)} vertex="1" connectable="0" '
            f'parent={quoteattr(parent)}>\n'
            f'          <mxGeometry x="{position}" y="0" '
            f'relative="1" as="geometry">\n'
            f'            <mxPoint x="{dx}" y="{dy}" as="offset" />\n'
            f'          </mxGeometry>\n'
            f'        </mxCell>\n'
        )


def emit_zone(xml: XmlBuilder, zone: dict, parent: str,
              nodes_by_id: dict, icons: IconLibrary, cell_ids: dict) -> None:
    zid = xml.next_id("z")
    box = zone["_box"]
    xml.cell(zid, zone.get("label", ""), zone_style(zone), parent, box)

    for nid in zone.get("nodes", []):
        node = nodes_by_id[nid]
        cid = xml.next_id("n")
        cell_ids[nid] = cid
        xml.cell(cid, node_label(node), node_style(node, icons), zid, node["_box"])

    for child in zone.get("zones", []):
        emit_zone(xml, child, zid, nodes_by_id, icons, cell_ids)


def build_page(xml: XmlBuilder, page: dict, spec: dict,
               nodes_by_id: dict, icons: IconLibrary) -> str:
    xml.parts = []
    cell_ids: dict[str, str] = {}
    root = "1"

    if page.get("header"):
        header = page["header"]
        value = (
            f"<font style='font-size:20px'><b>{escape(header.get('title', ''))}</b></font>"
        )
        if header.get("subtitle"):
            value += (
                f"<br/><font style='font-size:11px' color='#6B7280'>"
                f"{escape(header['subtitle'])}</font>"
            )
        xml.cell(
            xml.next_id("h"), value,
            "text;html=1;align=left;verticalAlign=middle;strokeColor=none;fillColor=none",
            root, Box(PAGE_MARGIN, PAGE_MARGIN - 20, 900, 56),
        )

    for zone in page.get("zones", []):
        emit_zone(xml, zone, root, nodes_by_id, icons, cell_ids)

    for node in page.get("nodes", []):
        nid = node if isinstance(node, str) else node["id"]
        n = nodes_by_id[nid]
        cid = xml.next_id("n")
        cell_ids[nid] = cid
        xml.cell(cid, node_label(n), node_style(n, icons), root, n["_box"])

    page_name = page.get("name", "")

    # Resolve every link's anchors first. Two links leaving the same side of the
    # same device would otherwise drop their port labels on identical pixels, so
    # each (device, side) group gets a running index used to fan the labels out.
    drawable = []
    for link in spec.get("links", []):
        src, dst = link["from"], link["to"]
        if src not in cell_ids or dst not in cell_ids:
            continue
        anchors = auto_anchors(nodes_by_id[src], nodes_by_id[dst])
        resolved = {**anchors, **{k: v for k, v in link.items()
                                  if k in ("exitX", "exitY", "entryX", "entryY")}}
        drawable.append((link, resolved))

    rank: dict[tuple, int] = {}

    def stagger(node_id: str, sx, sy) -> int:
        key = (node_id, sx, sy)
        rank[key] = rank.get(key, -1) + 1
        return rank[key]

    for link, resolved in drawable:
        eid = xml.next_id("e")
        xml.edge(eid, link.get("label", ""), edge_style({**link, **resolved}), root,
                 cell_ids[link["from"]], cell_ids[link["to"]])
        # Pin port labels to the exact endpoint, then nudge them in pixels away
        # from the side the link leaves on. A fractional position alone lands
        # them on top of the icon's caption whenever the link runs vertically.
        if link.get("fromPort"):
            sx, sy = resolved.get("exitX"), resolved.get("exitY")
            dx, dy = port_label_offset(sx, sy, stagger(link["from"], sx, sy))
            xml.edge_label(xml.next_id("l"), link["fromPort"], eid, -1, dx, dy)
        if link.get("toPort"):
            sx, sy = resolved.get("entryX"), resolved.get("entryY")
            dx, dy = port_label_offset(sx, sy, stagger(link["to"], sx, sy))
            xml.edge_label(xml.next_id("l"), link["toPort"], eid, 1, dx, dy)

    body = "".join(xml.parts)
    return (
        f'  <diagram name={quoteattr(page_name)} id={quoteattr(page_name or "page")}>\n'
        f'    <mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" guides="1" '
        f'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
        f'pageWidth="1600" pageHeight="1200" math="0" shadow="0">\n'
        f'      <root>\n'
        f'        <mxCell id="0" />\n'
        f'        <mxCell id="1" parent="0" />\n'
        f'{body}'
        f'      </root>\n'
        f'    </mxGraphModel>\n'
        f'  </diagram>\n'
    )


def build_legend_page(xml: XmlBuilder, spec: dict) -> str:
    """Colour key + port assignment table, built from what the spec used."""
    xml.parts = []
    root = "1"
    legend = spec.get("legend", {})

    xml.cell(
        xml.next_id("h"),
        "<font style='font-size:18px'><b>"
        + escape(legend.get("title", "Legend"))
        + "</b></font>",
        "text;html=1;align=left;verticalAlign=middle;strokeColor=none;fillColor=none",
        root, Box(PAGE_MARGIN, PAGE_MARGIN, 700, 34),
    )

    seen: list[tuple] = []
    for link in spec.get("links", []):
        key = (link.get("color", DEFAULT_LINK_COLOR), bool(link.get("dashed")),
               link.get("meaning", ""))
        if key[2] and key not in seen:
            seen.append(key)

    y = PAGE_MARGIN + 50
    for color, dashed, meaning in seen:
        line_style = (
            f"endArrow=none;html=1;strokeColor={color};strokeWidth=3"
            + (";dashed=1;dashPattern=6 4" if dashed else ";dashed=0")
        )
        lid = xml.next_id("lg")
        xml.parts.append(
            f'        <mxCell id={quoteattr(lid)} value="" '
            f'style={quoteattr(line_style)} edge="1" parent="1">\n'
            f'          <mxGeometry relative="1" as="geometry">\n'
            f'            <mxPoint x="{PAGE_MARGIN}" y="{y + 10}" as="sourcePoint" />\n'
            f'            <mxPoint x="{PAGE_MARGIN + 54}" y="{y + 10}" as="targetPoint" />\n'
            f'          </mxGeometry>\n'
            f'        </mxCell>\n'
        )
        xml.cell(
            xml.next_id("t"), escape(meaning),
            "text;html=1;align=left;verticalAlign=middle;strokeColor=none;"
            "fillColor=none;fontSize=12",
            root, Box(PAGE_MARGIN + 66, y, 520, 20),
        )
        y += 28

    if legend.get("ports"):
        rows = "".join(
            f"<tr><td style='padding:3px 14px 3px 0'><b>{escape(dev)}</b></td>"
            f"<td style='padding:3px 0'>{escape(assignment)}</td></tr>"
            for dev, assignment in legend["ports"].items()
        )
        xml.cell(
            xml.next_id("pt"),
            "<div style='text-align:left'><b>"
            + escape(legend.get("portsTitle", "PORT ASSIGNMENT")) + "</b>"
            f"<table style='font-size:10px'>{rows}</table></div>",
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#F9FAFB;strokeColor=#D1D5DB;"
            "align=left;verticalAlign=top;spacing=10;fontSize=11",
            root, Box(760, PAGE_MARGIN, 700, max(120, 34 + 20 * len(legend["ports"]))),
        )

    if legend.get("assumptions"):
        items = "".join(
            f"<div style='margin-bottom:4px'>{escape(a)}</div>"
            for a in legend["assumptions"]
        )
        xml.cell(
            xml.next_id("as"),
            "<div style='text-align:left'><b>"
            + escape(legend.get("assumptionsTitle", "ASSUMPTIONS")) + "</b>"
            f"<div style='font-size:10px;margin-top:6px'>{items}</div></div>",
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#F9FAFB;strokeColor=#D1D5DB;"
            "align=left;verticalAlign=top;spacing=10;fontSize=11",
            root, Box(PAGE_MARGIN, max(y + 24, 400), 1420,
                      40 + 18 * len(legend["assumptions"])),
        )

    body = "".join(xml.parts)
    return (
        f'  <diagram name={quoteattr(legend.get("pageName", "Legend"))} id="legend">\n'
        '    <mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" guides="1" '
        'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
        'pageWidth="1600" pageHeight="1200" math="0" shadow="0">\n'
        '      <root>\n'
        '        <mxCell id="0" />\n'
        '        <mxCell id="1" parent="0" />\n'
        f'{body}'
        '      </root>\n'
        '    </mxGraphModel>\n'
        '  </diagram>\n'
    )


# --- driver ---------------------------------------------------------------

def prepare_nodes(spec: dict, icons: IconLibrary) -> dict:
    nodes_by_id: dict[str, dict] = {}
    for node in spec.get("nodes", []):
        nid = node["id"]
        if nid in nodes_by_id:
            raise SpecError(f"duplicate node id {nid!r}")
        slug = icons.resolve(node.get("icon", ""))
        if slug is None:
            icons.missing.append(f"{nid} (icon={node.get('icon')!r})")
            node["_icon"] = None
            node["_aspect"] = 1.3
        else:
            node["_icon"] = slug
            node["_aspect"] = icons.aspect(slug)
        nodes_by_id[nid] = node
    return nodes_by_id


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", nargs="?", help="spec JSON path (default: stdin)")
    parser.add_argument("-o", "--out", required=True, help="output .drawio path")
    args = parser.parse_args()

    raw = Path(args.spec).read_text() if args.spec else sys.stdin.read()
    spec = json.loads(raw)

    icons = IconLibrary()
    nodes_by_id = prepare_nodes(spec, icons)

    placed: set[str] = set()

    def collect(zone: dict) -> None:
        for nid in zone.get("nodes", []):
            if nid in placed:
                raise SpecError(f"node {nid!r} placed in more than one zone")
            placed.add(nid)
        for child in zone.get("zones", []):
            collect(child)

    for page in spec.get("pages", []):
        for nid in page.get("nodes", []):
            if nid in placed:
                raise SpecError(f"node {nid!r} placed more than once")
            placed.add(nid)
        for zone in page.get("zones", []):
            collect(zone)

    orphans = set(nodes_by_id) - placed
    if orphans:
        raise SpecError(
            "nodes declared but never placed on a page or in a zone: "
            f"{sorted(orphans)}"
        )

    for link in spec.get("links", []):
        for end in ("from", "to"):
            if link[end] not in nodes_by_id:
                raise SpecError(f"link {end} references unknown node {link[end]!r}")

    xml = XmlBuilder()
    diagrams = []
    for page in spec.get("pages", []):
        layout_page(page, nodes_by_id, icons)
        diagrams.append(build_page(xml, page, spec, nodes_by_id, icons))
    if spec.get("legend"):
        diagrams.append(build_legend_page(xml, spec))

    out = (
        '<mxfile host="topology-creator" version="24.0.0" type="device">\n'
        + "".join(diagrams)
        + "</mxfile>\n"
    )
    Path(args.out).write_text(out)

    print(f"wrote {args.out} ({len(spec.get('nodes', []))} nodes, "
          f"{len(spec.get('links', []))} links, {len(diagrams)} pages)")
    if icons.missing:
        print("WARNING: no icon match, rendered as placeholder box:", file=sys.stderr)
        for m in icons.missing:
            print(f"  - {m}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SpecError as exc:
        print(f"spec error: {exc}", file=sys.stderr)
        raise SystemExit(2)
