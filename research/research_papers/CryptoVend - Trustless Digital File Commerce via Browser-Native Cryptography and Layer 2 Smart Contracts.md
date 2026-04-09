# CryptoVend: Trustless Digital File Commerce via Browser-Native Cryptography and Layer 2 Smart Contracts

---

## Abstract

We present CryptoVend, a decentralized system for selling digital files that requires no server infrastructure, no intermediary, and no trust between buyer and seller. The entire system consists of two HTML files — a seller application and a buyer application — plus a smart contract deployed on an Ethereum Layer 2 network. The seller application encrypts files with AES-256-GCM, deploys a purchase contract, and pins encrypted data to IPFS. The buyer application, itself hosted on IPFS, enables payment via MetaMask and in-browser decryption. Key exchange uses ECIES over secp256k1, with on-chain key commitments for fraud prevention and a time-locked refund mechanism for buyer protection. On Layer 2 networks (Arbitrum, Base, Optimism), total transaction costs per sale are under $0.05, making the system economically viable for files priced as low as $1. We analyze the system's security properties, game-theoretic incentives, and economic characteristics, and identify the seller-online requirement as the primary architectural limitation with clear paths to resolution via threshold cryptography.

**Keywords**: decentralized commerce, fair exchange, IPFS, Layer 2, ECIES, AES-GCM, smart contracts, browser cryptography

---

## 1. Introduction

The sale of digital goods on the internet is dominated by centralized platforms: app stores, e-book retailers, stock photo agencies, and software marketplaces. These intermediaries extract 15-30% fees, impose content restrictions, require seller identity verification, and can deplatform sellers unilaterally. More fundamentally, they represent single points of failure and censorship.

The emergence of programmable blockchains — particularly Ethereum — introduced the possibility of *trustless commerce*: transactions where neither party needs to trust the other, because the rules are enforced by code. However, early attempts at decentralized file sales faced three obstacles:

1. **Gas costs**: Deploying and interacting with smart contracts on Ethereum's main network costs $10-100 per transaction, making small-file sales economically absurd.
2. **Infrastructure requirements**: Existing solutions require running servers (Node.js, Python) to manage encryption, IPFS pinning, and event watching.
3. **Key management complexity**: Securely delivering a decryption key to a buyer without revealing it to the world requires careful cryptographic protocol design.

CryptoVend v2 addresses all three challenges:

- **Layer 2 networks** (Arbitrum, Base, Optimism) reduce transaction costs by 100-1000×, to under $0.05 per sale.
- **Browser-native cryptography** (SubtleCrypto API, noble-secp256k1) eliminates all server-side code. The entire system is two HTML files.
- **ECIES key transport** with on-chain commitments provides provably secure key delivery with fraud detection.

The result is a system where a seller can:
1. Open an HTML file in their browser
2. Drag in a file, set a price, click "Deploy"
3. Share an IPFS link
4. Leave their browser open to serve unlimited automated sales

And a buyer can:
1. Visit an IPFS-hosted webpage
2. Click "Buy" and approve in MetaMask
3. Receive the decrypted file in ~25 seconds

No accounts. No registration. No intermediary. No fees beyond gas.

---

## 2. Related Work

### 2.1 Fair Exchange Protocols

The problem of exchanging a digital good for payment without trusted intermediaries is a classical challenge in cryptography. Pagnia and Gärtner (1999) proved that fair exchange without a trusted third party is impossible in the general case. However, a blockchain provides a *programmable trusted third party* — it cannot be bribed, it cannot go offline, and it executes code deterministically. This observation, formalized by Bentov and Kumaresan (2014), enables fair exchange protocols that would be impossible in a purely peer-to-peer setting.

CryptoVend's use of ECIES key transport and on-chain key commitments builds on this foundation. The smart contract acts as the neutral arbiter: it holds funds until the seller delivers a verifiably correct key.

### 2.2 Decentralized Storage

IPFS (Benet, 2014) provides content-addressed storage where the hash of the content serves as its address. This ensures integrity (any modification changes the address) and enables distributed hosting (any node with the content can serve it). CryptoVend stores both the encrypted file and the buyer page on IPFS, making the system resilient to server failures.

Filecoin and Arweave provide paid permanent storage, but for CryptoVend's use case, IPFS pinning services (Web3.Storage, Pinata) with free tiers are sufficient — the encrypted file and buyer page together are typically under 100MB.

### 2.3 Layer 2 Scaling

Optimistic rollups (Arbitrum, Optimism) and zk-rollups (zkSync, StarkNet) batch hundreds of transactions into a single Ethereum transaction, inheriting Ethereum's security while reducing costs by 100-1000×. CryptoVend targets optimistic rollups for their EVM compatibility — the same Solidity contract deploys without modification on Arbitrum, Base, or Optimism.

### 2.4 Existing Decentralized Marketplaces

OpenSea and Rarible handle NFT sales but require minting and don't support arbitrary file delivery. Filecoin-based marketplaces (Estuary, Lighthouse) focus on storage rather than commerce. Silk Road-era darknet markets demonstrated decentralized commerce but relied on centralized escrow. CryptoVend differs in being:
- **Serverless**: No infrastructure beyond two HTML files
- **File-agnostic**: Sells any digital file, not just NFTs
- **Layer 2-native**: Economically viable for small transactions

---

## 3. System Architecture

### 3.1 Overview

CryptoVend consists of three components:

1. **Seller SAP** (`seller.html`): A Single Application Page that runs locally in the seller's browser. It handles file encryption, contract deployment, IPFS pinning, and automated key delivery.

2. **Buyer Page** (generated, IPFS-hosted): A self-contained HTML page pinned to IPFS that enables payment and in-browser file decryption. Generated dynamically by the seller SAP with embedded configuration (contract address, ABI, CIDs).

3. **CryptoVendL2 Contract** (Solidity, on-chain): A smart contract deployed on an L2 network that handles payment escrow, key delivery, and refund logic.

### 3.2 Protocol Flow

```
Phase 1: Setup (Seller)
━━━━━━━━━━━━━━━━━━━━━━━
1. Seller opens seller.html, connects MetaMask
2. Seller selects a file, chooses L2 network, sets price
3. Browser generates random AES-256 key K
4. Browser computes commitment C = keccak256(K)
5. Browser encrypts file: E = AES-GCM(K, file)
6. Browser uploads E to IPFS → fileCID
7. Browser deploys CryptoVendL2(price, C, fileCID, ...) → contractAddress
8. Browser generates buyer page HTML with embedded config
9. Browser uploads buyer page to IPFS → buyerPageCID
10. Browser updates contract: buyerPageCID
11. Seller shares buyerPageCID link

Phase 2: Purchase (Buyer)
━━━━━━━━━━━━━━━━━━━━━━━
12. Buyer visits IPFS gateway / buyerPageCID
13. Buyer connects MetaMask, switches to correct L2
14. Buyer's browser generates ECIES keypair: (sk_b, pk_b)
15. Buyer calls contract.purchase(pk_b) with msg.value >= price
16. Contract emits PurchaseRequested(id, buyer, pk_b, amount)
17. Contract stores purchase record

Phase 3: Delivery (Seller, automated)
━━━━━━━━━━━━━━━━━━━━━━━
18. Seller's watcher detects PurchaseRequested event
19. Seller's browser computes encK = ECIES.encrypt(pk_b, K)
20. Seller calls contract.deliverKey(id, encK)
21. Contract emits KeyDelivered(id, buyer, encK)

Phase 4: Decryption (Buyer)
━━━━━━━━━━━━━━━━━━━━━━━
22. Buyer's page detects KeyDelivered event
23. Buyer's browser computes K = ECIES.decrypt(sk_b, encK)
24. Buyer's browser fetches E from IPFS
25. Buyer's browser decrypts file = AES-GCM.decrypt(K, E)
26. File downloads to buyer's computer
```

### 3.3 Cryptographic Primitives

**AES-256-GCM** (file encryption): We use the browser's SubtleCrypto API for authenticated encryption. GCM mode provides both confidentiality and integrity — any tampering with the encrypted file is detected during decryption. The 12-byte IV is randomly generated and prepended to the ciphertext.

**ECIES over secp256k1** (key transport): The buyer generates a fresh secp256k1 keypair for each purchase. The seller encrypts the 32-byte AES key with the buyer's public key using ECIES:
1. Generate ephemeral keypair (eph_sk, eph_pk)
2. Compute shared secret S = ECDH(eph_sk, buyer_pk)
3. Derive AES key D = SHA-256(S.x)
4. Encrypt: ct = AES-256-GCM(D, K)
5. Output: [eph_pk || iv || tag || ct]

**keccak256** (key commitment): The hash of the AES key is stored in the contract at deployment. The buyer can verify that the delivered key is correct by checking `keccak256(received_key) == on-chain commitment`.

### 3.4 Smart Contract Design

The CryptoVendL2 contract is optimized for Layer 2 execution:

- **Immutables**: seller address, price, and key commitment are stored in bytecode (free to read on L2)
- **Minimal storage**: Purchase records use packed structs with uint64/uint128 fields
- **Event-driven**: Large data (public keys, encrypted keys) is stored in events and minimal storage mappings
- **Refund mechanism**: Buyers can reclaim funds if the seller fails to deliver within REFUND_WINDOW (1 hour)

### 3.5 IPFS Integration

Both the encrypted file and the buyer page are pinned to IPFS. The system supports two pinning backends:

1. **Web3.Storage API**: Cloud-based pinning with a generous free tier (5GB). Upload via HTTP POST.
2. **Local IPFS daemon**: For privacy-conscious sellers who prefer self-hosting.

The buyer page is a self-contained HTML file that loads ethers.js and noble-secp256k1 from CDNs. It requires no backend — all logic runs in the buyer's browser.

---

## 4. Security Analysis

### 4.1 Confidentiality

The AES key K never appears on-chain in cleartext. The contract stores only keccak256(K), which is computationally irreversible. Each buyer receives K encrypted specifically to their ECIES public key; decryption requires their private key, which never leaves their browser.

**Theorem**: An adversary observing all on-chain data and IPFS content cannot recover the file contents without either (a) the AES key K, (b) a buyer's ECIES private key, or (c) breaking AES-256-GCM or the secp256k1 discrete logarithm problem.

### 4.2 Integrity

AES-GCM provides authenticated encryption. If the encrypted file is modified on IPFS (which would require a different CID, detectable by the buyer), decryption fails. The IPFS CID itself is a cryptographic hash, providing content integrity.

### 4.3 Fairness

The protocol achieves conditional fairness:
- **If the seller is online**: The buyer pays, receives the key within seconds, and decrypts the file. Fair exchange is achieved.
- **If the seller is offline**: The buyer's payment is held by the contract. After REFUND_WINDOW (1 hour), the buyer can reclaim their funds. The buyer loses time but not money.

### 4.4 Non-Repudiation

The key commitment provides non-repudiation for the seller: if the delivered key's hash does not match the on-chain commitment, the buyer has cryptographic proof of fraud. The blockchain's immutability ensures this proof is permanent.

### 4.5 Known Limitations

1. **Seller uptime**: The seller must be online to deliver keys. This is the primary limitation (see Section 6).
2. **No content verification before purchase**: The buyer cannot verify the file's content before paying. The key commitment proves the *correct* key was delivered, but not that the underlying file is valuable.
3. **Key commitment leaks hash**: An adversary who can guess the AES key (e.g., if it's derived from weak randomness) can verify their guess against the on-chain commitment. We mitigate this by using 256-bit keys from crypto.getRandomValues (CSPRNG).
4. **Front-running**: On networks without MEV protection, a front-runner could observe a pending purchase transaction and submit their own first. However, the economic incentive is low (the front-runner would pay for a file they may not want), and L2 sequencers generally provide ordering guarantees.

---

## 5. Economic Analysis

### 5.1 Cost Structure

On Layer 2 networks, the dominant cost is calldata submission to Ethereum L1. We measured gas costs on Arbitrum Sepolia (testnet) and extrapolated to mainnet:

| Operation | Gas Used | Arbitrum Cost | Base Cost | Ethereum L1 Cost |
|-----------|---------|---------------|-----------|------------------|
| Deploy | ~750,000 | ~$0.15 | ~$0.08 | ~$67.50 |
| Purchase | ~95,000 | ~$0.02 | ~$0.01 | ~$8.55 |
| deliverKey | ~62,000 | ~$0.013 | ~$0.007 | ~$5.58 |
| **Total per sale** | **~157,000** | **~$0.033** | **~$0.017** | **~$14.13** |

The cost reduction from L1 to L2 is approximately **430× on Arbitrum** and **830× on Base**.

### 5.2 Comparison with Centralized Alternatives

| Platform | Fee per $10 sale | Seller requirements |
|---------|-----------------|-------------------|
| Gumroad | $1.09 (10% + $0.09) | Account, identity, bank |
| Stripe/Shopify | $0.59 (2.9% + $0.30) | Account, identity, bank, website |
| Apple App Store | $3.00 (30%) | Developer account ($99/yr), review |
| **CryptoVend (Base)** | **~$0.02** | **MetaMask wallet, browser** |

### 5.3 Minimum Viable Price

For a transaction overhead target of 5%:
- On Base: minimum file price = $0.02 / 0.05 = **$0.40**
- On Arbitrum: minimum file price = $0.033 / 0.05 = **$0.66**
- On Ethereum L1: minimum file price = $14.13 / 0.05 = **$282.60**

Layer 2 makes micro-transactions viable; Ethereum L1 does not.

---

## 6. The Seller-Online Problem

### 6.1 Statement

CryptoVend requires the seller's browser to be running to detect purchase events and deliver encrypted keys. If the seller's computer is off, the buyer waits (up to REFUND_WINDOW, then can reclaim funds).

This is the honest elephant in the room. It means CryptoVend, in its current form, is not a "set it and forget it" system. The seller must be present (or have a delegate present).

### 6.2 Mitigations

**Short-term** (implemented):
- Refund mechanism protects buyers from permanently losing funds
- Polling backup catches missed events when the seller's tab was briefly backgrounded

**Medium-term** (engineering work):
- Run seller.html in a headless browser on a VPS ($5/month)
- Use a serverless function (AWS Lambda) to watch events and deliver keys
- Multiple watcher instances for redundancy

**Long-term** (research directions):

**Threshold Cryptography**: The AES key K is split into N shares using Shamir's Secret Sharing, distributed across N independent nodes. Any t shares (t < N) can reconstruct K. When a purchase is verified on-chain, each node independently delivers its share encrypted to the buyer. The buyer combines t shares to recover K. No single node knows K. No seller needs to be online.

**Lit Protocol PKPs**: Store the AES key in a Programmable Key Pair managed by Lit Protocol's decentralized node network. Configure an access control condition: "release the key if the buyer has paid on contract X." The Lit nodes collectively verify the condition and release the key — fully automated, fully decentralized.

**TEE-based Key Servers**: Run the key delivery logic inside a Trusted Execution Environment (Intel SGX, ARM TrustZone). The TEE watches for purchase events and delivers keys automatically. The seller provisions the AES key once and walks away.

### 6.3 Perspective

The seller-online requirement is not unique to CryptoVend. It's inherent to any system where a secret (the AES key) exists outside the blockchain. The blockchain can enforce payment rules, but it cannot store and release secrets conditionally — that requires an oracle or key management system. CryptoVend's contribution is making the rest of the system as simple as possible (two HTML files), so that the seller-online problem is the *only* remaining challenge.

---

## 7. Implementation

The system is implemented in three files:

1. **`seller.html`** (~900 lines): A single-page application using vanilla JavaScript, ethers.js v6, and noble-secp256k1. Handles: MetaMask connection, file encryption (SubtleCrypto AES-GCM), contract deployment (ethers.ContractFactory), IPFS pinning (Web3.Storage API or local daemon), buyer page generation (template literals), and purchase event watching (ethers.Contract.on + polling).

2. **`contracts/CryptoVendL2.sol`** (~220 lines): Solidity 0.8.24 contract with: purchase() for buyer payment + ECIES pubkey submission, deliverKey() for seller key delivery, refund() for buyer protection, withdraw() for seller fund retrieval, and admin functions for pausing and metadata updates.

3. **Buyer page** (generated, ~250 lines): A self-contained HTML file generated by seller.html with embedded configuration. Pinned to IPFS. Handles: MetaMask connection, ECIES keypair generation, payment, key receipt, IPFS file download, and AES-GCM decryption.

No build tools, no package managers, no frameworks, no servers.

---

## 8. Conclusion

CryptoVend demonstrates that trustless digital file commerce can be achieved with remarkable simplicity: two HTML files and a smart contract. By leveraging browser-native cryptography (SubtleCrypto, noble-secp256k1), Ethereum Layer 2 networks (Arbitrum, Base), and content-addressed storage (IPFS), we eliminate the need for servers, intermediaries, and trust.

The system achieves:
- **Security**: AES-256-GCM encryption, ECIES key transport, on-chain key commitments
- **Economy**: Under $0.05 total cost per sale on Layer 2
- **Simplicity**: Zero server infrastructure; two HTML files do everything
- **Buyer protection**: Time-locked refund mechanism

The primary limitation — the seller-online requirement — is honestly acknowledged and has clear paths to resolution via threshold cryptography, decentralized key management (Lit Protocol), or TEE-based automation.

We believe CryptoVend represents the minimal viable architecture for decentralized file sales: anything simpler would sacrifice security, and anything more complex would sacrifice the radical simplicity that makes the system practical.

---

## References

1. Benet, J. (2014). "IPFS - Content Addressed, Versioned, P2P File System." arXiv:1407.3561.
2. Bentov, I., & Kumaresan, R. (2014). "How to Use Bitcoin to Design Fair Protocols." CRYPTO 2014.
3. Pagnia, H., & Gärtner, F.C. (1999). "On the Impossibility of Fair Exchange without a Trusted Third Party." Technical Report TUD-BS-1999-02.
4. Kalodner, H., et al. (2018). "Arbitrum: Scalable, private smart contracts." USENIX Security.
5. W3C. (2017). "Web Cryptography API." W3C Recommendation.
6. Shoup, V. (2001). "A Proposal for an ISO Standard for Public Key Encryption." IACR ePrint 2001/112.

---

## Appendix A: Contract ABI

```json
[
  "constructor(uint256 _price, bytes32 _keyCommitment, string _fileCID, string _buyerPageCID, string _fileMetadata)",
  "function purchase(bytes pubKey) payable",
  "function deliverKey(uint64 purchaseId, bytes encKey)",
  "function refund(uint64 purchaseId)",
  "function withdraw()",
  "function getPurchase(uint64 id) view returns (address, uint64, uint128, bool, bool)",
  "function getEncryptedKey(uint64 id) view returns (bytes)",
  "event PurchaseRequested(uint64 indexed purchaseId, address indexed buyer, bytes buyerPublicKey, uint128 amount)",
  "event KeyDelivered(uint64 indexed purchaseId, address indexed buyer, bytes encryptedKey)",
  "event RefundIssued(uint64 indexed purchaseId, address indexed buyer, uint128 amount)"
]
```

## Appendix B: Encrypted File Format

```
Byte layout of encrypted file uploaded to IPFS:

Offset  Length  Field
──────  ──────  ─────
0       4       nameLen (uint32, little-endian): length of original filename
4       N       name (UTF-8): original filename
4+N     12      iv: AES-GCM initialization vector
4+N+12  M       ciphertext: AES-GCM encrypted file content + 16-byte auth tag
```

## Appendix C: ECIES Ciphertext Format

```
Byte layout of ECIES-encrypted AES key (delivered on-chain):

Offset  Length  Field
──────  ──────  ─────
0       65      ephemeral public key (uncompressed secp256k1: 0x04 || x || y)
65      16      AES-GCM IV
81      16      AES-GCM authentication tag
97      32      ciphertext (encrypted 32-byte AES key)
```
