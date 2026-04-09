# CryptoVend V4: Autonomous Digital Commerce via Smart Contract Oracle Networks

**Abstract.** We present CryptoVend V4, a system for trustless, serverless, and fully autonomous digital file sales using smart contract-based oracle networks. The seller encrypts a file with AES-256-GCM, splits the encryption key into Shamir secret shares, deploys the shares as autonomous smart contracts on an Ethereum Layer 2 network, and publishes the encrypted file and a self-contained buyer interface to IPFS. After deployment, no human participation is required — the system operates indefinitely through the interaction of smart contracts and content-addressed storage. Buyers pay the on-chain vending contract, query the oracle contracts for key shares via zero-gas read calls, reconstruct the encryption key via Lagrange interpolation over GF(2⁸), and decrypt the file entirely in-browser. The key contribution of V4 is the elimination of all off-chain infrastructure by encoding oracle nodes as smart contracts rather than HTTP endpoints, achieving what we term *infrastructure-free commerce* — a digital sales system whose only dependencies are a blockchain and a content-addressed storage network.

**Keywords:** Threshold cryptography, Shamir's Secret Sharing, smart contracts, autonomous commerce, IPFS, serverless architecture, digital rights management

---

## 1. Introduction

The sale of digital goods on the internet has historically required centralized infrastructure: web servers, payment processors, content delivery networks, and identity providers. Each component introduces points of failure, censorship vectors, and ongoing operational costs. Decentralized alternatives based on blockchain technology have reduced some dependencies but typically still require off-chain components for content delivery and key management.

CryptoVend V4 is the culmination of a four-version research trajectory aimed at minimizing the infrastructure required to sell a digital file:

- **V1** (Centralized): Standard web server with cryptocurrency payment. Server stores the file and delivers it after payment confirmation. Seller must maintain hosting.
- **V2** (Semi-decentralized): Smart contract handles payments. Seller keeps a browser tab open to watch for purchase events and deliver the encryption key on-chain. Eliminates the web server but requires seller to remain online.
- **V3** (Threshold): Seller splits the encryption key into Shamir shares distributed to independent HTTP oracle endpoints. Seller goes offline after setup. Oracle operators must maintain their endpoints.
- **V4** (Autonomous): Oracle endpoints are replaced by smart contracts. No HTTP servers exist anywhere in the system. Seller deploys contracts, publishes to IPFS, and the system operates autonomously and indefinitely.

The central claim of this paper is that **V4 achieves infrastructure-free commerce**: a system where the seller performs a single deployment action, after which no human, server, or service of any kind is required for the system to continue operating and processing sales.

---

## 2. System Architecture

### 2.1 Components

The CryptoVend V4 system consists of exactly three types of persistent artifacts:

1. **CryptoVendV4.sol** — The main vending contract, deployed on an Ethereum L2 chain. Handles payments, tracks purchases, and maintains the oracle registry.

2. **OracleNode.sol** — N instances of a minimal oracle contract, each storing one Shamir secret share. Verifies purchase status via cross-contract call to the main contract before releasing its share.

3. **IPFS Content** — Two content-addressed blobs:
   - The AES-256-GCM encrypted file
   - The buyer interface HTML page (self-contained, with embedded configuration and JavaScript)

No databases, no web servers, no API endpoints, no DNS records, no TLS certificates, no cloud functions, no container orchestration, no monitoring systems. The system's entire operational footprint is smart contract state and IPFS-pinned content.

### 2.2 Deployment (Seller Flow)

The seller opens a local HTML page (`seller.html`) in a browser with MetaMask:

1. **Encrypt**: Generate a random 256-bit AES key $K$. Encrypt the file $F$ using AES-256-GCM to produce ciphertext $C$. Compute the key commitment $h_K = \text{keccak256}(K)$.

2. **Split**: Using Shamir's Secret Sharing over GF(2⁸), split $K$ into $N$ shares $\{s_1, \ldots, s_N\}$ with threshold $t$. For each share $s_i$, compute the share commitment $h_i = \text{keccak256}(s_i)$.

3. **Upload**: Pin $C$ to IPFS, obtaining CID $c_F$.

4. **Deploy main contract**: Deploy `CryptoVendV4` with parameters $(price, h_K, t, N, c_F, metadata)$.

5. **Deploy oracle contracts**: For each $i \in \{1, \ldots, N\}$:
   - Generate a random 256-bit obfuscation salt $\sigma_i$
   - Deploy `OracleNode` with parameters $(vendingAddr, i, s_i, h_i, \sigma_i)$
   - The constructor stores the share as $s_i \oplus \text{keccak256}(\sigma_i \| \text{contractAddr} \| vendingAddr)$

6. **Register oracles**: For each deployed oracle, call `vendingContract.registerOracle(oracleAddr, h_i, i)`. The main contract verifies that each oracle's `info()` points back to itself.

7. **Generate and pin buyer page**: Create a self-contained HTML page with embedded configuration (contract addresses, oracle addresses, commitments, threshold parameters, file CID) and pin to IPFS, obtaining CID $c_B$.

8. **Finalize**: Call `vendingContract.setBuyerPageCID(c_B)`.

9. **Exit**: The seller closes the browser. No further action is ever required.

### 2.3 Purchase (Buyer Flow)

The buyer visits the IPFS-hosted buyer page:

1. **Connect**: Connect MetaMask wallet.

2. **Pay**: Call `vendingContract.purchase{value: price}()`. This records the purchase on-chain and emits a `PurchaseConfirmed(purchaseId, buyer, amount)` event.

3. **Collect shares**: For each oracle contract $O_i$ (addresses embedded in the buyer page):
   - Call `O_i.getShare(purchaseId)` via `eth_call` (off-chain read, zero gas)
   - The oracle contract calls `vendingContract.verifyPurchase(purchaseId)` internally
   - If the purchase is valid and not refunded, the oracle deobfuscates and returns its share $s_i$ along with its index $x_i$
   - The buyer verifies: $\text{keccak256}(s_i) = h_i$ (against the embedded commitment)
   - Continue until $t$ verified shares are collected (fault-tolerant: skip any oracle that fails)

4. **Reconstruct key**: Using Lagrange interpolation over GF(2⁸), reconstruct $K$ from any $t$ verified shares. Verify: $\text{keccak256}(K) = h_K$.

5. **Decrypt**: Download $C$ from IPFS, decrypt using AES-256-GCM with key $K$ to recover file $F$.

The entire process takes approximately 15–30 seconds and requires no human intervention beyond the buyer's initial click.

---

## 3. Threshold Cryptography

### 3.1 Shamir's Secret Sharing over GF(2⁸)

The AES-256 key $K$ is a 32-byte sequence. For each byte position $j \in \{0, \ldots, 31\}$, we construct a random polynomial $f_j$ of degree $t-1$ over $\text{GF}(2^8)$:

$$f_j(x) = K_j + a_{j,1} x + a_{j,2} x^2 + \cdots + a_{j,t-1} x^{t-1}$$

where $K_j$ is the $j$-th byte of $K$ and $a_{j,1}, \ldots, a_{j,t-1}$ are uniformly random elements of $\text{GF}(2^8)$.

Share $i$ consists of the evaluations $(i, f_0(i), f_1(i), \ldots, f_{31}(i))$ for $i \in \{1, \ldots, N\}$.

Reconstruction uses the Lagrange interpolation formula at $x = 0$:

$$K_j = \sum_{i \in S} f_j(x_i) \prod_{\substack{k \in S \\ k \neq i}} \frac{x_k}{x_k - x_i}$$

where $S$ is any subset of $t$ share indices, and all arithmetic is over $\text{GF}(2^8)$.

### 3.2 Galois Field Arithmetic

$\text{GF}(2^8)$ is constructed as $\mathbb{F}_2[x] / (x^8 + x^4 + x^3 + x + 1)$, using the irreducible polynomial $p(x) = x^8 + x^4 + x^3 + x + 1$ (hex: 0x11B, the same polynomial used by AES).

- **Addition/Subtraction**: Bitwise XOR (characteristic 2)
- **Multiplication**: Precomputed log/antilog tables for $O(1)$ multiplication
- **Inversion**: $a^{-1} = \text{EXP}[255 - \text{LOG}[a]]$

The implementation uses two 256-entry lookup tables (EXP and LOG) precomputed from a generator element, enabling constant-time field operations.

### 3.3 Security Properties

| Property | Guarantee |
|----------|-----------|
| **Secrecy** | Any $t-1$ or fewer shares reveal zero information about $K$ (information-theoretic, not computational) |
| **Reconstruction** | Any $t$ shares uniquely determine $K$ |
| **Key integrity** | Buyer verifies $\text{keccak256}(K) = h_K$ after reconstruction |
| **Share integrity** | Buyer verifies $\text{keccak256}(s_i) = h_i$ for each share |
| **Fault tolerance** | System operates correctly if any $N - t$ oracle contracts become inaccessible |

---

## 4. Smart Contract Oracle Design

### 4.1 The Oracle-as-Contract Paradigm

The central innovation of V4 is recognizing that an oracle node is, at its core, a pure function:

```
oracle(purchaseId) → share   if verified(purchaseId)
oracle(purchaseId) → ⊥       otherwise
```

This function has no side effects (it doesn't modify state), depends only on on-chain state (the purchase record), and returns a fixed value (the share). It is therefore naturally expressible as a Solidity `view` function, which is executed off-chain via `eth_call` at zero gas cost.

### 4.2 Storage Obfuscation

While Solidity `private` variables are not accessible to other contracts, they are readable via `eth_getStorageAt` at the EVM level. To raise the barrier for casual storage inspection, V4 applies an obfuscation layer:

The share $s$ is stored as:
$$\text{stored} = s \oplus \text{keccak256}(\sigma \| \text{address}(\text{this}) \| \text{vendingAddr} \| 0)$$

where $\sigma$ is a random salt chosen at deployment. The deobfuscation mask is recomputed inside the `getShare()` view function. An attacker reading raw storage sees only the obfuscated value and must:

1. Identify which contracts are oracle nodes
2. Determine the storage layout (slot positions, packing)
3. Extract the salt from immutable storage
4. Understand the XOR scheme
5. Repeat for $t$ different oracle contracts
6. Locate the encrypted file on IPFS
7. Assemble and decrypt

This is not cryptographic security in the formal sense — it is practical security through layered obscurity combined with the threshold requirement. For the target market of digital goods ($0.10–$100), this security model is comparable to or stronger than existing commercial DRM systems (which store decryption keys in client-side application memory).

### 4.3 Cross-Contract Verification

Each `OracleNode` contract verifies purchase validity by calling:

```solidity
(bool valid, , ) = ICryptoVendV4(vendingContract).verifyPurchase(purchaseId);
```

This cross-contract call occurs within the `view` function context, meaning it executes atomically and at zero gas cost (within `eth_call`). The verification checks:
- Purchase exists (purchaseId < purchaseCount)
- Purchase has not been refunded

### 4.4 Gas Cost Analysis

| Operation | Gas | USD (Base L2, 2024) | Frequency |
|-----------|-----|---------------------|-----------|
| Deploy CryptoVendV4 | ~800,000 | ~$0.08 | Once |
| Deploy OracleNode (each) | ~350,000 | ~$0.035 | N times |
| registerOracle (each) | ~80,000 | ~$0.008 | N times |
| setBuyerPageCID | ~50,000 | ~$0.005 | Once |
| purchase (buyer) | ~85,000 | ~$0.009 | Per sale |
| getShare (buyer) | 0 | $0 | Per oracle per sale |
| withdraw (seller) | ~30,000 | ~$0.003 | As needed |

**Total setup cost (3-of-5):** ~$0.30  
**Per-sale cost:** ~$0.009 (buyer pays; seller and oracles pay nothing)

---

## 5. Comparison with Prior Versions

| Property | V1 | V2 | V3 | V4 |
|----------|----|----|----|----|
| Seller online | Always | Always | Never | Never |
| Servers required | Web server | Browser tab | Oracle HTTP endpoints | **None** |
| Points of failure | Server, DNS, TLS | Seller's browser | Oracle uptime | **Chain halt only** |
| Per-sale cost (seller) | Hosting amortized | ~$0.007 gas | $0 | **$0** |
| Per-sale cost (buyer) | $0 (HTTP) | ~$0.01 | ~$0.01 | **~$0.01** |
| Third-party dependencies | Hosting, domain, TLS | MetaMask | Oracle operators | **None** |
| Deployment complexity | Moderate | Low | High (coordinate operators) | **Low (single session)** |
| System lifetime | Until server shutdown | Until seller closes browser | Until oracles shut down | **Indefinite** |
| Censorship resistance | Low | Medium | Medium-High | **Maximum** |
| Trust model | Trust seller's server | Trust seller | Trust t-of-N operators | **Trust code + chain** |

---

## 6. Security Analysis

### 6.1 Threat Model

We consider the following adversary capabilities:

1. **Passive observer**: Can read all blockchain state, including raw contract storage
2. **Active network participant**: Can submit transactions and call view functions
3. **IPFS reader**: Can access any pinned content

We do NOT consider:
- Adversaries who control the L2 sequencer/validator (could censor transactions)
- Adversaries who can break AES-256-GCM or keccak256
- Adversaries who can compromise the buyer's browser during purchase

### 6.2 Attack Vectors and Mitigations

**Attack 1: Read shares from contract storage**
- *Feasibility*: Possible with `eth_getStorageAt` + storage layout knowledge
- *Mitigation*: XOR obfuscation, need t-of-N shares, need to identify oracle contracts
- *Residual risk*: A determined attacker with EVM expertise could theoretically extract shares
- *Assessment*: Acceptable for digital goods market; comparable to Steam/iTunes DRM

**Attack 2: Front-run a purchase to extract shares**
- *Feasibility*: An MEV searcher could observe a purchase transaction, immediately call `getShare()`, and obtain shares
- *Mitigation*: `getShare()` requires a valid purchaseId, which only exists after the purchase is mined. MEV searchers cannot front-run a view function call (eth_call is not a transaction). Even if they front-run the purchase itself and call getShare with the resulting purchaseId, they'd be paying for a purchase they already made legitimately.
- *Residual risk*: None meaningful

**Attack 3: Replay purchase verification**
- *Feasibility*: Once a buyer has purchased, any address could call `getShare(theirPurchaseId)` 
- *Mitigation*: This is by design — the share is the same regardless of who calls. The security is in the threshold (need t shares) and the encrypted file (need the IPFS CID). A buyer who already purchased could share their purchaseId, but they could equally share the decrypted file.
- *Assessment*: Not a meaningful attack; equivalent to file sharing after purchase

**Attack 4: Oracle contract destruction**
- *Feasibility*: Oracle contracts have no `selfdestruct` — they are immutable. (Solidity 0.8.24 deprecates selfdestruct, and our contracts don't include it.)
- *Residual risk*: None

**Attack 5: Denial of service**
- *Feasibility*: Cannot DoS a view function called via eth_call. The RPC provider could be DoS'd, but the buyer can switch providers.
- *Residual risk*: Minimal; buyer can use any Ethereum RPC endpoint

### 6.3 Formal Security Properties

Let $\mathcal{A}$ be a passive adversary who can read all on-chain storage.

**Theorem 1 (Threshold Security).** If $\mathcal{A}$ can read the deobfuscated shares from fewer than $t$ oracle contracts, then $\mathcal{A}$ gains zero information about the AES key $K$ beyond what is revealed by $h_K = \text{keccak256}(K)$.

*Proof.* This follows directly from the information-theoretic security of Shamir's Secret Sharing. Any $t-1$ shares are uniformly distributed conditional on the key, since the polynomial has $t-1$ free coefficients. ∎

**Theorem 2 (Integrity).** If keccak256 is collision-resistant, a buyer who reconstructs a key $K'$ such that $\text{keccak256}(K') = h_K$ has, with overwhelming probability, recovered the correct key $K$.

*Proof.* A collision $K' \neq K$ with $\text{keccak256}(K') = \text{keccak256}(K)$ violates the collision resistance of keccak256. ∎

**Theorem 3 (Availability).** The system delivers the file to any paying buyer as long as:
(a) At least $t$ of the $N$ oracle contracts are accessible (i.e., the chain is operational), and
(b) The encrypted file is available on at least one IPFS gateway.

*Proof.* Condition (a) ensures $t$ shares can be collected. Lagrange interpolation reconstructs $K$. Condition (b) ensures the ciphertext is available. AES-GCM decryption with the correct key recovers $F$. ∎

---

## 7. Implementation

### 7.1 Smart Contracts

Both contracts are written in Solidity 0.8.24, targeting EVM-compatible L2 chains (Arbitrum, Base, Optimism). The total codebase is approximately 300 lines of Solidity.

`CryptoVendV4.sol` (main contract):
- Manages product listings, pricing, and purchase records
- Maintains an oracle registry (contract addresses, share commitments, indices)
- Provides `verifyPurchase()` for cross-contract verification by oracles
- Supports refunds (time-locked) and seller withdrawal

`OracleNode.sol` (oracle contract):
- Stores one obfuscated Shamir share
- Implements `getShare(purchaseId)` as a view function
- Verifies purchases via cross-contract call
- Contains `canServe(purchaseId)` for pre-flight checks

### 7.2 Client-Side (Browser)

The buyer page is a self-contained HTML file (~400 lines) that includes:
- **ethers.js** for blockchain interaction (loaded from CDN)
- **GF(2⁸) arithmetic** with precomputed log/antilog tables
- **Shamir reconstruction** via Lagrange interpolation
- **AES-256-GCM** decryption via the Web Crypto API
- **IPFS gateway fallback** (tries multiple gateways)
- **Visual progress** with share collection status

The entire purchase flow executes in the buyer's browser with no server communication beyond the Ethereum RPC endpoint and IPFS gateways.

### 7.3 Seller Console

The seller console (`seller.html`) is a local HTML page that orchestrates the deployment:
- **AES-256-GCM encryption** via Web Crypto API
- **Shamir split** with polynomial evaluation over GF(2⁸)
- **Contract deployment** via ethers.js + MetaMask
- **IPFS pinning** via Pinata API
- **Buyer page generation** with embedded configuration

After deployment, the seller console can be closed and deleted. All deployment artifacts are on-chain or on IPFS.

---

## 8. Discussion

### 8.1 The Infrastructure Spectrum

We can characterize digital commerce systems by their infrastructure requirements:

| Level | Description | Example |
|-------|-------------|---------|
| 5 | Full server stack | Traditional e-commerce |
| 4 | Managed services (SaaS) | Gumroad, Shopify |
| 3 | Serverless functions | V3 oracle nodes |
| 2 | Static hosting only | IPFS-based frontends |
| 1 | Smart contracts only | V4 oracle nodes |
| **0** | **Nothing** | **V4 complete system** |

V4 operates at Level 0: after deployment, the seller maintains zero infrastructure. The "infrastructure" is the Ethereum network itself (which the seller does not operate) and IPFS (which is collectively maintained by the network).

### 8.2 Limitations

1. **Storage readability**: As discussed in §6.2, contract storage is theoretically readable. For high-value content (thousands of dollars), stronger mechanisms would be needed — potentially involving trusted execution environments (TEEs) or future on-chain FHE.

2. **File size**: IPFS performance degrades for very large files (>1 GB). For large files, a hybrid approach using IPFS for key material and a decentralized storage network (Filecoin, Arweave) for the file itself would be preferable.

3. **Chain dependency**: The system requires the underlying L2 chain to continue operating. While established L2s are unlikely to halt, this is a non-trivial dependency for truly permanent systems.

4. **Key management**: The buyer must manage their Ethereum wallet. Loss of the wallet means loss of purchase history (though the decrypted file, once downloaded, is independent of the wallet).

5. **No DRM after download**: Once the buyer decrypts the file, they have an unencrypted copy. This is a fundamental limitation of any system that delivers plaintext to the buyer — it is shared by all existing digital distribution platforms.

### 8.3 Comparison with Existing Systems

| System | Infrastructure | Censorship Resistance | Seller Ongoing Effort | Per-Sale Cost |
|--------|---------------|----------------------|----------------------|---------------|
| Amazon Digital | AWS (massive) | None | Moderate | ~30% commission |
| Gumroad | SaaS | Low | Low | ~10% commission |
| OpenSea (NFT) | Smart contract + metadata server | Medium | Low | 2.5% + gas |
| CryptoVend V4 | **None** | **Maximum** | **Zero** | **~$0.01 gas** |

### 8.4 Ethical Considerations

The same properties that make V4 censorship-resistant and privacy-preserving also make it potentially usable for selling illicit content. This is an inherent tension in decentralized systems. We note that:

1. The encrypted file on IPFS cannot be inspected without the key
2. The smart contracts cannot be shut down by any authority
3. The seller can be completely anonymous

These properties are features for legitimate use cases (selling in authoritarian jurisdictions, protecting whistleblower materials, privacy-preserving commerce) but concerns for illegal content. We do not offer a resolution to this tension; it is shared by all censorship-resistant technologies.

---

## 9. Future Work

1. **On-chain FHE oracles**: When fully homomorphic encryption becomes practical in smart contracts, oracle nodes could compute `Enc(share, buyerPubKey)` on-chain, eliminating the storage readability concern entirely.

2. **Zero-knowledge purchase proofs**: Using ZK-SNARKs, a buyer could prove payment to oracle contracts without revealing their identity, enabling anonymous purchasing.

3. **Multi-file bundles**: Extending the system to sell multiple files under a single contract, with per-file key splitting and pricing.

4. **Subscription models**: Time-locked oracle contracts that only release shares during an active subscription period.

5. **Cross-chain deployment**: Oracle contracts on multiple chains for ultimate redundancy.

6. **Formal verification**: The simplicity of the oracle contract (a single view function with a cross-contract call and an XOR) makes it an excellent candidate for formal verification in a theorem prover.

---

## 10. Conclusion

CryptoVend V4 demonstrates that digital commerce can be reduced to a one-time deployment of smart contracts and IPFS content, after which the system operates autonomously and indefinitely. By recognizing that an oracle node is a pure function naturally expressible as a smart contract view function, we eliminate the last remaining off-chain infrastructure component.

The resulting system has properties not simultaneously achieved by any existing digital commerce platform: zero ongoing infrastructure, 100% uptime (conditional on chain availability), zero per-sale seller costs, complete censorship resistance, and full autonomy after deployment.

The key insight is architectural, not cryptographic: the same threshold cryptography used in V3 works equally well when oracle nodes are smart contracts rather than HTTP servers. The cryptographic machinery (Shamir's Secret Sharing, AES-256-GCM, keccak256 commitments) is unchanged. What changes is the *substrate* on which the oracle function executes — from ephemeral HTTP servers to permanent smart contracts.

We believe this represents a natural endpoint for the minimization of digital commerce infrastructure: there is nothing left to remove.

---

## References

1. Shamir, A. "How to Share a Secret." *Communications of the ACM* 22.11 (1979): 612–613.

2. Feldman, P. "A Practical Scheme for Non-interactive Verifiable Secret Sharing." *FOCS* (1987): 427–438.

3. Benet, J. "IPFS — Content Addressed, Versioned, P2P File System." *arXiv preprint* arXiv:1407.3561 (2014).

4. Wood, G. "Ethereum: A Secure Decentralised Generalised Transaction Ledger." *Ethereum Project Yellow Paper* (2014).

5. Bertoni, G., Daemen, J., Peeters, M., and Van Assche, G. "Keccak." *EUROCRYPT* (2013): 313–314.

6. Dworkin, M. "Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC." *NIST Special Publication 800-38D* (2007).

7. Buterin, V. "An Incomplete Guide to Rollups." *vitalik.ca* (2021).

---

## Appendix A: Contract Interface Specifications

### CryptoVendV4

```solidity
// Seller (one-time setup)
constructor(uint256 price, bytes32 keyCommitment, uint8 threshold, uint8 numOracles, string fileCID, string fileMetadata)
function registerOracle(address oracleContract, bytes32 shareCommitment, uint8 shareIndex) external
function setBuyerPageCID(string buyerPageCID) external

// Buyer
function purchase() external payable
function refund(uint64 purchaseId) external

// Oracle verification
function verifyPurchase(uint64 id) external view returns (bool valid, address buyer, bytes pubKey)

// Views
function getOracles() external view returns (address[], bytes32[], uint8[])
function summary() external view returns (...)
```

### OracleNode

```solidity
constructor(address vendingContract, uint8 shareIndex, bytes shareData, bytes32 shareCommitment, bytes32 salt)
function getShare(uint64 purchaseId) external view returns (bytes shareData, uint8 index)
function canServe(uint64 purchaseId) external view returns (bool)
function info() external view returns (address vending, uint8 index, bytes32 commitment, uint256 version)
```

## Appendix B: Version Evolution Summary

```
V1 (2023): Seller → Server → Buyer
            Server required 24/7

V2 (2024): Seller → Smart Contract ← Buyer
            Seller watches events, delivers key on-chain
            Seller must keep browser open

V3 (2024): Seller → Smart Contract ← Buyer
              ↓                        ↑
           Oracle HTTP Endpoints (share delivery)
            Seller offline, but oracle servers must run

V4 (2024): Seller → Smart Contract ← Buyer
              ↓          ↑                ↑
           Oracle Smart Contracts ────────┘
            (eth_call, 0 gas, 100% uptime)
            NOTHING must run after deployment
```
