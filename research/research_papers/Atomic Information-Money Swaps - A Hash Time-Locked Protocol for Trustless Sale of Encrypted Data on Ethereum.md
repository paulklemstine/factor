# Atomic Information-Money Swaps: A Hash Time-Locked Protocol for Trustless Sale of Encrypted Data on Ethereum

**Oracle Council Research Group**

---

## Abstract

We present *PayToDecrypt*, a smart contract protocol that enables the trustless, atomic exchange of encrypted digital content for cryptocurrency payment on the Ethereum blockchain. The protocol adapts Hash Time-Locked Contract (HTLC) mechanisms — originally developed for cross-chain atomic swaps — to the domain of information commerce. A seller commits to an encryption key via its cryptographic hash, a buyer locks payment in escrow, and the seller must reveal the correct decryption key to claim funds. We prove that under standard cryptographic assumptions, the protocol satisfies atomicity (both parties receive their consideration or neither does), seller honesty (the correct key must be revealed), and buyer safety (funds are recoverable after timeout). We analyze the protocol's game-theoretic properties, characterize the front-running attack surface, quantify gas costs across Layer 1 and Layer 2 deployments, and propose extensions incorporating zero-knowledge proofs for content verification. Monte Carlo simulations with 10,000 trials demonstrate economic viability for content valued above $50 on Ethereum L1 and above $1 on Layer 2 networks.

**Keywords:** smart contracts, hash time-locked contracts, information marketplace, encrypted data exchange, Ethereum, atomic swaps

---

## 1. Introduction

### 1.1 The Information Commerce Problem

Digital information has a unique economic property: it is a non-rivalrous good whose value often depends on exclusivity. Once revealed, a secret cannot be un-revealed. This creates a fundamental trust problem in information commerce: the buyer must pay before seeing the goods, or the seller must reveal the goods before receiving payment. In either case, one party is vulnerable to defection by the other.

Traditional solutions rely on trusted intermediaries — publishers, marketplaces, escrow services — who add cost, latency, and single points of failure. The emergence of programmable blockchains offers an alternative: smart contracts that enforce fair exchange without any trusted third party.

### 1.2 The Core Challenge

Everything stored on a public blockchain is transparent. Contract storage, transaction calldata, and event logs are visible to all participants. This transparency, essential for consensus, appears fundamentally incompatible with the sale of secrets. How can one sell information on a platform where all information is public?

### 1.3 Our Contribution

We resolve this tension through an adaptation of Hash Time-Locked Contracts. The key insight is that the decryption key is never stored on-chain in plaintext. Instead, the seller publishes a *commitment* (cryptographic hash) to the key, the encrypted payload is stored off-chain (e.g., on IPFS), and the smart contract creates an atomic binding between key revelation and payment release. We call this mechanism an **Atomic Information-Money Swap (AIMS)**.

Our contributions are:

1. **Protocol Design**: A complete, auditable Solidity smart contract implementing the AIMS protocol with well-defined state machine and security invariants.

2. **Security Analysis**: Formal characterization of the protocol's security properties, threat model, and known attack vectors (including MEV-based front-running).

3. **Economic Analysis**: Gas cost modeling across multiple networks and Monte Carlo simulation of market outcomes under varying assumptions about participant behavior.

4. **Extensions**: Proposals for zero-knowledge content verification, threshold decryption for seller availability, and Layer 2 deployment for micro-transactions.

---

## 2. Background and Related Work

### 2.1 Hash Time-Locked Contracts

HTLCs were introduced in the context of the Lightning Network to enable trustless cross-chain atomic swaps. The core mechanism binds a payment to the revelation of a preimage: a hash `H` is published, and funds are released only when a value `K` satisfying `hash(K) = H` is presented. A timeout mechanism ensures funds are recoverable if the preimage is never revealed.

Our work adapts this mechanism from its original purpose (swapping cryptocurrencies across chains) to a new domain: swapping information for payment on a single chain.

### 2.2 Fairness in Digital Exchange

The problem of fair exchange — ensuring that two parties simultaneously receive each other's goods without a trusted third party — has been studied extensively. Theoretical results show that perfectly fair exchange without a trusted third party is impossible in general asynchronous networks. However, blockchain-based protocols achieve a practical form of fairness by using the consensus mechanism as an implicit trusted party.

### 2.3 Existing Approaches

Several projects have explored information marketplaces on blockchain:

- **Ocean Protocol**: Focuses on data tokenization and access control, using service agreements and proxy re-encryption. Requires a separate proxy network.
- **Filecoin retrieval market**: Enables payment for data retrieval from IPFS storage providers. Does not provide content verification.
- **Basic paywall contracts**: Simple access-control contracts that grant permissions after payment. Rely on off-chain enforcement.

Our protocol distinguishes itself by achieving atomic exchange purely through on-chain mechanisms, without requiring proxy networks, oracles, or off-chain enforcement.

---

## 3. Protocol Design

### 3.1 System Model

**Participants:**
- **Seller (S)**: Possesses plaintext content `P` and wishes to sell it.
- **Buyer (B)**: Wishes to acquire `P` and is willing to pay price `π` in ETH.
- **Contract (C)**: An immutable smart contract on Ethereum.

**Cryptographic Primitives:**
- `Enc(K, P)`: Authenticated symmetric encryption (AES-256-GCM) of plaintext `P` under key `K`.
- `Dec(K, C)`: Corresponding decryption.
- `H(·)`: Keccak-256 hash function (native to the EVM).

**Communication Channels:**
- Ethereum blockchain: Public, append-only, tamper-evident ledger.
- IPFS / off-chain storage: Public, content-addressed storage for the encrypted payload.

### 3.2 Protocol Steps

**Phase 1: Listing (Seller)**

1. Seller generates a random 256-bit key: `K ←$ {0,1}^256`
2. Seller encrypts the payload: `C ← Enc(K, P)`
3. Seller computes the key commitment: `H_K ← H(K)`
4. Seller computes the content hash: `H_P ← H(P)`
5. Seller uploads `C` to IPFS, obtaining content identifier `CID`
6. Seller calls `createListing(H_K, H_P, CID, description, π, τ)` where `τ` is the timeout duration

**Phase 2: Funding (Buyer)**

7. Buyer inspects the listing: reads description, downloads `C` from IPFS
8. Buyer calls `fundListing(id)` sending exactly `π` ETH
9. Contract locks `π` ETH in escrow, records `buyer` address and funding timestamp

**Phase 3: Revelation (Seller)**

10. Seller calls `revealKey(id, K)`
11. Contract verifies: `H(K) == H_K` (stored commitment)
12. If verification passes: contract transfers `π` ETH to seller
13. Contract emits `KeyRevealed(id, seller, K)` event

**Phase 4: Decryption (Buyer)**

14. Buyer reads `K` from the `KeyRevealed` event
15. Buyer computes `P ← Dec(K, C)`
16. Buyer verifies: `H(P) == H_P` (content hash from listing)

**Timeout Path:**

If seller does not reveal `K` within timeout `τ`:
- Buyer calls `claimRefund(id)`
- Contract verifies: `block.timestamp ≥ fundedAt + τ`
- Contract returns `π` ETH to buyer

### 3.3 State Machine

The contract maintains a finite state machine with the following states and transitions:

```
CREATED → FUNDED → REVEALED    (happy path)
CREATED → FUNDED → REFUNDED    (timeout path)
CREATED → CANCELLED            (seller cancels)
```

**Invariants:**
- I1: ETH can only leave escrow via REVEALED or REFUNDED transitions
- I2: REVEALED requires `H(K) == H_K` (hash verification)
- I3: REFUNDED requires `block.timestamp ≥ fundedAt + τ` (timeout check)
- I4: All transitions are irreversible
- I5: Exactly one terminal state is reached for each funded listing

### 3.4 Gas Cost Analysis

| Operation | Gas Units | Cost at 30 gwei (USD) |
|-----------|----------|----------------------|
| `createListing` | ~85,000 | $7.65 |
| `fundListing` | ~55,000 | $4.95 |
| `revealKey` | ~45,000 | $4.05 |
| `claimRefund` | ~35,000 | $3.15 |
| **Happy path total** | **~185,000** | **$16.65** |

*Costs assume ETH = $3,000 and gas price = 30 gwei.*

---

## 4. Security Analysis

### 4.1 Threat Model

We consider the following adversarial capabilities:

- **Malicious Seller**: May attempt to claim payment without revealing the correct key, or may encrypt garbage content.
- **Malicious Buyer**: May attempt to obtain the decryption key without paying.
- **Front-runner/MEV Searcher**: May monitor the mempool and extract the decryption key from pending transactions.
- **Network-level Adversary**: May censor or reorder transactions (bounded by Ethereum's consensus assumptions).

### 4.2 Security Properties

**Theorem 1 (Seller Honesty).** Under the preimage resistance of Keccak-256, a seller cannot claim escrowed payment without revealing a key `K` such that `H(K) = H_K`.

*Proof sketch.* The `revealKey` function computes `H(K)` and compares it to the stored commitment `H_K`. This check is enforced at the EVM level and cannot be bypassed. Finding `K' ≠ K` such that `H(K') = H(K)` would require a second-preimage attack on Keccak-256, which is computationally infeasible under standard assumptions.

**Theorem 2 (Buyer Safety).** A buyer's funds are either (a) transferred to the seller upon correct key revelation, or (b) refundable after timeout `τ`, regardless of seller behavior.

*Proof sketch.* The state machine has exactly two exit paths from FUNDED: REVEALED (requiring hash verification) and REFUNDED (requiring timeout expiry). The contract holds the ETH and no other code path can extract it. Since state transitions are irreversible, double-spending is prevented.

**Theorem 3 (Atomicity).** The protocol achieves atomic exchange: either both (seller receives ETH, buyer receives key) or neither.

*Proof sketch.* If the seller reveals `K`, the contract atomically emits the key in an event and transfers ETH. If the seller does not reveal, the buyer reclaims ETH and no key is exposed. There is no intermediate state where one party has received their consideration and the other has not (modulo the front-running issue discussed below).

### 4.3 The Front-Running Attack

The most significant vulnerability is front-running during key revelation. When the seller submits `revealKey(id, K)`, the value `K` is visible in the transaction's calldata in the public mempool before the transaction is mined. A front-runner could:

1. Observe the pending transaction containing `K`
2. Use `K` to decrypt the ciphertext `C`
3. Obtain the plaintext `P` without ever paying

**Severity**: The front-runner obtains the content for free, but the *buyer* is unaffected — they still receive the key when the transaction is mined, and their escrowed ETH is transferred to the seller. The seller is also unaffected (they receive payment). The harm is to the *exclusivity* of the information, not to the atomic exchange.

**Mitigations:**
1. **Private transaction submission**: Sellers can use Flashbots Protect or similar services to submit the `revealKey` transaction directly to block builders, bypassing the public mempool entirely.
2. **Encrypted calldata**: The seller could encrypt `K` under the buyer's public key and include the encrypted key in the transaction. The buyer decrypts it off-chain. This adds complexity but eliminates mempool leakage.
3. **Commit-reveal extension**: Add a two-phase reveal where the seller first commits to a blinded key, then reveals in a separate transaction.

### 4.4 Content Quality Problem

The hash commitment guarantees that the seller reveals the *correct* key (the one they originally committed to). However, it does not guarantee that the plaintext content is useful, accurate, or as described. The content hash `H_P` provides post-hoc verification but cannot prevent a seller from encrypting garbage.

**Proposed solution**: Zero-knowledge proofs of content properties. The seller generates a ZK proof that the plaintext satisfies certain properties (e.g., "is a valid JPEG," "contains data matching schema X," "has entropy > threshold"). The verifier circuit checks `Enc(K, P) = C ∧ property(P) = true`. This gives the buyer confidence in content quality before funding, without revealing the content itself.

---

## 5. Game-Theoretic Analysis

### 5.1 Single-Shot Game

Consider a single interaction between seller S and buyer B:

- S's strategies: {Reveal, Don't Reveal}
- B's strategies: {Fund, Don't Fund}

The payoff matrix (S, B) in a sequential game:

| | B: Fund | B: Don't Fund |
|---|---|---|
| S: Reveal | (π - gas, V - π - gas) | (0, 0) |
| S: Don't Reveal | (-rep, -gas) | (0, 0) |

Where `V` is the buyer's valuation of the content, `π` is the price, `gas` is transaction costs, and `rep` is reputation loss.

**Nash Equilibrium**: (Fund, Reveal) is the unique subgame-perfect Nash equilibrium when `V > π + 2·gas` and `π > gas + rep` (seller prefers payment to reputation loss).

### 5.2 Repeated Game

In a repeated game with reputation:
- Sellers build reputation through successful transactions
- Buyers can observe seller history on-chain
- The shadow of the future incentivizes honest behavior

**Result**: With a sufficiently low discount rate, cooperation is sustainable as a subgame-perfect equilibrium in the infinitely repeated game.

### 5.3 Monte Carlo Simulation

We simulated 10,000 market interactions with the following parameters:
- Content values: uniformly sampled from {0.1, 0.5, 1.0, 5.0, 10.0, 50.0} ETH
- Seller honest probability: 95%
- Buyer satisfaction probability: 90%
- Gas cost: 0.006 ETH per transaction

**Results:**
- 94.9% of transactions completed via happy path
- 5.1% resulted in timeout and refund
- Average seller profit: 10.56 ETH per trade
- Gas costs represented 0.1% of total volume
- Protocol is economically viable for content worth >$50 (L1) or >$1 (L2)

---

## 6. Extensions and Future Work

### 6.1 Zero-Knowledge Content Verification

Using zk-SNARKs (e.g., Groth16 or PLONK), sellers can prove properties of the encrypted content without revealing it:

- `π_zk = Prove(K, P: Enc(K, P) = C ∧ φ(P))`

Where `φ` is an arbitrary predicate over the plaintext. The verifier contract checks the proof before allowing funding, giving buyers cryptographic assurance of content quality.

### 6.2 Threshold Decryption

To eliminate seller availability as a requirement, the key `K` can be split using Shamir's Secret Sharing among `n` nodes, with a `t`-of-`n` threshold required for reconstruction. A DAO or decentralized committee holds the shares and releases them upon verified payment. This converts the single-seller model into a distributed availability model.

### 6.3 Layer 2 Deployment

Deploying on Layer 2 networks (Arbitrum, Optimism, Base) reduces gas costs by 20-50x, making micro-transactions viable. The security model inherits from Ethereum L1 via the rollup's fraud/validity proofs, preserving the protocol's security guarantees.

### 6.4 Streaming Payment for Partial Revelation

For large datasets, a streaming protocol could reveal data incrementally as payment flows. Each chunk has its own key commitment, and a payment channel provides continuous micropayments as chunks are revealed. This supports pay-per-byte pricing and reduces the trust required for large transactions.

### 6.5 Buyer Privacy

Current protocol reveals the buyer's address publicly. Future work could integrate stealth addresses or privacy-preserving payment channels to hide who purchased what content, while maintaining the atomic exchange guarantee.

---

## 7. Implementation

### 7.1 Smart Contract

We implemented the PayToDecrypt contract in Solidity 0.8.24 (see Appendix A). The contract follows the checks-effects-interactions pattern for reentrancy safety, uses custom errors for gas-efficient revert messages, and emits structured events for off-chain indexing.

### 7.2 Client Libraries

We provide Python demonstration scripts that implement:
- Cryptographic key generation, encryption, and decryption
- Contract interaction simulation with full state tracking
- Visualization of protocol flow, state machine, and economic analysis
- Monte Carlo simulation of market outcomes

### 7.3 Deployment Considerations

For production deployment, we recommend:
- Formal verification of the smart contract (e.g., using Certora or Halmos)
- OpenZeppelin-based access control patterns
- Flashbots integration for front-running protection
- IPFS pinning with Filecoin backup for ciphertext availability
- Subgraph deployment for efficient event indexing

---

## 8. Conclusion

The PayToDecrypt protocol demonstrates that trustless information commerce is achievable on public blockchains through the adaptation of hash time-locked contracts to the information domain. By separating the commitment to a decryption key (public, on-chain) from the encrypted content (public, off-chain) and the key itself (revealed only upon payment), the protocol achieves atomic exchange of information for payment without any trusted intermediary.

The protocol's security rests on standard cryptographic assumptions (preimage resistance of Keccak-256) and the consensus guarantees of Ethereum. The primary remaining challenge — front-running during key revelation — can be mitigated through private transaction submission (Flashbots) or encrypted calldata.

Our economic analysis shows the protocol is viable for content valued above $50 on Ethereum L1, with Layer 2 deployment extending viability to micro-transactions of $1 or less. Combined with zero-knowledge proofs for content verification, the protocol provides a foundation for a new class of decentralized information marketplaces where cryptographic guarantees replace institutional trust.

---

## References

1. Poon, J., Dryja, T. (2016). The Bitcoin Lightning Network: Scalable Off-Chain Instant Payments.
2. Herlihy, M. (2018). Atomic Cross-Chain Swaps. ACM PODC.
3. Buterin, V. (2014). A Next-Generation Smart Contract and Decentralized Application Platform. Ethereum White Paper.
4. Ben-Sasson, E., et al. (2014). Succinct Non-Interactive Zero Knowledge for a von Neumann Architecture. USENIX Security.
5. Daian, P., et al. (2020). Flash Boys 2.0: Frontrunning in Decentralized Exchanges, Miner Extractable Value, and Consensus Instability. IEEE S&P.
6. Shamir, A. (1979). How to Share a Secret. Communications of the ACM.
7. Even, S., Goldreich, O., Lempel, A. (1985). A Randomized Protocol for Signing Contracts. Communications of the ACM.

---

## Appendix A: Contract Source Code

See `contracts/PayToDecrypt.sol` in the project repository.

## Appendix B: Demonstration Scripts

See `demos/` directory:
- `demo_1_crypto_primitives.py`: Core cryptographic operations
- `demo_2_protocol_visualization.py`: Protocol flow and state diagrams
- `demo_3_full_simulation.py`: Full protocol simulation with Monte Carlo analysis
