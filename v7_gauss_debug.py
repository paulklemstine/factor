#!/usr/bin/env python3
"""
Track 4: Diagnose and fix bitpacked_gauss spurious null vectors
================================================================
Session 7

The bitpacked_gauss in block_lanczos.py may produce spurious null vectors
that don't actually XOR to zero. This script:
1. Generates test matrices of various sizes
2. Compares mpz-based Gauss vs bitpacked Gauss
3. Identifies the bug
4. Proposes a fix
"""

import numpy as np
import time
import sys
sys.path.insert(0, '/home/raver1975/factor')

from block_lanczos import bitpacked_gauss, _verify, _rand_sparse


def mpz_gauss(sparse_rows, ncols):
    """
    Reference GF(2) Gaussian elimination using Python sets.
    Simple, correct, slow. Used to validate bitpacked version.
    """
    nrows = len(sparse_rows)
    # Work on copies
    mat = [set(row) for row in sparse_rows]
    # Combination tracking: which original rows contribute to each current row
    combo = [set([i]) for i in range(nrows)]

    used = [False] * nrows
    pivot_row = {}

    for col in range(ncols):
        # Find pivot: first unused row with this column
        piv = -1
        for r in range(nrows):
            if not used[r] and col in mat[r]:
                piv = r
                break
        if piv == -1:
            continue

        used[piv] = True
        pivot_row[col] = piv

        # Eliminate from all other rows
        for r in range(nrows):
            if r != piv and col in mat[r]:
                mat[r].symmetric_difference_update(mat[piv])
                combo[r].symmetric_difference_update(combo[piv])

    # Extract null vectors
    null_vecs = []
    for r in range(nrows):
        if len(mat[r]) == 0:  # zero row
            if combo[r]:
                null_vecs.append(sorted(combo[r]))

    return null_vecs


def compare_gauss(nrows, ncols, avg_w, seed=42):
    """Compare reference vs bitpacked Gauss on same matrix."""
    rows = _rand_sparse(nrows, ncols, avg_w, seed)

    # Reference
    t0 = time.time()
    ref_vecs = mpz_gauss(rows, ncols)
    ref_time = time.time() - t0
    ref_good = _verify(rows, ref_vecs)

    # Bitpacked
    t0 = time.time()
    bp_vecs = bitpacked_gauss(rows, ncols)
    bp_time = time.time() - t0
    bp_good = _verify(rows, bp_vecs)

    print(f"  {nrows}x{ncols} w={avg_w} seed={seed}:")
    print(f"    Reference: {len(ref_vecs)} vecs, {ref_good} valid, {ref_time:.3f}s")
    print(f"    Bitpacked: {len(bp_vecs)} vecs, {bp_good} valid, {bp_time:.3f}s")

    if bp_good < len(bp_vecs):
        spurious = len(bp_vecs) - bp_good
        print(f"    *** BUG: {spurious} spurious null vectors! ***")
        # Find a spurious vector for debugging
        for vec in bp_vecs:
            combined = set()
            for idx in vec:
                if idx < len(rows):
                    combined.symmetric_difference_update(rows[idx])
            if combined:
                print(f"    Spurious vec (len={len(vec)}): residual cols = {sorted(combined)[:20]}")
                return rows, bp_vecs, ref_vecs, "SPURIOUS"

    if len(bp_vecs) != len(ref_vecs):
        print(f"    Note: different count ({len(bp_vecs)} vs {len(ref_vecs)}) but all valid")

    return rows, bp_vecs, ref_vecs, "OK" if bp_good == len(bp_vecs) else "BUG"


def diagnose_pivot_selection():
    """
    Test if the bug is in pivot selection.
    The bitpacked version picks 'first unused' from np.where(has_bit),
    which returns rows in order. But if a row was already used as a pivot
    for a different column, it shouldn't be picked again.

    The current code checks `if not used[r]` which should be correct.
    Let's check if there's an issue with the 'all_set != piv' filter
    in the elimination step.
    """
    print("\n" + "=" * 60)
    print("DIAGNOSIS: Checking pivot selection edge cases")
    print("=" * 60)

    # Create a matrix where we KNOW the null space
    # Row 0: {0, 1}
    # Row 1: {0, 2}
    # Row 2: {1, 2}
    # Row 3: {0, 1, 2}
    # Null space: rows {0,1,2} XOR to {0,1}+{0,2}+{1,2} = {} (each col appears 2x)
    # Also: rows {0,1,2,3} XOR to {0,1}+{0,2}+{1,2}+{0,1,2} = {0,1,2} (not zero!)
    # Wait: {0,1}^{0,2}^{1,2} = {}: 0 appears 2x, 1 appears 2x, 2 appears 2x -> all cancel
    # {0,1}^{0,2}^{1,2}^{0,1,2} = {}^{0,1,2} = {0,1,2} -> not zero
    # So only {0,1,2} is a null vector.
    rows_known = [{0, 1}, {0, 2}, {1, 2}, {0, 1, 2}]
    print("\nKnown matrix: [{0,1}, {0,2}, {1,2}, {0,1,2}]")
    print("Expected null space: {0,1,2} -> XOR = {}")

    ref = mpz_gauss(rows_known, 3)
    bp = bitpacked_gauss(rows_known, 3)
    ref_good = _verify(rows_known, ref)
    bp_good = _verify(rows_known, bp)

    print(f"Reference: {ref} (valid={ref_good})")
    print(f"Bitpacked: {bp} (valid={bp_good})")


def diagnose_row_identity():
    """
    Check if combo tracking (identity matrix init) is correct.

    In the bitpacked version, rows that were zero from the START
    (no columns set) would appear as null vectors with just their own index.
    This is correct — a zero row IS a null vector (trivially).

    But the real question: after elimination, does a zero-result row
    correctly track which ORIGINAL rows were XORed into it?
    """
    print("\n" + "=" * 60)
    print("DIAGNOSIS: Row identity / combo tracking")
    print("=" * 60)

    # Matrix where row 3 = row 0 XOR row 1
    rows = [{0, 1, 3}, {1, 2, 3}, {0, 2}, {0, 2}]
    # row0 XOR row1 = {0,2}
    # row0 XOR row1 XOR row2 = {} -> null vec {0,1,2}
    # row2 XOR row3 = {} -> null vec {2,3}
    print("Matrix: [{0,1,3}, {1,2,3}, {0,2}, {0,2}]")
    print("Expected null vecs: {0,1,2} and {2,3}")

    ref = mpz_gauss(rows, 4)
    bp = bitpacked_gauss(rows, 4)
    ref_good = _verify(rows, ref)
    bp_good = _verify(rows, bp)

    print(f"Reference: {ref} (valid={ref_good})")
    print(f"Bitpacked: {bp} (valid={bp_good})")


def stress_test():
    """Run many random matrices to find the bug."""
    print("\n" + "=" * 60)
    print("STRESS TEST: Looking for spurious vectors")
    print("=" * 60)

    configs = [
        (20, 15, 5),
        (50, 40, 8),
        (100, 90, 10),
        (200, 180, 12),
        (500, 450, 15),
        (1000, 950, 15),
    ]

    total_bugs = 0
    for nrows, ncols, w in configs:
        for seed in range(10):
            rows = _rand_sparse(nrows, ncols, w, seed=seed*100+nrows)
            bp_vecs = bitpacked_gauss(rows, ncols)
            bp_good = _verify(rows, bp_vecs)
            if bp_good < len(bp_vecs):
                spurious = len(bp_vecs) - bp_good
                print(f"  BUG: {nrows}x{ncols} w={w} seed={seed*100+nrows}: "
                      f"{spurious}/{len(bp_vecs)} spurious")
                total_bugs += 1

    if total_bugs == 0:
        print("  No bugs found in random tests!")
        print("  The bug may only manifest with GNFS-structured matrices.")
    else:
        print(f"\n  Found {total_bugs} buggy cases!")

    return total_bugs


def test_gnfs_like_matrix():
    """
    Test with a matrix structured like GNFS output:
    - Many columns (ncols >> 1000)
    - Sparse rows (weight 10-30)
    - nrows slightly > ncols (excess ~10%)
    """
    print("\n" + "=" * 60)
    print("TEST: GNFS-like matrix structure")
    print("=" * 60)

    for ncols in [500, 1000, 2000]:
        nrows = int(ncols * 1.1)
        rows = _rand_sparse(nrows, ncols, avg_w=20, seed=ncols+7)

        t0 = time.time()
        bp_vecs = bitpacked_gauss(rows, ncols)
        bp_time = time.time() - t0
        bp_good = _verify(rows, bp_vecs)

        print(f"  {nrows}x{ncols}: {len(bp_vecs)} vecs, {bp_good} valid, "
              f"{bp_time:.2f}s {'BUG!' if bp_good < len(bp_vecs) else 'OK'}")


def analyze_identity_init_bug():
    """
    Potential bug: in bitpacked_gauss, the zero-row detection at the end
    uses `np.all(mat == 0, axis=1)` which catches ALL zero rows, including
    rows that were used as pivots. But a pivot row gets zeroed out by
    subsequent eliminations!

    Wait, no — pivot rows should NOT get zeroed. They keep their pivot column.
    Unless another pivot row later XORs into them... but used rows are skipped
    as targets.

    Actually, the elimination does: rows_to_xor = all_set[all_set != piv]
    This correctly excludes the pivot row. But what about previously used
    pivot rows? If a used pivot row has the current column bit set, it would
    be in all_set but NOT excluded by 'all_set != piv' (since it's a different row).

    THE BUG: used rows still get XORed! The elimination step should skip
    ALL used rows, not just the current pivot.
    """
    print("\n" + "=" * 60)
    print("ANALYSIS: The Used-Row XOR Bug")
    print("=" * 60)

    # Construct a case where this matters:
    # Row 0: {0, 2}  -> pivot for col 0, used[0]=True
    # Row 1: {1, 2}  -> pivot for col 1, used[1]=True
    # Row 2: {0, 1}  -> eliminated by row 0 -> becomes {1, 2}, then by row 1 -> becomes {}
    # Row 3: {2}     -> col 2 processing
    #
    # When col=2 is processed:
    #   all_set = rows with bit 2: row 0 ({0,2}), row 1 ({1,2}->wait it changed), row 3 ({2})
    #   Actually after col 0 elim: row 2 becomes {1,2} (XOR with row 0's {0,2})
    #   After col 1 elim: row 2 becomes {} (XOR with row 1's {1,2})
    #   Now row 1 still has {1,2} (used, not eliminated by others)
    #   For col 2: all_set includes row 0 (has {0,2}), row 1 (has {1,2}), row 3 ({2})
    #   pivot = row 3 (first unused with bit 2)
    #   rows_to_xor = all_set != row3 = {row 0, row 1}
    #   Row 0 (USED!) gets XORed with row 3: {0,2} ^ {2} = {0}  -- CHANGES A PIVOT ROW!
    #   Row 1 (USED!) gets XORed with row 3: {1,2} ^ {2} = {1}  -- CHANGES ANOTHER PIVOT ROW!
    #
    # This corrupts the pivot rows! The combo tracking for these rows is now wrong.

    rows = [{0, 2}, {1, 2}, {0, 1}, {2}]
    ncols = 3
    print("Matrix: [{0,2}, {1,2}, {0,1}, {2}]")
    print("Expected: row 2 = row0 XOR row1 -> null vec {0,1,2}")
    print("          row 3 eliminates col 2 from rows 0,1 (BUG: modifies used pivot rows)")

    ref = mpz_gauss(rows, ncols)
    bp = bitpacked_gauss(rows, ncols)
    ref_good = _verify(rows, ref)
    bp_good = _verify(rows, bp)

    print(f"\nReference: {ref} (valid={ref_good}/{len(ref)})")
    print(f"Bitpacked: {bp} (valid={bp_good}/{len(bp)})")

    if bp_good < len(bp_vecs := bp):
        print("\n*** CONFIRMED: Used-row XOR bug! ***")
        print("Fix: filter out used rows from elimination targets")
        return True
    else:
        print("This specific case didn't trigger. Trying larger...")

    # Larger test designed to trigger the bug
    # Create matrix where pivot rows share columns with later pivots
    print("\nLarger constructed test...")
    ncols = 10
    rows2 = [
        {0, 5, 7},    # row 0: pivot for col 0
        {1, 5, 8},    # row 1: pivot for col 1
        {2, 5, 9},    # row 2: pivot for col 2
        {3, 6, 7},    # row 3: pivot for col 3
        {4, 6, 8},    # row 4: pivot for col 4
        {0, 1, 2},    # row 5: eliminated -> null vec
        {5, 7, 8, 9}, # row 6: pivot for col 5, but XORs into rows 0,1,2 (USED!)
        {6, 7, 8},    # row 7: pivot for col 6, XORs into rows 3,4 (USED!)
        {7},           # row 8: pivot for col 7, XORs into MANY used rows
        {8},           # row 9: pivot for col 8
        {9},           # row 10: pivot for col 9
    ]

    ref2 = mpz_gauss(rows2, ncols)
    bp2 = bitpacked_gauss(rows2, ncols)
    ref2_good = _verify(rows2, ref2)
    bp2_good = _verify(rows2, bp2)

    print(f"Reference: {len(ref2)} vecs, {ref2_good} valid")
    print(f"Bitpacked: {len(bp2)} vecs, {bp2_good} valid")

    # Check if results differ
    ref_sets = [frozenset(v) for v in ref2]
    bp_sets = [frozenset(v) for v in bp2]

    if set(ref_sets) != set(bp_sets):
        print("Vectors differ!")
        only_ref = set(ref_sets) - set(bp_sets)
        only_bp = set(bp_sets) - set(ref_sets)
        if only_ref:
            print(f"  Only in reference: {[sorted(s) for s in only_ref]}")
        if only_bp:
            print(f"  Only in bitpacked: {[sorted(s) for s in only_bp]}")

    return bp2_good < len(bp2)


if __name__ == "__main__":
    print("=" * 60)
    print("Track 4: Bitpacked Gauss Bug Diagnosis")
    print("=" * 60)

    # Step 1: Small known-answer tests
    diagnose_pivot_selection()
    diagnose_row_identity()

    # Step 2: Analyze the suspected bug
    has_bug = analyze_identity_init_bug()

    # Step 3: Stress test random matrices
    stress_test()

    # Step 4: GNFS-like matrices
    test_gnfs_like_matrix()

    # Step 5: Compare on larger matrices
    print("\n" + "=" * 60)
    print("COMPARISON: Reference vs Bitpacked on larger matrices")
    print("=" * 60)
    for nrows, ncols, w, seed in [(100, 80, 10, 1), (200, 180, 12, 2), (500, 450, 15, 3)]:
        compare_gauss(nrows, ncols, w, seed)
