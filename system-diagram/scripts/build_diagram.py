#!/usr/bin/env python3
"""
Turns a diagram spec into an SVG, an animated SVG, and optionally a GIF.

    build_diagram.py spec.json -o diagram.svg
    build_diagram.py spec.json -o diagram.svg --animate
    build_diagram.py spec.json -o diagram.svg --gif

The static SVG is self-contained: Inter and every icon are embedded, so it
renders identically offline, inside a published artifact under CSP, and in a
browser print dialog. `--animate` writes a second file that reveals the
diagram step by step and loops; it is still one text file with no runtime.

`--gif` additionally rasterises each step through headless Chrome and encodes
a real GIF89a. Chrome is the only part of this skill that is not stdlib, and
it is absent from Claude's sandbox — see the message the flag prints there.

Validation is strict on purpose. A diagram with a silently dropped edge is
worse than no diagram: it is read as the truth about a system.
"""

import argparse
import json
import pathlib
import subprocess
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import layout as L          # noqa: E402
import render as R          # noqa: E402

SHAPES = set(L.SHAPE_H)
TONES = set(R.TONES)
STYLES = {'dotted', 'dashed', 'solid'}


def die(msg):
    sys.exit(f'spec error: {msg}')


def validate(spec):
    if not isinstance(spec.get('nodes'), list) or not spec['nodes']:
        die('"nodes" must be a non-empty list')

    ids = []
    for i, n in enumerate(spec['nodes']):
        where = f'nodes[{i}]'
        if not n.get('id'):
            die(f'{where} has no id')
        if not n.get('label'):
            die(f'{where} ({n["id"]}) has no label')
        n.setdefault('shape', 'box')
        n.setdefault('tone', 'neutral')
        if n['shape'] not in SHAPES:
            die(f'{where} shape {n["shape"]!r} unknown. Use one of: {", ".join(sorted(SHAPES))}')
        if n['tone'] not in TONES:
            die(f'{where} tone {n["tone"]!r} unknown. Use one of: {", ".join(sorted(TONES))}')
        ids.append(n['id'])

    for car in spec.get('sidecars', []):
        car.setdefault('tone', 'slate')
        if not car.get('id') or not car.get('label'):
            die('every sidecar needs an id and a label')
        if car['tone'] not in TONES:
            die(f'sidecar {car["id"]} tone {car["tone"]!r} unknown')
        ids.append(car['id'])

    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        die(f'duplicate ids: {", ".join(sorted(dupes))}')

    known = set(ids)
    node_ids = {n['id'] for n in spec['nodes']}

    for car in spec.get('sidecars', []):
        if car.get('anchor') not in node_ids:
            die(f'sidecar {car["id"]} anchors to {car.get("anchor")!r}, which is not a flow node')

    for kind in ('flow', 'links'):
        for i, e in enumerate(spec.get(kind, [])):
            for end in ('from', 'to'):
                if e.get(end) not in known:
                    die(f'{kind}[{i}] {end}={e.get(end)!r} is not a known id')
            if kind == 'flow' and (e['from'] not in node_ids or e['to'] not in node_ids):
                die(f'flow[{i}] must connect two flow nodes; use "links" for sidecars')
            if e.get('style') and e['style'] not in STYLES:
                die(f'{kind}[{i}] style {e["style"]!r} unknown. Use: {", ".join(sorted(STYLES))}')

    zone = spec.get('zone')
    if zone:
        for end in ('from', 'to'):
            if zone.get(end) not in node_ids:
                die(f'zone {end}={zone.get(end)!r} is not a flow node')
        if ids.index(zone['from']) > ids.index(zone['to']):
            die('zone "from" must come before "to" in the node order')
        if not zone.get('label'):
            die('zone needs a label')

    # Icons resolve here rather than mid-render, so a typo is one clear error
    # instead of a half-drawn diagram.
    for n in spec['nodes']:
        for name in filter(None, [n.get('icon')] + [t.get('icon') for t in n.get('tiles', [])]):
            if name not in R._ICONS:
                die(f'unknown icon {name!r} on node {n["id"]}. See references/icons.md')
    for car in spec.get('sidecars', []):
        if car.get('icon') and car['icon'] not in R._ICONS:
            die(f'unknown icon {car["icon"]!r} on sidecar {car["id"]}')

    return spec


def find_chrome():
    for c in ('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
              '/Applications/Chromium.app/Contents/MacOS/Chromium',
              'google-chrome', 'chromium'):
        if pathlib.Path(c).exists() or shutil.which(c):
            return c
    return None


def make_gif(rend, out_svg, frames, reveal, hold, scale):
    """Rasterise the loop through Chrome, then encode a GIF."""
    import gifenc

    chrome = find_chrome()
    if not chrome:
        sys.exit('--gif needs Chrome or Chromium, which is not on this machine.\n'
                 'The animated SVG (--animate) needs nothing and loops in any browser.')

    tmp = out_svg.parent / f'.{out_svg.stem}-frames'
    tmp.mkdir(exist_ok=True)
    w, h = int(rend.lay.width * scale), int(rend.lay.height * scale)

    if reveal:
        # One frame per stage; the diagram builds up and rests on the finished one.
        poses = [{'upto': i} for i in range(rend.max_order + 1)]
        delays = [55] * len(poses)
        delays[-1] = int(hold * 100)
    else:
        # A closed loop of the icon motion: last frame hands back to the first,
        # so the GIF cycles without a visible seam.
        poses = [{'t': i / frames} for i in range(frames)]
        delays = [max(2, round(R.CYCLE * 100 / frames))] * frames

    pngs = []
    try:
        for i, pose in enumerate(poses):
            f = tmp / f'f{i:03d}.svg'
            f.write_text(rend.svg(**pose), encoding='utf-8')
            png = tmp / f'f{i:03d}.png'
            subprocess.run([chrome, '--headless', '--disable-gpu', '--hide-scrollbars',
                            f'--force-device-scale-factor={scale}',
                            # resolve(): a relative -o path has no file: URI
                            f'--window-size={int(rend.lay.width)},{int(rend.lay.height)}',
                            f'--screenshot={png.resolve()}', f.resolve().as_uri()],
                           check=True, capture_output=True)
            pngs.append(png)
            print(f'\r  frame {i + 1}/{len(poses)}', end='', file=sys.stderr)
        print('', file=sys.stderr)

        gif = out_svg.with_suffix('.gif')
        gifenc.write_gif(gif, [gifenc.read_png(p) for p in pngs], delays)
        return gif
    finally:
        for p in tmp.glob('*'):
            p.unlink()
        tmp.rmdir()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('spec', type=pathlib.Path)
    ap.add_argument('-o', '--output', type=pathlib.Path)
    ap.add_argument('--animate', action='store_true', help='also write a looping animated SVG')
    ap.add_argument('--gif', action='store_true', help='also write a GIF (needs Chrome)')
    ap.add_argument('--reveal', action='store_true',
                    help='build the diagram up stage by stage instead of looping icon motion')
    ap.add_argument('--frames', type=int, default=30, help='frames in the motion loop')
    ap.add_argument('--hold', type=float, default=2.5, help='seconds on the last reveal frame')
    ap.add_argument('--scale', type=float, default=1.0, help='GIF pixel scale (0.6 for a smaller file)')
    ap.add_argument('--no-font', action='store_true', help='skip embedding Inter (smaller, less faithful)')
    args = ap.parse_args()

    try:
        spec = json.loads(args.spec.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        sys.exit(f'{args.spec}: invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}')

    validate(spec)
    lay = L.Layout(spec)
    rend = R.Renderer(spec, lay, embed_font=not args.no_font)

    out = args.output or args.spec.with_suffix('.svg')
    out.write_text(rend.svg(), encoding='utf-8')
    print(f'{out}  {out.stat().st_size / 1024:.0f} KB  {lay.width:.0f}x{lay.height:.0f}')

    # Say what had to be moved, and name anything that could not be.
    report = rend.board.report()
    if report:
        print(report, file=sys.stderr)

    if args.animate:
        anim = out.with_name(f'{out.stem}.anim.svg')
        anim.write_text(rend.svg(animate=True, reveal=args.reveal), encoding='utf-8')
        kind = f'{rend.max_order + 1} steps' if args.reveal else f'{R.CYCLE}s motion loop'
        print(f'{anim}  {anim.stat().st_size / 1024:.0f} KB  {kind}')

    if args.gif:
        gif = make_gif(rend, out, args.frames, args.reveal, args.hold, args.scale)
        print(f'{gif}  {gif.stat().st_size / 1024:.0f} KB')


if __name__ == '__main__':
    main()
