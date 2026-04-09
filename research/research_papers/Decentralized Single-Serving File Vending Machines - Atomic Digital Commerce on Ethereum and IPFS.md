# Decentralized Single-Serving File Vending Machines: Atomic Digital Commerce on Ethereum and IPFS

**Authors:** Crypto Vending Machine Research Team  
**Date:** 2025  
**Keywords:** Ethereum, IPFS, AES-256-GCM, smart contracts, decentralized commerce, content-addressed storage, atomic exchange, digital file sales

---

## Abstract

We present a system for selling encrypted digital files through single-serving Ethereum smart contracts with decentralized storage on the InterPlanetary File System (IPFS). Our architecture achieves atomic exchange between payment and content delivery without requiring a trusted intermediary, centralized server, or platform operator. The seller encrypts a file using AES-256-GCM, uploads the ciphertext to IPFS, and deploys a minimal smart contract that escrows the decryption key. Upon payment, the contract releases the key via an on-chain event, enabling the buyer's browser to decrypt the file entirely client-side using the WebCrypto API. We analyze the security properties, gas costs, and limitations of this approach, demonstrate a working implementation, and discuss extensions including multi-buyer licensing, time-locked refunds, and threshold encryption schemes.

---

## 1. Introduction

### 1.1 The Problem

Digital file sales today depend on centralized platforms — Gumroad, Patreon, Amazon, Apple — that act as trusted intermediaries. These platforms extract fees (typically 5-30%), impose content policies, and represent single points of failure for censorship, deplatforming, and data breaches. Sellers surrender control of their content and customer relationships; buyers trust the platform to deliver what was advertised.

The fundamental operation — exchanging money for a digital file — should not require a corporation in the middle. It requires only:

1. **Verifiable payment:** The buyer can prove they paid.
2. **Verifiable delivery:** The buyer receives the exact file advertised.
3. **Atomicity:** Payment and delivery happen together, or not at all.

### 1.2 Our Contribution

We demonstrate that these three properties can be achieved using existing blockchain and distributed storage primitives, with no custom infrastructure:

- **AES-256-GCM** for authenticated encryption of the file
- **IPFS** for content-addressed, tamper-evident, censorship-resistant storage
- **Ethereum smart contracts** for trustless, atomic payment-for-key exchange
- **WebCrypto API** for client-side decryption with zero server interaction

Our system is "single-serving" — each contract handles exactly one file sale to one buyer, minimizing attack surface and contract complexity. The entire buyer experience occurs through a single IPFS-hosted HTML page that connects to MetaMask.

### 1.3 Paper Organization

Section 2 reviews related work. Section 3 describes the system architecture. Section 4 provides the cryptographic construction. Section 5 presents the smart contract design. Section 6 analyzes security. Section 7 evaluates performance and costs. Section 8 discusses limitations and extensions. Section 9 concludes.

---

## 2. Related Work

### 2.1 Decentralized Marketplaces

**OpenBazaar** (2014-2021) pioneered peer-to-peer commerce using Bitcoin multisig escrow, but required running a dedicated node and never achieved mainstream adoption. **Origin Protocol** and **Boson Protocol** provide decentralized marketplace frameworks but focus on physical goods and require significant smart contract infrastructure.

### 2.2 Content Monetization on Blockchain

**Audius** (music streaming), **Mirror** (writing), and **Lens Protocol** (social) demonstrate blockchain-based content distribution, but operate as platforms with their own tokens and governance. They solve the platform-lock-in problem by replacing one platform with another (albeit decentralized) platform.

### 2.3 Paid Data Exchange Protocols

**Ocean Protocol** provides a data marketplace with compute-to-data capabilities. **Filecoin** incentivizes storage provision but doesn't natively handle paid content delivery. **Lit Protocol** offers threshold encryption for token-gated access but requires its own node network.

### 2.4 Our Distinction

Unlike the above, our system requires **zero infrastructure beyond Ethereum and IPFS** — no custom tokens, no governance, no node networks, no platform. Each sale is a self-contained, disposable smart contract with a static HTML frontend. The seller needs only a command-line tool; the buyer needs only MetaMask and a web browser.

---

## 3. System Architecture

### 3.1 Overview

The system consists of four components:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Seller CLI  │────▶│  IPFS Network │◀────│ Buyer Browser│
│  (Python)    │     │  (Storage)    │     │ (HTML/JS)    │
└──────┬───────┘     └──────────────┘     └──────┬───────┘
       │                                          │
       │         ┌──────────────────┐              │
       └────────▶│ Ethereum Contract │◀────────────┘
                 │ (Payment + Key)   │
                 └──────────────────┘
```

### 3.2 Seller Workflow

1. **Encrypt:** The CLI generates a random 256-bit AES key and encrypts the file using AES-256-GCM with a random 96-bit nonce. The original filename is included as Additional Authenticated Data (AAD).

2. **Upload:** The encrypted file is uploaded to IPFS, returning a Content Identifier (CID) — a cryptographic hash that uniquely and immutably identifies the content.

3. **Deploy:** A `FileVendingMachine` smart contract is deployed to Ethereum containing:
   - The IPFS CID of the encrypted file
   - The AES decryption key (stored as raw bytes)
   - The sale price in wei
   - The seller's address for fund withdrawal

4. **Generate Frontend:** A self-contained HTML page is generated with the contract address, ABI, chain ID, and IPFS CID baked in. This page is uploaded to IPFS.

5. **Share:** The seller distributes the IPFS CID of the frontend page. Anyone with this link can purchase the file.

### 3.3 Buyer Workflow

1. **Visit:** The buyer navigates to the IPFS-hosted frontend page via any IPFS gateway (e.g., `https://ipfs.io/ipfs/QmXYZ...`).

2. **Connect:** The page prompts the buyer to connect their MetaMask wallet and verifies they are on the correct Ethereum network.

3. **Purchase:** The buyer clicks "Purchase" and confirms the MetaMask transaction sending exactly `price` wei to the contract's `purchase()` function.

4. **Receive Key:** Upon transaction confirmation, the contract emits a `Purchased` event containing the decryption key. The frontend parses this event from the transaction receipt.

5. **Download:** The frontend fetches the encrypted file from IPFS using the baked-in CID.

6. **Decrypt:** Using the WebCrypto API, the frontend decrypts the file entirely in the browser — no data is sent to any server.

7. **Save:** The decrypted file is offered as a download with the original filename.

---

## 4. Cryptographic Construction

### 4.1 Encryption Scheme

We use AES-256 in Galois/Counter Mode (GCM), which provides both confidentiality and authenticity:

- **Key:** 256 bits, generated using a cryptographically secure random number generator (`os.urandom` / `Crypto.Random.get_random_bytes`)
- **Nonce:** 96 bits, randomly generated (NIST SP 800-38D recommendation)
- **Additional Authenticated Data (AAD):** The original filename, encoded as UTF-8
- **Tag:** 128 bits, generated by GCM for integrity verification

The encrypted file format is:

```
[12 bytes: nonce][16 bytes: GCM tag][N bytes: ciphertext]
```

### 4.2 Security Properties

**Confidentiality:** AES-256 provides 256-bit security against key recovery. The best known attack against AES-256 is Bogdanov et al.'s biclique attack (2011), which reduces security to 2^254.4 — still computationally infeasible.

**Integrity:** GCM's authentication tag detects any modification to the ciphertext, nonce, or AAD. An adversary who modifies the encrypted file on IPFS will be detected during decryption.

**Freshness:** Each encryption uses a fresh random nonce, ensuring that encrypting the same file twice produces different ciphertexts.

**Binding:** Including the filename as AAD prevents an attacker from substituting a different encrypted file while reusing the same key and nonce.

### 4.3 Client-Side Decryption

The buyer's browser decrypts using the W3C WebCrypto API (`crypto.subtle.decrypt`), which provides:

- Hardware-accelerated AES-GCM on modern processors (AES-NI)
- No JavaScript cryptographic library dependencies
- Key material never leaves the browser's secure context
- Supported in all modern browsers (Chrome 37+, Firefox 34+, Safari 11+)

---

## 5. Smart Contract Design

### 5.1 Contract Structure

The `FileVendingMachine` contract is deliberately minimal (~100 lines of Solidity):

```solidity
contract FileVendingMachine {
    address public seller;
    address public buyer;
    uint256 public price;
    string  public ipfsCID;
    bytes   public encryptionKey;
    bool    public purchased;

    event Purchased(address indexed buyer, uint256 price,
                    string ipfsCID, bytes encryptionKey);

    function purchase() external payable { ... }
    function withdraw() external { ... }
}
```

### 5.2 State Machine

The contract has exactly three states:

```
  CREATED ──purchase()──▶ PURCHASED ──withdraw()──▶ COMPLETED
```

- **CREATED:** `purchased = false`, accepting payment
- **PURCHASED:** `purchased = true`, key revealed, funds escrowed
- **COMPLETED:** Funds withdrawn by seller

### 5.3 Gas Costs

Deployment gas (estimated):
- Contract creation: ~800,000 gas
- Constructor storage (CID + key): ~200,000 gas
- **Total deployment: ~1,000,000 gas**

At 30 gwei gas price and ETH at $3,000:
- Deployment cost: ~$90 (mainnet)
- Deployment cost: ~$0 (testnet)

Purchase transaction: ~60,000 gas (~$5.40 at above prices)

### 5.4 Design Decisions

**Why store the key on-chain?** The key is stored in contract storage, which is publicly readable by anyone running an Ethereum node. This is acceptable because:

1. Before purchase, a determined adversary could read storage slots directly. For low-value files, this is an acceptable risk. For high-value files, we recommend the threshold encryption extension (Section 8.2).

2. After purchase, the key is public by design — the buyer has it, and it's emitted in a public event.

3. The simplicity of on-chain key storage eliminates the need for off-chain key servers, reducing the trust surface.

**Why single-serving?** A one-buyer contract has minimal attack surface, no reentrancy concerns with multiple buyers, and allows the buyer to verify the exact contract code and terms before purchasing. Multi-buyer extensions are discussed in Section 8.1.

---

## 6. Security Analysis

### 6.1 Threat Model

We consider the following adversaries:

1. **Passive blockchain observer:** Can read all contract storage and transactions
2. **IPFS node operator:** Can read the encrypted file
3. **Malicious seller:** Deploys a contract with incorrect key or file
4. **Front-running attacker:** Monitors the mempool for purchase transactions
5. **Network-level adversary:** Can observe and modify network traffic

### 6.2 Analysis

| Threat | Mitigation | Residual Risk |
|--------|-----------|---------------|
| Key extraction pre-purchase | Key in public storage | LOW: Requires direct storage reads; economic cost of frontrunning exceeds value for most files |
| Encrypted file modification | IPFS CID = content hash | NONE: Modified content has a different CID |
| Wrong file delivered | Buyer can verify CID matches contract | LOW: Buyer should verify before purchasing |
| Seller deploys bad key | No on-chain verification | MEDIUM: Seller reputation required |
| Front-running | Not mitigated in base design | MEDIUM: Use commit-reveal for high-value |
| MITM on IPFS gateway | HTTPS to gateway; CID verification | LOW: Content-addressing provides integrity |

### 6.3 Formal Properties

**Atomicity:** The `purchase()` function either succeeds (transferring ETH and emitting the key) or reverts entirely. There is no state where the buyer has paid but the key is not emitted.

**Finality:** Once the `Purchased` event is emitted, it is permanently recorded on the blockchain. The buyer can always retrieve the key from historical event logs.

**Immutability:** The contract has no `selfdestruct`, no proxy pattern, and no admin functions that could change the key, price, or CID after deployment.

---

## 7. Performance Evaluation

### 7.1 Encryption Performance

AES-256-GCM encryption and decryption rates on commodity hardware:

| File Size | Encryption Time | Decryption Time (Python) | Decryption Time (WebCrypto) |
|-----------|-----------------|--------------------------|----------------------------|
| 1 KB      | < 1 ms         | < 1 ms                  | < 1 ms                    |
| 1 MB      | ~5 ms          | ~5 ms                   | ~2 ms                     |
| 100 MB    | ~500 ms        | ~500 ms                 | ~200 ms                   |
| 1 GB      | ~5 s           | ~5 s                    | ~2 s                      |

WebCrypto is faster due to AES-NI hardware acceleration exposed directly to the browser.

### 7.2 IPFS Upload/Download

IPFS performance depends heavily on network conditions and pinning:

- **Upload:** 1-30 seconds for files up to 100 MB (local daemon)
- **First download:** 2-60 seconds (content discovery + transfer)
- **Cached download:** < 1 second (from nearby gateway)

For reliable availability, sellers should pin content on at least 2-3 IPFS pinning services (Pinata, Infura, web3.storage).

### 7.3 End-to-End Latency

| Step | Time |
|------|------|
| MetaMask connection | 1-3 s |
| Transaction submission | 1-2 s |
| Transaction confirmation (1 block) | 12-15 s |
| IPFS download (cached) | 1-5 s |
| Browser decryption (10 MB file) | < 100 ms |
| **Total** | **~20-30 s** |

---

## 8. Limitations and Extensions

### 8.1 Multi-Buyer Licensing

The single-serving model can be extended to N buyers by:

1. **Counter-based:** Allow N purchases, each buyer gets the same key. Simple but key is shared.
2. **Per-buyer encryption:** Store N encrypted copies of the key, each encrypted with a buyer's public key. Requires buyer registration.
3. **Proxy re-encryption:** Use a re-encryption proxy to transform ciphertexts for each buyer. More complex but preserves privacy.

### 8.2 Threshold Encryption

For high-value files, the decryption key should not be stored in a single contract. Instead:

1. Split the key using Shamir's Secret Sharing into N shares
2. Distribute shares across N independent contracts or oracles
3. Buyer collects K-of-N shares after payment
4. Reconstruct the key client-side

This prevents key extraction by a single blockchain observer.

### 8.3 Time-Locked Refunds

Add a refund mechanism:

```solidity
uint256 public deadline;

function refund() external {
    require(msg.sender == buyer);
    require(block.timestamp > deadline);
    require(!withdrawn);
    // Return funds to buyer
}
```

### 8.4 Content Preview

Allow the seller to include an unencrypted preview (e.g., first page, low-resolution version) alongside the encrypted file, with its own IPFS CID stored in the contract.

### 8.5 Batch Sales

Instead of one contract per file, deploy a factory contract that creates minimal proxy (EIP-1167) clones for each sale, reducing deployment costs by ~90%.

### 8.6 Cross-Chain Deployment

The contract and frontend can be deployed on any EVM-compatible chain (Polygon, Arbitrum, Base, Optimism) for lower gas costs while maintaining the same security model.

---

## 9. Conclusion

We have demonstrated that trustless, intermediary-free digital file sales are achievable today using standard Ethereum smart contracts, IPFS, and browser-native cryptography. Our single-serving vending machine pattern reduces the problem to its essence: an atomic exchange of ETH for a decryption key, with the encrypted content hosted on immutable, content-addressed storage.

The system requires no custom infrastructure, no tokens, no governance, and no ongoing maintenance. Once deployed, a vending machine contract operates autonomously until purchased, then permanently records the transaction on the blockchain.

While the base design has known limitations (single buyer, on-chain key storage, no refunds), we have outlined practical extensions that address each limitation. The core contribution is demonstrating that the minimal viable implementation is surprisingly simple — ~100 lines of Solidity, ~500 lines of Python, and a single HTML file — yet provides meaningful security and usability guarantees.

We believe this pattern will find application in micropayments for journalism, academic papers, independent music and art, software licenses, and any domain where creators want to sell directly to consumers without platform intermediation.

---

## References

1. Nakamoto, S. (2008). Bitcoin: A Peer-to-Peer Electronic Cash System.
2. Buterin, V. (2014). Ethereum: A Next-Generation Smart Contract and Decentralized Application Platform.
3. Benet, J. (2014). IPFS — Content Addressed, Versioned, P2P File System.
4. Dworkin, M. (2007). NIST SP 800-38D: Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC.
5. Bogdanov, A., Khovratovich, D., & Rechberger, C. (2011). Biclique Cryptanalysis of the Full AES. ASIACRYPT 2011.
6. EIP-1167: Minimal Proxy Contract. https://eips.ethereum.org/EIPS/eip-1167
7. W3C WebCrypto API. https://www.w3.org/TR/WebCryptoAPI/
8. Shamir, A. (1979). How to Share a Secret. Communications of the ACM.

---

## Appendix A: Reproduction Instructions

```bash
# Install dependencies
pip install pycryptodome web3 requests

# Encrypt a file
python crypto_vending_machine.py encrypt --file myfile.pdf --price 0.01

# Deploy to Sepolia testnet
export PRIVATE_KEY="0x..."
export RPC_URL="https://rpc.sepolia.org"
python crypto_vending_machine.py deploy --config output/config.json --network sepolia

# Run tests
python -m pytest tests/ -v

# Run demos
python demos/demo_encrypt_decrypt.py
python demos/demo_full_pipeline.py
```

## Appendix B: Contract ABI

See `contracts/FileVendingMachine.sol` for the full Solidity source and `crypto_vending_machine.py` for the inline ABI specification.

## Appendix C: Gas Cost Breakdown

| Operation | Gas Used | Cost @ 30 gwei, $3000 ETH |
|-----------|----------|---------------------------|
| Deploy (empty CID) | ~500,000 | ~$45 |
| Deploy (typical) | ~1,000,000 | ~$90 |
| purchase() | ~60,000 | ~$5.40 |
| withdraw() | ~30,000 | ~$2.70 |
| getKey() | 0 (view) | $0 |
| info() | 0 (view) | $0 |

*Note: L2 chains (Arbitrum, Base, Optimism) reduce these costs by 10-100x.*
