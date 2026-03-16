/* ============================================================
   Enhanced Image Viewer -- B3 Pythagorean Tree Research
   Full-screen viewer with nav, keyboard, swipe, preload
   ============================================================ */

(function() {
  'use strict';

  // --- Image description database ---
  var IMAGE_DESCRIPTIONS = {
    // Series A (viz_b3_01.py) -- Tree Structure
    'img_A01.png': 'Radial layout of B3 tree to depth 6, concentric rings showing branching',
    'img_A02.png': 'Tree colored by a-value normalized, showing value distribution across branches',
    'img_A03.png': 'Hypotenuse primality scatter -- green dots are prime hypotenuses, red composite',
    'img_A04.png': 'B1 subtree (matrix A only) showing linear growth in (a,b) plane to depth 8',
    'img_A05.png': 'B2 subtree (matrix B only) showing exponential growth -- note scale difference',
    'img_A06.png': 'B3 subtree (matrix C only) showing the "flat" branch where b grows slowly',
    'img_A07.png': 'All three subtrees overlaid -- shows dramatically different growth rates',
    'img_A08.png': 'Radial node plot with size proportional to hypotenuse -- larger = deeper',
    'img_A09.png': 'Polar tree with angle = arctan(B/A) and radius = log(C) -- fan structure',
    'img_A10.png': 'Triples sorted by hypotenuse with color showing tree depth -- exponential growth curve',

    // Series B (viz_b3_02.py) -- Modular Orbits
    'img_B01.png': 'Pythagorean orbit density mod 7. Size/color shows count of triples hitting each (a mod p, b mod p) cell. Note forbidden residue classes and density hotspots.',
    'img_B02.png': 'Pythagorean orbit density mod 11. Size/color shows count of triples hitting each (a mod p, b mod p) cell. Note forbidden residue classes and density hotspots.',
    'img_B03.png': 'Pythagorean orbit density mod 13. Size/color shows count of triples hitting each (a mod p, b mod p) cell. Note forbidden residue classes and density hotspots.',
    'img_B04.png': 'Pythagorean orbit density mod 17. Size/color shows count of triples hitting each (a mod p, b mod p) cell. Note forbidden residue classes and density hotspots.',
    'img_B05.png': 'Pythagorean orbit density mod 19. Size/color shows count of triples hitting each (a mod p, b mod p) cell. Note forbidden residue classes and density hotspots.',
    'img_B06.png': 'Pythagorean orbit density mod 23. Size/color shows count of triples hitting each (a mod p, b mod p) cell. Note forbidden residue classes and density hotspots.',
    'img_B07.png': 'Pythagorean orbit density mod 29. Size/color shows count of triples hitting each (a mod p, b mod p) cell. Note forbidden residue classes and density hotspots.',
    'img_B08.png': 'Pythagorean orbit density mod 31. Size/color shows count of triples hitting each (a mod p, b mod p) cell. Note forbidden residue classes and density hotspots.',
    'img_B09.png': 'Pythagorean orbit density mod 37. Size/color shows count of triples hitting each (a mod p, b mod p) cell. Note forbidden residue classes and density hotspots.',
    'img_B10.png': 'Pythagorean orbit density mod 41. Size/color shows count of triples hitting each (a mod p, b mod p) cell. Note forbidden residue classes and density hotspots.',

    // Series C (viz_b3_03.py) -- SIQS Internals
    'img_C01.png': 'Dickman rho function with SIQS and GNFS operating regimes marked',
    'img_C02.png': 'Sieve array snapshot showing log-sum accumulation pattern',
    'img_C03.png': 'Factor base primes colored by residue class (cyan=1 mod 4, red=3 mod 4)',
    'img_C04.png': 'Partial relation graph showing DLP combining opportunities',
    'img_C05.png': 'GF(2) relation matrix sparsity pattern -- each cyan dot is a non-zero entry',
    'img_C06.png': 'Sieve yield rate vs polynomial count -- how quickly relations accumulate',
    'img_C07.png': 'GF(2) null vector barcode -- magenta=1, dark=0 -- this IS the factoring solution',
    'img_C08.png': 'Factor base coverage histogram',
    'img_C09.png': 'Smoothness rate heatmap -- digits vs smoothness bound B',
    'img_C10.png': 'Trial division timing breakdown',

    // Series D (viz_b3_04.py) -- Spectral Analysis
    'img_D01.png': 'Phase portrait of B2 matrix iterations -- convergence to fixed point',
    'img_D02.png': 'Singular value spectrum of Berggren product matrices',
    'img_D03.png': 'Lyapunov exponent distribution (mean=1.308) measuring chaos in tree paths',
    'img_D04.png': 'Spectral gap analysis across matrix products',
    'img_D05.png': 'Trace growth |Tr(M^n)| -- B1/B2 grow exponentially, B3 stays constant!',
    'img_D06.png': 'Characteristic polynomial roots on complex plane',
    'img_D07.png': 'Eigenvalues of all 3 Berggren matrices with unit circle reference',
    'img_D08.png': 'Spectral radius vs product depth',
    'img_D09.png': 'Eigenvector directions (x-y projection) -- geometric symmetry between branches',
    'img_D10.png': 'Matrix norm growth comparison',

    // Series E (viz_b3_05.py) -- Number Theory
    'img_E01.png': '(m,n) parameter distribution -- the fan structure showing branch ratios',
    'img_E02.png': 'Digit sum patterns across tree',
    'img_E03.png': 'Hypotenuse residues mod small primes (3,5,7,11,13,17) as pie charts',
    'img_E04.png': 'Prime factor count distribution',
    'img_E05.png': 'Quadratic residue/non-residue scatter of A mod 101 (green=QR, red=NQR)',
    'img_E06.png': 'Mobius function values on hypotenuses',
    'img_E07.png': 'Continued fraction quotients of sqrt(C) for various hypotenuses',
    'img_E08.png': 'Sum-of-divisors sigma(C) distribution',
    'img_E09.png': 'Euler totient phi(C) vs C -- multiple stripes below y=x show composite structure',
    'img_E10.png': 'Radical rad(C) distribution',

    // Series F (viz_b3_06.py) -- Geometry
    'img_F01.png': 'Actual right triangles drawn -- 30 Pythagorean triangles with labels and color by branch',
    'img_F02.png': 'Pythagorean triangle geometry analysis',
    'img_F03.png': 'Triangle area (AB/2) vs hypotenuse -- quadratic growth',
    'img_F04.png': 'Geometric properties of Pythagorean triples',
    'img_F05.png': 'Incircle radius r=(A+B-C)/2 vs hypotenuse -- multi-ray structure',
    'img_F06.png': 'Geometric invariant analysis',
    'img_F07.png': 'Lattice points (A,B) with parent-child connections forming fan of rays',
    'img_F08.png': 'Lattice geometry exploration',
    'img_F09.png': 'Stereographic projection A/(C+1), B/(C+1) -- triples map to quarter-circle arc',
    'img_F10.png': 'Extended geometric analysis',

    // Series G (viz_b3_07.py) -- Algorithm Performance
    'img_G01.png': 'SIQS vs GNFS vs ECM timing comparison (log scale)',
    'img_G02.png': 'Algorithm performance scaling analysis',
    'img_G03.png': 'Sieve throughput comparison',
    'img_G04.png': 'Polynomial selection efficiency',
    'img_G05.png': 'Memory usage vs digit size with 5GB OOM limit',
    'img_G06.png': 'Relation collection rate analysis',
    'img_G07.png': 'Linear algebra phase timing',
    'img_G08.png': 'Factor base optimization curves',
    'img_G09.png': 'Knuth-Schroeppel multiplier scores -- k=5 wins (pink bar)',
    'img_G10.png': 'End-to-end factoring pipeline profiling',

    // Series H (viz_b3_08.py) -- Factoring Hardness
    'img_H01.png': 'Factoring hardness distribution -- heavy right tail, most numbers easy',
    'img_H02.png': 'Hardness vs digit count relationship',
    'img_H03.png': 'Difficulty distribution by number type',
    'img_H04.png': 'Hardness correlation with factor balance',
    'img_H05.png': 'Information bits per relation -- grows with digit size (Dickman barrier)',
    'img_H06.png': 'Information-theoretic analysis of sieving',
    'img_H07.png': 'Entropy growth in relation collection',
    'img_H08.png': 'Compression barrier visualization',
    'img_H09.png': 'Theoretical vs empirical hardness',
    'img_H10.png': 'Hardness landscape summary',

    // Series I (viz_b3_11.py) -- Mandalas
    'img_I01.png': 'Golden-angle phyllotaxis mandala -- concentric rings with twilight_shifted colors',
    'img_I02.png': 'Angle-of-legs mandala -- natural fan showing three branch angular sectors',
    'img_I03.png': 'Three-fold branch symmetry overlay -- each subtree rotated 120 degrees, gold star at root',
    'img_I04.png': 'Extended mandala pattern analysis',
    'img_I05.png': 'Mandala symmetry exploration',
    'img_I06.png': 'Angular distribution mandala',
    'img_I07.png': 'Depth-coded mandala visualization',
    'img_I08.png': 'Branch path mandala pattern',
    'img_I09.png': 'Combined mandala synthesis',
    'img_I10.png': 'Mandala series summary',

    // Series J (viz_b3_12.py) -- Kaleidoscopes
    'img_J01.png': 'Residue grid mod 5 showing (a mod p, b mod p) counts. Circle size = frequency, color = count. Reveals forbidden classes and symmetry patterns.',
    'img_J02.png': 'Residue grid mod 7 showing (a mod p, b mod p) counts. Circle size = frequency, color = count. Reveals forbidden classes and symmetry patterns.',
    'img_J03.png': 'Residue grid mod 11 showing (a mod p, b mod p) counts. Circle size = frequency, color = count. Reveals forbidden classes and symmetry patterns.',
    'img_J04.png': 'Residue grid mod 13 showing (a mod p, b mod p) counts. Circle size = frequency, color = count. Reveals forbidden classes and symmetry patterns.',
    'img_J05.png': 'Extended kaleidoscope pattern analysis',
    'img_J06.png': 'Kaleidoscope symmetry exploration',
    'img_J07.png': 'Multi-prime kaleidoscope overlay',
    'img_J08.png': 'Kaleidoscope frequency analysis',
    'img_J09.png': 'Combined kaleidoscope synthesis',
    'img_J10.png': 'Kaleidoscope series summary',

    // Series K (viz_b3_13.py) -- Spiral Galaxy
    'img_K01.png': 'Golden-angle spiral -- each triple on spiral arm, colored by branch path (plasma)',
    'img_K02.png': 'Poincare disk model -- B3 tree in hyperbolic space, glowing cyan boundary',
    'img_K03.png': 'Angular spectrum by depth -- 2D heatmap of (theta, depth) with stacked histogram',

    // Series L (viz_b3_14.py) -- Fibonacci Web
    'img_L01.png': 'Log-log leg space with golden ratio reference lines showing branch trajectories',
    'img_L02.png': 'Leg ratio distributions a/b and b/c with phi, 1/phi, phi-squared markers -- multi-modal',

    // Series M (viz_b3_15.py) -- Tree of Life
    'img_M01.png': 'Radial tree (3280 nodes, depth 7) colored by hypotenuse magnitude (plasma)',
    'img_M02.png': 'Same tree, red=prime hypotenuse, blue=composite (coolwarm)',
    'img_M03.png': 'Same tree colored by digital root of hypotenuse (twilight_shifted, 9 values)',

    // Standalone images
    'galois_period.png': 'Order of B3 mod p -- bifurcation by Legendre symbol (2/p)',
    'tree_fractal.png': 'Fractal structure of the Pythagorean tree -- self-similar branching at every scale',
    'b3_mandelbrot.png': 'Mandelbrot-like set from Berggren matrix iteration -- connection to complex dynamics',
    'b3_arithmetic_progression.png': 'Arithmetic progressions discovered within B3 tree branches',
    'dickman_barrier.png': 'Dickman information barrier -- the fundamental limit on sieve-based factoring',
    'cfrac_tree_equivalence.png': 'Visual proof of CFRAC-Tree equivalence -- continued fraction walks match tree paths',
    'pyth_tree_spiral.png': 'Pythagorean tree rendered as an Archimedean spiral, triples along the arm',
    'eigenvalue_circle.png': 'Eigenvalue distribution following the circle law for Berggren products',
    'sieve_heatmap.png': 'Sieve array heatmap showing smooth number concentration patterns',
    'factor_landscape_3d.png': '3D landscape of factoring difficulty -- peaks are hard semiprimes, valleys are smooth numbers',
    'prime_spiral_pyth.png': 'Ulam-like prime spiral with Pythagorean hypotenuses highlighted',
    'discriminant_diversity.png': 'Discriminant diversity analysis for MPQS polynomial families',
    'factor_time_scaling.png': 'Factoring time vs digit count -- empirical L[1/2] and L[1/3] curves',
    'lyapunov_growth.png': 'Lyapunov exponent growth along random tree walks',
    'orbit_animation_frame.png': 'Single frame from modular orbit animation -- triples circling mod p',
    'smoothness_by_depth.png': 'Smoothness probability decreasing with tree depth',
    'smoothness_heatmap_2d.png': '2D heatmap of smoothness probability over (B, digit count) parameter space',
    'spectral_gap.png': 'Spectral gap measurement for Berggren group action',
    'tree_density.png': 'Node density at each tree depth -- exponential growth rate 3^d',
    'tree_mod_p.png': 'Tree structure projected into F_p -- cyclic orbits become visible',

    // Viz series
    'viz01_tree_branches.png': 'Tree branch geometry -- how the three Berggren matrices partition the (a,b) plane',
    'viz01_tree_fractal.png': 'Fractal dimension estimation of the Pythagorean tree boundary',
    'viz02_angle_depth_heatmap.png': 'Heatmap of arctan(b/a) vs tree depth -- angle concentrates with depth',
    'viz02_angular_rose.png': 'Rose diagram of branch angles -- three-fold near-symmetry',
    'viz03_cycle_structure.png': 'Cycle structure of B3 group action mod small primes',
    'viz03_full_orbit_mod5.png': 'Complete orbit of (3,4,5) under all Berggren matrices mod 5',
    'viz03_modular_orbits.png': 'Comparison of orbit sizes mod p for p = 5, 7, 11, 13',
    'viz04_hypotenuse_growth.png': 'Hypotenuse growth rate along each branch type (B1 exponential, B3 linear)',
    'viz04_hypotenuse_spiral.png': 'Hypotenuses plotted on a spiral -- note gaps at non-1-mod-4 primes',
    'viz05_coprimality_analysis.png': 'Coprimality structure: gcd(a_i, a_j) for sibling triples',
    'viz05_coprimality_heatmap.png': 'Heatmap of pairwise coprimality across tree levels',
    'viz06_eigenvalue_3d.png': 'Eigenvalues of depth-n products in 3D (Re, Im, depth)',
    'viz06_eigenvalue_complex.png': 'Eigenvalue trajectories in the complex plane as product depth increases',
    'viz06_spectral_radius_bars.png': 'Spectral radius comparison: B1 > B2 >> B3 = 1',
    'viz07_factor_density.png': 'Density of smooth numbers among tree hypotenuses vs random integers',
    'viz07_factor_overlay.png': 'Factor structure overlay on tree -- showing which primes divide which branches',
    'viz08_digital_mandala.png': 'Mandala pattern from digital roots of all triples to depth 8',
    'viz08_digital_root_analysis.png': 'Digital root cycle analysis -- why only {1,2,4,5,7,8} appear',
    'viz09_prime_density.png': 'Prime density among hypotenuses by depth -- converges to ~1/2 of pi(x)/x',
    'viz09_prime_hypotenuses.png': 'Distribution of prime vs composite hypotenuses across the tree',
    'viz10_galois_bifurcation.png': 'Bifurcation diagram: order of B3 mod p splits by Legendre symbol (2/p)',
    'viz10_order_ratios.png': 'Ratio of |<B3>| to p-1 and p+1 -- clustering at 1/2 and 1/4',

    // Berggren-Price analysis
    'bp_connection_density.png': 'Cross-tree connection density between Berggren and Price tree nodes',
    'bp_cross_tree_graph.png': 'Graph showing shared nodes between Berggren and Price Pythagorean trees',
    'bp_depth_scatter.png': 'Depth comparison scatter: Berggren depth vs Price depth for same triple',
    'bp_parent_comparison.png': 'Parent structure comparison between Berggren and Price trees',
    'bp_ppt_tree_growth.png': 'Growth rate comparison of primitive Pythagorean triple trees',
    'bp_prime_trees.png': 'Prime-focused subtrees extracted from both tree constructions',

    // Prime tree approaches
    'prime_tree_00_summary.png': 'Summary of 10 approaches to building prime-generating trees',
    'prime_tree_01_cunningham.png': 'Cunningham chain tree -- primes connected by 2p+1 relation',
    'prime_tree_02_linear_recurrence.png': 'Linear recurrence tree generating primes by recursive formula',
    'prime_tree_03_polynomial.png': 'Polynomial-based prime tree using quadratic generators',
    'prime_tree_04_modular.png': 'Modular arithmetic prime tree -- primes organized by residue class',
    'prime_tree_05_gcd_gap.png': 'GCD-gap prime tree -- spacing patterns between consecutive primes',
    'prime_tree_06_gaussian.png': 'Gaussian integer prime tree in the complex plane',
    'prime_tree_07_stern_brocot.png': 'Stern-Brocot tree adapted for prime generation',
    'prime_tree_08_totient.png': 'Euler totient-based tree connecting primes through phi function',
    'prime_tree_09_binary_split.png': 'Binary splitting prime tree -- recursive interval bisection',
    'prime_tree_10_ffm_hybrid.png': 'FFM hybrid prime tree combining multiple generation strategies'
  };

  // --- Series metadata ---
  var SERIES_META = {
    'A': { name: 'Tree Structure', script: 'viz_b3_01.py', count: 10 },
    'B': { name: 'Modular Orbits', script: 'viz_b3_02.py', count: 10 },
    'C': { name: 'SIQS Internals', script: 'viz_b3_03.py', count: 10 },
    'D': { name: 'Spectral Analysis', script: 'viz_b3_04.py', count: 10 },
    'E': { name: 'Number Theory', script: 'viz_b3_05.py', count: 10 },
    'F': { name: 'Geometry', script: 'viz_b3_06.py', count: 10 },
    'G': { name: 'Algorithm Performance', script: 'viz_b3_07.py', count: 10 },
    'H': { name: 'Factoring Hardness', script: 'viz_b3_08.py', count: 10 },
    'I': { name: 'Mandalas', script: 'viz_b3_11.py', count: 10 },
    'J': { name: 'Kaleidoscopes', script: 'viz_b3_12.py', count: 10 },
    'K': { name: 'Spiral Galaxy', script: 'viz_b3_13.py', count: 3 },
    'L': { name: 'Fibonacci Web', script: 'viz_b3_14.py', count: 2 },
    'M': { name: 'Tree of Life', script: 'viz_b3_15.py', count: 3 }
  };

  // Expose globally
  window.IMAGE_DESCRIPTIONS = IMAGE_DESCRIPTIONS;
  window.SERIES_META = SERIES_META;

  // --- Viewer state ---
  var viewerCollection = [];
  var viewerIndex = -1;
  var viewerOverlay = null;
  var viewerImg = null;
  var viewerCounter = null;
  var viewerDesc = null;
  var touchStartX = 0;
  var touchStartY = 0;

  // --- Create viewer DOM ---
  function createViewer() {
    if (document.getElementById('img-viewer')) return;

    var overlay = document.createElement('div');
    overlay.className = 'viewer-overlay';
    overlay.id = 'img-viewer';

    overlay.innerHTML =
      '<div class="viewer-top-bar">' +
        '<span class="viewer-counter" id="viewer-counter"></span>' +
        '<span class="viewer-caption-bar" id="viewer-caption"></span>' +
        '<button class="viewer-close" id="viewer-close" title="Close (Esc)">&times;</button>' +
      '</div>' +
      '<div class="viewer-img-container" id="viewer-img-container">' +
        '<img id="viewer-img" src="" alt="Full size">' +
      '</div>' +
      '<button class="viewer-nav prev" id="viewer-prev" title="Previous (Left Arrow)">&#8249;</button>' +
      '<button class="viewer-nav next" id="viewer-next" title="Next (Right Arrow)">&#8250;</button>' +
      '<div class="viewer-bottom-bar">' +
        '<span class="viewer-description" id="viewer-desc"></span>' +
      '</div>';

    document.body.appendChild(overlay);
    viewerOverlay = overlay;
    viewerImg = document.getElementById('viewer-img');
    viewerCounter = document.getElementById('viewer-counter');
    viewerDesc = document.getElementById('viewer-desc');

    // Close on overlay background click (not on image or controls)
    document.getElementById('viewer-img-container').addEventListener('click', function(e) {
      if (e.target === this) closeViewer();
    });
    document.getElementById('viewer-close').addEventListener('click', closeViewer);
    document.getElementById('viewer-prev').addEventListener('click', function(e) {
      e.stopPropagation(); navViewer(-1);
    });
    document.getElementById('viewer-next').addEventListener('click', function(e) {
      e.stopPropagation(); navViewer(1);
    });

    // Keyboard
    document.addEventListener('keydown', function(e) {
      if (!viewerOverlay || !viewerOverlay.classList.contains('active')) return;
      if (e.key === 'Escape') closeViewer();
      else if (e.key === 'ArrowLeft') navViewer(-1);
      else if (e.key === 'ArrowRight') navViewer(1);
    });

    // Touch/swipe
    overlay.addEventListener('touchstart', function(e) {
      touchStartX = e.changedTouches[0].screenX;
      touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });
    overlay.addEventListener('touchend', function(e) {
      var dx = e.changedTouches[0].screenX - touchStartX;
      var dy = e.changedTouches[0].screenY - touchStartY;
      if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 50) {
        if (dx > 0) navViewer(-1); else navViewer(1);
      }
    }, { passive: true });
  }

  function getFilename(src) {
    return src.split('/').pop();
  }

  function getDescription(filename) {
    return IMAGE_DESCRIPTIONS[filename] || '';
  }

  function getCaption(filename) {
    // Extract a short label from the filename
    var name = filename.replace('.png', '').replace(/^img_/, '').replace(/_/g, ' ');
    return name;
  }

  // --- Open viewer with a collection of image sources ---
  function openViewer(collection, startIndex) {
    createViewer();
    viewerCollection = collection;
    viewerIndex = startIndex || 0;
    showCurrentImage(false);
    viewerOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    preloadAdjacent();
  }

  function showCurrentImage(animate) {
    if (viewerIndex < 0 || viewerIndex >= viewerCollection.length) return;
    var item = viewerCollection[viewerIndex];

    if (animate) {
      viewerImg.classList.add('fade-out');
      setTimeout(function() {
        viewerImg.src = item.src;
        viewerImg.alt = item.label || '';
        viewerImg.classList.remove('fade-out');
      }, 120);
    } else {
      viewerImg.src = item.src;
      viewerImg.alt = item.label || '';
    }

    viewerCounter.textContent = (viewerIndex + 1) + ' / ' + viewerCollection.length;

    var caption = document.getElementById('viewer-caption');
    caption.textContent = item.label || getCaption(getFilename(item.src));

    var filename = getFilename(item.src);
    var desc = item.description || getDescription(filename);
    viewerDesc.textContent = desc;

    // Show/hide nav buttons
    document.getElementById('viewer-prev').style.display = viewerCollection.length > 1 ? '' : 'none';
    document.getElementById('viewer-next').style.display = viewerCollection.length > 1 ? '' : 'none';
  }

  function navViewer(dir) {
    if (viewerCollection.length <= 1) return;
    viewerIndex = (viewerIndex + dir + viewerCollection.length) % viewerCollection.length;
    showCurrentImage(true);
    preloadAdjacent();
  }

  function preloadAdjacent() {
    var len = viewerCollection.length;
    if (len <= 1) return;
    var nextIdx = (viewerIndex + 1) % len;
    var prevIdx = (viewerIndex - 1 + len) % len;
    new Image().src = viewerCollection[nextIdx].src;
    new Image().src = viewerCollection[prevIdx].src;
  }

  function closeViewer() {
    if (viewerOverlay) {
      viewerOverlay.classList.remove('active');
      document.body.style.overflow = '';
      viewerIndex = -1;
    }
  }

  // --- Public API ---
  window.ImageViewer = {
    open: openViewer,
    close: closeViewer,
    nav: navViewer,
    descriptions: IMAGE_DESCRIPTIONS,
    seriesMeta: SERIES_META
  };

  // --- Back to Top button ---
  function initBackToTop() {
    var btn = document.createElement('button');
    btn.className = 'back-to-top';
    btn.id = 'back-to-top';
    btn.innerHTML = '&#8593;';
    btn.title = 'Back to top';
    btn.addEventListener('click', function() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    document.body.appendChild(btn);

    window.addEventListener('scroll', function() {
      if (window.scrollY > 400) {
        btn.classList.add('visible');
      } else {
        btn.classList.remove('visible');
      }
    }, { passive: true });
  }

  // Init when DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBackToTop);
  } else {
    initBackToTop();
  }

})();
