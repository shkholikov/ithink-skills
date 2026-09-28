"""
Geometry for a system diagram: turns a validated spec into positioned boxes.

Kept apart from rendering because the layout is the part worth testing. A box
either lands where the arithmetic says or it does not, and that can be asserted
without parsing a single line of SVG.

The shape of every diagram is the same: one vertical column of flow nodes, an
optional zone drawn around a run of them, sidecar cards in the right margin,
and feedback edges routed up the left gutter. That constraint is deliberate —
a general graph layout engine produces diagrams nobody can follow, while a
column reads top to bottom the way the system it describes actually runs.
"""

_WIDE = set('MWmw@%')
_NARROW = set('iljItfr.,:;!|\'" ')


def text_w(s, size, bold=False):
    """Approximate Inter's advance width. Only wrapping depends on it."""
    total = 0.0
    for ch in s:
        if ch in _WIDE:
            f = 0.86
        elif ch in _NARROW:
            f = 0.32
        elif ch.isupper():
            f = 0.66
        elif ch.isdigit():
            f = 0.58
        else:
            f = 0.54
        total += f
    return total * size * (1.05 if bold else 1.0)


def wrap(s, max_w, size, bold=False):
    lines, cur = [], ''
    for word in s.split():
        trial = f'{cur} {word}'.strip()
        if cur and text_w(trial, size, bold) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines or ['']


MARGIN = 44
GUTTER = 116          # left channel where feedback edges run
COL_W = 404           # flow node width
SIDE_W = 268          # sidecar card width
SIDE_GAP = 56
VGAP = 62             # vertical space between flow nodes, holds the edge label

HEAD_H = 104          # title band: title, subtitle, logo
TILE_H = 92           # icon-tile strip inside a node

SHAPE_H = {
    'box': 82,
    'pill': 76,
    'ellipse': 156,
    'diamond': 152,
}


def node_height(node):
    h = SHAPE_H[node['shape']]
    if node.get('tiles'):
        h += TILE_H
    return h


class Layout:
    """Positioned diagram. All coordinates are absolute, origin top-left."""

    def __init__(self, spec):
        self.spec = spec
        self.boxes = {}       # id -> dict(x, y, w, h, cx, cy)
        self.zone = None
        self.width = 0
        self.height = 0
        self._place()

    # -- placement ---------------------------------------------------------

    def _place(self):
        spec = self.spec
        has_side = bool(spec.get('sidecars'))

        col_x = MARGIN + GUTTER
        self.width = col_x + COL_W + MARGIN
        if has_side:
            self.width += SIDE_GAP + SIDE_W

        y = MARGIN + HEAD_H          # always reserved: the logo sits there even untitled

        zone_ids = set()
        zone = spec.get('zone')
        if zone:
            ids = [n['id'] for n in spec['nodes']]
            lo, hi = ids.index(zone['from']), ids.index(zone['to'])
            zone_ids = set(ids[lo:hi + 1])

        zone_top = zone_bottom = None
        for i, node in enumerate(spec['nodes']):
            # The zone frame needs room above its first node for the tab label.
            if node['id'] in zone_ids and zone_top is None:
                y += 46
                zone_top = y - 30

            h = node_height(node)
            self.boxes[node['id']] = {
                'x': col_x, 'y': y, 'w': COL_W, 'h': h,
                'cx': col_x + COL_W / 2, 'cy': y + h / 2,
            }
            y += h

            if node['id'] in zone_ids:
                zone_bottom = y + 26

            if i < len(spec['nodes']) - 1:
                y += VGAP

        if zone_top is not None:
            self.zone = {
                'x': MARGIN + 24, 'y': zone_top,
                'w': self.width - 2 * MARGIN - 24 - (0 if not has_side else 0),
                'h': zone_bottom - zone_top,
                'label': zone['label'],
            }
            # Stop the frame short of the right margin so sidecars sit outside it.
            self.zone['w'] = (col_x + COL_W + 40) - self.zone['x']

        self._place_sidecars()
        self.height = y + MARGIN

    def _place_sidecars(self):
        """Anchor each sidecar beside the node it watches, then de-overlap."""
        spec = self.spec
        side_x = MARGIN + GUTTER + COL_W + SIDE_GAP
        placed = []
        for car in spec.get('sidecars', []):
            anchor = self.boxes[car['anchor']]
            sub_lines = len(wrap(car['sub'], SIDE_W - 30, 12)) if car.get('sub') else 0
            h = (28 + 22 + sub_lines * 16 + (44 if car.get('icon') else 0)
                 + (22 if car.get('note') else 0) + 20)
            y = anchor['cy'] - h / 2
            for prev in placed:
                if y < prev['y'] + prev['h'] + 28:
                    y = prev['y'] + prev['h'] + 28
            box = {'x': side_x, 'y': y, 'w': SIDE_W, 'h': h,
                   'cx': side_x + SIDE_W / 2, 'cy': y + h / 2}
            self.boxes[car['id']] = box
            placed.append(box)

    # -- queries used by the renderer --------------------------------------

    def bottom(self, node_id):
        b = self.boxes[node_id]
        return (b['cx'], b['y'] + b['h'])

    def top(self, node_id):
        b = self.boxes[node_id]
        return (b['cx'], b['y'])

    def left(self, node_id):
        b = self.boxes[node_id]
        return (b['x'], b['cy'])

    def right(self, node_id):
        b = self.boxes[node_id]
        return (b['x'] + b['w'], b['cy'])
