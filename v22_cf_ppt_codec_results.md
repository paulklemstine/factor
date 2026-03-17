# V22: CF-PPT Production Codec — Benchmark Results

Date: 2026-03-16

gmpy2 available: True


## Codec Performance by Mode


### Mode: bitpack

| Dataset | Size | Enc ms | Dec ms | Encoded | Ratio | Enc MB/s | Dec MB/s | OK |
|---------|------|--------|--------|---------|-------|---------|----------|----|
| binary_compressed | 10240 | 1.97 | 1.77 | 16936 | 1.654x | 5.2 | 5.8 | PASS |
| random_100KB | 102400 | 21.15 | 18.32 | 168218 | 1.643x | 4.8 | 5.6 | PASS |
| random_10KB | 10240 | 1.90 | 1.78 | 16861 | 1.647x | 5.4 | 5.8 | PASS |
| random_1KB | 1024 | 0.19 | 0.19 | 1722 | 1.682x | 5.4 | 5.4 | PASS |
| structured_csv | 9064 | 1.39 | 1.21 | 10362 | 1.143x | 6.5 | 7.5 | PASS |
| structured_repeat | 10240 | 2.01 | 2.05 | 21940 | 2.143x | 5.1 | 5.0 | PASS |
| structured_zeros | 10240 | 1.52 | 1.36 | 11700 | 1.143x | 6.8 | 7.6 | PASS |
| text_code | 9750 | 1.47 | 1.33 | 11147 | 1.143x | 6.7 | 7.3 | PASS |
| text_english | 10240 | 1.54 | 1.40 | 11700 | 1.143x | 6.6 | 7.3 | PASS |
| text_json | 10240 | 1.55 | 1.35 | 11700 | 1.143x | 6.6 | 7.6 | PASS |

### Mode: bigint

| Dataset | Size | Enc ms | Dec ms | Encoded | Ratio | Enc MB/s | Dec MB/s | OK |
|---------|------|--------|--------|---------|-------|---------|----------|----|
| binary_compressed | 10240 | 17.60 | 16.78 | 50302 | 4.912x | 0.6 | 0.6 | PASS |
| random_10KB | 10240 | 17.75 | 16.97 | 50534 | 4.935x | 0.6 | 0.6 | PASS |
| random_1KB | 1024 | 1.80 | 1.75 | 5077 | 4.958x | 0.6 | 0.6 | PASS |
| structured_csv | 9064 | 15.83 | 14.77 | 44603 | 4.921x | 0.6 | 0.6 | PASS |
| structured_repeat | 10240 | 17.96 | 16.79 | 50475 | 4.929x | 0.6 | 0.6 | PASS |
| structured_zeros | 10240 | 17.90 | 16.41 | 49300 | 4.814x | 0.6 | 0.6 | PASS |
| text_code | 9750 | 17.01 | 16.11 | 47637 | 4.886x | 0.6 | 0.6 | PASS |
| text_english | 10240 | 18.06 | 17.66 | 50384 | 4.920x | 0.6 | 0.6 | PASS |
| text_json | 10240 | 18.27 | 16.72 | 50671 | 4.948x | 0.6 | 0.6 | PASS |

### Mode: adaptive

| Dataset | Size | Enc ms | Dec ms | Encoded | Ratio | Enc MB/s | Dec MB/s | OK |
|---------|------|--------|--------|---------|-------|---------|----------|----|
| binary_compressed | 10240 | 21.76 | 1.81 | 17096 | 1.670x | 0.5 | 5.7 | PASS |
| random_100KB | 102400 | 223.65 | 18.22 | 169818 | 1.658x | 0.5 | 5.6 | PASS |
| random_10KB | 10240 | 22.84 | 1.84 | 17021 | 1.662x | 0.4 | 5.6 | PASS |
| random_1KB | 1024 | 2.22 | 0.18 | 1738 | 1.697x | 0.5 | 5.8 | PASS |
| structured_csv | 9064 | 18.08 | 1.22 | 10504 | 1.159x | 0.5 | 7.4 | PASS |
| structured_repeat | 10240 | 22.26 | 2.02 | 22100 | 2.158x | 0.5 | 5.1 | PASS |
| structured_zeros | 10240 | 20.56 | 1.40 | 11860 | 1.158x | 0.5 | 7.3 | PASS |
| text_code | 9750 | 19.90 | 1.38 | 11300 | 1.159x | 0.5 | 7.0 | PASS |
| text_english | 10240 | 21.21 | 1.41 | 11860 | 1.158x | 0.5 | 7.3 | PASS |
| text_json | 10240 | 20.52 | 1.39 | 11860 | 1.158x | 0.5 | 7.4 | PASS |

## Comparison vs Standard Codecs

| Dataset | Raw | Bitpack | zlib | bz2 | lzma | base64 |
|---------|-----|---------|------|-----|------|--------|
| binary_compressed | 10240 | 16936 | 10251 | 10723 | 10300 | 13656 |
| random_100KB | 102400 | 168218 | 102441 | 103220 | 102464 | 136536 |
| random_10KB | 10240 | 16861 | 10251 | 10728 | 10300 | 13656 |
| random_1KB | 1024 | 1722 | 1035 | 1294 | 1084 | 1368 |
| structured_csv | 9064 | 10362 | 4646 | 3999 | 3168 | 12088 |
| structured_repeat | 10240 | 21940 | 38 | 50 | 112 | 13656 |
| structured_zeros | 10240 | 11700 | 33 | 46 | 108 | 13656 |
| text_code | 9750 | 11147 | 184 | 288 | 232 | 13000 |
| text_english | 10240 | 11700 | 157 | 270 | 212 | 13656 |
| text_json | 10240 | 11700 | 2133 | 1635 | 1620 | 13656 |

**Note**: CF-PPT is not a compression codec. It is a *mathematical mapping* from binary data to continued fractions and Pythagorean triples. The unique value is the bijection: data <-> CF <-> Stern-Brocot <-> PPT.

## Error Detection

- CRC-32 per chunk: detected 1 corrupted chunks
- Bytes wrong after corruption: 64
- Data preserved: 93.8%
- Error isolation: corrupted chunks return zeros, rest decoded correctly

## Metadata

- Metadata round-trip: PASS
- Data round-trip with metadata: PASS
- Metadata overhead: 100 bytes

## Streaming

- Stream encode produced 129 parts, 13435 bytes total
- Stream decode round-trip: PASS

## Wire Format

```
Header (20 bytes):
  [CFPT]  Magic (4B)
  [01]    Version (1B)
  [MM]    Mode: 0=bitpack, 1=bigint, 2=adaptive (1B)
  [LLLL]  Original data length (4B, little-endian)
  [CCCC]  Chunk count (4B, little-endian)
  [MMMM]  Metadata JSON length (4B, little-endian)
  [RR]    Reserved (2B)

Metadata (variable): JSON bytes

Per chunk:
  ChunkHeader (8 bytes):
    [DD]    Data/PQ count (2B)
    [EE]    Encoded payload length (2B)
    [CCCC]  CRC-32 of payload (4B)
  Payload:
    [varint: PQ count][varint: PQ0][varint: PQ1]...
    (bigint mode adds [varint: fib_k] before PQ count)
    (adaptive mode adds [mode_byte] before everything)
```

## Summary

- **Bitpack mode**: avg 5.9 MB/s encode, 6.5 MB/s decode
- **Average overhead**: 1.448x
- **Round-trip correctness**: ALL PASS
- **Error detection**: CRC-32 per chunk, graceful degradation
- **Streaming**: yield-based encode/decode for large files
- **Metadata**: JSON metadata embedded in wire format