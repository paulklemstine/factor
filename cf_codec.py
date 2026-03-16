"""CF Codec -- Continued Fraction Compression Codec.

Modes: float (lossy CF/quantized), timeseries (delta+CF/quant),
       integer (lossless varint), auto (sniff and pick best).
Sub-modes for float: CF (varint), Quant, Log, CF+Arithmetic coding.
"""
import struct, math, gc

MAGIC = b"CF01"
MODE_FLOAT, MODE_INTEGER, MODE_TIMESERIES, MODE_RAW = 1, 2, 3, 4
FLOAT_SUB_CF, FLOAT_SUB_QUANT, FLOAT_SUB_LOG, FLOAT_SUB_CF_ARITH = 0, 1, 2, 3

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

# -- Arithmetic coding with Gauss-Kuzmin model -----------------------------

# Precompute Gauss-Kuzmin CDF for PQ values 1..MAX_GK_SYM, plus escape
_MAX_GK_SYM = 128
_GK_PROBS = []
_GK_CDF = [0]
for _k in range(1, _MAX_GK_SYM + 1):
    _GK_PROBS.append(-math.log2(1 - 1 / (_k + 1) ** 2) / math.log2(math.e) * math.log(2))
# Normalize: use actual GK probabilities (they sum to ~1 for large max)
_GK_PROBS = [-math.log2(1 - 1 / (_k + 1) ** 2) for _k in range(1, _MAX_GK_SYM + 1)]
_gk_total = sum(_GK_PROBS)
_gk_escape = max(0.001, 1.0 - _gk_total)
_GK_PROBS = [p / (_gk_total + _gk_escape) for p in _GK_PROBS]
_GK_PROBS.append(_gk_escape / (_gk_total + _gk_escape))  # escape symbol
_GK_CDF = [0.0]
for _p in _GK_PROBS:
    _GK_CDF.append(_GK_CDF[-1] + _p)
_GK_CDF[-1] = 1.0

# Use integer arithmetic for precision (32-bit range)
_AC_BITS = 32
_AC_TOP = (1 << _AC_BITS)
_AC_HALF = _AC_TOP >> 1
_AC_QTR = _AC_HALF >> 1

# Integer CDF (scaled to _AC_TOP)
_GK_ICDF = [int(c * _AC_TOP) for c in _GK_CDF]
_GK_ICDF[0] = 0
_GK_ICDF[-1] = _AC_TOP
# Ensure monotonic
for _i in range(1, len(_GK_ICDF)):
    if _GK_ICDF[_i] <= _GK_ICDF[_i - 1]:
        _GK_ICDF[_i] = _GK_ICDF[_i - 1] + 1


def _arith_encode_pqs(pq_list):
    """Arithmetic-encode a list of CF partial quotients using GK model.
    Returns bytes."""
    lo, hi = 0, _AC_TOP
    pending = 0
    bits_out = []

    def _emit(bit):
        nonlocal pending
        bits_out.append(bit)
        while pending > 0:
            bits_out.append(1 - bit)
            pending -= 1

    for pq in pq_list:
        # Map pq to symbol index
        if 1 <= pq <= _MAX_GK_SYM:
            sym = pq - 1
        else:
            sym = _MAX_GK_SYM  # escape

        rng = hi - lo
        hi = lo + (rng * _GK_ICDF[sym + 1]) // _AC_TOP
        lo = lo + (rng * _GK_ICDF[sym]) // _AC_TOP

        # Renormalize
        while True:
            if hi <= _AC_HALF:
                _emit(0)
                lo <<= 1
                hi <<= 1
            elif lo >= _AC_HALF:
                _emit(1)
                lo = (lo - _AC_HALF) << 1
                hi = (hi - _AC_HALF) << 1
            elif lo >= _AC_QTR and hi <= 3 * _AC_QTR:
                pending += 1
                lo = (lo - _AC_QTR) << 1
                hi = (hi - _AC_QTR) << 1
            else:
                break

    # Flush
    pending += 1
    _emit(0 if lo < _AC_QTR else 1)

    # Pack bits -> bytes
    buf = bytearray((len(bits_out) + 7) // 8)
    for i, b in enumerate(bits_out):
        if b:
            buf[i >> 3] |= (1 << (7 - (i & 7)))

    # Encode escapes (values > _MAX_GK_SYM) as varint appendix
    esc_buf = bytearray()
    for pq in pq_list:
        if pq < 1 or pq > _MAX_GK_SYM:
            esc_buf.extend(_enc_uv(max(0, pq)))

    # Header: bit_count(4) + esc_count(4) + arith_bytes + esc_bytes
    n_esc = sum(1 for pq in pq_list if pq < 1 or pq > _MAX_GK_SYM)
    result = struct.pack('<II', len(bits_out), n_esc)
    result += bytes(buf) + bytes(esc_buf)
    return result


def _arith_decode_pqs(data, pos, count):
    """Decode arithmetic-coded PQ list. Returns (pq_list, new_pos)."""
    n_bits, n_esc = struct.unpack_from('<II', data, pos)
    pos += 8
    n_arith_bytes = (n_bits + 7) // 8
    arith_data = data[pos:pos + n_arith_bytes]
    pos += n_arith_bytes

    # Read escapes
    escapes = []
    esc_pos = pos
    for _ in range(n_esc):
        v, esc_pos = _dec_uv(data, esc_pos)
        escapes.append(v)
    pos = esc_pos

    # Decode arithmetic stream
    def _get_bit(idx):
        if idx >= n_bits:
            return 0
        byte_idx = idx >> 3
        bit_idx = 7 - (idx & 7)
        if byte_idx >= len(arith_data):
            return 0
        return (arith_data[byte_idx] >> bit_idx) & 1

    lo, hi = 0, _AC_TOP
    val = 0
    bit_pos = 0
    for i in range(_AC_BITS):
        val = (val << 1) | _get_bit(bit_pos)
        bit_pos += 1

    pqs = []
    esc_idx = 0

    for _ in range(count):
        rng = hi - lo
        # Find symbol
        target = ((val - lo + 1) * _AC_TOP - 1) // rng
        sym = 0
        for s in range(len(_GK_ICDF) - 1):
            if _GK_ICDF[s + 1] > target:
                sym = s
                break

        # Update range
        hi = lo + (rng * _GK_ICDF[sym + 1]) // _AC_TOP
        lo = lo + (rng * _GK_ICDF[sym]) // _AC_TOP

        # Renormalize
        while True:
            if hi <= _AC_HALF:
                lo <<= 1
                hi <<= 1
                val = (val << 1) | _get_bit(bit_pos)
                bit_pos += 1
            elif lo >= _AC_HALF:
                lo = (lo - _AC_HALF) << 1
                hi = (hi - _AC_HALF) << 1
                val = ((val - _AC_HALF) << 1) | _get_bit(bit_pos)
                bit_pos += 1
            elif lo >= _AC_QTR and hi <= 3 * _AC_QTR:
                lo = (lo - _AC_QTR) << 1
                hi = (hi - _AC_QTR) << 1
                val = ((val - _AC_QTR) << 1) | _get_bit(bit_pos)
                bit_pos += 1
            else:
                break

        if sym == _MAX_GK_SYM:
            # Escape
            if esc_idx < len(escapes):
                pqs.append(escapes[esc_idx])
                esc_idx += 1
            else:
                pqs.append(1)
        else:
            pqs.append(sym + 1)

    return pqs, pos


def _generic_arith_encode(symbols, max_sym):
    """Arithmetic-encode a list of non-negative integer symbols with uniform-ish model.
    Uses adaptive frequency model for better compression."""
    # Build frequency table from data
    freq = [1] * (max_sym + 2)  # +1 for escape, +1 padding
    for s in symbols:
        if 0 <= s <= max_sym:
            freq[s] += 1
        else:
            freq[max_sym + 1] += 1

    total = sum(freq)
    # Build integer CDF
    icdf = [0]
    for f in freq:
        icdf.append(icdf[-1] + f)
    # Scale to _AC_TOP
    scale = _AC_TOP / icdf[-1]
    icdf_scaled = [int(c * scale) for c in icdf]
    icdf_scaled[0] = 0
    icdf_scaled[-1] = _AC_TOP
    for i in range(1, len(icdf_scaled)):
        if icdf_scaled[i] <= icdf_scaled[i-1]:
            icdf_scaled[i] = icdf_scaled[i-1] + 1

    lo, hi = 0, _AC_TOP
    pending = 0
    bits_out = []

    def _emit(bit):
        nonlocal pending
        bits_out.append(bit)
        while pending > 0:
            bits_out.append(1 - bit)
            pending -= 1

    escapes = []
    for s in symbols:
        if 0 <= s <= max_sym:
            sym = s
        else:
            sym = max_sym + 1
            escapes.append(s)

        rng = hi - lo
        hi = lo + (rng * icdf_scaled[sym + 1]) // _AC_TOP
        lo = lo + (rng * icdf_scaled[sym]) // _AC_TOP

        while True:
            if hi <= _AC_HALF:
                _emit(0); lo <<= 1; hi <<= 1
            elif lo >= _AC_HALF:
                _emit(1); lo = (lo - _AC_HALF) << 1; hi = (hi - _AC_HALF) << 1
            elif lo >= _AC_QTR and hi <= 3 * _AC_QTR:
                pending += 1; lo = (lo - _AC_QTR) << 1; hi = (hi - _AC_QTR) << 1
            else:
                break

    pending += 1
    _emit(0 if lo < _AC_QTR else 1)

    buf = bytearray((len(bits_out) + 7) // 8)
    for i, b in enumerate(bits_out):
        if b: buf[i >> 3] |= (1 << (7 - (i & 7)))

    esc_buf = bytearray()
    for e in escapes:
        esc_buf.extend(_enc_sv(e))

    # Header: freq table (compact), bit_count, esc_count, bits, escapes
    # Encode freq table as: max_sym+2 entries, each as uv
    freq_buf = bytearray()
    for f in freq:
        freq_buf.extend(_enc_uv(f))

    result = struct.pack('<HII', max_sym, len(bits_out), len(escapes))
    result += bytes(freq_buf) + bytes(buf) + bytes(esc_buf)
    return result


def _generic_arith_decode(data, pos, count):
    """Decode generic arithmetic-coded symbol list."""
    max_sym, n_bits, n_esc = struct.unpack_from('<HII', data, pos)
    pos += 10

    # Read freq table
    freq = []
    for _ in range(max_sym + 2):
        v, pos = _dec_uv(data, pos)
        freq.append(v)

    total = sum(freq)
    icdf = [0]
    for f in freq:
        icdf.append(icdf[-1] + f)
    scale = _AC_TOP / icdf[-1]
    icdf_scaled = [int(c * scale) for c in icdf]
    icdf_scaled[0] = 0
    icdf_scaled[-1] = _AC_TOP
    for i in range(1, len(icdf_scaled)):
        if icdf_scaled[i] <= icdf_scaled[i-1]:
            icdf_scaled[i] = icdf_scaled[i-1] + 1

    n_arith_bytes = (n_bits + 7) // 8
    arith_data = data[pos:pos + n_arith_bytes]
    pos += n_arith_bytes

    escapes = []
    for _ in range(n_esc):
        v, pos = _dec_sv(data, pos)
        escapes.append(v)

    def _get_bit(idx):
        if idx >= n_bits: return 0
        byte_idx = idx >> 3
        if byte_idx >= len(arith_data): return 0
        return (arith_data[byte_idx] >> (7 - (idx & 7))) & 1

    lo, hi = 0, _AC_TOP
    val = 0
    bit_pos = 0
    for _ in range(_AC_BITS):
        val = (val << 1) | _get_bit(bit_pos)
        bit_pos += 1

    symbols = []
    esc_idx = 0
    n_syms = len(icdf_scaled) - 1

    for _ in range(count):
        rng = hi - lo
        target = ((val - lo + 1) * _AC_TOP - 1) // rng
        sym = 0
        for s in range(n_syms):
            if icdf_scaled[s + 1] > target:
                sym = s
                break

        hi = lo + (rng * icdf_scaled[sym + 1]) // _AC_TOP
        lo = lo + (rng * icdf_scaled[sym]) // _AC_TOP

        while True:
            if hi <= _AC_HALF:
                lo <<= 1; hi <<= 1
                val = (val << 1) | _get_bit(bit_pos); bit_pos += 1
            elif lo >= _AC_HALF:
                lo = (lo - _AC_HALF) << 1; hi = (hi - _AC_HALF) << 1
                val = ((val - _AC_HALF) << 1) | _get_bit(bit_pos); bit_pos += 1
            elif lo >= _AC_QTR and hi <= 3 * _AC_QTR:
                lo = (lo - _AC_QTR) << 1; hi = (hi - _AC_QTR) << 1
                val = ((val - _AC_QTR) << 1) | _get_bit(bit_pos); bit_pos += 1
            else:
                break

        if sym == max_sym + 1:
            if esc_idx < len(escapes):
                symbols.append(escapes[esc_idx]); esc_idx += 1
            else:
                symbols.append(0)
        else:
            symbols.append(sym)

    return symbols, pos


def _enc_cf_arith(cf_list):
    """Encode CF list using arithmetic coding for ALL streams (a0, lengths, PQs).
    Much better than varint for structured data."""
    a0s = [cf[0] for cf in cf_list]
    lengths = [len(cf) - 1 for cf in cf_list]
    all_pqs = []
    for cf in cf_list:
        all_pqs.extend(cf[1:])

    # Handle sign of a0: encode as (sign_bit, abs_val)
    a0_signs = bytearray((len(a0s) + 7) // 8)
    a0_abs = []
    for i, a in enumerate(a0s):
        if a < 0:
            a0_signs[i >> 3] |= (1 << (i & 7))
        a0_abs.append(abs(a))

    # Arithmetic-code a0 absolute values (typically 0-50)
    max_a0 = max(a0_abs) if a0_abs else 0
    a0_payload = _generic_arith_encode(a0_abs, min(max_a0, 255))

    # Arithmetic-code lengths (typically 0-8)
    max_len = max(lengths) if lengths else 0
    len_payload = _generic_arith_encode(lengths, min(max_len, 31))

    # Arithmetic-code PQs with Gauss-Kuzmin model
    if all_pqs:
        pq_payload = _arith_encode_pqs(all_pqs)
    else:
        pq_payload = b''

    # Pack: sign_bytes_len(2) + a0_len(4) + len_len(4) + pq_len(4)
    #      + signs + a0_payload + len_payload + pq_payload
    header = struct.pack('<HIII', len(a0_signs), len(a0_payload), len(len_payload), len(pq_payload))
    return header + bytes(a0_signs) + a0_payload + len_payload + pq_payload


def _dec_cf_arith(data, pos, count):
    """Decode arithmetic-coded CF list."""
    signs_len, a0_len, len_len, pq_len = struct.unpack_from('<HIII', data, pos)
    pos += 14

    # Read signs
    signs = data[pos:pos + signs_len]
    pos += signs_len

    # Decode a0 absolute values
    a0_abs, pos2 = _generic_arith_decode(data, pos, count)
    pos += a0_len

    # Reconstruct a0 with signs
    a0s = []
    for i, a in enumerate(a0_abs):
        if (signs[i >> 3] >> (i & 7)) & 1:
            a0s.append(-a)
        else:
            a0s.append(a)

    # Decode lengths
    lengths, pos2 = _generic_arith_decode(data, pos, count)
    pos += len_len

    # Decode PQs
    total_pqs = sum(lengths)
    if total_pqs > 0:
        pqs, _ = _arith_decode_pqs(data, pos, total_pqs)
    else:
        pqs = []
    pos += pq_len

    # Reassemble CFs
    result = []
    pq_idx = 0
    for i in range(count):
        cf = [a0s[i]]
        for _ in range(lengths[i]):
            cf.append(pqs[pq_idx])
            pq_idx += 1
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
        """Compress float array. Picks best of CF, CF+arith, linear-quant, log-quant."""
        n = len(values)
        if n == 0: return _make_hdr(MODE_FLOAT, 0, lossy_depth, 0)
        cands = [(FLOAT_SUB_CF, self._cf_enc(values, lossy_depth))]
        # Try arithmetic-coded CF (much better for near-rational data)
        cands.append((FLOAT_SUB_CF_ARITH, self._cf_arith_enc(values, lossy_depth)))
        nz = [abs(v) for v in values if v != 0]
        dr = max(nz) / min(nz) if nz and min(nz) > 0 else 1
        if dr < 1e6:
            for bits in (8, 10, 12, 16, 20):
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
        elif sub == FLOAT_SUB_CF_ARITH:
            return [cf_to_float(c) for c in _dec_cf_arith(data, off, count)[0]]
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

    def _cf_arith_enc(self, values, depth):
        """CF encode with arithmetic-coded PQ stream (Gauss-Kuzmin model)."""
        cf_list = [float_to_cf(v, depth) for v in values]
        return _enc_cf_arith(cf_list)

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
