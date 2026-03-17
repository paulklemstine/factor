#!/usr/bin/env python3
"""
v20_supernatural_codec_v3.py — Supernatural Maximum Compression Codec v3

Eight NEW techniques on top of v19's best findings:
1. 4-bit and 5-bit quantization (extreme lossy)
2. Pythagorean wavelet + quantize preprocessing
3. Prediction + residual quantization (LP-2/LP-4)
4. Range-adaptive quantization (per-segment bit allocation)
5. Second-order delta + 3-4 bit quantize (GPS/smooth killer)
6. rANS (asymmetric numeral systems) replacing arithmetic coding
7. Hybrid: wavelet -> delta -> quant -> ANS pipeline
8. Context-adaptive quantization (previous-value prediction)

v19 records to beat:
- stock_prices: 20.94x (quant_6)
- gps_coords: 42.55x (dquant_6)
- temperatures: 11.94x (quant_6)
- pixel_values: 10.18x (bitplane_6)
- near_rational: 12.25x (fused_dqa_6)
- audio: 12.48x (quant_6)
"""

import struct, math, time, zlib, gc, os, sys
from collections import Counter

# ==============================================================================
# VARINT ENCODING (from v19)
# ==============================================================================

def _enc_uv(val):
    buf = bytearray()
    while val > 0x7F:
        buf.append((val & 0x7F) | 0x80); val >>= 7
    buf.append(val & 0x7F)
    return bytes(buf)

def _enc_sv(val):
    z = (val << 1) ^ (val >> 63) if val >= 0 else (((-val) << 1) - 1)
    return _enc_uv(z)

def _dec_uv(data, pos):
    result = shift = 0
    while pos < len(data):
        b = data[pos]; result |= (b & 0x7F) << shift; pos += 1
        if not (b & 0x80): return result, pos
        shift += 7
    raise ValueError("truncated varint")

def _dec_sv(data, pos):
    z, pos = _dec_uv(data, pos)
    return (z >> 1) ^ -(z & 1), pos

# ==============================================================================
# ARITHMETIC CODER (32-bit, from v19)
# ==============================================================================

_AC_BITS = 32
_AC_TOP = 1 << _AC_BITS
_AC_HALF = _AC_TOP >> 1
_AC_QTR = _AC_HALF >> 1

class ArithEncoder:
    __slots__ = ('lo', 'hi', 'pending', 'bits')
    def __init__(self):
        self.lo = 0; self.hi = _AC_TOP; self.pending = 0; self.bits = []

    def _emit(self, bit):
        self.bits.append(bit)
        p = self.pending; opp = 1 - bit
        for _ in range(p): self.bits.append(opp)
        self.pending = 0

    def encode_sym(self, icdf, sym):
        rng = self.hi - self.lo
        self.hi = self.lo + (rng * icdf[sym + 1]) // _AC_TOP
        self.lo = self.lo + (rng * icdf[sym]) // _AC_TOP
        while True:
            if self.hi <= _AC_HALF:
                self._emit(0); self.lo <<= 1; self.hi <<= 1
            elif self.lo >= _AC_HALF:
                self._emit(1)
                self.lo = (self.lo - _AC_HALF) << 1
                self.hi = (self.hi - _AC_HALF) << 1
            elif self.lo >= _AC_QTR and self.hi <= 3 * _AC_QTR:
                self.pending += 1
                self.lo = (self.lo - _AC_QTR) << 1
                self.hi = (self.hi - _AC_QTR) << 1
            else:
                break

    def finish(self):
        self.pending += 1
        self._emit(0 if self.lo < _AC_QTR else 1)
        bits = self.bits
        buf = bytearray((len(bits) + 7) // 8)
        for i, b in enumerate(bits):
            if b: buf[i >> 3] |= (1 << (7 - (i & 7)))
        return bytes(buf), len(bits)


class ArithDecoder:
    __slots__ = ('data', 'n_bits', 'bit_pos', 'lo', 'hi', 'val')
    def __init__(self, data, n_bits):
        self.data = data; self.n_bits = n_bits; self.bit_pos = 0
        self.lo = 0; self.hi = _AC_TOP; self.val = 0
        for _ in range(_AC_BITS):
            self.val = (self.val << 1) | self._get_bit()

    def _get_bit(self):
        bp = self.bit_pos
        if bp >= self.n_bits:
            self.bit_pos = bp + 1; return 0
        self.bit_pos = bp + 1
        byte_idx = bp >> 3
        if byte_idx >= len(self.data): return 0
        return (self.data[byte_idx] >> (7 - (bp & 7))) & 1

    def decode_sym(self, icdf, n_syms):
        rng = self.hi - self.lo
        target = ((self.val - self.lo + 1) * _AC_TOP - 1) // rng
        lo_s, hi_s = 0, n_syms
        while lo_s < hi_s:
            mid = (lo_s + hi_s) // 2
            if icdf[mid + 1] <= target: lo_s = mid + 1
            else: hi_s = mid
        sym = lo_s
        self.hi = self.lo + (rng * icdf[sym + 1]) // _AC_TOP
        self.lo = self.lo + (rng * icdf[sym]) // _AC_TOP
        while True:
            if self.hi <= _AC_HALF:
                self.lo <<= 1; self.hi <<= 1
                self.val = (self.val << 1) | self._get_bit()
            elif self.lo >= _AC_HALF:
                self.lo = (self.lo - _AC_HALF) << 1
                self.hi = (self.hi - _AC_HALF) << 1
                self.val = ((self.val - _AC_HALF) << 1) | self._get_bit()
            elif self.lo >= _AC_QTR and self.hi <= 3 * _AC_QTR:
                self.lo = (self.lo - _AC_QTR) << 1
                self.hi = (self.hi - _AC_QTR) << 1
                self.val = ((self.val - _AC_QTR) << 1) | self._get_bit()
            else:
                break
        return sym


def build_adaptive_icdf(symbols, max_sym):
    freq = [1] * (max_sym + 1)
    for s in symbols:
        if 0 <= s <= max_sym: freq[s] += 1
    total = sum(freq)
    icdf = [0]; running = 0
    for f in freq:
        running += f
        icdf.append(int(running / total * _AC_TOP))
    icdf[0] = 0; icdf[-1] = _AC_TOP
    for i in range(1, len(icdf)):
        if icdf[i] <= icdf[i-1]: icdf[i] = icdf[i-1] + 1
    return icdf, freq


def arith_encode_adaptive(symbols, max_sym):
    icdf, freq = build_adaptive_icdf(symbols, max_sym)
    enc = ArithEncoder()
    for s in symbols:
        enc.encode_sym(icdf, min(s, max_sym))
    buf, n_bits = enc.finish()
    freq_buf = bytearray()
    for f in freq: freq_buf.extend(_enc_uv(f))
    return struct.pack('<HI', max_sym, n_bits) + bytes(freq_buf) + buf, n_bits


def arith_decode_adaptive(data, pos, count):
    max_sym, n_bits = struct.unpack_from('<HI', data, pos); pos += 6
    freq = []
    for _ in range(max_sym + 1):
        v, pos = _dec_uv(data, pos); freq.append(v)
    total = sum(freq)
    icdf = [0]; running = 0
    for f in freq:
        running += f
        icdf.append(int(running / total * _AC_TOP))
    icdf[0] = 0; icdf[-1] = _AC_TOP
    for i in range(1, len(icdf)):
        if icdf[i] <= icdf[i-1]: icdf[i] = icdf[i-1] + 1
    n_bytes = (n_bits + 7) // 8
    arith_data = data[pos:pos + n_bytes]; pos += n_bytes
    dec = ArithDecoder(arith_data, n_bits)
    syms = [dec.decode_sym(icdf, max_sym + 1) for _ in range(count)]
    return syms, pos


# ==============================================================================
# rANS ENCODER/DECODER (Technique 6)
# Asymmetric Numeral Systems — faster than arithmetic coding, same compression
# ==============================================================================

_RANS_BITS = 32
_RANS_LOWER = 1 << 23  # renorm threshold
_RANS_UPPER = _RANS_LOWER << 8

def _rans_build_table(freq, total):
    """Build cumulative frequency table for rANS."""
    cdf = [0]
    for f in freq:
        cdf.append(cdf[-1] + f)
    return cdf

def rans_encode(symbols, max_sym):
    """rANS encode a list of symbols. Returns bytes."""
    freq = [1] * (max_sym + 1)
    for s in symbols:
        if 0 <= s <= max_sym: freq[s] += 1
    total = sum(freq)

    # Normalize frequencies to power of 2 for fast division
    # Use M = 1 << 12 = 4096
    M_BITS = 12
    M = 1 << M_BITS
    # Scale frequencies
    scaled = [max(1, int(f * M / total)) for f in freq]
    # Adjust to sum to M
    diff = M - sum(scaled)
    # Add/subtract from largest
    max_idx = max(range(len(scaled)), key=lambda i: scaled[i])
    scaled[max_idx] += diff

    cdf = [0]
    for f in scaled:
        cdf.append(cdf[-1] + f)

    # Encode in reverse order (rANS requirement)
    state = _RANS_LOWER
    out_bytes = bytearray()

    for s in reversed(symbols):
        sym = min(s, max_sym)
        f_s = scaled[sym]
        c_s = cdf[sym]

        # Renormalize: push bytes out while state is too large
        while state >= f_s * _RANS_UPPER // M:
            out_bytes.append(state & 0xFF)
            state >>= 8

        # Encode: state = (state // f_s) * M + (state % f_s) + c_s
        state = (state // f_s) * M + (state % f_s) + c_s

    # Flush final state (4 bytes)
    for _ in range(4):
        out_bytes.append(state & 0xFF)
        state >>= 8

    out_bytes.reverse()

    # Pack: freq table + encoded data
    freq_buf = bytearray()
    for f in scaled:
        freq_buf.extend(_enc_uv(f))

    header = struct.pack('<HI', max_sym, len(out_bytes))
    return header + bytes(freq_buf) + bytes(out_bytes)


def rans_decode(data, pos, count):
    """rANS decode."""
    max_sym, data_len = struct.unpack_from('<HI', data, pos); pos += 6

    scaled = []
    for _ in range(max_sym + 1):
        v, pos = _dec_uv(data, pos)
        scaled.append(v)

    M_BITS = 12
    M = 1 << M_BITS
    cdf = [0]
    for f in scaled:
        cdf.append(cdf[-1] + f)

    # Build reverse lookup: for each cumulative value, which symbol?
    sym_lookup = [0] * M
    for s in range(max_sym + 1):
        for j in range(cdf[s], cdf[s + 1]):
            if j < M:
                sym_lookup[j] = s

    enc_data = data[pos:pos + data_len]; pos += data_len

    # Initialize state from first 4 bytes
    state = 0
    byte_pos = 0
    for _ in range(4):
        state = (state << 8) | enc_data[byte_pos]
        byte_pos += 1

    symbols = []
    for _ in range(count):
        # Find symbol from state
        slot = state & (M - 1)  # state mod M (fast since M is power of 2)
        sym = sym_lookup[slot]
        f_s = scaled[sym]
        c_s = cdf[sym]

        # Decode step
        state = f_s * (state >> M_BITS) + slot - c_s

        # Renormalize
        while state < _RANS_LOWER and byte_pos < len(enc_data):
            state = (state << 8) | enc_data[byte_pos]
            byte_pos += 1

        symbols.append(sym)

    return symbols, pos


# ==============================================================================
# HELPER: Zigzag encoding for signed integers
# ==============================================================================

def _zigzag(vals):
    return [(v << 1) if v >= 0 else (((-v) << 1) - 1) for v in vals]

def _unzigzag(zz):
    return [(z >> 1) if z % 2 == 0 else -((z + 1) >> 1) for z in zz]


# ==============================================================================
# v19 BASELINE TECHNIQUES (needed for comparison)
# ==============================================================================

def _quantize_arith_encode(values, bits=16):
    if not values: return b''
    vmin = min(values); vmax = max(values)
    span = vmax - vmin if vmax > vmin else 1.0
    scale = ((1 << bits) - 1) / span
    ints = [max(0, min((1 << bits)-1, round((v - vmin) * scale))) for v in values]
    deltas = [ints[0]] + [ints[i] - ints[i-1] for i in range(1, len(ints))]
    zz = _zigzag(deltas)
    max_zz = max(zz) if zz else 0
    payload, _ = arith_encode_adaptive(zz, min(max_zz, 4095))
    return struct.pack('<ddH', vmin, scale, bits) + payload

def _quantize_arith_decode(data, pos, count):
    vmin, scale, bits = struct.unpack_from('<ddH', data, pos); pos += 18
    zz, pos = arith_decode_adaptive(data, pos, count)
    deltas = _unzigzag(zz)
    ints = [deltas[0]]
    for i in range(1, len(deltas)): ints.append(ints[-1] + deltas[i])
    return [vmin + i / scale for i in ints]

def _delta_quant_encode(values, bits=12):
    if len(values) < 2:
        return b'\x00' + _quantize_arith_encode(values, bits)
    deltas = [values[0]] + [values[i] - values[i-1] for i in range(1, len(values))]
    return b'\x01' + _quantize_arith_encode(deltas, bits)

def _delta_quant_decode(data, pos, count):
    order = data[pos]; pos += 1
    if order == 0:
        return _quantize_arith_decode(data, pos, count)
    vals = _quantize_arith_decode(data, pos, count)
    for i in range(1, len(vals)): vals[i] += vals[i-1]
    return vals

def fused_dqa_encode(values, bits=8):
    """Delta + quantize + arithmetic in a fused pipeline (from v19)."""
    n = len(values)
    if n == 0: return b''
    results = []

    # Order 0: direct quantize
    vmin0 = min(values); vmax0 = max(values)
    span0 = vmax0 - vmin0 if vmax0 > vmin0 else 1.0
    scale0 = ((1 << bits) - 1) / span0
    ints0 = [max(0, min((1 << bits)-1, round((v - vmin0) * scale0))) for v in values]
    zz0 = _zigzag(ints0)
    max_zz0 = max(zz0) if zz0 else 0
    p0, _ = arith_encode_adaptive(zz0, min(max_zz0, 4095))
    enc0 = struct.pack('<BddH', 0, vmin0, scale0, bits) + p0
    results.append(enc0)

    # Order 1: delta + quantize
    deltas1 = [values[0]] + [values[i] - values[i-1] for i in range(1, n)]
    vmin1 = min(deltas1); vmax1 = max(deltas1)
    span1 = vmax1 - vmin1 if vmax1 > vmin1 else 1.0
    scale1 = ((1 << bits) - 1) / span1
    ints1 = [max(0, min((1 << bits)-1, round((d - vmin1) * scale1))) for d in deltas1]
    dd1 = [ints1[0]] + [ints1[i] - ints1[i-1] for i in range(1, n)]
    zz1 = _zigzag(dd1)
    max_zz1 = max(zz1) if zz1 else 0
    p1, _ = arith_encode_adaptive(zz1, min(max_zz1, 4095))
    enc1 = struct.pack('<BddH', 1, vmin1, scale1, bits) + p1
    results.append(enc1)

    # Order 2: double delta + quantize
    if n >= 3:
        deltas2 = [deltas1[0], deltas1[1]] + [deltas1[i] - deltas1[i-1] for i in range(2, n)]
        vmin2 = min(deltas2); vmax2 = max(deltas2)
        span2 = vmax2 - vmin2 if vmax2 > vmin2 else 1.0
        scale2 = ((1 << bits) - 1) / span2
        ints2 = [max(0, min((1 << bits)-1, round((d - vmin2) * scale2))) for d in deltas2]
        dd2 = [ints2[0]] + [ints2[i] - ints2[i-1] for i in range(1, n)]
        zz2 = _zigzag(dd2)
        max_zz2 = max(zz2) if zz2 else 0
        p2, _ = arith_encode_adaptive(zz2, min(max_zz2, 4095))
        enc2 = struct.pack('<BddH', 2, vmin2, scale2, bits) + p2
        results.append(enc2)

    return min(results, key=len)

def fused_dqa_decode(data, pos, count):
    order = data[pos]
    vmin, scale, bits = struct.unpack_from('<ddH', data, pos + 1); pos += 19
    zz, pos = arith_decode_adaptive(data, pos, count)
    dd = _unzigzag(zz)
    if order == 0:
        return [vmin + i / scale for i in dd]
    ints = [dd[0]]
    for i in range(1, len(dd)): ints.append(ints[-1] + dd[i])
    vals = [vmin + i / scale for i in ints]
    if order == 1:
        for i in range(1, len(vals)): vals[i] += vals[i-1]
    elif order == 2:
        for i in range(2, len(vals)): vals[i] += vals[i-1]
        for i in range(1, len(vals)): vals[i] += vals[i-1]
    return vals

def bitplane_encode(values, bits=12):
    """Bit-plane coding from v19."""
    n = len(values)
    if n == 0: return b''
    vmin = min(values); vmax = max(values)
    span = vmax - vmin if vmax > vmin else 1.0
    scale = ((1 << bits) - 1) / span
    ints = [max(0, min((1 << bits)-1, round((v - vmin) * scale))) for v in values]
    planes = []
    for bit_pos in range(bits - 1, -1, -1):
        plane = bytearray((n + 7) // 8)
        for i, val in enumerate(ints):
            if (val >> bit_pos) & 1:
                plane[i >> 3] |= (1 << (7 - (i & 7)))
        planes.append(bytes(plane))
    plane_data = bytearray()
    for plane in planes:
        zp = zlib.compress(plane, 6)
        if len(zp) < len(plane):
            plane_data.append(1)
            plane_data.extend(struct.pack('<H', len(zp)))
            plane_data.extend(zp)
        else:
            plane_data.append(0)
            plane_data.extend(plane)
    return struct.pack('<ddHH', vmin, scale, bits, n) + bytes(plane_data)

def bitplane_decode(data, pos, count):
    vmin, scale, bits, n = struct.unpack_from('<ddHH', data, pos); pos += 20
    plane_bytes = (n + 7) // 8
    ints = [0] * n
    for bit_pos in range(bits - 1, -1, -1):
        flag = data[pos]; pos += 1
        if flag == 1:
            zlen = struct.unpack_from('<H', data, pos)[0]; pos += 2
            plane = zlib.decompress(data[pos:pos + zlen]); pos += zlen
        else:
            plane = data[pos:pos + plane_bytes]; pos += plane_bytes
        for i in range(n):
            if (plane[i >> 3] >> (7 - (i & 7))) & 1:
                ints[i] |= (1 << bit_pos)
    return [vmin + val / scale for val in ints]


# ==============================================================================
# TECHNIQUE 1: 4-bit and 5-bit quantization
# ==============================================================================

def quant_extreme_encode(values, bits=4):
    """Extreme low-bit quantization (4 or 5 bits). Higher error, extreme compression."""
    n = len(values)
    if n == 0: return b''
    vmin = min(values); vmax = max(values)
    span = vmax - vmin if vmax > vmin else 1.0
    scale = ((1 << bits) - 1) / span
    ints = [max(0, min((1 << bits)-1, round((v - vmin) * scale))) for v in values]
    # Pack directly: 4-bit = 2 per byte, 5-bit needs bit packing
    if bits == 4:
        buf = bytearray((n + 1) // 2)
        for i, v in enumerate(ints):
            if i % 2 == 0:
                buf[i // 2] |= (v & 0xF) << 4
            else:
                buf[i // 2] |= (v & 0xF)
        return struct.pack('<ddBH', vmin, scale, bits, n) + bytes(buf)
    elif bits == 5:
        # 5-bit packing: use bit stream
        total_bits = n * 5
        buf = bytearray((total_bits + 7) // 8)
        bit_pos = 0
        for v in ints:
            for b in range(4, -1, -1):
                if (v >> b) & 1:
                    buf[bit_pos >> 3] |= (1 << (7 - (bit_pos & 7)))
                bit_pos += 1
        return struct.pack('<ddBH', vmin, scale, bits, n) + bytes(buf)
    else:
        # Fallback to arith for other bit widths
        zz = _zigzag(ints)
        max_zz = max(zz) if zz else 0
        payload, _ = arith_encode_adaptive(zz, min(max_zz, 4095))
        return struct.pack('<ddBH', vmin, scale, bits, n) + payload

def quant_extreme_decode(data, pos, count):
    vmin, scale, bits, n = struct.unpack_from('<ddBH', data, pos); pos += 19
    if bits == 4:
        ints = []
        for i in range(n):
            byte_val = data[pos + i // 2]
            if i % 2 == 0:
                ints.append((byte_val >> 4) & 0xF)
            else:
                ints.append(byte_val & 0xF)
        pos += (n + 1) // 2
    elif bits == 5:
        ints = []
        bit_pos = pos * 8
        raw = data
        for _ in range(n):
            v = 0
            for b in range(4, -1, -1):
                byte_idx = (bit_pos) >> 3
                bit_idx = 7 - ((bit_pos) & 7)
                if byte_idx < len(raw) and (raw[byte_idx] >> bit_idx) & 1:
                    v |= (1 << b)
                bit_pos += 1
            ints.append(v)
    else:
        zz, pos = arith_decode_adaptive(data, pos, count)
        ints = []
        for z in zz:
            ints.append((z >> 1) if z % 2 == 0 else -((z + 1) >> 1))
    return [vmin + i / scale for i in ints]


# ==============================================================================
# TECHNIQUE 1b: 4/5-bit delta+quantize
# ==============================================================================

def delta_quant_extreme_encode(values, bits=4):
    """Delta + extreme quantize."""
    n = len(values)
    results = []
    # Order 0
    enc0 = b'\x00' + quant_extreme_encode(values, bits)
    results.append(enc0)
    # Order 1
    if n >= 2:
        deltas = [values[0]] + [values[i] - values[i-1] for i in range(1, n)]
        enc1 = b'\x01' + quant_extreme_encode(deltas, bits)
        results.append(enc1)
    # Order 2
    if n >= 3:
        deltas = [values[0]] + [values[i] - values[i-1] for i in range(1, n)]
        deltas2 = [deltas[0], deltas[1]] + [deltas[i] - deltas[i-1] for i in range(2, n)]
        enc2 = b'\x02' + quant_extreme_encode(deltas2, bits)
        results.append(enc2)
    return min(results, key=len)

def delta_quant_extreme_decode(data, pos, count):
    order = data[pos]; pos += 1
    if order == 0:
        return quant_extreme_decode(data, pos, count)
    elif order == 1:
        vals = quant_extreme_decode(data, pos, count)
        for i in range(1, len(vals)): vals[i] += vals[i-1]
        return vals
    elif order == 2:
        vals = quant_extreme_decode(data, pos, count)
        for i in range(2, len(vals)): vals[i] += vals[i-1]
        for i in range(1, len(vals)): vals[i] += vals[i-1]
        return vals
    return quant_extreme_decode(data, pos, count)


# ==============================================================================
# TECHNIQUE 2: Pythagorean wavelet + quantize
# ==============================================================================

def _pyth_wavelet_forward(values):
    """(3,4,5) Haar-like wavelet transform. Exact rational reconstruction.
    Split into even/odd, compute averages and differences scaled by 3/5, 4/5."""
    n = len(values)
    if n < 2: return values, []
    # Pad to even length
    padded = list(values)
    if n % 2 == 1:
        padded.append(padded[-1])
    m = len(padded)
    approx = []
    detail = []
    for i in range(0, m, 2):
        a, b = padded[i], padded[i+1]
        # Haar: approx = (a+b)/2, detail = (a-b)/2
        # Pythagorean scaling: use 3/5 and 4/5 weights
        approx.append((3*a + 4*b) / 5.0)  # weighted average
        detail.append((4*a - 3*b) / 5.0)  # weighted difference
    return approx, detail

def _pyth_wavelet_inverse(approx, detail, orig_n):
    """Inverse Pythagorean wavelet."""
    m = len(approx)
    values = []
    for i in range(m):
        a_coeff = approx[i]
        d_coeff = detail[i] if i < len(detail) else 0.0
        # Inverse: solve (3a+4b)/5 = A, (4a-3b)/5 = D
        # => a = (3A+4D)/5, b = (4A-3D)/5
        # Check: 3*(3A+4D)/5 + 4*(4A-3D)/5 = (9A+12D+16A-12D)/5 = 25A/5 = 5A ... /5 = A. Correct.
        orig_a = (3*a_coeff + 4*d_coeff) / 5.0
        orig_b = (4*a_coeff - 3*d_coeff) / 5.0
        values.append(orig_a)
        values.append(orig_b)
    return values[:orig_n]

def wavelet_quant_encode(values, bits=5):
    """Wavelet transform then quantize coefficients."""
    n = len(values)
    if n == 0: return b''
    approx, detail = _pyth_wavelet_forward(values)
    # Detail coefficients are typically small -> quantize with fewer bits
    # Approx coefficients have same range as original
    approx_enc = quant_extreme_encode(approx, bits)
    detail_bits = max(3, bits - 1)  # fewer bits for detail
    detail_enc = quant_extreme_encode(detail, detail_bits) if detail else b''
    return struct.pack('<HIH', n, len(approx_enc), len(detail_enc)) + approx_enc + detail_enc

def wavelet_quant_decode(data, pos, count):
    n, approx_len, detail_len = struct.unpack_from('<HIH', data, pos); pos += 8
    approx_n = (n + 1) // 2
    detail_n = (n + 1) // 2
    approx = quant_extreme_decode(data, pos, approx_n); pos += approx_len
    detail = quant_extreme_decode(data, pos, detail_n) if detail_len > 0 else [0.0]*detail_n
    pos += detail_len
    return _pyth_wavelet_inverse(approx, detail, n)


# ==============================================================================
# TECHNIQUE 3: Prediction + residual quantization
# ==============================================================================

def pred_residual_encode(values, bits=5, order=2):
    """Linear prediction of order 2 or 4, quantize residuals only."""
    n = len(values)
    if n == 0: return b''

    # Compute residuals using LP-order prediction
    residuals = []
    for i in range(n):
        if i == 0:
            pred = 0.0
        elif i == 1:
            pred = values[0]
        elif order >= 2 and i >= 2:
            if order >= 4 and i >= 4:
                # LP-4: weighted extrapolation
                pred = (4*values[i-1] - 6*values[i-2] + 4*values[i-3] - values[i-4])
            else:
                # LP-2: linear extrapolation
                pred = 2*values[i-1] - values[i-2]
        else:
            pred = values[i-1]
        residuals.append(values[i] - pred)

    # Store first few values exactly (as float16 or scaled int)
    # Then quantize residuals
    header_vals = values[:min(order, n)]
    header_buf = struct.pack(f'<{len(header_vals)}d', *header_vals)

    # Quantize residuals[order:] with given bits
    res_to_encode = residuals[len(header_vals):]
    if res_to_encode:
        res_enc = quant_extreme_encode(res_to_encode, bits)
    else:
        res_enc = b''

    return struct.pack('<HBH', n, order, len(header_buf)) + header_buf + res_enc

def pred_residual_decode(data, pos, count):
    n, order, hdr_len = struct.unpack_from('<HBH', data, pos); pos += 5
    n_hdr = min(order, n)
    header_vals = list(struct.unpack_from(f'<{n_hdr}d', data, pos)); pos += hdr_len

    n_residuals = n - n_hdr
    if n_residuals > 0:
        residuals = quant_extreme_decode(data, pos, n_residuals)
    else:
        residuals = []

    # Reconstruct
    values = list(header_vals)
    for r in residuals:
        i = len(values)
        if i == 0:
            pred = 0.0
        elif i == 1:
            pred = values[0]
        elif order >= 4 and i >= 4:
            pred = 4*values[i-1] - 6*values[i-2] + 4*values[i-3] - values[i-4]
        elif i >= 2:
            pred = 2*values[i-1] - values[i-2]
        else:
            pred = values[i-1]
        values.append(pred + r)
    return values[:n]


# ==============================================================================
# TECHNIQUE 4: Range-adaptive quantization
# ==============================================================================

def range_adaptive_encode(values, total_bits=5):
    """Split data into blocks, measure variance per block, allocate bits adaptively."""
    n = len(values)
    if n == 0: return b''
    block_size = 64
    n_blocks = (n + block_size - 1) // block_size

    blocks = []
    for i in range(n_blocks):
        start = i * block_size
        end = min(start + block_size, n)
        blocks.append(values[start:end])

    # Measure variance per block
    variances = []
    for blk in blocks:
        if len(blk) < 2:
            variances.append(0.0)
            continue
        mean = sum(blk) / len(blk)
        var = sum((v - mean)**2 for v in blk) / len(blk)
        variances.append(var)

    max_var = max(variances) if variances else 1.0
    if max_var < 1e-30: max_var = 1.0

    # Allocate bits: low variance = fewer bits (min 3), high variance = more bits (max total_bits+2)
    block_bits = []
    for v in variances:
        ratio = v / max_var
        bits = max(3, min(total_bits + 2, round(total_bits * (0.5 + 0.5 * math.sqrt(ratio)))))
        block_bits.append(bits)

    # Encode each block with its allocated bits
    encoded_blocks = []
    for i, blk in enumerate(blocks):
        enc = quant_extreme_encode(blk, block_bits[i])
        encoded_blocks.append(enc)

    # Pack: n_blocks, block_size, bits_per_block, then block payloads
    bits_buf = bytes(block_bits)
    payload = bytearray()
    block_lens = []
    for enc in encoded_blocks:
        block_lens.append(len(enc))
        payload.extend(enc)

    lens_buf = struct.pack(f'<{n_blocks}H', *block_lens)
    return struct.pack('<HHH', n, block_size, n_blocks) + bits_buf + lens_buf + bytes(payload)

def range_adaptive_decode(data, pos, count):
    n, block_size, n_blocks = struct.unpack_from('<HHH', data, pos); pos += 6
    block_bits = list(data[pos:pos + n_blocks]); pos += n_blocks
    block_lens = list(struct.unpack_from(f'<{n_blocks}H', data, pos)); pos += n_blocks * 2

    values = []
    for i in range(n_blocks):
        blen = block_lens[i]
        start_idx = i * block_size
        end_idx = min(start_idx + block_size, n)
        blk_count = end_idx - start_idx
        blk = quant_extreme_decode(data, pos, blk_count)
        values.extend(blk)
        pos += blen
    return values[:n]


# ==============================================================================
# TECHNIQUE 5: Second-order delta + tiny quantize (GPS/smooth killer)
# ==============================================================================

def delta2_tiny_encode(values, bits=3):
    """Compute second-order differences, quantize with 3-4 bits.
    Ideal for GPS coordinates and smooth signals."""
    n = len(values)
    if n < 3: return quant_extreme_encode(values, bits + 2)

    # First differences
    d1 = [values[i] - values[i-1] for i in range(1, n)]
    # Second differences
    d2 = [d1[i] - d1[i-1] for i in range(1, len(d1))]

    # Store first 2 values exactly
    header = struct.pack('<Hdd', n, values[0], values[1])

    # Store first delta exactly
    header += struct.pack('<d', d1[0])

    # Quantize d2 with tiny bits
    if d2:
        d2_enc = quant_extreme_encode(d2, bits)
    else:
        d2_enc = b''

    return header + d2_enc

def delta2_tiny_decode(data, pos, count):
    n, v0, v1 = struct.unpack_from('<Hdd', data, pos); pos += 18
    d1_0 = struct.unpack_from('<d', data, pos)[0]; pos += 8

    if n < 3:
        return [v0, v1][:n]

    n_d2 = n - 2
    d2 = quant_extreme_decode(data, pos, n_d2) if n_d2 > 0 else []

    # Reconstruct d1 from d2
    d1 = [d1_0]
    for dd in d2:
        d1.append(d1[-1] + dd)

    # Reconstruct values from d1
    values = [v0, v1]
    for i in range(len(d1) - 0):
        if i == 0:
            continue  # d1[0] = v1 - v0, already used
        values.append(values[-1] + d1[i])

    # Fix: rebuild properly
    values = [v0]
    val = v0
    for d in d1:
        val = val + d
        values.append(val)

    return values[:n]


# ==============================================================================
# TECHNIQUE 5b: Delta2 + rANS (combine techniques 5 and 6)
# ==============================================================================

def delta2_rans_encode(values, bits=4):
    """Second-order delta + rANS encoding."""
    n = len(values)
    if n < 3:
        return b'\x00' + quant_extreme_encode(values, bits + 2)

    d1 = [values[i] - values[i-1] for i in range(1, n)]
    d2 = [d1[i] - d1[i-1] for i in range(1, len(d1))]

    header = struct.pack('<Hdd', n, values[0], values[1])
    header += struct.pack('<d', d1[0])

    if not d2:
        return b'\x01' + header

    # Quantize d2
    vmin = min(d2); vmax = max(d2)
    span = vmax - vmin if vmax > vmin else 1.0
    scale = ((1 << bits) - 1) / span
    ints = [max(0, min((1 << bits)-1, round((v - vmin) * scale))) for v in d2]

    # rANS encode
    max_int = (1 << bits) - 1
    try:
        rans_payload = rans_encode(ints, max_int)
    except Exception:
        # Fallback to arith
        zz = _zigzag(ints)
        max_zz = max(zz) if zz else 0
        rans_payload = b'\xFF' + struct.pack('<dd', vmin, scale)
        p, _ = arith_encode_adaptive(zz, min(max_zz, 4095))
        rans_payload += p
        return b'\x02' + header + rans_payload

    return b'\x01' + header + struct.pack('<dd', vmin, scale) + rans_payload

def delta2_rans_decode(data, pos, count):
    flag = data[pos]; pos += 1

    if flag == 0:
        return quant_extreme_decode(data, pos, count)

    n, v0, v1 = struct.unpack_from('<Hdd', data, pos); pos += 18
    d1_0 = struct.unpack_from('<d', data, pos)[0]; pos += 8
    n_d2 = n - 2

    if n_d2 <= 0 or flag == 1 and pos >= len(data):
        d1 = [d1_0]
        values = [v0]
        val = v0
        for d in d1:
            val += d; values.append(val)
        return values[:n]

    if flag == 2:
        # Arith fallback
        if data[pos] == 0xFF:
            pos += 1
            vmin, scale = struct.unpack_from('<dd', data, pos); pos += 16
            zz, pos = arith_decode_adaptive(data, pos, n_d2)
            ints = _unzigzag(zz)
            d2 = [vmin + i / scale for i in ints]
        else:
            d2 = quant_extreme_decode(data, pos, n_d2)
    else:
        vmin, scale = struct.unpack_from('<dd', data, pos); pos += 16
        ints, pos = rans_decode(data, pos, n_d2)
        d2 = [vmin + i / scale for i in ints]

    d1 = [d1_0]
    for dd in d2:
        d1.append(d1[-1] + dd)

    values = [v0]
    val = v0
    for d in d1:
        val += d; values.append(val)
    return values[:n]


# ==============================================================================
# TECHNIQUE 7: Hybrid wavelet -> delta -> quant -> zlib pipeline
# ==============================================================================

def hybrid_pipeline_encode(values, bits=5):
    """Full pipeline: wavelet -> delta -> quantize -> zlib/arith."""
    n = len(values)
    if n == 0: return b''

    results = []

    # Pipeline A: wavelet -> quant -> zlib
    approx, detail = _pyth_wavelet_forward(values)
    all_coeffs = approx + detail
    vmin = min(all_coeffs); vmax = max(all_coeffs)
    span = vmax - vmin if vmax > vmin else 1.0
    scale = ((1 << bits) - 1) / span
    ints = [max(0, min((1 << bits)-1, round((v - vmin) * scale))) for v in all_coeffs]
    # Pack and zlib
    if bits <= 4:
        raw = bytearray((len(ints) + 1) // 2)
        for i, v in enumerate(ints):
            if i % 2 == 0: raw[i//2] |= (v & 0xF) << 4
            else: raw[i//2] |= (v & 0xF)
    else:
        raw = bytes(ints)  # each as a byte (5-8 bit values fit in byte)
    zraw = zlib.compress(bytes(raw), 9)
    enc_a = struct.pack('<BHddH', 0, n, vmin, scale, len(all_coeffs)) + \
            struct.pack('<BH', bits, len(zraw)) + zraw
    results.append(enc_a)

    # Pipeline B: delta -> quant -> zlib
    deltas = [values[0]] + [values[i] - values[i-1] for i in range(1, n)]
    vmin_d = min(deltas); vmax_d = max(deltas)
    span_d = vmax_d - vmin_d if vmax_d > vmin_d else 1.0
    scale_d = ((1 << bits) - 1) / span_d
    ints_d = [max(0, min((1 << bits)-1, round((v - vmin_d) * scale_d))) for v in deltas]
    if bits <= 4:
        raw_d = bytearray((len(ints_d) + 1) // 2)
        for i, v in enumerate(ints_d):
            if i % 2 == 0: raw_d[i//2] |= (v & 0xF) << 4
            else: raw_d[i//2] |= (v & 0xF)
    else:
        raw_d = bytes(ints_d)
    zraw_d = zlib.compress(bytes(raw_d), 9)
    enc_b = struct.pack('<BHddH', 1, n, vmin_d, scale_d, n) + \
            struct.pack('<BH', bits, len(zraw_d)) + zraw_d
    results.append(enc_b)

    # Pipeline C: delta2 -> quant -> zlib
    if n >= 3:
        d2 = [deltas[0], deltas[1]] + [deltas[i] - deltas[i-1] for i in range(2, n)]
        vmin_d2 = min(d2); vmax_d2 = max(d2)
        span_d2 = vmax_d2 - vmin_d2 if vmax_d2 > vmin_d2 else 1.0
        scale_d2 = ((1 << bits) - 1) / span_d2
        ints_d2 = [max(0, min((1 << bits)-1, round((v - vmin_d2) * scale_d2))) for v in d2]
        if bits <= 4:
            raw_d2 = bytearray((len(ints_d2) + 1) // 2)
            for i, v in enumerate(ints_d2):
                if i % 2 == 0: raw_d2[i//2] |= (v & 0xF) << 4
                else: raw_d2[i//2] |= (v & 0xF)
        else:
            raw_d2 = bytes(ints_d2)
        zraw_d2 = zlib.compress(bytes(raw_d2), 9)
        enc_c = struct.pack('<BHddH', 2, n, vmin_d2, scale_d2, n) + \
                struct.pack('<BH', bits, len(zraw_d2)) + zraw_d2
        results.append(enc_c)

    return min(results, key=len)

def hybrid_pipeline_decode(data, pos, count):
    pipeline = data[pos]; pos += 1
    n = struct.unpack_from('<H', data, pos)[0]; pos += 2
    vmin, scale, total_n = struct.unpack_from('<ddH', data, pos); pos += 18
    bits = data[pos]; pos += 1
    zlen = struct.unpack_from('<H', data, pos)[0]; pos += 2
    raw = zlib.decompress(data[pos:pos + zlen]); pos += zlen

    # Unpack quantized ints
    if bits <= 4:
        ints = []
        for i in range(total_n):
            byte_val = raw[i // 2] if i // 2 < len(raw) else 0
            if i % 2 == 0:
                ints.append((byte_val >> 4) & 0xF)
            else:
                ints.append(byte_val & 0xF)
    else:
        ints = list(raw[:total_n])

    values = [vmin + i / scale for i in ints]

    if pipeline == 0:
        # Wavelet inverse
        half = (n + 1) // 2
        approx = values[:half]
        detail = values[half:half + half]
        return _pyth_wavelet_inverse(approx, detail, n)
    elif pipeline == 1:
        # Undo first-order delta
        for i in range(1, len(values)): values[i] += values[i-1]
        return values[:n]
    elif pipeline == 2:
        # Undo second-order delta
        for i in range(2, len(values)): values[i] += values[i-1]
        for i in range(1, len(values)): values[i] += values[i-1]
        return values[:n]
    return values[:n]


# ==============================================================================
# TECHNIQUE 8: Context-adaptive quantization
# ==============================================================================

def context_adaptive_encode(values, base_bits=5):
    """Use running statistics to predict range, allocate bits adaptively."""
    n = len(values)
    if n == 0: return b''

    # Compute deltas first (context works better on deltas)
    deltas = [values[0]] + [values[i] - values[i-1] for i in range(1, n)]

    # Sliding window to estimate local range
    window = 16
    # Quantize in blocks, adapting bits based on recent variance
    block_size = 32
    n_blocks = (n + block_size - 1) // block_size

    encoded_blocks = []
    block_bits_list = []

    running_var = 0.0
    running_count = 0

    for bi in range(n_blocks):
        start = bi * block_size
        end = min(start + block_size, n)
        blk = deltas[start:end]

        # Estimate bits needed from running variance
        if running_count > 0:
            std = math.sqrt(running_var / running_count) if running_var > 0 else 0
            # Bits needed ~ log2(range/std) approximately
            blk_range = max(blk) - min(blk) if len(blk) > 1 else 1.0
            if std > 0 and blk_range > 0:
                needed = max(3, min(base_bits + 2, round(math.log2(blk_range / std + 1) + 2)))
            else:
                needed = base_bits
        else:
            needed = base_bits

        block_bits_list.append(needed)
        enc = quant_extreme_encode(blk, needed)
        encoded_blocks.append(enc)

        # Update running stats
        for v in blk:
            running_var += v * v
            running_count += 1

    # Pack
    bits_buf = bytes(block_bits_list)
    payload = bytearray()
    block_lens = []
    for enc in encoded_blocks:
        block_lens.append(len(enc))
        payload.extend(enc)

    lens_buf = struct.pack(f'<{n_blocks}H', *block_lens)
    return struct.pack('<HHH', n, block_size, n_blocks) + bits_buf + lens_buf + bytes(payload)

def context_adaptive_decode(data, pos, count):
    n, block_size, n_blocks = struct.unpack_from('<HHH', data, pos); pos += 6
    block_bits = list(data[pos:pos + n_blocks]); pos += n_blocks
    block_lens = list(struct.unpack_from(f'<{n_blocks}H', data, pos)); pos += n_blocks * 2

    deltas = []
    for i in range(n_blocks):
        start = i * block_size
        end = min(start + block_size, n)
        blk_count = end - start
        blk = quant_extreme_decode(data, pos, blk_count)
        deltas.extend(blk)
        pos += block_lens[i]

    # Undo delta
    values = [deltas[0]]
    for i in range(1, len(deltas)):
        values.append(values[-1] + deltas[i])
    return values[:n]


# ==============================================================================
# TECHNIQUE 6b: rANS versions of best v19 methods
# ==============================================================================

def quant_rans_encode(values, bits=6):
    """Quantize + rANS (replacing arithmetic coding)."""
    n = len(values)
    if n == 0: return b''
    vmin = min(values); vmax = max(values)
    span = vmax - vmin if vmax > vmin else 1.0
    scale = ((1 << bits) - 1) / span
    ints = [max(0, min((1 << bits)-1, round((v - vmin) * scale))) for v in values]
    max_int = (1 << bits) - 1
    try:
        payload = rans_encode(ints, max_int)
    except Exception:
        # Fallback
        zz = _zigzag(ints)
        max_zz = max(zz) if zz else 0
        p, _ = arith_encode_adaptive(zz, min(max_zz, 4095))
        payload = b'\xFF' + p
    return struct.pack('<ddH', vmin, scale, bits) + payload

def quant_rans_decode(data, pos, count):
    vmin, scale, bits = struct.unpack_from('<ddH', data, pos); pos += 18
    if data[pos:pos+1] == b'\xFF':
        pos += 1
        zz, pos = arith_decode_adaptive(data, pos, count)
        ints = _unzigzag(zz)
    else:
        ints, pos = rans_decode(data, pos, count)
    return [vmin + i / scale for i in ints]

def delta_quant_rans_encode(values, bits=6):
    """Delta + quantize + rANS."""
    n = len(values)
    results = []
    enc0 = b'\x00' + quant_rans_encode(values, bits)
    results.append(enc0)
    if n >= 2:
        deltas = [values[0]] + [values[i] - values[i-1] for i in range(1, n)]
        enc1 = b'\x01' + quant_rans_encode(deltas, bits)
        results.append(enc1)
    if n >= 3:
        deltas = [values[0]] + [values[i] - values[i-1] for i in range(1, n)]
        deltas2 = [deltas[0], deltas[1]] + [deltas[i] - deltas[i-1] for i in range(2, n)]
        enc2 = b'\x02' + quant_rans_encode(deltas2, bits)
        results.append(enc2)
    return min(results, key=len)

def delta_quant_rans_decode(data, pos, count):
    order = data[pos]; pos += 1
    vals = quant_rans_decode(data, pos, count)
    if order == 1:
        for i in range(1, len(vals)): vals[i] += vals[i-1]
    elif order == 2:
        for i in range(2, len(vals)): vals[i] += vals[i-1]
        for i in range(1, len(vals)): vals[i] += vals[i-1]
    return vals


# ==============================================================================
# TECHNIQUE 3b: LP-4 prediction + delta2 combo
# ==============================================================================

def pred_delta2_encode(values, bits=4):
    """LP-2 prediction with delta2 on residuals, then quantize."""
    n = len(values)
    if n < 4: return quant_extreme_encode(values, bits + 2)

    # LP-2 residuals
    residuals = [0.0, 0.0]  # first two are stored exactly
    for i in range(2, n):
        pred = 2*values[i-1] - values[i-2]
        residuals.append(values[i] - pred)

    # Header: first 2 values
    header = struct.pack('<Hdd', n, values[0], values[1])

    # Quantize residuals[2:] directly
    res = residuals[2:]
    if res:
        res_enc = quant_extreme_encode(res, bits)
    else:
        res_enc = b''

    # Also try delta on residuals
    if len(res) >= 2:
        res_d = [res[0]] + [res[i] - res[i-1] for i in range(1, len(res))]
        res_d_enc = b'\x01' + quant_extreme_encode(res_d, bits)
    else:
        res_d_enc = b'\x01' + (quant_extreme_encode(res, bits) if res else b'')

    enc_direct = b'\x00' + header + res_enc
    enc_delta = b'\x01' + header + (quant_extreme_encode(res_d[0:] if len(res) >= 2 else res, bits) if res else b'')

    # Pick shorter
    if len(res) >= 2:
        res_d = [res[0]] + [res[i] - res[i-1] for i in range(1, len(res))]
        res_d_enc_payload = quant_extreme_encode(res_d, bits)
        enc_delta = b'\x01' + header + res_d_enc_payload
    else:
        enc_delta = enc_direct

    return min([enc_direct, enc_delta], key=len)

def pred_delta2_decode(data, pos, count):
    mode = data[pos]; pos += 1
    n, v0, v1 = struct.unpack_from('<Hdd', data, pos); pos += 18
    n_res = n - 2

    if n_res <= 0:
        return [v0, v1][:n]

    if mode == 0:
        res = quant_extreme_decode(data, pos, n_res)
    else:
        res_d = quant_extreme_decode(data, pos, n_res)
        # Undo delta on residuals
        res = [res_d[0]]
        for i in range(1, len(res_d)): res.append(res[-1] + res_d[i])

    # Reconstruct from LP-2 prediction
    values = [v0, v1]
    for r in res:
        pred = 2*values[-1] - values[-2]
        values.append(pred + r)
    return values[:n]


# ==============================================================================
# MASTER CODEC: try ALL techniques, pick shortest
# ==============================================================================

MAGIC = b"SN04"
TAG_QUANT_ARITH = 1
TAG_DELTA_QUANT = 2
TAG_FUSED_DQA = 3
TAG_BITPLANE = 4
TAG_QUANT_EXTREME = 10
TAG_DQUANT_EXTREME = 11
TAG_WAVELET_QUANT = 12
TAG_PRED_RESIDUAL = 13
TAG_RANGE_ADAPTIVE = 14
TAG_DELTA2_TINY = 15
TAG_DELTA2_RANS = 16
TAG_HYBRID_PIPE = 17
TAG_CONTEXT_ADAPTIVE = 18
TAG_QUANT_RANS = 19
TAG_DQUANT_RANS = 20
TAG_PRED_DELTA2 = 21


def v20_compress(values):
    """Try ALL v19 + v20 approaches, return shortest encoding + method name."""
    n = len(values)
    if n == 0:
        return MAGIC + struct.pack('<BBI', TAG_QUANT_ARITH, 0, 0), 'empty'

    candidates = {}

    def _try(name, tag, param, encode_fn, decode_fn):
        try:
            enc = encode_fn()
            dec = decode_fn(enc)
            if dec is None or len(dec) != n: return
            max_err = max(abs(a-b) for a,b in zip(values, dec))
            candidates[name] = (tag, param, enc, max_err)
        except Exception:
            pass

    # === V19 BASELINES ===

    for bits in [4, 5, 6, 8]:
        _try(f'quant_{bits}', TAG_QUANT_ARITH, bits,
             lambda b=bits: _quantize_arith_encode(values, b),
             lambda e, b=bits: _quantize_arith_decode(e, 0, n))

    for bits in [4, 5, 6, 8]:
        _try(f'dquant_{bits}', TAG_DELTA_QUANT, bits,
             lambda b=bits: _delta_quant_encode(values, b),
             lambda e, b=bits: _delta_quant_decode(e, 0, n))

    for bits in [4, 5, 6, 8]:
        _try(f'fused_dqa_{bits}', TAG_FUSED_DQA, bits,
             lambda b=bits: fused_dqa_encode(values, b),
             lambda e, b=bits: fused_dqa_decode(e, 0, n))

    for bits in [4, 5, 6, 8]:
        _try(f'bitplane_{bits}', TAG_BITPLANE, bits,
             lambda b=bits: bitplane_encode(values, b),
             lambda e, b=bits: bitplane_decode(e, 0, n))

    # === V20 NEW TECHNIQUES ===

    # T1: Extreme quantization (4-bit, 5-bit)
    for bits in [3, 4, 5]:
        _try(f'qext_{bits}', TAG_QUANT_EXTREME, bits,
             lambda b=bits: quant_extreme_encode(values, b),
             lambda e, b=bits: quant_extreme_decode(e, 0, n))

    # T1b: Delta + extreme quant
    for bits in [3, 4, 5]:
        _try(f'dqext_{bits}', TAG_DQUANT_EXTREME, bits,
             lambda b=bits: delta_quant_extreme_encode(values, b),
             lambda e, b=bits: delta_quant_extreme_decode(e, 0, n))

    # T2: Wavelet + quantize
    for bits in [4, 5, 6]:
        _try(f'wavelet_{bits}', TAG_WAVELET_QUANT, bits,
             lambda b=bits: wavelet_quant_encode(values, b),
             lambda e, b=bits: wavelet_quant_decode(e, 0, n))

    # T3: Prediction + residual
    for bits in [4, 5, 6]:
        for order in [2, 4]:
            _try(f'pred_r{order}_{bits}', TAG_PRED_RESIDUAL, bits,
                 lambda b=bits, o=order: pred_residual_encode(values, b, o),
                 lambda e, b=bits: pred_residual_decode(e, 0, n))

    # T4: Range-adaptive
    for bits in [4, 5, 6]:
        _try(f'radapt_{bits}', TAG_RANGE_ADAPTIVE, bits,
             lambda b=bits: range_adaptive_encode(values, b),
             lambda e, b=bits: range_adaptive_decode(e, 0, n))

    # T5: Delta2 + tiny quantize
    for bits in [3, 4, 5]:
        _try(f'd2tiny_{bits}', TAG_DELTA2_TINY, bits,
             lambda b=bits: delta2_tiny_encode(values, b),
             lambda e, b=bits: delta2_tiny_decode(e, 0, n))

    # T5b: Delta2 + rANS
    for bits in [3, 4, 5]:
        _try(f'd2rans_{bits}', TAG_DELTA2_RANS, bits,
             lambda b=bits: delta2_rans_encode(values, b),
             lambda e, b=bits: delta2_rans_decode(e, 0, n))

    # T7: Hybrid pipeline
    for bits in [4, 5, 6]:
        _try(f'hybrid_{bits}', TAG_HYBRID_PIPE, bits,
             lambda b=bits: hybrid_pipeline_encode(values, b),
             lambda e, b=bits: hybrid_pipeline_decode(e, 0, n))

    # T8: Context-adaptive
    for bits in [4, 5, 6]:
        _try(f'ctxadapt_{bits}', TAG_CONTEXT_ADAPTIVE, bits,
             lambda b=bits: context_adaptive_encode(values, b),
             lambda e, b=bits: context_adaptive_decode(e, 0, n))

    # T6b: rANS versions
    for bits in [4, 5, 6]:
        _try(f'qrans_{bits}', TAG_QUANT_RANS, bits,
             lambda b=bits: quant_rans_encode(values, b),
             lambda e, b=bits: quant_rans_decode(e, 0, n))

    for bits in [4, 5, 6]:
        _try(f'dqrans_{bits}', TAG_DQUANT_RANS, bits,
             lambda b=bits: delta_quant_rans_encode(values, b),
             lambda e, b=bits: delta_quant_rans_decode(e, 0, n))

    # T3b: Pred + delta2
    for bits in [3, 4, 5]:
        _try(f'predd2_{bits}', TAG_PRED_DELTA2, bits,
             lambda b=bits: pred_delta2_encode(values, b),
             lambda e, b=bits: pred_delta2_decode(e, 0, n))

    if not candidates:
        enc = _quantize_arith_encode(values, 6)
        candidates['fallback'] = (TAG_QUANT_ARITH, 6, enc, float('inf'))

    best_name = min(candidates, key=lambda k: len(candidates[k][2]))
    tag, param, payload, _ = candidates[best_name]
    return MAGIC + struct.pack('<BBI', tag, param, n) + payload, best_name


def v20_decompress(data):
    if data[:4] != MAGIC:
        raise ValueError("bad magic")
    tag, param, n = struct.unpack_from('<BBI', data, 4)
    off = 10

    if tag == TAG_QUANT_ARITH:
        return _quantize_arith_decode(data, off, n)
    elif tag == TAG_DELTA_QUANT:
        return _delta_quant_decode(data, off, n)
    elif tag == TAG_FUSED_DQA:
        return fused_dqa_decode(data, off, n)
    elif tag == TAG_BITPLANE:
        return bitplane_decode(data, off, n)
    elif tag == TAG_QUANT_EXTREME:
        return quant_extreme_decode(data, off, n)
    elif tag == TAG_DQUANT_EXTREME:
        return delta_quant_extreme_decode(data, off, n)
    elif tag == TAG_WAVELET_QUANT:
        return wavelet_quant_decode(data, off, n)
    elif tag == TAG_PRED_RESIDUAL:
        return pred_residual_decode(data, off, n)
    elif tag == TAG_RANGE_ADAPTIVE:
        return range_adaptive_decode(data, off, n)
    elif tag == TAG_DELTA2_TINY:
        return delta2_tiny_decode(data, off, n)
    elif tag == TAG_DELTA2_RANS:
        return delta2_rans_decode(data, off, n)
    elif tag == TAG_HYBRID_PIPE:
        return hybrid_pipeline_decode(data, off, n)
    elif tag == TAG_CONTEXT_ADAPTIVE:
        return context_adaptive_decode(data, off, n)
    elif tag == TAG_QUANT_RANS:
        return quant_rans_decode(data, off, n)
    elif tag == TAG_DQUANT_RANS:
        return delta_quant_rans_decode(data, off, n)
    elif tag == TAG_PRED_DELTA2:
        return pred_delta2_decode(data, off, n)
    raise ValueError(f"unknown tag {tag}")


# ==============================================================================
# BENCHMARK
# ==============================================================================

def generate_datasets(n=1000):
    import random
    rng = random.Random(42)
    datasets = {}

    prices = [150.0]
    for _ in range(n-1):
        prices.append(prices[-1] * (1 + rng.gauss(0.0001, 0.015)))
    datasets['stock_prices'] = prices

    datasets['temperatures'] = [20.0 + 10.0*math.sin(2*math.pi*i/365) + rng.gauss(0,2.0) for i in range(n)]
    datasets['gps_coords'] = [40.7128 + rng.gauss(0,0.01) + rng.gauss(0,0.001)*(i/n) for i in range(n)]
    datasets['pixel_values'] = [rng.randint(0,255)/255.0 for _ in range(n)]
    datasets['near_rational'] = [rng.randint(1,50)/rng.randint(1,20) + rng.gauss(0,1e-10) for _ in range(n)]
    datasets['audio_samples'] = [0.3*math.sin(2*math.pi*440*i/44100) +
                                  0.2*math.sin(2*math.pi*880*i/44100) +
                                  rng.gauss(0,0.05) for i in range(n)]
    return datasets


def benchmark_all():
    datasets = generate_datasets(1000)

    v19_best = {
        'stock_prices': ('quant_6', 20.94),
        'gps_coords': ('dquant_6', 42.55),
        'temperatures': ('quant_6', 11.94),
        'pixel_values': ('bitplane_6', 10.18),
        'near_rational': ('fused_dqa_6', 12.25),
        'audio_samples': ('quant_6', 12.48),
    }

    print("=" * 120)
    print("v20 SUPERNATURAL CODEC v3 -- FULL BENCHMARK")
    print("=" * 120)

    results = {}

    header = (f"{'Dataset':<18} {'Raw':>6} {'zlib9':>6} "
              f"{'v19':>7} {'v20':>7} {'v20/v19':>8} {'Method':<24} {'MaxErr':>10} {'EncMs':>7} {'DecMs':>7}")
    print(f"\n{header}")
    print("-" * len(header))

    for ds_name, values in datasets.items():
        n = len(values)
        raw_size = n * 8
        raw_bytes = struct.pack(f'<{n}d', *values)

        zlib_size = len(zlib.compress(raw_bytes, 9))

        # v20 codec
        t0 = time.time()
        sn_enc, sn_method = v20_compress(values)
        enc_time = (time.time() - t0) * 1000

        sn_size = len(sn_enc)

        try:
            t0 = time.time()
            sn_dec = v20_decompress(sn_enc)
            dec_time = (time.time() - t0) * 1000
            max_err = max(abs(a-b) for a,b in zip(values, sn_dec))
        except Exception as e:
            max_err = float('inf')
            dec_time = 0
            sn_dec = None
            print(f"  DECODE ERROR for {ds_name}: {e}")

        sn_ratio = raw_size / sn_size

        v19_method, v19_ratio = v19_best.get(ds_name, ('?', 0.0))
        improvement = sn_ratio / v19_ratio if v19_ratio > 0 else 0.0

        results[ds_name] = {
            'raw': raw_size, 'zlib': zlib_size,
            'sn': sn_size, 'sn_ratio': sn_ratio, 'sn_method': sn_method,
            'max_err': max_err, 'enc_time': enc_time, 'dec_time': dec_time,
            'v19_ratio': v19_ratio, 'v19_method': v19_method,
            'improvement': improvement,
        }

        beat = "NEW!" if sn_ratio > v19_ratio else "    "
        print(f"{ds_name:<18} {raw_size:>6} {zlib_size:>6} "
              f"{v19_ratio:>6.2f}x {sn_ratio:>6.2f}x {improvement:>7.1%} {beat} "
              f"{sn_method:<24} {max_err:>10.2e} {enc_time:>6.1f}ms {dec_time:>6.1f}ms")

    return results


def detailed_breakdown():
    """Show ALL approaches per dataset."""
    datasets = generate_datasets(1000)

    print("\n" + "=" * 120)
    print("PER-APPROACH BREAKDOWN (bytes, ratio = raw/compressed)")
    print("=" * 120)

    all_results = {}

    for ds_name, values in datasets.items():
        n = len(values)
        raw_size = n * 8
        print(f"\n--- {ds_name} (raw={raw_size}) ---")

        approaches = {}

        def _try_show(name, encode_fn, decode_fn):
            try:
                t0 = time.time()
                enc = encode_fn()
                enc_ms = (time.time() - t0) * 1000
                t0 = time.time()
                dec = decode_fn(enc)
                dec_ms = (time.time() - t0) * 1000
                if len(dec) != n: return
                err = max(abs(a-b) for a,b in zip(values, dec))
                ratio = raw_size / len(enc)
                approaches[name] = (len(enc), ratio, err, enc_ms, dec_ms)
                print(f"  {name:<28} {len(enc):>6} ({ratio:>7.2f}x) err={err:.2e}  enc={enc_ms:.1f}ms dec={dec_ms:.1f}ms")
            except Exception as e:
                print(f"  {name:<28} FAILED: {e}")

        # V19 baselines
        for b in [4, 5, 6, 8]:
            _try_show(f'quant_{b}',
                      lambda b=b: _quantize_arith_encode(values, b),
                      lambda e: _quantize_arith_decode(e, 0, n))

        for b in [4, 5, 6, 8]:
            _try_show(f'dquant_{b}',
                      lambda b=b: _delta_quant_encode(values, b),
                      lambda e: _delta_quant_decode(e, 0, n))

        for b in [4, 5, 6, 8]:
            _try_show(f'fused_dqa_{b}',
                      lambda b=b: fused_dqa_encode(values, b),
                      lambda e: fused_dqa_decode(e, 0, n))

        for b in [4, 5, 6]:
            _try_show(f'bitplane_{b}',
                      lambda b=b: bitplane_encode(values, b),
                      lambda e: bitplane_decode(e, 0, n))

        # V20 NEW
        for b in [3, 4, 5]:
            _try_show(f'qext_{b}',
                      lambda b=b: quant_extreme_encode(values, b),
                      lambda e: quant_extreme_decode(e, 0, n))

        for b in [3, 4, 5]:
            _try_show(f'dqext_{b}',
                      lambda b=b: delta_quant_extreme_encode(values, b),
                      lambda e: delta_quant_extreme_decode(e, 0, n))

        for b in [4, 5, 6]:
            _try_show(f'wavelet_{b}',
                      lambda b=b: wavelet_quant_encode(values, b),
                      lambda e: wavelet_quant_decode(e, 0, n))

        for b in [4, 5, 6]:
            for o in [2, 4]:
                _try_show(f'pred_r{o}_{b}',
                          lambda b=b, o=o: pred_residual_encode(values, b, o),
                          lambda e: pred_residual_decode(e, 0, n))

        for b in [4, 5, 6]:
            _try_show(f'radapt_{b}',
                      lambda b=b: range_adaptive_encode(values, b),
                      lambda e: range_adaptive_decode(e, 0, n))

        for b in [3, 4, 5]:
            _try_show(f'd2tiny_{b}',
                      lambda b=b: delta2_tiny_encode(values, b),
                      lambda e: delta2_tiny_decode(e, 0, n))

        for b in [3, 4, 5]:
            _try_show(f'd2rans_{b}',
                      lambda b=b: delta2_rans_encode(values, b),
                      lambda e: delta2_rans_decode(e, 0, n))

        for b in [4, 5, 6]:
            _try_show(f'hybrid_{b}',
                      lambda b=b: hybrid_pipeline_encode(values, b),
                      lambda e: hybrid_pipeline_decode(e, 0, n))

        for b in [4, 5, 6]:
            _try_show(f'ctxadapt_{b}',
                      lambda b=b: context_adaptive_encode(values, b),
                      lambda e: context_adaptive_decode(e, 0, n))

        for b in [4, 5, 6]:
            _try_show(f'qrans_{b}',
                      lambda b=b: quant_rans_encode(values, b),
                      lambda e: quant_rans_decode(e, 0, n))

        for b in [4, 5, 6]:
            _try_show(f'dqrans_{b}',
                      lambda b=b: delta_quant_rans_encode(values, b),
                      lambda e: delta_quant_rans_decode(e, 0, n))

        for b in [3, 4, 5]:
            _try_show(f'predd2_{b}',
                      lambda b=b: pred_delta2_encode(values, b),
                      lambda e: pred_delta2_decode(e, 0, n))

        if approaches:
            best = min(approaches, key=lambda k: approaches[k][0])
            sz, ratio, err, enc_ms, dec_ms = approaches[best]
            print(f"  >>> BEST: {best} = {sz} bytes ({ratio:.2f}x) err={err:.2e}")

        all_results[ds_name] = approaches

    return all_results


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == '__main__':
    t0 = time.time()

    # Detailed per-approach breakdown
    approach_results = detailed_breakdown()

    print("\n")

    # Summary benchmark
    results = benchmark_all()

    total_time = time.time() - t0
    print(f"\nTotal benchmark time: {total_time:.1f}s")

    # Summary table for results file
    print("\n" + "=" * 80)
    print("SUMMARY: v20 vs v19")
    print("=" * 80)
    for ds_name, r in results.items():
        beat = "BEAT" if r['improvement'] > 1.0 else "MISS"
        print(f"  {ds_name:<18} v19={r['v19_ratio']:>6.2f}x  v20={r['sn_ratio']:>6.2f}x  "
              f"change={r['improvement']:>7.1%}  {beat}  method={r['sn_method']}")

    gc.collect()
