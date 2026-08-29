"""
A GIF89a encoder in the standard library, plus the PNG reader that feeds it.

This exists because the repo's rule is stdlib only, and Python ships neither a
GIF writer nor a PNG reader. Both are small once written: PNG is zlib plus five
filter types, GIF is LZW plus a header. Pillow would be one import, but it is
not installable inside Claude's sandbox, and a skill that only runs on the
author's laptop is not a skill.

Only what this skill produces is supported: 8-bit non-interlaced RGB/RGBA PNGs,
which is what headless Chrome writes.
"""

import struct
import zlib

# -- PNG in ----------------------------------------------------------------

PNG_SIG = b'\x89PNG\r\n\x1a\n'


def read_png(path):
    """-> (width, height, pixels) where pixels is a flat list of (r, g, b)."""
    data = path.read_bytes() if hasattr(path, 'read_bytes') else open(path, 'rb').read()
    if data[:8] != PNG_SIG:
        raise ValueError(f'{path}: not a PNG')

    pos, idat, w = 8, bytearray(), None
    while pos < len(data):
        (length,) = struct.unpack('>I', data[pos:pos + 4])
        kind = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if kind == b'IHDR':
            w, h, depth, color, _, _, interlace = struct.unpack('>IIBBBBB', body)
            if depth != 8:
                raise ValueError(f'{path}: only 8-bit PNGs supported, got {depth}')
            if interlace:
                raise ValueError(f'{path}: interlaced PNGs not supported')
            if color not in (2, 6):
                raise ValueError(f'{path}: only RGB/RGBA PNGs supported, got colour type {color}')
            channels = 3 if color == 2 else 4
        elif kind == b'IDAT':
            idat += body
        elif kind == b'IEND':
            break
    if w is None:
        raise ValueError(f'{path}: no IHDR')

    raw = zlib.decompress(bytes(idat))
    stride = w * channels
    out, prev = [], bytearray(stride)
    at = 0
    for _ in range(h):
        ftype = raw[at]
        line = bytearray(raw[at + 1:at + 1 + stride])
        at += 1 + stride
        if ftype == 1:
            for i in range(channels, stride):
                line[i] = (line[i] + line[i - channels]) & 0xFF
        elif ftype == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif ftype == 3:
            for i in range(stride):
                left = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 0xFF
        elif ftype == 4:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                b = prev[i]
                c = prev[i - channels] if i >= channels else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pred) & 0xFF
        elif ftype != 0:
            raise ValueError(f'{path}: unknown PNG filter {ftype}')
        for x in range(0, stride, channels):
            out.append((line[x], line[x + 1], line[x + 2]))
        prev = line
    return w, h, out


# -- quantisation ----------------------------------------------------------

def quantise(frames, max_colors=256):
    """One palette for every frame. Diagrams are flat, so exact is the norm."""
    counts = {}
    for _, _, px in frames:
        for p in px:
            counts[p] = counts.get(p, 0) + 1

    if len(counts) <= max_colors:
        palette = sorted(counts)
        index = {c: i for i, c in enumerate(palette)}
        return palette, index, None

    # Median cut: split the widest channel of the heaviest box until the
    # palette is full. Antialiased text is the only thing that needs this.
    boxes = [list(counts)]
    while len(boxes) < max_colors:
        boxes.sort(key=lambda b: -_spread(b))
        box = boxes.pop(0)
        if len(box) < 2:
            boxes.append(box)
            break
        ch = _widest(box)
        box.sort(key=lambda c: c[ch])
        mid = len(box) // 2
        boxes += [box[:mid], box[mid:]]

    palette = []
    for box in boxes:
        wsum = sum(counts[c] for c in box) or 1
        palette.append(tuple(
            min(255, round(sum(c[k] * counts[c] for c in box) / wsum)) for k in range(3)))
    index = {}
    for box, rep in zip(boxes, palette):
        i = palette.index(rep)
        for c in box:
            index[c] = i
    return palette, index, True


def _spread(box):
    return max(max(c[k] for c in box) - min(c[k] for c in box) for k in range(3))


def _widest(box):
    return max(range(3), key=lambda k: max(c[k] for c in box) - min(c[k] for c in box))


# -- LZW -------------------------------------------------------------------

class _Bits:
    def __init__(self):
        self.out = bytearray()
        self.acc = 0
        self.n = 0

    def write(self, code, size):
        self.acc |= code << self.n
        self.n += size
        while self.n >= 8:
            self.out.append(self.acc & 0xFF)
            self.acc >>= 8
            self.n -= 8

    def flush(self):
        if self.n:
            self.out.append(self.acc & 0xFF)
            self.acc = self.n = 0


def lzw_encode(indices, min_code_size):
    clear, eoi = 1 << min_code_size, (1 << min_code_size) + 1
    bits = _Bits()

    def fresh():
        return {bytes([i]): i for i in range(clear)}, min_code_size + 1, eoi + 1

    table, size, nxt = fresh()
    bits.write(clear, size)

    cur = b''
    for px in indices:
        trial = cur + bytes([px])
        if trial in table:
            cur = trial
            continue
        bits.write(table[cur], size)
        table[trial] = nxt
        nxt += 1
        # The decoder adds each entry one code later than the encoder does, so
        # its table is always one short of ours when it reads the next code.
        # Widening at (1 << size) would emit a wide code while the decoder is
        # still reading narrow ones; the extra 1 keeps the two in step.
        if size < 12 and nxt == (1 << size) + 1:
            size += 1
        elif nxt == 4096:
            bits.write(clear, size)
            table, size, nxt = fresh()
        cur = bytes([px])

    if cur:
        bits.write(table[cur], size)
    bits.write(eoi, size)
    bits.flush()
    return bytes(bits.out)


def _blocks(data):
    """GIF carries LZW output in sub-blocks of at most 255 bytes."""
    out = bytearray()
    for i in range(0, len(data), 255):
        chunk = data[i:i + 255]
        out.append(len(chunk))
        out += chunk
    out.append(0)
    return bytes(out)


# -- GIF out ---------------------------------------------------------------

def write_gif(path, frames, delays, loop=0, diff=True):
    """
    frames: [(w, h, [(r,g,b), ...])]; delays in hundredths of a second.

    With `diff`, each frame after the first stores only the rectangle that
    changed, and inside it only the pixels that actually differ — the rest is
    a transparent index over the frame already on screen. Micro-motion touches
    a few percent of the canvas, so this is the difference between a GIF that
    is pleasant to send and one that is not.
    """
    if not frames:
        raise ValueError('no frames')
    if len(frames) != len(delays):
        raise ValueError(f'{len(frames)} frames but {len(delays)} delays')
    w, h, _ = frames[0]
    for i, (fw, fh, _) in enumerate(frames):
        if (fw, fh) != (w, h):
            raise ValueError(f'frame {i} is {fw}x{fh}, expected {w}x{h}')

    # One slot is held back for transparency when differencing.
    palette, index, approx = quantise(frames, 255 if diff and len(frames) > 1 else 256)
    transparent = len(palette) if diff and len(frames) > 1 else None
    total = len(palette) + (1 if transparent is not None else 0)
    bits = max(1, (total - 1).bit_length())
    size = 1 << bits

    out = bytearray(b'GIF89a')
    out += struct.pack('<HHBBB', w, h, 0xF0 | (bits - 1), 0, 0)
    for i in range(size):
        out += bytes(palette[i]) if i < len(palette) else b'\0\0\0'

    out += b'\x21\xFF\x0BNETSCAPE2.0\x03\x01' + struct.pack('<H', loop) + b'\x00'

    min_code = max(2, bits)
    prev = None
    for (fw, fh, px), delay in zip(frames, delays):
        if prev is None or transparent is None:
            x0, y0, cw, ch = 0, 0, w, h
            data = [index[p] for p in px]
            packed_gce = 0x00
        else:
            box = _changed_box(prev, px, w, h)
            if box is None:
                # Nothing moved: hold the previous frame for longer instead of
                # storing a duplicate.
                out[-1:] = out[-1:]
                x0, y0, cw, ch = 0, 0, 1, 1
                data = [transparent]
                packed_gce = 0x01 | (1 << 2)
            else:
                x0, y0, cw, ch = box
                data = []
                for yy in range(y0, y0 + ch):
                    row = yy * w
                    for xx in range(x0, x0 + cw):
                        cur = px[row + xx]
                        data.append(index[cur] if cur != prev[row + xx] else transparent)
                packed_gce = 0x01 | (1 << 2)      # transparency on, disposal = leave

        out += b'\x21\xF9\x04' + bytes([packed_gce]) + struct.pack('<H', delay)
        out += bytes([transparent if transparent is not None else 0, 0])
        out += b'\x2C' + struct.pack('<HHHHB', x0, y0, cw, ch, 0)
        out += bytes([min_code])
        out += _blocks(lzw_encode(data, min_code))
        prev = px
    out += b'\x3B'

    raw = bytes(out)
    path.write_bytes(raw) if hasattr(path, 'write_bytes') else open(path, 'wb').write(raw)
    return approx


def _changed_box(prev, cur, w, h):
    """Tightest rectangle covering every differing pixel, or None."""
    top, bottom = None, None
    left, right = w, -1
    for y in range(h):
        row = y * w
        rl, rr = None, None
        for x in range(w):
            if prev[row + x] != cur[row + x]:
                if rl is None:
                    rl = x
                rr = x
        if rl is not None:
            if top is None:
                top = y
            bottom = y
            left = min(left, rl)
            right = max(right, rr)
    if top is None:
        return None
    return left, top, right - left + 1, bottom - top + 1
