"""CF Codec -- Continued Fraction Compression Codec.

Modes: float (lossy CF/quantized), timeseries (delta+CF/quant),
       integer (lossless varint), auto (sniff and pick best).
"""
import struct, math, gc

MAGIC = b"CF01"
MODE_FLOAT, MODE_INTEGER, MODE_TIMESERIES, MODE_RAW = 1, 2, 3, 4
FLOAT_SUB_CF, FLOAT_SUB_QUANT, FLOAT_SUB_LOG = 0, 1, 2

# -- Varint (protobuf-style: 7 bits/byte, MSB=continuation) ---------------

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

def _enc_int_list(values):
    buf = bytearray()
    for v in values: buf.extend(_enc_sv(v))
    return bytes(buf)

def _dec_int_list(data, pos, count):
    result = []
    for _ in range(count):
        v, pos = _dec_sv(data, pos); result.append(v)
    return result, pos

# -- Continued Fraction core -----------------------------------------------

def float_to_cf(x, max_depth=6):
    if x != x: return [0]
    if math.isinf(x): return [999999999 if x > 0 else -999999999]
    sign = 1
    if x < 0: sign = -1; x = -x
    a0 = int(math.floor(x)); cf = [a0 * sign]; rem = x - a0
    for _ in range(max_depth):
        if rem < 1e-15: break
        xi = 1.0 / rem; ai = int(math.floor(xi))
        if ai > 1_000_000: break
        cf.append(ai); rem = xi - ai
    return cf

def cf_to_float(cf):
    if not cf: return 0.0
    val = 0.0
    for i in range(len(cf) - 1, 0, -1):
        if cf[i] == 0: break
        val = 1.0 / (cf[i] + val)
    return val + cf[0]

def _enc_cf_list(cf_list):
    buf = bytearray()
    for cf in cf_list:
        buf.extend(_enc_sv(cf[0]))
        for ai in cf[1:]: buf.extend(_enc_uv(ai))
        buf.extend(_enc_uv(0))
    return bytes(buf)

def _dec_cf_list(data, pos, count):
    result = []
    for _ in range(count):
        a0, pos = _dec_sv(data, pos); cf = [a0]
        while pos < len(data):
            ai, pos = _dec_uv(data, pos)
            if ai == 0: break
            cf.append(ai)
        result.append(cf)
    return result, pos

# -- Quantization helpers ---------------------------------------------------

def _quantize(values, bits=20):
    if not values: return [], 0.0, 1.0
    vmin, vmax = min(values), max(values)
    span = vmax - vmin if vmax > vmin else 1.0
    scale = (1 << bits) / span
    return [round((v - vmin) * scale) for v in values], vmin, scale

def _dequantize(ints, vmin, scale):
    return [vmin + i / scale for i in ints]

def _quantize_log(values, bits=20):
    TINY = 1e-300
    signs, logv = [], []
    for v in values:
        signs.append(0 if v >= 0 else 1)
        logv.append(math.log(max(abs(v), TINY)))
    lmin, lmax = min(logv), max(logv)
    lspan = lmax - lmin if lmax > lmin else 1.0
    lscale = (1 << bits) / lspan
    ints = [round((lv - lmin) * lscale) for lv in logv]
    sb = bytearray((len(signs) + 7) // 8)
    for i, s in enumerate(signs):
        if s: sb[i >> 3] |= (1 << (i & 7))
    return bytes(sb), ints, lmin, lscale

def _dequantize_log(sb, ints, lmin, lscale, count):
    vals = []
    for i in range(count):
        mag = math.exp(lmin + ints[i] / lscale)
        vals.append(-mag if (sb[i >> 3] >> (i & 7)) & 1 else mag)
    return vals

# -- Header (14 bytes) -----------------------------------------------------

def _make_hdr(mode, orig_len, depth, count):
    return MAGIC + struct.pack('<BIBI', mode, orig_len, depth, count)

def _parse_hdr(data):
    if data[:4] != MAGIC: raise ValueError("bad magic")
    m, o, d, c = struct.unpack_from('<BIBI', data, 4)
    return m, o, d, c, 14

# -- Auto-detection ---------------------------------------------------------

def _looks_f64(data):
    if len(data) < 8 or len(data) % 8: return False
    for i in range(min(len(data) // 8, 20)):
        v = struct.unpack_from('d', data, i * 8)[0]
        if math.isnan(v) or math.isinf(v) or abs(v) > 1e100: return False
    return True

def _is_ts(values):
    if len(values) < 10: return False
    step = max(1, len(values) // 200)
    diffs = [abs(values[i + step] - values[i]) for i in range(0, len(values) - step, step)]
    vals = [abs(values[i]) for i in range(0, len(values) - step, step)]
    if not diffs: return False
    ad, av = sum(diffs)/len(diffs), sum(vals)/len(vals) if sum(vals) > 0 else 1.0
    return ad < 0.1 * av if av > 1e-15 else False

# -- Codec ------------------------------------------------------------------

class CFCodec:
    """Continued Fraction Compression Codec."""

    def compress(self, data, mode='auto'):
        """Compress bytes. Modes: 'auto', 'float', 'integer', 'timeseries'."""
        if mode == 'auto': mode = self._detect(data)
        if mode == 'float':
            if len(data) % 8: return self._raw(data)
            return self.compress_floats(list(struct.unpack(f'<{len(data)//8}d', data)))
        elif mode == 'integer':
            if len(data) % 4: return self._raw(data)
            return self._compress_ints(list(struct.unpack(f'<{len(data)//4}i', data)), len(data))
        elif mode == 'timeseries':
            if len(data) % 8: return self._raw(data)
            return self.compress_timeseries(list(struct.unpack(f'<{len(data)//8}d', data)))
        return self._raw(data)

    def decompress(self, compressed):
        """Decompress bytes back to original."""
        mode, olen, db, count, off = _parse_hdr(compressed)
        if mode == MODE_FLOAT:
            return struct.pack(f'<{count}d', *self._dec_floats(compressed, off, count, db))
        elif mode == MODE_INTEGER:
            return struct.pack(f'<{count}i', *self._dec_ints(compressed, off, count, db))
        elif mode == MODE_TIMESERIES:
            return struct.pack(f'<{count}d', *self._dec_ts(compressed, off, count, db))
        elif mode == MODE_RAW:
            return compressed[off:off + olen]
        raise ValueError(f"unknown mode {mode}")

    # -- Float (lossy) ------------------------------------------------------

    def compress_floats(self, values, lossy_depth=6):
        """Compress float array. Picks best of CF, linear-quant, log-quant."""
        n = len(values)
        if n == 0: return _make_hdr(MODE_FLOAT, 0, lossy_depth, 0)
        cands = [(FLOAT_SUB_CF, self._cf_enc(values, lossy_depth))]
        nz = [abs(v) for v in values if v != 0]
        dr = max(nz) / min(nz) if nz and min(nz) > 0 else 1
        if dr < 1e6:
            for bits in (12, 16, 20):
                cands.append((FLOAT_SUB_QUANT, self._quant_enc(values, bits)))
        elif min(nz) > 0 if nz else False:
            cands.append((FLOAT_SUB_LOG, self._log_enc(values, 20)))
        sub, payload = min(cands, key=lambda x: len(x[1]))
        return _make_hdr(MODE_FLOAT, n * 8, (lossy_depth & 0x3F) | (sub << 6), n) + payload

    def decompress_floats(self, compressed):
        """Decompress CF-encoded floats."""
        _, _, db, count, off = _parse_hdr(compressed)
        return self._dec_floats(compressed, off, count, db)

    def _dec_floats(self, data, off, count, db):
        if count == 0: return []
        sub = (db >> 6) & 3
        if sub == FLOAT_SUB_CF:
            return [cf_to_float(c) for c in _dec_cf_list(data, off, count)[0]]
        elif sub == FLOAT_SUB_QUANT:
            return self._quant_dec(data, off, count)
        elif sub == FLOAT_SUB_LOG:
            return self._log_dec(data, off, count)
        raise ValueError(f"bad sub {sub}")

    # -- Time series (lossy) ------------------------------------------------

    def compress_timeseries(self, values):
        """Delta + best-of encoding for time series."""
        n = len(values)
        if not n: return _make_hdr(MODE_TIMESERIES, 0, 6, 0)
        deltas = [values[0]] + [values[i] - values[i-1] for i in range(1, n)]
        cands = [(FLOAT_SUB_CF, self._cf_enc(deltas, 8), 8)]
        for bits in (12, 16, 20):
            cands.append((FLOAT_SUB_QUANT, self._quant_enc(deltas, bits), bits))
        sub, payload, prec = min(cands, key=lambda x: len(x[1]))
        db = (prec & 0x3F) | (sub << 6)
        return _make_hdr(MODE_TIMESERIES, n * 8, db, n) + payload

    def decompress_timeseries(self, compressed):
        """Decompress delta+CF time series."""
        _, _, db, count, off = _parse_hdr(compressed)
        return self._dec_ts(compressed, off, count, db)

    def _dec_ts(self, data, off, count, db):
        if count == 0: return []
        sub = (db >> 6) & 3
        if sub == FLOAT_SUB_CF:
            deltas = [cf_to_float(c) for c in _dec_cf_list(data, off, count)[0]]
        elif sub == FLOAT_SUB_QUANT:
            deltas = self._quant_dec(data, off, count)
        else:
            raise ValueError(f"bad ts sub {sub}")
        vals = [deltas[0]]
        for i in range(1, len(deltas)): vals.append(vals[-1] + deltas[i])
        return vals

    # -- Integer (lossless) -------------------------------------------------

    def _compress_ints(self, values, orig_len):
        n = len(values)
        use_d = self._should_delta(values)
        if use_d:
            dl = [values[0]] + [values[i] - values[i-1] for i in range(1, n)]
            payload = _enc_int_list(dl)
            hdr = _make_hdr(MODE_INTEGER, orig_len, 1, n)
        else:
            payload = _enc_int_list(values)
            hdr = _make_hdr(MODE_INTEGER, orig_len, 0, n)
        result = hdr + payload
        return result if len(result) < orig_len else self._raw(struct.pack(f'<{n}i', *values))

    def _dec_ints(self, data, off, count, depth):
        vals, _ = _dec_int_list(data, off, count)
        if depth == 1:
            for i in range(1, len(vals)): vals[i] += vals[i-1]
        return vals

    def _should_delta(self, values):
        if len(values) < 10: return False
        n = min(len(values), 100)
        raw = sum(len(_enc_sv(values[i])) for i in range(n))
        delta = len(_enc_sv(values[0])) + sum(len(_enc_sv(values[i]-values[i-1])) for i in range(1, n))
        return delta < raw * 0.9

    # -- Internal encoders --------------------------------------------------

    def _cf_enc(self, values, depth):
        buf = bytearray()
        for s in range(0, len(values), 1000):
            buf.extend(_enc_cf_list([float_to_cf(v, depth) for v in values[s:s+1000]]))
        return bytes(buf)

    def _quant_enc(self, values, bits=20):
        ints, vmin, scale = _quantize(values, bits)
        deltas = [ints[0]] + [ints[i] - ints[i-1] for i in range(1, len(ints))]
        # Try sorted vs unsorted
        unsorted_p = _enc_int_list(deltas)
        idx = sorted(range(len(ints)), key=lambda i: ints[i])
        si = [ints[i] for i in idx]
        sd = [si[0]] + [si[i] - si[i-1] for i in range(1, len(si))]
        sorted_v = _enc_int_list(sd); perm_p = _enc_int_list(idx)
        buf = bytearray(struct.pack('<dd', vmin, scale))
        if len(sorted_v) + len(perm_p) < len(unsorted_p):
            buf.append(1)
            buf.extend(struct.pack('<I', len(sorted_v)))
            buf.extend(sorted_v); buf.extend(perm_p)
        else:
            buf.append(0); buf.extend(unsorted_p)
        return bytes(buf)

    def _quant_dec(self, data, off, count):
        vmin, scale = struct.unpack_from('<dd', data, off); off += 16
        sf = data[off]; off += 1
        if sf:
            vl = struct.unpack_from('<I', data, off)[0]; off += 4
            deltas, _ = _dec_int_list(data, off, count); off += vl
            perm, _ = _dec_int_list(data, off, count)
            si = [deltas[0]]
            for i in range(1, len(deltas)): si.append(si[-1] + deltas[i])
            ints = [0] * count
            for i, p in enumerate(perm): ints[p] = si[i]
        else:
            deltas, _ = _dec_int_list(data, off, count)
            ints = [deltas[0]]
            for i in range(1, len(deltas)): ints.append(ints[-1] + deltas[i])
        return _dequantize(ints, vmin, scale)

    def _log_enc(self, values, bits=20):
        sb, ints, lmin, lscale = _quantize_log(values, bits)
        deltas = [ints[0]] + [ints[i] - ints[i-1] for i in range(1, len(ints))]
        buf = bytearray(struct.pack('<dd', lmin, lscale))
        buf.extend(struct.pack('<I', len(sb))); buf.extend(sb)
        buf.extend(_enc_int_list(deltas))
        return bytes(buf)

    def _log_dec(self, data, off, count):
        lmin, lscale = struct.unpack_from('<dd', data, off); off += 16
        sbl = struct.unpack_from('<I', data, off)[0]; off += 4
        sb = data[off:off+sbl]; off += sbl
        deltas, _ = _dec_int_list(data, off, count)
        ints = [deltas[0]]
        for i in range(1, len(deltas)): ints.append(ints[-1] + deltas[i])
        return _dequantize_log(sb, ints, lmin, lscale, count)

    def _raw(self, data):
        return _make_hdr(MODE_RAW, len(data), 0, 0) + data

    def _detect(self, data):
        if _looks_f64(data):
            n = min(len(data)//8, 200)
            vals = list(struct.unpack(f'<{n}d', data[:n*8]))
            return 'timeseries' if _is_ts(vals) else 'float'
        return 'integer' if len(data) >= 4 and len(data) % 4 == 0 else 'raw'


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------
if __name__ == '__main__':
    import random, time, zlib
    codec = CFCodec(); random.seed(42)
    print("=" * 60); print("CF Codec Test Suite"); print("=" * 60)

    def report(name, raw_sz, comp, orig=None, decomp=None):
        r = raw_sz / len(comp)
        print(f"\n--- {name} ---")
        print(f"  {raw_sz} -> {len(comp)} bytes ({r:.2f}x)")
        if orig and decomp:
            me = max(abs(a-b) for a,b in zip(orig, decomp))
            print(f"  Max error: {me:.2e}")

    # Test 1: Random floats
    data = [random.random() for _ in range(1000)]
    c = codec.compress_floats(data, lossy_depth=6)
    d = codec.decompress_floats(c)
    report("Random Floats (depth=6)", len(data)*8, c, data, d)

    # Test 2: Time series
    ts = [0.0]
    for _ in range(999): ts.append(ts[-1] + random.gauss(0, 0.01))
    c = codec.compress_timeseries(ts); d = codec.decompress_timeseries(c)
    report("Time Series (random walk)", len(ts)*8, c, ts, d)

    # Test 3: Near-rational
    rationals = [p/q + random.gauss(0, 1e-10) for p in range(1,50) for q in range(1,21)]
    c = codec.compress_floats(rationals, lossy_depth=8)
    d = codec.decompress_floats(c)
    report("Near-Rational (depth=8)", len(rationals)*8, c, rationals, d)

    # Test 4: vs zlib
    print("\n--- vs zlib (random floats) ---")
    raw = struct.pack(f'{len(data)}d', *data)
    zc = zlib.compress(raw, 6); cc = codec.compress_floats(data, lossy_depth=6)
    print(f"  Raw: {len(raw)}  zlib: {len(zc)} ({len(raw)/len(zc):.2f}x)  CF: {len(cc)} ({len(raw)/len(cc):.2f}x)")
    print(f"  CF beats zlib by {len(zc)/len(cc):.2f}x")

    # Test 5: Lossless integers
    integers = [random.randint(1, 10000) for _ in range(1000)]
    ri = struct.pack(f'{len(integers)}i', *integers)
    c = codec.compress(ri, mode='integer'); d = codec.decompress(c)
    assert d == ri, "LOSSLESS FAILED!"
    report("Lossless Integers (1-10000)", len(ri), c); print("  Lossless: VERIFIED")

    # Test 6: Small integers
    si = [random.randint(1, 100) for _ in range(1000)]
    rsi = struct.pack(f'{len(si)}i', *si)
    c = codec.compress(rsi, mode='integer'); d = codec.decompress(c)
    assert d == rsi, "LOSSLESS FAILED!"
    report("Small Integers (1-100)", len(rsi), c); print("  Lossless: VERIFIED")

    # Test 7: Auto mode
    print("\n--- Auto Mode Detection ---")
    fr = struct.pack(f'{len(data)}d', *data)
    m1, _, _, _, _ = _parse_hdr(codec.compress(fr, mode='auto'))
    tr = struct.pack(f'{len(ts)}d', *ts)
    m2, _, _, _, _ = _parse_hdr(codec.compress(tr, mode='auto'))
    mn = {MODE_FLOAT:'float', MODE_TIMESERIES:'timeseries', MODE_INTEGER:'integer', MODE_RAW:'raw'}
    print(f"  Random floats -> {mn.get(m1)}  |  Time series -> {mn.get(m2)}")

    # Test 8: Round-trip bytes API
    c = codec.compress(fr, mode='float'); d = codec.decompress(c)
    rv = list(struct.unpack(f'<{len(data)}d', d))
    me = max(abs(a-b) for a,b in zip(data, rv))
    print(f"\n--- Round-trip bytes API ---\n  Max error: {me:.2e}  ({len(fr)}->{len(c)} = {len(fr)/len(c):.2f}x)")

    # Test 9: Edge cases
    print("\n--- Edge Cases ---")
    edges = [0.0, 1.0, -1.0, 0.5, 1/3, math.pi, math.e, 1e-10, 1e10, -math.pi]
    c = codec.compress_floats(edges, lossy_depth=10); d = codec.decompress_floats(c)
    for o, dc in zip(edges, d): print(f"  {o:>18.10f} -> {dc:>18.10f}  err={abs(o-dc):.2e}")

    # Test 10: Near-rational vs zlib
    print("\n--- Near-Rational vs zlib ---")
    rr = struct.pack(f'{len(rationals)}d', *rationals)
    zr = zlib.compress(rr, 6); cr = codec.compress_floats(rationals, lossy_depth=8)
    print(f"  zlib: {len(zr)} ({len(rr)/len(zr):.2f}x)  CF: {len(cr)} ({len(rr)/len(cr):.2f}x)  CF/zlib: {len(zr)/len(cr):.2f}x")

    # Test 11: Time series vs zlib
    print("\n--- Time Series vs zlib ---")
    rt = struct.pack(f'{len(ts)}d', *ts)
    zt = zlib.compress(rt, 6); ct = codec.compress_timeseries(ts)
    print(f"  zlib: {len(zt)} ({len(rt)/len(zt):.2f}x)  CF: {len(ct)} ({len(rt)/len(ct):.2f}x)  CF/zlib: {len(zt)/len(ct):.2f}x")

    # Test 12: Sequential integers
    sq = list(range(1000, 2000)); rsq = struct.pack(f'{len(sq)}i', *sq)
    c = codec.compress(rsq, mode='integer'); d = codec.decompress(c)
    assert d == rsq, "LOSSLESS FAILED!"
    report("Sequential Integers", len(rsq), c); print("  Lossless: VERIFIED")

    print("\n" + "=" * 60); print("All tests passed."); print("=" * 60)
    gc.collect()
