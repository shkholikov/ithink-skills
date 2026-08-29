#!/usr/bin/env python3
"""
Run with plain python3, no dependencies:

    python3 tests/test_system_diagram.py
"""

import json
import pathlib
import random
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

import build_diagram as B   # noqa: E402
import collide as C         # noqa: E402
import gifenc               # noqa: E402
import layout as L          # noqa: E402
import render as R          # noqa: E402


def spec(**over):
    base = {
        'nodes': [
            {'id': 'a', 'label': 'A'},
            {'id': 'b', 'label': 'B', 'tone': 'blue'},
        ],
        'flow': [{'from': 'a', 'to': 'b'}],
    }
    # Replacing the default nodes invalidates the default flow, and a helper
    # that quietly produces a dangling edge tests the wrong failure.
    if 'nodes' in over and 'flow' not in over:
        base.pop('flow')
    base.update(over)
    return json.loads(json.dumps(base))


class Validation(unittest.TestCase):
    """Every bad spec must name what is wrong, not raise a traceback."""

    def bad(self, s, fragment):
        with self.assertRaises(SystemExit) as cm:
            B.validate(s)
        self.assertIn(fragment, str(cm.exception))

    def test_accepts_minimal(self):
        self.assertIsNotNone(B.validate(spec()))

    def test_rejects_no_nodes(self):
        self.bad({'nodes': []}, 'non-empty')

    def test_rejects_missing_label(self):
        self.bad(spec(nodes=[{'id': 'a'}]), 'no label')

    def test_rejects_duplicate_ids(self):
        s = spec(nodes=[{'id': 'a', 'label': 'A'}, {'id': 'a', 'label': 'B'}])
        self.bad(s, 'duplicate ids')

    def test_rejects_unknown_shape(self):
        self.bad(spec(nodes=[{'id': 'a', 'label': 'A', 'shape': 'hexagon'}]), 'hexagon')

    def test_rejects_unknown_tone(self):
        self.bad(spec(nodes=[{'id': 'a', 'label': 'A', 'tone': 'puce'}]), 'puce')

    def test_rejects_dangling_edge(self):
        self.bad(spec(flow=[{'from': 'a', 'to': 'ghost'}]), 'ghost')

    def test_rejects_unknown_icon(self):
        self.bad(spec(nodes=[{'id': 'a', 'label': 'A', 'icon': 'unicorn'}]), 'unicorn')

    def test_rejects_sidecar_anchored_to_nothing(self):
        s = spec(sidecars=[{'id': 's', 'label': 'S', 'anchor': 'nope'}])
        self.bad(s, 'not a flow node')

    def test_rejects_backwards_zone(self):
        self.bad(spec(zone={'label': 'Z', 'from': 'b', 'to': 'a'}), 'must come before')

    def test_rejects_flow_edge_to_sidecar(self):
        s = spec(sidecars=[{'id': 's', 'label': 'S', 'anchor': 'a'}],
                 flow=[{'from': 'a', 'to': 's'}])
        self.bad(s, 'use "links"')


class Geometry(unittest.TestCase):
    def test_nodes_stack_without_overlap(self):
        s = B.validate(spec(nodes=[{'id': str(i), 'label': f'N{i}'} for i in range(6)]))
        lay = L.Layout(s)
        boxes = [lay.boxes[str(i)] for i in range(6)]
        for lo, hi in zip(boxes, boxes[1:]):
            self.assertGreaterEqual(hi['y'], lo['y'] + lo['h'], 'nodes overlap vertically')

    def test_tiles_make_a_node_taller(self):
        plain = L.node_height({'shape': 'box'})
        tiled = L.node_height({'shape': 'box', 'tiles': [{'icon': 'user', 'label': 'x'}]})
        self.assertEqual(tiled - plain, L.TILE_H)

    def test_zone_encloses_its_nodes(self):
        s = B.validate(spec(zone={'label': 'Z', 'from': 'a', 'to': 'b'}))
        lay = L.Layout(s)
        z = lay.zone
        for nid in ('a', 'b'):
            b = lay.boxes[nid]
            self.assertGreater(b['y'], z['y'])
            self.assertLess(b['y'] + b['h'], z['y'] + z['h'])

    def test_sidecars_do_not_overlap_each_other(self):
        s = B.validate(spec(sidecars=[
            {'id': 's1', 'label': 'One', 'anchor': 'a', 'sub': 'x'},
            {'id': 's2', 'label': 'Two', 'anchor': 'a', 'sub': 'y'},
        ]))
        lay = L.Layout(s)
        one, two = lay.boxes['s1'], lay.boxes['s2']
        self.assertGreaterEqual(two['y'], one['y'] + one['h'])

    def test_sidecar_height_grows_with_wrapped_text(self):
        short = B.validate(spec(sidecars=[{'id': 's', 'label': 'S', 'anchor': 'a', 'sub': 'one'}]))
        long = B.validate(spec(sidecars=[{'id': 's', 'label': 'S', 'anchor': 'a',
                                          'sub': 'a much longer subtitle ' * 4}]))
        self.assertGreater(L.Layout(long).boxes['s']['h'], L.Layout(short).boxes['s']['h'])

    def test_everything_fits_the_canvas(self):
        s = B.validate(json.loads((ROOT / 'examples/harness.json').read_text()))
        lay = L.Layout(s)
        for nid, b in lay.boxes.items():
            self.assertGreaterEqual(b['x'], 0, nid)
            self.assertLessEqual(b['x'] + b['w'], lay.width, nid)
            self.assertLessEqual(b['y'] + b['h'], lay.height, nid)


class Svg(unittest.TestCase):
    def build(self, s):
        s = B.validate(s)
        return R.Renderer(s, L.Layout(s), embed_font=False)

    def test_is_well_formed_xml(self):
        from xml.etree import ElementTree
        svg = self.build(json.loads((ROOT / 'examples/harness.json').read_text())).svg()
        ElementTree.fromstring(svg)   # raises if malformed

    def test_labels_are_escaped(self):
        r = self.build(spec(nodes=[{'id': 'a', 'label': 'A & <b>B</b>'}]))
        svg = r.svg()
        self.assertIn('A &amp; &lt;b&gt;', svg)
        self.assertNotIn('<b>B</b>', svg)

    def test_frames_grow_monotonically(self):
        r = self.build(json.loads((ROOT / 'examples/harness.json').read_text()))
        sizes = [len(r.svg(upto=i)) for i in range(r.max_order + 1)]
        self.assertEqual(sizes, sorted(sizes), 'a later frame drew less than an earlier one')

    def test_motion_poses_differ_and_static_has_none(self):
        r = self.build(json.loads((ROOT / 'examples/harness.json').read_text()))
        still = r.svg()
        self.assertNotIn('m-swing', still)
        self.assertNotEqual(r.svg(t=0.0), r.svg(t=0.3))

    def test_animated_svg_declares_motion_and_respects_reduced_motion(self):
        r = self.build(json.loads((ROOT / 'examples/harness.json').read_text()))
        css = r.svg(animate=True)
        self.assertIn('@keyframes m-swing', css)
        self.assertIn('prefers-reduced-motion', css)

    def test_last_frame_equals_static(self):
        r = self.build(json.loads((ROOT / 'examples/harness.json').read_text()))
        self.assertEqual(r.svg(upto=r.max_order), r.svg())

    def test_solid_links_are_not_dashed(self):
        s = spec(links=[{'from': 'a', 'to': 'b', 'style': 'solid'}])
        self.assertNotIn('stroke-dasharray', self.build(s).svg().split('<defs>')[-1])

    def test_no_external_references(self):
        svg = self.build(json.loads((ROOT / 'examples/harness.json').read_text())).svg()
        self.assertNotIn('http://', svg.replace('http://www.w3.org', ''))
        self.assertNotIn('https://', svg)


class Collision(unittest.TestCase):
    """Rules: lines miss boxes, lines miss lines, nothing sits on anything."""

    def test_segment_through_box_is_detected(self):
        box = (10, 10, 20, 20)
        self.assertTrue(C.seg_hits_rect((0, 20), (40, 20), box))
        self.assertFalse(C.seg_hits_rect((0, 60), (40, 60), box))

    def test_segment_touching_the_pad_counts(self):
        box = (10, 10, 20, 20)
        self.assertTrue(C.seg_hits_rect((0, 8), (40, 8), box, pad=4))
        self.assertFalse(C.seg_hits_rect((0, 8), (40, 8), box, pad=0))

    def test_crossing_segments(self):
        self.assertTrue(C.segs_cross((0, 0), (10, 10), (0, 10), (10, 0)))
        self.assertFalse(C.segs_cross((0, 0), (10, 0), (0, 5), (10, 5)))

    def test_touching_endpoints_are_not_a_crossing(self):
        # Edges legitimately meet at a node; that must not be reported.
        self.assertFalse(C.segs_cross((0, 0), (10, 0), (10, 0), (20, 0)))

    def test_label_moves_to_a_free_slot(self):
        b = C.Board()
        b.block((0, 0, 50, 20), 'node')
        x, y = b.place_label([(25, 10), (25, 60)], 40, 16, 'lbl')
        self.assertEqual((x, y), (25, 60), 'label should have moved off the node')
        self.assertEqual(b.resolved['label'], 1)

    def test_label_warns_when_nothing_is_free(self):
        b = C.Board()
        b.block((0, 0, 200, 200), 'wall')
        b.place_label([(50, 50), (60, 60)], 20, 10, 'lbl')
        self.assertTrue(any('no free slot' in w for w in b.warnings))

    def test_lanes_separate_overlapping_spans(self):
        b, lanes = C.Board(), {}
        self.assertEqual(b.pick_lane((0, 100), lanes, 'a'), 0)
        self.assertEqual(b.pick_lane((50, 150), lanes, 'b'), 1, 'overlapping spans need lanes')
        self.assertEqual(b.pick_lane((400, 500), lanes, 'c'), 0, 'disjoint spans may share')

    def test_example_diagram_has_no_unresolved_overlap(self):
        s = B.validate(json.loads((ROOT / 'examples/harness.json').read_text()))
        r = R.Renderer(s, L.Layout(s), embed_font=False)
        r.svg()
        self.assertEqual(r.board.warnings, [], 'the shipped example must be clean')

    def test_no_edge_passes_through_a_node(self):
        s = B.validate(json.loads((ROOT / 'examples/harness.json').read_text()))
        lay = L.Layout(s)
        r = R.Renderer(s, lay, embed_font=False)
        r.svg()
        node_ids = {n['id'] for n in s['nodes']}
        for segs, name in r.board.paths:
            ends = set(name.split('->'))
            for p, q in segs:
                for nid in node_ids - ends:
                    box = lay.boxes[nid]
                    self.assertFalse(
                        C.seg_hits_rect(p, q, (box['x'], box['y'], box['w'], box['h']), pad=0),
                        f'edge {name} crosses node {nid}')


class Lzw(unittest.TestCase):
    """The encoder shipped broken once; these are the cases that caught it."""

    @staticmethod
    def decode(data, mcs):
        clear, eoi = 1 << mcs, (1 << mcs) + 1

        def reset():
            return {c: [c] for c in range(clear)}, mcs + 1, eoi + 1

        table, size, nxt = reset()
        out, prev, acc, accn, i = [], None, 0, 0, 0
        while True:
            while accn < size:
                if i >= len(data):
                    return out
                acc |= data[i] << accn
                accn += 8
                i += 1
            code = acc & ((1 << size) - 1)
            acc >>= size
            accn -= size
            if code == clear:
                table, size, nxt = reset()
                prev = None
                continue
            if code == eoi:
                return out
            if code in table:
                entry = table[code]
            elif prev is not None and code == nxt:
                entry = prev + [prev[0]]
            else:
                raise ValueError(f'bad code {code} at {len(out)} px')
            out += entry
            if prev is not None:
                table[nxt] = prev + [entry[0]]
                nxt += 1
                if nxt == (1 << size) and size < 12:
                    size += 1
            prev = entry

    def roundtrip(self, data, colors):
        mcs = max(2, (colors - 1).bit_length())
        self.assertEqual(self.decode(gifenc.lzw_encode(data, mcs), mcs), data)

    def test_short(self):
        self.roundtrip([0, 1, 2, 3, 3, 2, 1, 0], 4)

    def test_widths_grow(self):
        random.seed(1)
        self.roundtrip([random.randrange(256) for _ in range(70000)], 256)

    def test_dictionary_reset(self):
        # Long and varied enough to exhaust 4096 codes and force a clear.
        self.roundtrip([(i * 7) % 251 for i in range(600000)], 256)

    def test_two_colours(self):
        random.seed(2)
        self.roundtrip([random.randrange(2) for _ in range(20000)], 2)


class Gif(unittest.TestCase):
    def frames(self, n=3, w=4, h=3):
        return [(w, h, [(i * 40 % 256, 10, 20)] * (w * h)) for i in range(n)]

    def test_header_and_trailer(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / 'a.gif'
            gifenc.write_gif(p, self.frames(), [10, 10, 10])
            raw = p.read_bytes()
            self.assertTrue(raw.startswith(b'GIF89a'))
            self.assertTrue(raw.endswith(b'\x3B'))
            self.assertIn(b'NETSCAPE2.0', raw)

    def test_rejects_mismatched_delays(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                gifenc.write_gif(pathlib.Path(d) / 'a.gif', self.frames(3), [10])

    def test_rejects_mixed_sizes(self):
        frames = self.frames(2) + [(8, 8, [(0, 0, 0)] * 64)]
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                gifenc.write_gif(pathlib.Path(d) / 'a.gif', frames, [10, 10, 10])

    def test_exact_palette_when_few_colours(self):
        palette, index, approx = gifenc.quantise(self.frames(3))
        self.assertIsNone(approx, 'should not approximate a 3-colour image')
        self.assertEqual(len(palette), 3)

    def test_changed_box_is_none_when_identical(self):
        px = [(1, 2, 3)] * 12
        self.assertIsNone(gifenc._changed_box(px, list(px), 4, 3))

    def test_changed_box_is_tight(self):
        a = [(0, 0, 0)] * 25
        b = list(a)
        b[2 * 5 + 3] = (9, 9, 9)      # one pixel at x=3, y=2
        self.assertEqual(gifenc._changed_box(a, b, 5, 5), (3, 2, 1, 1))

    def test_differencing_shrinks_a_mostly_static_loop(self):
        w = h = 24
        base = [(240, 240, 240)] * (w * h)
        frames = []
        for k in range(8):
            px = list(base)
            px[k * w + k] = (10, 20, 30)   # one moving dot
            frames.append((w, h, px))
        delays = [8] * len(frames)
        with tempfile.TemporaryDirectory() as d:
            big = pathlib.Path(d) / 'full.gif'
            small = pathlib.Path(d) / 'diff.gif'
            gifenc.write_gif(big, frames, delays, diff=False)
            gifenc.write_gif(small, frames, delays, diff=True)
            self.assertLess(small.stat().st_size, big.stat().st_size)
            for f in (big, small):
                raw = f.read_bytes()
                self.assertTrue(raw.startswith(b'GIF89a') and raw.endswith(b'\x3B'))

    def test_quantises_when_over_256(self):
        px = [(i % 256, (i // 256) % 256, i % 7) for i in range(20000)]
        palette, index, approx = gifenc.quantise([(200, 100, px)])
        self.assertTrue(approx)
        self.assertLessEqual(len(palette), 256)
        self.assertTrue(all(p in index for p in px), 'every colour needs a palette slot')


if __name__ == '__main__':
    unittest.main(verbosity=2)
