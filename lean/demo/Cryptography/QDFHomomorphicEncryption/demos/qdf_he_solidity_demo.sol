// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title QDFHomomorphicEncryption
 * @notice On-chain verification of QDF-based homomorphic encryption operations.
 *
 * This contract demonstrates how Pythagorean quadruple identities can be used
 * for privacy-preserving computation on Ethereum:
 *
 * - Verify that ciphertexts are valid Pythagorean quadruples (a² + b² + c² = d²)
 * - Perform noise-free homomorphic addition when the alignment condition holds
 * - Detect errors via the QDF syndrome
 * - Modular arithmetic preservation for gas-efficient verification
 *
 * Key Theorem (formally verified in Lean 4):
 *   (a₁+a₂)² + (b₁+b₂)² + (c₁+c₂)² = (d₁+d₂)²
 *   ⟺ a₁a₂ + b₁b₂ + c₁c₂ = d₁d₂
 */
contract QDFHomomorphicEncryption {

    // ============================================================
    // DATA STRUCTURES
    // ============================================================

    /// @notice A Pythagorean quadruple (a, b, c, d) with a² + b² + c² = d²
    struct Quadruple {
        int256 a;
        int256 b;
        int256 c;
        int256 d;
    }

    /// @notice Encrypted value stored as a Pythagorean quadruple
    struct EncryptedValue {
        Quadruple quad;
        uint256 modulus;      // Modular reduction parameter
        address owner;        // Who owns this ciphertext
        uint256 timestamp;    // When it was created
    }

    // ============================================================
    // STATE
    // ============================================================

    mapping(bytes32 => EncryptedValue) public encryptedValues;
    mapping(address => bytes32[]) public userValues;

    uint256 public totalOperations;
    uint256 public noiseFreeOperations;

    // ============================================================
    // EVENTS
    // ============================================================

    event ValueEncrypted(bytes32 indexed id, address indexed owner, uint256 modulus);
    event HomomorphicAddition(bytes32 indexed result, bytes32 indexed input1, bytes32 indexed input2, bool noiseFree);
    event HomomorphicScaling(bytes32 indexed result, bytes32 indexed input, int256 scalar);
    event ErrorDetected(bytes32 indexed id, int256 syndrome);
    event QuadrupleVerified(bytes32 indexed id, bool valid);

    // ============================================================
    // CORE VERIFICATION
    // ============================================================

    /**
     * @notice Verify that a tuple is a valid Pythagorean quadruple.
     * @dev Checks a² + b² + c² = d² (the fundamental QDF identity)
     */
    function isValidQuadruple(Quadruple memory q) public pure returns (bool) {
        return q.a * q.a + q.b * q.b + q.c * q.c == q.d * q.d;
    }

    /**
     * @notice Compute the 3D inner product of two quadruples' legs.
     * @return The inner product a₁a₂ + b₁b₂ + c₁c₂
     */
    function innerProduct(Quadruple memory q1, Quadruple memory q2)
        public pure returns (int256)
    {
        return q1.a * q2.a + q1.b * q2.b + q1.c * q2.c;
    }

    /**
     * @notice Compute the hypotenuse product d₁ · d₂.
     */
    function hypotenuseProduct(Quadruple memory q1, Quadruple memory q2)
        public pure returns (int256)
    {
        return q1.d * q2.d;
    }

    /**
     * @notice Compute the noise from component-wise addition.
     * @dev Noise = 2(⟨v₁,v₂⟩ - d₁d₂)
     * @return The exact noise value (0 means noise-free addition)
     */
    function computeNoise(Quadruple memory q1, Quadruple memory q2)
        public pure returns (int256)
    {
        return 2 * (innerProduct(q1, q2) - hypotenuseProduct(q1, q2));
    }

    /**
     * @notice Check if two quadruples satisfy the exact homomorphism condition.
     * @dev Returns true iff ⟨v₁,v₂⟩ = d₁d₂ (noise-free addition)
     */
    function isAligned(Quadruple memory q1, Quadruple memory q2)
        public pure returns (bool)
    {
        return innerProduct(q1, q2) == hypotenuseProduct(q1, q2);
    }

    /**
     * @notice Compute the Gram diagonal (should equal 2d²).
     */
    function gramDiagonal(Quadruple memory q) public pure returns (int256) {
        return q.a * q.a + q.b * q.b + q.c * q.c + q.d * q.d;
    }

    /**
     * @notice Compute error syndrome for a single-component perturbation.
     * @dev Syndrome = e(2a + e)
     */
    function errorSyndrome(int256 a, int256 e) public pure returns (int256) {
        return e * (2 * a + e);
    }

    // ============================================================
    // HOMOMORPHIC OPERATIONS
    // ============================================================

    /**
     * @notice Component-wise addition of two quadruples.
     * @dev Always returns a result, but it's only a valid quadruple when aligned.
     */
    function homomorphicAdd(Quadruple memory q1, Quadruple memory q2)
        public pure returns (Quadruple memory)
    {
        return Quadruple(
            q1.a + q2.a,
            q1.b + q2.b,
            q1.c + q2.c,
            q1.d + q2.d
        );
    }

    /**
     * @notice Scalar multiplication of a quadruple (always exact).
     * @dev (ka)² + (kb)² + (kc)² = k²(a² + b² + c²) = k²d² = (kd)²
     */
    function homomorphicScale(Quadruple memory q, int256 k)
        public pure returns (Quadruple memory)
    {
        return Quadruple(k * q.a, k * q.b, k * q.c, k * q.d);
    }

    /**
     * @notice Modular verification: check QDF identity mod m.
     * @dev (a² + b² + c²) mod m == d² mod m
     */
    function verifyModular(Quadruple memory q, uint256 m)
        public pure returns (bool)
    {
        require(m > 0, "Modulus must be positive");
        int256 im = int256(m);
        int256 lhs = ((q.a * q.a + q.b * q.b + q.c * q.c) % im + im) % im;
        int256 rhs = ((q.d * q.d) % im + im) % im;
        return lhs == rhs;
    }

    // ============================================================
    // PARAMETRIC FAMILY GENERATION
    // ============================================================

    /**
     * @notice Generate a quadruple from the quadratic family.
     * @dev n² + (n+1)² + (n(n+1))² = (n²+n+1)²
     */
    function quadraticFamily(int256 n) public pure returns (Quadruple memory) {
        return Quadruple(n, n + 1, n * (n + 1), n * n + n + 1);
    }

    /**
     * @notice Generate a classical Pythagorean triple as a quadruple.
     * @dev (2mn)² + (m²-n²)² + 0² = (m²+n²)²
     */
    function classicalTriple(int256 m, int256 n)
        public pure returns (Quadruple memory)
    {
        return Quadruple(2 * m * n, m * m - n * n, 0, m * m + n * n);
    }

    // ============================================================
    // ENCRYPTED VALUE MANAGEMENT
    // ============================================================

    /**
     * @notice Store an encrypted value as a verified Pythagorean quadruple.
     */
    function storeEncrypted(
        int256 a, int256 b, int256 c, int256 d,
        uint256 modulus
    ) external returns (bytes32) {
        Quadruple memory q = Quadruple(a, b, c, d);

        // Verify the quadruple is valid (mod modulus if provided)
        if (modulus > 0) {
            require(verifyModular(q, modulus), "Invalid quadruple mod m");
        } else {
            require(isValidQuadruple(q), "Invalid Pythagorean quadruple");
        }

        bytes32 id = keccak256(abi.encodePacked(a, b, c, d, msg.sender, block.timestamp));

        encryptedValues[id] = EncryptedValue({
            quad: q,
            modulus: modulus,
            owner: msg.sender,
            timestamp: block.timestamp
        });

        userValues[msg.sender].push(id);
        emit ValueEncrypted(id, msg.sender, modulus);
        emit QuadrupleVerified(id, true);

        return id;
    }

    /**
     * @notice Homomorphically add two encrypted values.
     */
    function addEncrypted(bytes32 id1, bytes32 id2)
        external returns (bytes32)
    {
        EncryptedValue storage ev1 = encryptedValues[id1];
        EncryptedValue storage ev2 = encryptedValues[id2];

        require(ev1.owner != address(0), "Value 1 not found");
        require(ev2.owner != address(0), "Value 2 not found");

        Quadruple memory sum = homomorphicAdd(ev1.quad, ev2.quad);
        bool noiseFree = isAligned(ev1.quad, ev2.quad);

        bytes32 resultId = keccak256(abi.encodePacked(
            sum.a, sum.b, sum.c, sum.d, msg.sender, block.timestamp
        ));

        encryptedValues[resultId] = EncryptedValue({
            quad: sum,
            modulus: ev1.modulus, // Use first value's modulus
            owner: msg.sender,
            timestamp: block.timestamp
        });

        userValues[msg.sender].push(resultId);
        totalOperations++;
        if (noiseFree) noiseFreeOperations++;

        emit HomomorphicAddition(resultId, id1, id2, noiseFree);
        return resultId;
    }

    /**
     * @notice Homomorphically scale an encrypted value.
     */
    function scaleEncrypted(bytes32 id, int256 scalar)
        external returns (bytes32)
    {
        EncryptedValue storage ev = encryptedValues[id];
        require(ev.owner != address(0), "Value not found");

        Quadruple memory scaled = homomorphicScale(ev.quad, scalar);

        bytes32 resultId = keccak256(abi.encodePacked(
            scaled.a, scaled.b, scaled.c, scaled.d, msg.sender, block.timestamp
        ));

        encryptedValues[resultId] = EncryptedValue({
            quad: scaled,
            modulus: ev.modulus,
            owner: msg.sender,
            timestamp: block.timestamp
        });

        userValues[msg.sender].push(resultId);
        totalOperations++;
        noiseFreeOperations++; // Scaling is always noise-free

        emit HomomorphicScaling(resultId, id, scalar);
        return resultId;
    }

    /**
     * @notice Verify integrity of an encrypted value.
     * @return valid Whether the QDF identity holds
     * @return noise The deviation from the identity (0 = valid)
     */
    function verifyIntegrity(bytes32 id)
        external view returns (bool valid, int256 noise)
    {
        EncryptedValue storage ev = encryptedValues[id];
        require(ev.owner != address(0), "Value not found");

        Quadruple memory q = ev.quad;
        noise = q.a * q.a + q.b * q.b + q.c * q.c - q.d * q.d;
        valid = (noise == 0);

        return (valid, noise);
    }

    // ============================================================
    // VIEW FUNCTIONS
    // ============================================================

    function getUserValueCount(address user) external view returns (uint256) {
        return userValues[user].length;
    }

    function getNoiseFreeFraction() external view returns (uint256 nf, uint256 total) {
        return (noiseFreeOperations, totalOperations);
    }
}
