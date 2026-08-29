"""
Draws a laid-out diagram as SVG.

Every visible group carries a reveal order. A static diagram renders every
group; a frame of the animation renders the groups up to order k. Both paths
run through the same code, so the last frame of a GIF is byte-for-byte the
static diagram rather than a near-miss redrawn by a second code path.
"""

import json
import pathlib
from xml.sax.saxutils import escape, quoteattr

import layout as L

ASSETS = pathlib.Path(__file__).resolve().parent.parent / 'assets'

# Zone tints, derived from the ITHINK blue and navy rather than picked freely.
# references/palette.md records how, and why a diagram needs more than six.
TONES = {
    'blue':    {'fill': '#eef4ff', 'line': '#377dff', 'ink': '#1a2138'},
    'violet':  {'fill': '#f2eeff', 'line': '#7c5cff', 'ink': '#1a2138'},
    'amber':   {'fill': '#fff7e8', 'line': '#d99a2b', 'ink': '#1a2138'},
    'rust':    {'fill': '#fff0ea', 'line': '#d1603d', 'ink': '#1a2138'},
    'green':   {'fill': '#eaf7f0', 'line': '#2e7d5b', 'ink': '#1a2138'},
    'slate':   {'fill': '#f4f6fa', 'line': 'rgba(26,33,56,0.28)', 'ink': '#1a2138'},
    'neutral': {'fill': '#ffffff', 'line': 'rgba(26,33,56,0.20)', 'ink': '#1a2138'},
}

NAVY = '#1a2138'
BLUE = '#377dff'
INK_SOFT = 'rgba(30,32,34,0.64)'
INK_FAINT = 'rgba(30,32,34,0.44)'

_ICONS = json.loads((ASSETS / 'icons.json').read_text(encoding='utf-8'))


# -- text ---------------------------------------------------------------

text_w = L.text_w
wrap = L.wrap


def esc(s):
    return escape(str(s))


# -- primitives ------------------------------------------------------------

def icon(name, x, y, size, color, width=2.0):
    if name not in _ICONS:
        available = ', '.join(sorted(_ICONS)[:8])
        raise KeyError(f'unknown icon {name!r}. {len(_ICONS)} available, e.g. {available}')
    s = size / 24.0
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({s:.4f})" '
            f'fill="none" stroke="{color}" stroke-width="{width / s:.2f}" '
            f'stroke-linecap="round" stroke-linejoin="round">{_ICONS[name]}</g>')


def tspans(lines, x, y, size, weight, fill, lh=1.28, anchor='middle'):
    out = []
    for i, line in enumerate(lines):
        out.append(f'<text x="{x:.1f}" y="{y + i * size * lh:.1f}" text-anchor="{anchor}" '
                   f'font-size="{size}" font-weight="{weight}" fill="{fill}">{esc(line)}</text>')
    return ''.join(out)


class Renderer:
    def __init__(self, spec, lay, embed_font=True):
        self.spec = spec
        self.lay = lay
        self.embed_font = embed_font
        self.items = []      # (order, svg)
        self.max_order = 0
        self._build()

    def add(self, order, svg):
        self.items.append((order, svg))
        self.max_order = max(self.max_order, order)

    # -- assembly ----------------------------------------------------------

    def _build(self):
        spec, lay = self.spec, self.lay
        order = {}

        if spec.get('title'):
            self.add(0, self._header())
        if lay.zone:
            self.add(0, self._zone())

        for i, node in enumerate(spec['nodes']):
            order[node['id']] = i + 1
            self.add(i + 1, self._node(node))

        for car in spec.get('sidecars', []):
            o = order[car['anchor']] + 1
            order[car['id']] = o
            self.add(o, self._sidecar(car))

        for e in spec.get('flow', []):
            self.add(max(order[e['from']], order[e['to']]), self._flow_edge(e))

        for e in spec.get('links', []):
            self.add(max(order[e['from']], order[e['to']]), self._link_edge(e, order))

    # -- pieces ------------------------------------------------------------

    def _header(self):
        spec = self.spec
        x, y = L.MARGIN, L.MARGIN + 26
        title, hi = spec['title'], spec.get('highlight')
        parts = []
        parts.append(f'<rect x="{x - 16:.0f}" y="{y - 30:.0f}" width="6" height="46" rx="3" fill="{BLUE}"/>')
        if hi and hi in title:
            head, tail = title.split(hi, 1)
            cx = x
            if head.strip():
                parts.append(f'<text x="{cx:.0f}" y="{y:.0f}" font-size="38" font-weight="800" '
                             f'fill="{NAVY}" letter-spacing="-0.02em">{esc(head.strip())}</text>')
                cx += text_w(head.strip(), 38, True) + 18
            w = text_w(hi, 38, True) + 28
            parts.append(f'<rect x="{cx:.0f}" y="{y - 34:.0f}" width="{w:.0f}" height="50" rx="8" fill="{BLUE}"/>')
            parts.append(f'<text x="{cx + 14:.0f}" y="{y:.0f}" font-size="38" font-weight="800" '
                         f'fill="#ffffff" letter-spacing="-0.02em">{esc(hi)}</text>')
            if tail.strip():
                parts.append(f'<text x="{cx + w + 9:.0f}" y="{y:.0f}" font-size="38" font-weight="800" '
                             f'fill="{NAVY}" letter-spacing="-0.02em">{esc(tail.strip())}</text>')
        else:
            parts.append(f'<text x="{x:.0f}" y="{y:.0f}" font-size="38" font-weight="800" '
                         f'fill="{NAVY}" letter-spacing="-0.02em">{esc(title)}</text>')
        if spec.get('subtitle'):
            parts.append(f'<text x="{x:.0f}" y="{y + 28:.0f}" font-size="14" fill="{INK_SOFT}">'
                         f'{esc(spec["subtitle"])}</text>')
        if spec.get('brand'):
            parts.append(f'<text x="{self.lay.width - L.MARGIN:.0f}" y="{y - 6:.0f}" text-anchor="end" '
                         f'font-size="15" font-weight="700" fill="{NAVY}">{esc(spec["brand"])}</text>')
        return f'<g>{"".join(parts)}</g>'

    def _zone(self):
        z = self.lay.zone
        lw = text_w(z['label'], 12, True) + 34
        return (
            f'<g>'
            f'<rect x="{z["x"]:.0f}" y="{z["y"]:.0f}" width="{z["w"]:.0f}" height="{z["h"]:.0f}" '
            f'rx="16" fill="#f7faff" stroke="{BLUE}" stroke-opacity="0.35" stroke-width="1.5"/>'
            f'<rect x="{z["x"] + 22:.0f}" y="{z["y"] - 17:.0f}" width="{lw:.0f}" height="34" rx="10" fill="{NAVY}"/>'
            f'<text x="{z["x"] + 22 + lw / 2:.0f}" y="{z["y"] + 5:.0f}" text-anchor="middle" font-size="12" '
            f'font-weight="700" letter-spacing="0.08em" fill="#ffffff">{esc(z["label"])}</text>'
            f'</g>'
        )

    def _shape(self, node, b, tone):
        s = node['shape']
        if s == 'ellipse':
            return (f'<ellipse cx="{b["cx"]:.1f}" cy="{b["cy"]:.1f}" rx="{b["w"] / 2:.1f}" '
                    f'ry="{b["h"] / 2:.1f}" fill="{tone["fill"]}" stroke="{tone["line"]}" stroke-width="2"/>')
        if s == 'diamond':
            cx, cy, hw, hh = b['cx'], b['cy'], b['w'] / 2, b['h'] / 2
            pts = f'{cx:.1f},{cy - hh:.1f} {cx + hw:.1f},{cy:.1f} {cx:.1f},{cy + hh:.1f} {cx - hw:.1f},{cy:.1f}'
            return f'<polygon points="{pts}" fill="{tone["fill"]}" stroke="{tone["line"]}" stroke-width="2"/>'
        rx = b['h'] / 2 if s == 'pill' else 14
        return (f'<rect x="{b["x"]:.0f}" y="{b["y"]:.0f}" width="{b["w"]:.0f}" height="{b["h"]:.0f}" '
                f'rx="{rx:.0f}" fill="{tone["fill"]}" stroke="{tone["line"]}" stroke-width="2"/>')

    def _node(self, node):
        b = self.lay.boxes[node['id']]
        tone = TONES[node['tone']]
        parts = [self._shape(node, b, tone)]

        head_h = b['h'] - (L.TILE_H if node.get('tiles') else 0)
        head_cy = b['y'] + head_h / 2

        # An inline icon sits left of the label; a shape with tiles puts the
        # icon inside each tile instead, so it is not repeated up here.
        label_cx = b['cx']
        if node.get('icon') and not node.get('tiles'):
            iw = 30
            total = iw + 12 + text_w(node['label'], 19, True)
            ix = b['cx'] - total / 2
            parts.append(icon(node['icon'], ix, head_cy - 15 - (7 if node.get('sub') else 0), iw, tone['line'], 2.1))
            label_cx = ix + iw + 12 + text_w(node['label'], 19, True) / 2

        ly = head_cy + (0 if not node.get('sub') else -4)
        parts.append(tspans([node['label']], label_cx, ly + 6, 19, 700, tone['ink']))
        if node.get('sub'):
            parts.append(tspans([node['sub']], label_cx, ly + 26, 13, 400, INK_SOFT))

        if node.get('step'):
            sx, sy = b['x'] - 4, b['y'] + 4
            parts.append(f'<circle cx="{sx:.0f}" cy="{sy:.0f}" r="17" fill="{NAVY}"/>')
            parts.append(f'<text x="{sx:.0f}" y="{sy + 6:.0f}" text-anchor="middle" font-size="15" '
                         f'font-weight="700" fill="#ffffff">{node["step"]}</text>')

        if node.get('tiles'):
            parts.append(self._tiles(node['tiles'], b, tone))
        return f'<g>{"".join(parts)}</g>'

    def _tiles(self, tiles, b, tone):
        n = len(tiles)
        span = b['w'] - 48
        step = span / n
        y = b['y'] + b['h'] - L.TILE_H + 8
        out = []
        for i, t in enumerate(tiles):
            cx = b['x'] + 24 + step * (i + 0.5)
            out.append(icon(t['icon'], cx - 17, y, 34, tone['line'], 1.9))
            out.append(tspans([t['label']], cx, y + 54, 12, 600, tone['ink']))
        return ''.join(out)

    def _sidecar(self, car):
        b = self.lay.boxes[car['id']]
        tone = TONES[car['tone']]
        parts = [f'<rect x="{b["x"]:.0f}" y="{b["y"]:.0f}" width="{b["w"]:.0f}" height="{b["h"]:.0f}" '
                 f'rx="14" fill="{tone["fill"]}" stroke="{tone["line"]}" stroke-width="1.6"/>']
        cy = b['y'] + 34
        parts.append(tspans([car['label']], b['cx'], cy, 17, 700, tone['ink']))
        cy += 8
        if car.get('sub'):
            lines = wrap(car['sub'], b['w'] - 30, 12)
            parts.append(tspans(lines, b['cx'], cy + 12, 12, 400, INK_SOFT))
            cy += len(lines) * 16
        if car.get('icon'):
            parts.append(icon(car['icon'], b['cx'] - 16, cy + 6, 32, tone['line'], 2.0))
            cy += 44
        if car.get('note'):
            # A translucent tone line is fine for a border and unreadable as text.
            parts.append(tspans([car['note']], b['cx'], cy + 14, 11, 600, INK_SOFT))
        return f'<g>{"".join(parts)}</g>'

    # -- edges -------------------------------------------------------------

    def _label(self, x, y, text, color=INK_SOFT, anchor='start'):
        w = text_w(text, 12) + 10
        rx = x - 5 if anchor == 'start' else x - w / 2
        return (f'<rect x="{rx:.1f}" y="{y - 10:.1f}" width="{w:.1f}" height="16" rx="4" fill="#f7faff"/>'
                f'<text x="{x:.1f}" y="{y + 2:.1f}" text-anchor="{anchor}" font-size="12" '
                f'fill="{color}">{esc(text)}</text>')

    def _flow_edge(self, e):
        x1, y1 = self.lay.bottom(e['from'])
        x2, y2 = self.lay.top(e['to'])
        color = e.get('color', NAVY)
        parts = [f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2 - 9:.1f}" '
                 f'stroke="{color}" stroke-width="2" marker-end="url(#arrow)"/>']
        if e.get('label'):
            parts.append(self._label(x1 + 12, (y1 + y2) / 2, e['label'], color))
        return f'<g>{"".join(parts)}</g>'

    def _link_edge(self, e, order):
        """Sidecar tethers and feedback loops — everything not in the main column."""
        style = e.get('style', 'dotted')
        color = {'dotted': 'rgba(26,33,56,0.34)', 'dashed': '#d1603d',
                 'accent': BLUE, 'green': '#2e7d5b'}.get(e.get('tone', ''), None)
        if color is None:
            color = '#d1603d' if style == 'dashed' else 'rgba(26,33,56,0.34)'
        dash = {'dotted': '2 5', 'dashed': '8 6', 'solid': None}[style]

        a, b = self.lay.boxes[e['from']], self.lay.boxes[e['to']]
        if e.get('route') == 'gutter':
            # Feedback: leave the source on its left, run up the gutter, come
            # back into the target. Kept off the column so it never crosses a node.
            gx = L.MARGIN + 30 + e.get('lane', 0) * 36
            x1, y1 = a['x'], a['cy']
            x2, y2 = b['x'], b['cy']
            d = (f'M {x1:.1f} {y1:.1f} H {gx:.1f} V {y2:.1f} H {x2 - 10:.1f}')
            lx, ly = gx + 14, y2 - 10
            anchor = 'start'
        else:
            x1, y1 = (a['x'], a['cy']) if a['x'] > b['x'] else (a['x'] + a['w'], a['cy'])
            x2, y2 = (b['x'] + b['w'], b['cy']) if a['x'] > b['x'] else (b['x'], b['cy'])
            mx = (x1 + x2) / 2
            d = f'M {x1:.1f} {y1:.1f} C {mx:.1f} {y1:.1f} {mx:.1f} {y2:.1f} {x2:.1f} {y2:.1f}'
            lx, ly = mx, (y1 + y2) / 2 - 6
            anchor = 'middle'

        marker = ' marker-end="url(#arrow-soft)"' if e.get('arrow', True) else ''
        da = f' stroke-dasharray="{dash}"' if dash else ''
        parts = [f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.8"'
                 f'{da}{marker}/>']
        if e.get('label'):
            parts.append(self._label(lx, ly, e['label'], color, anchor))
        return f'<g>{"".join(parts)}</g>'

    # -- output ------------------------------------------------------------

    def _defs(self):
        font = ''
        if self.embed_font:
            import base64
            faces = []
            for name, rng in (('inter-latin', 'U+0000-00FF,U+0131,U+0152-0153,U+2000-206F,U+20AC,U+2122'),
                              ('inter-cyrillic', 'U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116')):
                p = ASSETS / f'{name}.woff2'
                b64 = base64.b64encode(p.read_bytes()).decode('ascii')
                faces.append("@font-face{font-family:'Inter';font-style:normal;font-weight:100 900;"
                             f"src:url(data:font/woff2;base64,{b64}) format('woff2');unicode-range:{rng};}}")
            font = ''.join(faces)
        return (
            '<defs>'
            '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            'orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke"/></marker>'
            '<marker id="arrow-soft" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
            'orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke"/></marker>'
            f'</defs><style>{font}'
            "text{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;}"
            '</style>'
        )

    def svg(self, upto=None, animate=False):
        items = sorted(self.items, key=lambda kv: kv[0])
        if upto is not None:
            items = [(o, s) for o, s in items if o <= upto]

        body = []
        anim_css = ''
        if animate:
            n = self.max_order
            hold, step = 1.6, 0.55
            total = step * (n + 1) + hold
            keys = []
            for o in range(n + 1):
                start = (step * o) / total * 100
                end = (step * o + 0.35) / total * 100
                keys.append(f'@keyframes r{o}{{0%,{start:.2f}%{{opacity:0}}'
                            f'{end:.2f}%,100%{{opacity:1}}}}')
            anim_css = ('<style>' + ''.join(keys) +
                        ''.join(f'.o{o}{{opacity:0;animation:r{o} {total:.2f}s infinite}}'
                                for o in range(n + 1)) + '</style>')
            body = [s.replace('<g>', f'<g class="o{o}">', 1) for o, s in items]
        else:
            body = [s for _, s in items]

        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.lay.width:.0f}" '
            f'height="{self.lay.height:.0f}" viewBox="0 0 {self.lay.width:.0f} {self.lay.height:.0f}">'
            f'{self._defs()}{anim_css}'
            f'<rect width="100%" height="100%" fill="#f7faff"/>'
            f'{"".join(body)}</svg>'
        )
