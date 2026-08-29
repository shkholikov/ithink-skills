"""
Overlap detection and resolution.

Three rules, in the order they are worth enforcing:

1. An edge never passes through a box — a node, a card, a label.
2. Two edges never share a track. Where they must cross, they cross cleanly at
   a right angle and not where either one is labelled.
3. Nothing is drawn on top of anything else. A label that lands on a line, on
   another label, or on a border is moved until it does not.

The renderer registers every box it draws, then asks this module where the
lines and labels may go. Anything that cannot be resolved is reported by name
rather than drawn over, because a diagram that hides part of itself is read as
the truth about a system and is wrong in a way nobody notices.
"""

PAD = 6.0          # breathing room around a box before a line counts as touching
LABEL_PAD = 3.0


def overlaps(a, b, pad=0.0):
    """a, b are (x, y, w, h)."""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw + pad <= bx or bx + bw + pad <= ax or
                ay + ah + pad <= by or by + bh + pad <= ay)


def seg_hits_rect(p, q, rect, pad=PAD):
    """Does the segment p->q pass through rect (grown by pad)?"""
    x, y, w, h = rect
    x, y, w, h = x - pad, y - pad, w + 2 * pad, h + 2 * pad
    # Cohen–Sutherland: if both ends share an outside zone, it misses.
    def code(px, py):
        c = 0
        if px < x:
            c |= 1
        elif px > x + w:
            c |= 2
        if py < y:
            c |= 4
        elif py > y + h:
            c |= 8
        return c

    c0, c1 = code(*p), code(*q)
    while True:
        if not (c0 | c1):
            return True          # both inside
        if c0 & c1:
            return False         # both beyond the same edge
        out = c0 or c1
        px, py = p if out == c0 else q
        qx, qy = q if out == c0 else p
        if out & 8:
            nx, ny = px + (qx - px) * (y + h - py) / (qy - py), y + h
        elif out & 4:
            nx, ny = px + (qx - px) * (y - py) / (qy - py), y
        elif out & 2:
            nx, ny = x + w, py + (qy - py) * (x + w - px) / (qx - px)
        else:
            nx, ny = x, py + (qy - py) * (x - px) / (qx - px)
        if out == c0:
            p, c0 = (nx, ny), code(nx, ny)
        else:
            q, c1 = (nx, ny), code(nx, ny)


def segs_cross(a1, a2, b1, b2):
    """Proper intersection of two segments, endpoints touching excluded."""
    def side(p, q, r):
        v = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        return (v > 1e-9) - (v < -1e-9)

    d1, d2 = side(a1, a2, b1), side(a1, a2, b2)
    d3, d4 = side(b1, b2, a1), side(b1, b2, a2)
    return d1 * d2 < 0 and d3 * d4 < 0


def path_segments(points):
    return list(zip(points, points[1:]))


class Board:
    """Everything already committed to the canvas."""

    def __init__(self):
        self.boxes = []       # (rect, name, kind)
        self.paths = []       # (segments, name)
        self.warnings = []
        self.resolved = {'edge/box': 0, 'edge/edge': 0, 'label': 0}

    # -- registration ------------------------------------------------------

    def block(self, rect, name, kind='box'):
        self.boxes.append((rect, name, kind))

    def path(self, points, name):
        self.paths.append((path_segments(points), name))

    # -- queries -----------------------------------------------------------

    def boxes_hit(self, points, ignore=()):
        out = []
        for p, q in path_segments(points):
            for rect, name, _ in self.boxes:
                if name in ignore or name in out:
                    continue
                if seg_hits_rect(p, q, rect):
                    out.append(name)
        return out

    def paths_crossed(self, points, ignore=()):
        out = []
        for p, q in path_segments(points):
            for segs, name in self.paths:
                if name in ignore or name in out:
                    continue
                if any(segs_cross(p, q, r, s) for r, s in segs):
                    out.append(name)
        return out

    def rect_free(self, rect, ignore=()):
        for other, name, _ in self.boxes:
            if name not in ignore and overlaps(rect, other, LABEL_PAD):
                return False
        for segs, name in self.paths:
            if name in ignore:
                continue
            for p, q in segs:
                if seg_hits_rect(p, q, rect, LABEL_PAD):
                    return False
        return True

    # -- resolution --------------------------------------------------------

    def place_label(self, candidates, w, h, name, ignore=()):
        """
        candidates: (x, y) anchor points in preference order, each the centre
        of where the label would sit. Returns the first that collides with
        nothing, or the first candidate plus a warning if none are free.
        """
        for cx, cy in candidates:
            rect = (cx - w / 2, cy - h / 2, w, h)
            if self.rect_free(rect, ignore):
                self.block(rect, name, 'label')
                if (cx, cy) != candidates[0]:
                    self.resolved['label'] += 1
                return cx, cy
        cx, cy = candidates[0]
        blocker = self._first_blocker((cx - w / 2, cy - h / 2, w, h), ignore)
        self.warnings.append(f'label {name!r} overlaps {blocker}; no free slot among '
                             f'{len(candidates)} positions')
        self.block((cx - w / 2, cy - h / 2, w, h), name, 'label')
        return cx, cy

    def _first_blocker(self, rect, ignore=()):
        for other, name, _ in self.boxes:
            if name not in ignore and overlaps(rect, other, LABEL_PAD):
                return name
        for segs, name in self.paths:
            if name in ignore:
                continue
            for p, q in segs:
                if seg_hits_rect(p, q, rect, LABEL_PAD):
                    return f'edge {name}'
        return 'something'

    def pick_lane(self, span, lanes, name):
        """
        Choose a vertical track for an edge spanning (top, bottom).

        `lanes` maps lane index -> list of spans already using it. The first
        lane whose spans do not overlap this one is free by construction, so
        two feedback loops can never share a column over the same rows.
        """
        top, bottom = min(span), max(span)
        i = 0
        while True:
            taken = lanes.setdefault(i, [])
            if all(bottom + 24 <= t or b + 24 <= top for t, b in taken):
                taken.append((top, bottom))
                if i:
                    self.resolved['edge/edge'] += 1
                return i
            i += 1

    def report(self):
        fixed = sum(self.resolved.values())
        lines = []
        if fixed:
            detail = ', '.join(f'{v} {k}' for k, v in self.resolved.items() if v)
            lines.append(f'  resolved {fixed} collision{"s" if fixed != 1 else ""} ({detail})')
        lines += [f'  warning: {w}' for w in self.warnings]
        return '\n'.join(lines)
