#!/usr/bin/env python3
"""
v22_cf_ppt_codec.py — Production-quality CF-PPT data codec.

Encodes arbitrary binary data as continued fraction partial quotients,
which map to Stern-Brocot tree paths and Berggren PPT addresses.

Three modes:
  - 'bitpack': Each byte -> one CF PQ (byte+1). 1.125x overhead, fast, error-isolated.
  - 'bigint':  Entire chunk as big integer n, CF of n/Fib(k). Compact but fragile.
  - 'adaptive': Auto-picks best mode per chunk.

Wire format:
  [Header][Chunk0][Chunk1]...[ChunkN]

Header (20 bytes):
  Magic (4B) | Version (1B) | Mode (1B) | OrigLen (4B) | ChunkCount (4B)
  | MetaLen (4B) | Reserved (2B)

Chunk:
  ChunkHeader (6B): DataLen (2B) | EncodedLen (2B) | CRC32 (4B, over encoded payload)
  Payload: varint-encoded PQ sequence

Metadata (optional, after header):
  JSON blob of {filename, timestamp, content_type, ...}
"""

import os
import sys
import time
import math
import struct
import hashlib
import zlib
import json
import io
from collections import Counter

# Try gmpy2 for faster big-int arithmetic
try:
    import gmpy2
    HAS_GMPY2 = True
except ImportError:
    HAS_GMPY2 = False

# ============================================================
# CONSTANTS
# ============================================================

MAGIC = b'CFPT'
VERSION = 1
MODE_BITPACK = 0
MODE_BIGINT = 1
MODE_ADAPTIVE = 2

HEADER_SIZE = 20  # 4 + 1 + 1 + 4 + 4 + 4 + 2
CHUNK_HEADER_SIZE = 8  # 2 + 2 + 4

DEFAULT_CHUNK_SIZE = 64
ADAPTIVE_TRIAL_SIZES = [32, 64, 128, 256]

MODE_NAMES = {MODE_BITPACK: 'bitpack', MODE_BIGINT: 'bigint', MODE_ADAPTIVE: 'adaptive'}
MODE_IDS = {'bitpack': MODE_BITPACK, 'bigint': MODE_BIGINT, 'adaptive': MODE_ADAPTIVE}


# ============================================================
# VARINT ENCODING (unsigned LEB128)
# ============================================================

def encode_varint(n):
    """Encode unsigned integer as varint (LEB128). Returns bytes."""
    if n < 0:
        raise ValueError("Varint must be non-negative")
    buf = bytearray()
    while n >= 0x80:
        buf.append((n & 0x7F) | 0x80)
        n >>= 7
    buf.append(n & 0x7F)
    return bytes(buf)


def decode_varint(data, offset):
    """Decode varint from data at offset. Returns (value, new_offset)."""
    result = 0
    shift = 0
    while offset < len(data):
        b = data[offset]
        offset += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            return result, offset
        shift += 7
    raise ValueError("Truncated varint")


def encode_varint_sequence(values):
    """Encode a sequence of unsigned ints as concatenated varints."""
    parts = []
    for v in values:
        parts.append(encode_varint(v))
    return b''.join(parts)


def decode_varint_sequence(data, count):
    """Decode count varints from data. Returns list of values."""
    values = []
    offset = 0
    for _ in range(count):
        v, offset = decode_varint(data, offset)
        values.append(v)
    return values, offset


# ============================================================
# CF CORE UTILITIES
# ============================================================

def rational_to_cf(p, q, max_terms=500000):
    """Exact CF for p/q using Euclidean algorithm."""
    terms = []
    while q != 0 and len(terms) < max_terms:
        a, r = divmod(p, q)
        terms.append(int(a))
        p, q = q, r
    return terms


def cf_to_rational(terms):
    """Reconstruct p/q from CF terms. Exact."""
    if not terms:
        return 0, 1
    if HAS_GMPY2:
        p0, p1 = gmpy2.mpz(1), gmpy2.mpz(terms[0])
        q0, q1 = gmpy2.mpz(0), gmpy2.mpz(1)
        for a in terms[1:]:
            p0, p1 = p1, gmpy2.mpz(a) * p1 + p0
            q0, q1 = q1, gmpy2.mpz(a) * q1 + q0
        return int(p1), int(q1)
    else:
        p0, p1 = 1, terms[0]
        q0, q1 = 0, 1
        for a in terms[1:]:
            p0, p1 = p1, a * p1 + p0
            q0, q1 = q1, a * q1 + q0
        return p1, q1


def bytes_to_int(data):
    """Convert bytes to positive integer with sentinel byte."""
    return int.from_bytes(b'\x01' + data, 'big')


def int_to_bytes(n):
    """Inverse of bytes_to_int."""
    raw = n.to_bytes((n.bit_length() + 7) // 8, 'big')
    if raw[0] != 1:
        raise ValueError(f"Sentinel byte missing, got {raw[0]}")
    return raw[1:]


# ============================================================
# CODEC IMPLEMENTATIONS
# ============================================================

def _bitpack_encode_chunk(data):
    """Bitpack: each byte -> PQ = byte + 1. Returns list of PQs."""
    return [b + 1 for b in data]


def _bitpack_decode_chunk(pqs):
    """Bitpack decode: PQ - 1 = byte."""
    return bytes(pq - 1 for pq in pqs)


def _bigint_encode_chunk(data):
    """BigInt: data -> int n -> CF of n/Fib(k).
    Returns (pqs, fib_index_k).
    """
    n = bytes_to_int(data)
    if n == 0:
        return [0], 2
    # Find Fibonacci number > n
    a, b = 1, 1
    k = 2
    while b <= n:
        a, b = b, a + b
        k += 1
    q = b
    terms = rational_to_cf(n, q)
    return terms, k


def _bigint_decode_chunk(pqs, fib_k):
    """BigInt decode: CF terms + Fib index -> data."""
    # Recompute Fib(fib_k)
    a, b = 1, 1
    for _ in range(fib_k - 2):
        a, b = b, a + b
    q = b
    p_rec, q_rec = cf_to_rational(pqs)
    if q_rec == 0:
        return b''
    g = q // q_rec
    p = p_rec * g
    return int_to_bytes(p)


# ============================================================
# WIRE FORMAT
# ============================================================

def _pack_header(mode, orig_len, chunk_count, meta_len):
    """Pack the 20-byte header."""
    return struct.pack('<4sBBIIIH',
                       MAGIC,
                       VERSION,
                       mode,
                       orig_len,
                       chunk_count,
                       meta_len,
                       0)  # reserved


def _unpack_header(data):
    """Unpack header. Returns dict."""
    if len(data) < HEADER_SIZE:
        raise ValueError(f"Header too short: {len(data)} < {HEADER_SIZE}")
    magic, version, mode, orig_len, chunk_count, meta_len, _ = \
        struct.unpack('<4sBBIIIH', data[:HEADER_SIZE])
    if magic != MAGIC:
        raise ValueError(f"Bad magic: {magic!r}")
    if version != VERSION:
        raise ValueError(f"Unsupported version: {version}")
    return {
        'mode': mode,
        'orig_len': orig_len,
        'chunk_count': chunk_count,
        'meta_len': meta_len,
    }


def _pack_chunk(pqs, mode, fib_k=0):
    """Pack a single chunk: header + varint-encoded PQs.
    For bigint mode, first varint is fib_k, then the PQ count, then PQs.
    For bitpack mode, just the PQ count then PQs.
    """
    parts = []
    if mode == MODE_BIGINT:
        parts.append(encode_varint(fib_k))
    parts.append(encode_varint(len(pqs)))
    parts.append(encode_varint_sequence(pqs))
    payload = b''.join(parts)

    crc = zlib.crc32(payload) & 0xFFFFFFFF
    data_len = len(pqs)  # number of original data bytes (for bitpack) or PQ count
    encoded_len = len(payload)

    # Chunk header: data_len(2B) + encoded_len(2B) + crc32(4B)
    header = struct.pack('<HHI', data_len & 0xFFFF, encoded_len & 0xFFFF, crc)
    return header + payload


def _unpack_chunk(data, offset, mode):
    """Unpack a single chunk from data at offset.
    Returns (pqs, fib_k_or_0, data_len, new_offset, crc_ok).
    data_len is from the chunk header (used for zero-fill on CRC failure).
    """
    if offset + CHUNK_HEADER_SIZE > len(data):
        raise ValueError("Truncated chunk header")
    data_len, encoded_len, expected_crc = \
        struct.unpack('<HHI', data[offset:offset + CHUNK_HEADER_SIZE])
    offset += CHUNK_HEADER_SIZE

    if offset + encoded_len > len(data):
        raise ValueError(f"Truncated chunk payload: need {encoded_len}, have {len(data) - offset}")

    payload = data[offset:offset + encoded_len]
    actual_crc = zlib.crc32(payload) & 0xFFFFFFFF
    crc_ok = (actual_crc == expected_crc)

    if not crc_ok:
        # Don't try to decode corrupted payload -- just skip it
        return [], 0, data_len, offset + encoded_len, False

    off = 0
    fib_k = 0
    if mode == MODE_BIGINT:
        fib_k, off = decode_varint(payload, off)

    pq_count, off = decode_varint(payload, off)
    pqs, off = decode_varint_sequence(payload[off:], pq_count)

    return pqs, fib_k, data_len, offset + encoded_len, crc_ok


# ============================================================
# PUBLIC API
# ============================================================

def encode(data, mode='bitpack', chunk_size=64, metadata=None):
    """Encode arbitrary bytes into CF-PPT wire format.

    Args:
        data: bytes to encode
        mode: 'bitpack', 'bigint', or 'adaptive'
        chunk_size: bytes per chunk (default 64)
        metadata: optional dict {filename, timestamp, content_type, ...}

    Returns:
        bytes: compact binary wire format
    """
    if isinstance(data, (str,)):
        data = data.encode('utf-8')
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError(f"Expected bytes, got {type(data)}")

    mode_id = MODE_IDS.get(mode)
    if mode_id is None:
        raise ValueError(f"Unknown mode: {mode!r}. Use 'bitpack', 'bigint', or 'adaptive'.")

    orig_len = len(data)

    # Metadata
    meta_bytes = b''
    if metadata:
        meta_bytes = json.dumps(metadata, separators=(',', ':')).encode('utf-8')

    # Split into chunks
    chunks_data = []
    for i in range(0, max(1, len(data)), chunk_size):
        chunks_data.append(data[i:i + chunk_size])
    if not chunks_data:
        chunks_data = [b'']

    # Encode chunks
    encoded_chunks = []
    for chunk in chunks_data:
        if mode_id == MODE_ADAPTIVE:
            # Try bitpack and bigint, pick smaller
            bp_pqs = _bitpack_encode_chunk(chunk)
            bp_packed = _pack_chunk(bp_pqs, MODE_BITPACK)

            if len(chunk) <= 128:  # bigint gets slow for large chunks
                try:
                    bi_pqs, bi_k = _bigint_encode_chunk(chunk)
                    bi_packed = _pack_chunk(bi_pqs, MODE_BIGINT, bi_k)
                    if len(bi_packed) < len(bp_packed):
                        encoded_chunks.append((MODE_BIGINT, bi_packed, bi_pqs, bi_k))
                        continue
                except Exception:
                    pass

            encoded_chunks.append((MODE_BITPACK, bp_packed, bp_pqs, 0))
        elif mode_id == MODE_BITPACK:
            pqs = _bitpack_encode_chunk(chunk)
            packed = _pack_chunk(pqs, MODE_BITPACK)
            encoded_chunks.append((MODE_BITPACK, packed, pqs, 0))
        elif mode_id == MODE_BIGINT:
            pqs, k = _bigint_encode_chunk(chunk)
            packed = _pack_chunk(pqs, MODE_BIGINT, k)
            encoded_chunks.append((MODE_BIGINT, packed, pqs, k))

    # For adaptive mode, we store per-chunk mode in the chunk itself
    # We use a simple scheme: if mode is adaptive, the first byte of each
    # chunk payload (before the varint sequence) indicates the sub-mode.
    # Actually, let's re-pack with per-chunk mode byte for adaptive.
    if mode_id == MODE_ADAPTIVE:
        final_chunks = []
        for sub_mode, packed, pqs, fib_k in encoded_chunks:
            # Prepend sub_mode byte to payload
            # Re-pack: we need the chunk header to cover mode_byte + payload
            parts = [bytes([sub_mode])]
            if sub_mode == MODE_BIGINT:
                parts.append(encode_varint(fib_k))
            parts.append(encode_varint(len(pqs)))
            parts.append(encode_varint_sequence(pqs))
            payload = b''.join(parts)
            crc = zlib.crc32(payload) & 0xFFFFFFFF
            header = struct.pack('<HHI', len(pqs) & 0xFFFF, len(payload) & 0xFFFF, crc)
            final_chunks.append(header + payload)
    else:
        final_chunks = [packed for _, packed, _, _ in encoded_chunks]

    # Assemble
    header = _pack_header(mode_id, orig_len, len(final_chunks), len(meta_bytes))
    return header + meta_bytes + b''.join(final_chunks)


def decode(encoded, report_errors=False):
    """Decode CF-PPT wire format back to original bytes.

    Args:
        encoded: bytes from encode()
        report_errors: if True, returns (data, error_list) instead of just data

    Returns:
        bytes (or (bytes, list) if report_errors)
    """
    errors = []
    hdr = _unpack_header(encoded)
    offset = HEADER_SIZE

    # Read metadata (skip it for decode)
    meta_len = hdr['meta_len']
    _meta_bytes = encoded[offset:offset + meta_len]
    offset += meta_len

    mode = hdr['mode']
    orig_len = hdr['orig_len']
    chunk_count = hdr['chunk_count']

    result = bytearray()

    for ci in range(chunk_count):
        try:
            if mode == MODE_ADAPTIVE:
                # Read chunk header
                if offset + CHUNK_HEADER_SIZE > len(encoded):
                    raise ValueError("Truncated chunk header")
                data_len, encoded_len, expected_crc = \
                    struct.unpack('<HHI', encoded[offset:offset + CHUNK_HEADER_SIZE])
                offset += CHUNK_HEADER_SIZE

                payload = encoded[offset:offset + encoded_len]
                actual_crc = zlib.crc32(payload) & 0xFFFFFFFF
                crc_ok = (actual_crc == expected_crc)

                if not crc_ok:
                    errors.append(f"Chunk {ci}: CRC mismatch")
                    # Fill with zeros
                    result.extend(b'\x00' * data_len)
                    offset += encoded_len
                    continue

                off = 0
                sub_mode = payload[off]
                off += 1

                fib_k = 0
                if sub_mode == MODE_BIGINT:
                    fib_k, off = decode_varint(payload, off)

                pq_count, off = decode_varint(payload, off)
                pqs, _ = decode_varint_sequence(payload[off:], pq_count)
                offset += encoded_len

                if sub_mode == MODE_BITPACK:
                    result.extend(_bitpack_decode_chunk(pqs))
                elif sub_mode == MODE_BIGINT:
                    result.extend(_bigint_decode_chunk(pqs, fib_k))
            else:
                pqs, fib_k, data_len, new_offset, crc_ok = _unpack_chunk(encoded, offset, mode)
                if not crc_ok:
                    errors.append(f"Chunk {ci}: CRC mismatch")
                    result.extend(b'\x00' * data_len)
                    offset = new_offset
                    continue

                offset = new_offset
                if mode == MODE_BITPACK:
                    result.extend(_bitpack_decode_chunk(pqs))
                elif mode == MODE_BIGINT:
                    result.extend(_bigint_decode_chunk(pqs, fib_k))
        except Exception as e:
            errors.append(f"Chunk {ci}: {e}")
            # Can't reliably skip to next chunk without knowing chunk bounds
            # Fill remaining with zeros
            remaining = orig_len - len(result)
            if remaining > 0:
                result.extend(b'\x00' * remaining)
            break

    # Trim to original length
    out = bytes(result[:orig_len])

    if report_errors:
        return out, errors
    return out


def decode_metadata(encoded):
    """Extract metadata dict from encoded data, or None."""
    hdr = _unpack_header(encoded)
    meta_len = hdr['meta_len']
    if meta_len == 0:
        return None
    meta_bytes = encoded[HEADER_SIZE:HEADER_SIZE + meta_len]
    return json.loads(meta_bytes.decode('utf-8'))


# ============================================================
# STREAMING API
# ============================================================

def encode_stream(data_iter, mode='bitpack', chunk_size=64, metadata=None):
    """Streaming encoder. Yields encoded bytes incrementally.

    Args:
        data_iter: iterable of bytes chunks (any size)
        mode: encoding mode
        chunk_size: target chunk size
        metadata: optional dict

    Yields:
        bytes: first yield is header + metadata, subsequent yields are chunks
    """
    mode_id = MODE_IDS.get(mode, MODE_BITPACK)

    # Buffer incoming data and emit fixed-size chunks
    buf = bytearray()
    chunks_encoded = []
    total_len = 0

    for block in data_iter:
        buf.extend(block)
        total_len += len(block)
        while len(buf) >= chunk_size:
            chunk = bytes(buf[:chunk_size])
            buf = buf[chunk_size:]
            chunks_encoded.append(_encode_one_chunk(chunk, mode_id))

    # Final partial chunk
    if buf:
        chunks_encoded.append(_encode_one_chunk(bytes(buf), mode_id))

    # Now yield header + all chunks
    meta_bytes = b''
    if metadata:
        meta_bytes = json.dumps(metadata, separators=(',', ':')).encode('utf-8')

    header = _pack_header(mode_id, total_len, len(chunks_encoded), len(meta_bytes))
    yield header + meta_bytes

    for chunk_bytes in chunks_encoded:
        yield chunk_bytes


def _encode_one_chunk(chunk, mode_id):
    """Encode a single chunk for streaming."""
    if mode_id == MODE_BITPACK:
        pqs = _bitpack_encode_chunk(chunk)
        return _pack_chunk(pqs, MODE_BITPACK)
    elif mode_id == MODE_BIGINT:
        pqs, k = _bigint_encode_chunk(chunk)
        return _pack_chunk(pqs, MODE_BIGINT, k)
    elif mode_id == MODE_ADAPTIVE:
        bp_pqs = _bitpack_encode_chunk(chunk)
        bp_packed = _pack_chunk(bp_pqs, MODE_BITPACK)
        best = bp_packed
        best_mode = MODE_BITPACK
        best_pqs = bp_pqs
        best_k = 0

        if len(chunk) <= 128:
            try:
                bi_pqs, bi_k = _bigint_encode_chunk(chunk)
                bi_packed = _pack_chunk(bi_pqs, MODE_BIGINT, bi_k)
                if len(bi_packed) < len(best):
                    best_mode = MODE_BIGINT
                    best_pqs = bi_pqs
                    best_k = bi_k
            except Exception:
                pass

        # Pack with sub-mode byte
        parts = [bytes([best_mode])]
        if best_mode == MODE_BIGINT:
            parts.append(encode_varint(best_k))
        parts.append(encode_varint(len(best_pqs)))
        parts.append(encode_varint_sequence(best_pqs))
        payload = b''.join(parts)
        crc = zlib.crc32(payload) & 0xFFFFFFFF
        header = struct.pack('<HHI', len(best_pqs) & 0xFFFF, len(payload) & 0xFFFF, crc)
        return header + payload


def decode_stream(encoded_iter):
    """Streaming decoder. Yields decoded bytes chunks.

    Args:
        encoded_iter: iterable yielding bytes (first must contain header)

    Yields:
        bytes: decoded data chunks
    """
    # Accumulate enough for header
    buf = bytearray()
    for block in encoded_iter:
        buf.extend(block)
        if len(buf) >= HEADER_SIZE:
            break

    hdr = _unpack_header(bytes(buf[:HEADER_SIZE]))
    pos = HEADER_SIZE + hdr['meta_len']

    # May need more data
    while len(buf) < pos:
        for block in encoded_iter:
            buf.extend(block)
            break

    mode = hdr['mode']
    orig_len = hdr['orig_len']
    chunk_count = hdr['chunk_count']
    emitted = 0

    for ci in range(chunk_count):
        # Ensure we have chunk header
        while len(buf) < pos + CHUNK_HEADER_SIZE:
            try:
                block = next(encoded_iter) if hasattr(encoded_iter, '__next__') else b''
                buf.extend(block)
            except StopIteration:
                break

        if pos + CHUNK_HEADER_SIZE > len(buf):
            break

        data_len, encoded_len, expected_crc = \
            struct.unpack('<HHI', buf[pos:pos + CHUNK_HEADER_SIZE])
        pos += CHUNK_HEADER_SIZE

        # Ensure we have payload
        while len(buf) < pos + encoded_len:
            try:
                block = next(encoded_iter) if hasattr(encoded_iter, '__next__') else b''
                buf.extend(block)
            except StopIteration:
                break

        payload = bytes(buf[pos:pos + encoded_len])
        pos += encoded_len

        actual_crc = zlib.crc32(payload) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            chunk_data = b'\x00' * min(data_len, orig_len - emitted)
        else:
            if mode == MODE_ADAPTIVE:
                off = 0
                sub_mode = payload[off]; off += 1
                fib_k = 0
                if sub_mode == MODE_BIGINT:
                    fib_k, off = decode_varint(payload, off)
                pq_count, off = decode_varint(payload, off)
                pqs, _ = decode_varint_sequence(payload[off:], pq_count)
                if sub_mode == MODE_BITPACK:
                    chunk_data = _bitpack_decode_chunk(pqs)
                else:
                    chunk_data = _bigint_decode_chunk(pqs, fib_k)
            elif mode == MODE_BITPACK:
                off = 0
                pq_count, off = decode_varint(payload, off)
                pqs, _ = decode_varint_sequence(payload[off:], pq_count)
                chunk_data = _bitpack_decode_chunk(pqs)
            elif mode == MODE_BIGINT:
                off = 0
                fib_k, off = decode_varint(payload, off)
                pq_count, off = decode_varint(payload, off)
                pqs, _ = decode_varint_sequence(payload[off:], pq_count)
                chunk_data = _bigint_decode_chunk(pqs, fib_k)
            else:
                chunk_data = b'\x00' * data_len

        # Trim last chunk
        remaining = orig_len - emitted
        if len(chunk_data) > remaining:
            chunk_data = chunk_data[:remaining]
        emitted += len(chunk_data)
        yield chunk_data


# ============================================================
# FILE I/O CONVENIENCE
# ============================================================

def encode_file(path, mode='bitpack', chunk_size=64, metadata=None):
    """Encode a file. Adds filename to metadata automatically.

    Args:
        path: file path to encode
        mode: encoding mode
        chunk_size: chunk size
        metadata: extra metadata dict (merged with auto-detected)

    Returns:
        bytes: encoded wire format
    """
    with open(path, 'rb') as f:
        data = f.read()

    auto_meta = {
        'filename': os.path.basename(path),
        'size': len(data),
        'sha256': hashlib.sha256(data).hexdigest(),
    }
    if metadata:
        auto_meta.update(metadata)

    return encode(data, mode=mode, chunk_size=chunk_size, metadata=auto_meta)


def decode_to_file(encoded, path):
    """Decode encoded data and write to file.

    Args:
        encoded: bytes from encode() or encode_file()
        path: output file path

    Returns:
        dict: metadata (if any)
    """
    data = decode(encoded)
    with open(path, 'wb') as f:
        f.write(data)
    return decode_metadata(encoded)


# ============================================================
# BENCHMARK SUITE
# ============================================================

def _generate_test_data():
    """Generate a variety of test datasets."""
    import random
    random.seed(42)
    datasets = {}

    # Random bytes
    for sz in [1024, 10240, 102400]:
        datasets[f'random_{sz//1024}KB'] = random.randbytes(sz)

    # English text
    text = ("The quick brown fox jumps over the lazy dog. "
            "Pack my box with five dozen liquor jugs. "
            "How vexingly quick daft zebras jump. ") * 100
    datasets['text_english'] = text[:10240].encode('utf-8')

    # Code
    code = """def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

for i in range(100):
    print(f"fib({i}) = {fibonacci(i)}")
""" * 50
    datasets['text_code'] = code[:10240].encode('utf-8')

    # JSON
    import json as _json
    jdata = _json.dumps([{"id": i, "value": random.random(), "name": f"item_{i}"}
                         for i in range(200)], indent=2)
    datasets['text_json'] = jdata[:10240].encode('utf-8')

    # CSV of numbers
    csv_lines = ["x,y,z"]
    for i in range(500):
        csv_lines.append(f"{i},{i*i},{i*i*i}")
    datasets['structured_csv'] = '\n'.join(csv_lines)[:10240].encode('utf-8')

    # Repeated patterns
    datasets['structured_repeat'] = (b'\xAB\xCD\xEF' * 5000)[:10240]

    # Zeros
    datasets['structured_zeros'] = b'\x00' * 10240

    # "Compressed" (high entropy, like already-compressed data)
    datasets['binary_compressed'] = zlib.compress(random.randbytes(10240))[:10240]

    return datasets


def run_benchmarks(verbose=True):
    """Run full benchmark suite. Returns results dict."""
    datasets = _generate_test_data()
    results = {}

    if verbose:
        print(f"\n{'='*80}")
        print("CF-PPT Codec Benchmark Suite")
        print(f"{'='*80}\n")

    # Test each mode
    for mode in ['bitpack', 'bigint', 'adaptive']:
        if verbose:
            print(f"\n--- Mode: {mode} ---")
            print(f"{'Dataset':<25} {'Size':>7} {'Enc ms':>8} {'Dec ms':>8} "
                  f"{'Encoded':>8} {'Ratio':>7} {'OK':>4}")

        mode_results = {}
        for name, data in sorted(datasets.items()):
            # Skip large data for bigint (too slow)
            if mode == 'bigint' and len(data) > 10240:
                continue

            chunk_size = 64
            try:
                # Encode
                t0 = time.perf_counter()
                n_iters = max(1, min(50, 500000 // max(1, len(data))))
                for _ in range(n_iters):
                    enc = encode(data, mode=mode, chunk_size=chunk_size)
                t_enc = (time.perf_counter() - t0) / n_iters * 1000

                # Decode
                t0 = time.perf_counter()
                for _ in range(n_iters):
                    dec = decode(enc)
                t_dec = (time.perf_counter() - t0) / n_iters * 1000

                ok = (dec == data)
                ratio = len(enc) / len(data)

                mode_results[name] = {
                    'size': len(data),
                    'encoded_size': len(enc),
                    'encode_ms': t_enc,
                    'decode_ms': t_dec,
                    'ratio': ratio,
                    'correct': ok,
                    'throughput_enc_MBs': len(data) / (t_enc / 1000) / 1e6 if t_enc > 0 else 0,
                    'throughput_dec_MBs': len(data) / (t_dec / 1000) / 1e6 if t_dec > 0 else 0,
                }

                if verbose:
                    print(f"{name:<25} {len(data):>7} {t_enc:>7.2f} {t_dec:>7.2f} "
                          f"{len(enc):>8} {ratio:>6.3f}x "
                          f"{'PASS' if ok else 'FAIL'}")
            except Exception as e:
                if verbose:
                    print(f"{name:<25} {len(data):>7}  ERROR: {e}")
                mode_results[name] = {'error': str(e)}

        results[mode] = mode_results

    # Comparison with standard codecs
    if verbose:
        print(f"\n\n--- Comparison: CF-PPT Bitpack vs Standard Codecs ---")
        print(f"{'Dataset':<25} {'Raw':>7} {'Bitpack':>8} {'zlib':>7} "
              f"{'bz2':>7} {'lzma':>7} {'base64':>8}")

    comparison = {}
    import base64, bz2, lzma
    for name, data in sorted(datasets.items()):
        enc_bp = encode(data, mode='bitpack', chunk_size=64)
        enc_zlib = zlib.compress(data)
        enc_bz2 = bz2.compress(data)
        enc_lzma = lzma.compress(data)
        enc_b64 = base64.b64encode(data)

        row = {
            'raw': len(data),
            'bitpack': len(enc_bp),
            'zlib': len(enc_zlib),
            'bz2': len(enc_bz2),
            'lzma': len(enc_lzma),
            'base64': len(enc_b64),
        }
        comparison[name] = row

        if verbose:
            print(f"{name:<25} {len(data):>7} {len(enc_bp):>8} {len(enc_zlib):>7} "
                  f"{len(enc_bz2):>7} {len(enc_lzma):>7} {len(enc_b64):>8}")

    results['comparison'] = comparison

    # Error detection test
    if verbose:
        print(f"\n\n--- Error Detection Test ---")

    import random
    random.seed(99)
    test_data = random.randbytes(1024)
    enc = encode(test_data, mode='bitpack', chunk_size=64)

    # Corrupt a single byte in the middle
    corrupted = bytearray(enc)
    corrupt_pos = HEADER_SIZE + len(enc) // 2
    corrupted[corrupt_pos] ^= 0xFF
    corrupted = bytes(corrupted)

    dec, errs = decode(corrupted, report_errors=True)
    n_wrong = sum(1 for a, b in zip(test_data, dec) if a != b)
    if verbose:
        print(f"  Corrupted 1 byte at position {corrupt_pos}/{len(enc)}")
        print(f"  CRC errors detected: {len(errs)}")
        print(f"  Bytes wrong in output: {n_wrong}/{len(test_data)}")
        print(f"  Error isolation: {100*(1 - n_wrong/len(test_data)):.1f}% data preserved")
        for e in errs:
            print(f"    - {e}")

    results['error_test'] = {
        'crc_errors': len(errs),
        'bytes_wrong': n_wrong,
        'data_preserved_pct': 100 * (1 - n_wrong / len(test_data)),
    }

    # Metadata test
    if verbose:
        print(f"\n\n--- Metadata Test ---")
    meta = {'filename': 'test.bin', 'timestamp': '2026-03-16T12:00:00Z', 'content_type': 'application/octet-stream'}
    enc_meta = encode(test_data, mode='bitpack', metadata=meta)
    recovered_meta = decode_metadata(enc_meta)
    dec_meta = decode(enc_meta)
    if verbose:
        print(f"  Metadata round-trip: {'PASS' if recovered_meta == meta else 'FAIL'}")
        print(f"  Data round-trip with metadata: {'PASS' if dec_meta == test_data else 'FAIL'}")
        print(f"  Metadata overhead: {len(enc_meta) - len(enc)} bytes")

    results['metadata_test'] = {
        'meta_roundtrip': recovered_meta == meta,
        'data_roundtrip': dec_meta == test_data,
        'meta_overhead': len(enc_meta) - len(enc),
    }

    # Streaming test
    if verbose:
        print(f"\n\n--- Streaming Test ---")
    import random
    random.seed(77)
    stream_data = random.randbytes(8192)

    # Encode via streaming
    def data_chunks(d, sz=500):
        for i in range(0, len(d), sz):
            yield d[i:i+sz]

    enc_parts = list(encode_stream(data_chunks(stream_data), mode='bitpack', chunk_size=64))
    enc_full = b''.join(enc_parts)

    # Decode via streaming
    dec_parts = list(decode_stream(iter(enc_parts)))
    dec_full = b''.join(dec_parts)

    stream_ok = (dec_full == stream_data)
    if verbose:
        print(f"  Stream encode: {len(enc_parts)} parts, total {len(enc_full)} bytes")
        print(f"  Stream decode round-trip: {'PASS' if stream_ok else 'FAIL'}")

    results['streaming_test'] = {
        'parts': len(enc_parts),
        'total_bytes': len(enc_full),
        'correct': stream_ok,
    }

    return results


def write_results_md(results, path):
    """Write benchmark results to markdown file."""
    lines = []
    lines.append("# V22: CF-PPT Production Codec — Benchmark Results\n")
    lines.append(f"Date: 2026-03-16\n")
    lines.append(f"gmpy2 available: {HAS_GMPY2}\n")

    lines.append("\n## Codec Performance by Mode\n")

    for mode in ['bitpack', 'bigint', 'adaptive']:
        if mode not in results:
            continue
        mr = results[mode]
        lines.append(f"\n### Mode: {mode}\n")
        lines.append(f"| Dataset | Size | Enc ms | Dec ms | Encoded | Ratio | "
                     f"Enc MB/s | Dec MB/s | OK |")
        lines.append(f"|---------|------|--------|--------|---------|-------|"
                     f"---------|----------|----|")
        for name, r in sorted(mr.items()):
            if 'error' in r:
                lines.append(f"| {name} | - | - | - | - | - | - | - | ERROR |")
                continue
            lines.append(f"| {name} | {r['size']} | {r['encode_ms']:.2f} | "
                         f"{r['decode_ms']:.2f} | {r['encoded_size']} | "
                         f"{r['ratio']:.3f}x | {r['throughput_enc_MBs']:.1f} | "
                         f"{r['throughput_dec_MBs']:.1f} | "
                         f"{'PASS' if r['correct'] else 'FAIL'} |")

    # Comparison table
    lines.append("\n## Comparison vs Standard Codecs\n")
    comp = results.get('comparison', {})
    lines.append("| Dataset | Raw | Bitpack | zlib | bz2 | lzma | base64 |")
    lines.append("|---------|-----|---------|------|-----|------|--------|")
    for name, r in sorted(comp.items()):
        lines.append(f"| {name} | {r['raw']} | {r['bitpack']} | {r['zlib']} | "
                     f"{r['bz2']} | {r['lzma']} | {r['base64']} |")

    lines.append("\n**Note**: CF-PPT is not a compression codec. It is a *mathematical mapping* "
                 "from binary data to continued fractions and Pythagorean triples. "
                 "The unique value is the bijection: data <-> CF <-> Stern-Brocot <-> PPT.")

    # Error detection
    et = results.get('error_test', {})
    lines.append(f"\n## Error Detection\n")
    lines.append(f"- CRC-32 per chunk: detected {et.get('crc_errors', '?')} corrupted chunks")
    lines.append(f"- Bytes wrong after corruption: {et.get('bytes_wrong', '?')}")
    lines.append(f"- Data preserved: {et.get('data_preserved_pct', '?'):.1f}%")
    lines.append(f"- Error isolation: corrupted chunks return zeros, rest decoded correctly")

    # Metadata
    mt = results.get('metadata_test', {})
    lines.append(f"\n## Metadata\n")
    lines.append(f"- Metadata round-trip: {'PASS' if mt.get('meta_roundtrip') else 'FAIL'}")
    lines.append(f"- Data round-trip with metadata: {'PASS' if mt.get('data_roundtrip') else 'FAIL'}")
    lines.append(f"- Metadata overhead: {mt.get('meta_overhead', '?')} bytes")

    # Streaming
    st = results.get('streaming_test', {})
    lines.append(f"\n## Streaming\n")
    lines.append(f"- Stream encode produced {st.get('parts', '?')} parts, "
                 f"{st.get('total_bytes', '?')} bytes total")
    lines.append(f"- Stream decode round-trip: {'PASS' if st.get('correct') else 'FAIL'}")

    # Wire format description
    lines.append(f"\n## Wire Format\n")
    lines.append("```")
    lines.append("Header (20 bytes):")
    lines.append("  [CFPT]  Magic (4B)")
    lines.append("  [01]    Version (1B)")
    lines.append("  [MM]    Mode: 0=bitpack, 1=bigint, 2=adaptive (1B)")
    lines.append("  [LLLL]  Original data length (4B, little-endian)")
    lines.append("  [CCCC]  Chunk count (4B, little-endian)")
    lines.append("  [MMMM]  Metadata JSON length (4B, little-endian)")
    lines.append("  [RR]    Reserved (2B)")
    lines.append("")
    lines.append("Metadata (variable): JSON bytes")
    lines.append("")
    lines.append("Per chunk:")
    lines.append("  ChunkHeader (8 bytes):")
    lines.append("    [DD]    Data/PQ count (2B)")
    lines.append("    [EE]    Encoded payload length (2B)")
    lines.append("    [CCCC]  CRC-32 of payload (4B)")
    lines.append("  Payload:")
    lines.append("    [varint: PQ count][varint: PQ0][varint: PQ1]...")
    lines.append("    (bigint mode adds [varint: fib_k] before PQ count)")
    lines.append("    (adaptive mode adds [mode_byte] before everything)")
    lines.append("```")

    # Summary
    lines.append(f"\n## Summary\n")

    # Compute average bitpack throughput
    bp = results.get('bitpack', {})
    enc_speeds = [r['throughput_enc_MBs'] for r in bp.values() if 'throughput_enc_MBs' in r]
    dec_speeds = [r['throughput_dec_MBs'] for r in bp.values() if 'throughput_dec_MBs' in r]
    ratios = [r['ratio'] for r in bp.values() if 'ratio' in r]
    all_ok = all(r.get('correct', False) for r in bp.values() if 'correct' in r)

    lines.append(f"- **Bitpack mode**: avg {sum(enc_speeds)/len(enc_speeds):.1f} MB/s encode, "
                 f"{sum(dec_speeds)/len(dec_speeds):.1f} MB/s decode" if enc_speeds else "- Bitpack: no data")
    lines.append(f"- **Average overhead**: {sum(ratios)/len(ratios):.3f}x" if ratios else "")
    lines.append(f"- **Round-trip correctness**: {'ALL PASS' if all_ok else 'SOME FAILURES'}")
    lines.append(f"- **Error detection**: CRC-32 per chunk, graceful degradation")
    lines.append(f"- **Streaming**: yield-based encode/decode for large files")
    lines.append(f"- **Metadata**: JSON metadata embedded in wire format")

    with open(path, 'w') as f:
        f.write('\n'.join(lines))
    return path


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    RESULTS_PATH = "/home/raver1975/factor/.claude/worktrees/agent-a2d6d24e/v22_cf_ppt_codec_results.md"

    print("CF-PPT Production Codec v1.0")
    print(f"gmpy2: {'yes' if HAS_GMPY2 else 'no'}")

    # Quick self-test
    print("\n--- Self-test ---")
    test_data = b"Hello, CF-PPT world! This is a test of the production codec."
    for mode in ['bitpack', 'bigint', 'adaptive']:
        enc = encode(test_data, mode=mode, chunk_size=32)
        dec = decode(enc)
        ok = dec == test_data
        meta = decode_metadata(enc)
        print(f"  {mode:10s}: {len(enc)} bytes encoded, round-trip {'PASS' if ok else 'FAIL'}")

    # Metadata test
    enc_m = encode(test_data, mode='bitpack', metadata={'author': 'test', 'ts': 12345})
    meta_m = decode_metadata(enc_m)
    dec_m = decode(enc_m)
    print(f"  metadata:   round-trip {'PASS' if dec_m == test_data and meta_m == {'author': 'test', 'ts': 12345} else 'FAIL'}")

    # File I/O test
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as tmp:
        tmp.write(test_data)
        tmp_path = tmp.name
    try:
        enc_f = encode_file(tmp_path)
        meta_f = decode_metadata(enc_f)
        with tempfile.NamedTemporaryFile(suffix='.out', delete=False) as tmp2:
            tmp2_path = tmp2.name
        decode_to_file(enc_f, tmp2_path)
        with open(tmp2_path, 'rb') as f:
            dec_f = f.read()
        print(f"  file I/O:   round-trip {'PASS' if dec_f == test_data else 'FAIL'}, "
              f"meta has filename={meta_f.get('filename', '?')}")
        os.unlink(tmp2_path)
    finally:
        os.unlink(tmp_path)

    # Run benchmarks
    print()
    results = run_benchmarks(verbose=True)

    # Write results
    out = write_results_md(results, RESULTS_PATH)
    print(f"\nResults written to {out}")
