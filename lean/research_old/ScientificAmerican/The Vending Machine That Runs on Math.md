# The Vending Machine That Runs on Math

### *A new system lets anyone sell digital files without a middleman, a server, or a shred of trust — just two web pages and a smart contract*

**By the CryptoVend Project**

---

Imagine walking up to a vending machine. You insert a coin, press a button, and a candy bar drops into the tray. You don't know who owns the machine. You don't need to. The mechanism itself guarantees the deal: money in, candy out.

Now imagine the same thing, but for digital files. You visit a web page. You click "Buy." A dataset, a song, a piece of software downloads to your computer. The seller could be anyone, anywhere in the world. You've never met them. You don't need to trust them. The mathematics of the transaction guarantees that if you pay, you get the file — and if you don't get the file, you get your money back.

This is CryptoVend: a digital vending machine built from nothing but cryptography.

---

## The Problem with Digital Marketplaces

When you buy an e-book on Amazon, a song on iTunes, or a dataset on a research platform, you're not really buying from the creator. You're buying from a *middleman*. Amazon takes a cut. Apple takes 30%. Stock photo sites take 60-85%.

These middlemen exist because digital commerce has a fundamental trust problem. If a seller emails you a file and you send them money, either party can cheat. The seller can send a corrupt file. The buyer can reverse the payment. So we outsource trust to a platform: Amazon guarantees delivery, Stripe guarantees payment, and both charge handsomely for the privilege.

But what if the rules of the transaction could be enforced by mathematics instead of by a corporation?

## Smart Contracts: A Robot Notary

In 2015, the Ethereum blockchain introduced *smart contracts* — programs that run on a global, decentralized computer network. Once deployed, a smart contract executes exactly as written. No one can change it, shut it down, or override its rules. It's like a notary that works 24/7, never takes bribes, and can't be fired.

CryptoVend uses a smart contract as the vending machine's mechanism. Here's how it works, step by step:

**The seller** has a file to sell — say, a proprietary dataset of satellite imagery. She opens a single web page (the "Seller Console") in her browser and drags the file in. The browser generates a random encryption key — a 256-bit number so large that guessing it would take longer than the age of the universe — and uses it to scramble the file into unreadable ciphertext. The encrypted file is uploaded to IPFS, a decentralized storage network where files are addressed by their cryptographic fingerprint.

Then the browser deploys a smart contract onto a blockchain. This contract is the vending machine. It knows the price, it knows the fingerprint of the encrypted file, and it knows the *hash* of the encryption key — a one-way mathematical summary that proves the seller committed to a specific key without revealing it.

Finally, the browser generates a buyer web page — a self-contained HTML file with all the purchase logic built in — and pins it to IPFS as well. The seller shares a link to this page. Her job is done.

**The buyer** clicks the link and lands on a clean, simple page: file name, price, a "Buy" button. He connects his crypto wallet (MetaMask, the browser extension used by over 30 million people) and clicks Buy.

Here's where the cryptography gets clever. Before paying, the buyer's browser generates a *fresh pair of cryptographic keys* — a public key and a private key, mathematically linked. Think of the public key as a padlock that anyone can close, and the private key as the only key that opens it. The buyer sends his public key along with his payment to the smart contract.

The payment triggers an alert on the seller's computer. Her browser sees the buyer's public key, takes the original file encryption key, and *locks it inside the buyer's padlock* — encrypting the encryption key specifically for this buyer. She sends this locked package back to the smart contract.

The buyer's browser picks up the locked package, opens it with his private key, recovers the original encryption key, downloads the encrypted file from IPFS, and decrypts it. The file appears on his computer. The entire process takes about 25 seconds.

## Why This is Remarkable

Several things make this system unusual:

**No server.** The seller's console is an HTML file that runs entirely in the browser. The buyer's page is hosted on IPFS — a peer-to-peer network with no central server. There is no backend, no database, no cloud instance. If the seller's website disappeared tomorrow, the buyer page would still be accessible through IPFS.

**No intermediary.** The smart contract handles the money. IPFS handles the storage. The browser handles the cryptography. No company sits in the middle taking a percentage.

**No trust.** The buyer doesn't need to trust the seller because the encryption key's hash is stored on the blockchain at the moment of deployment. If the seller delivered the wrong key, the buyer could prove it mathematically — the hash wouldn't match. And if the seller goes offline and never delivers the key at all? The smart contract has a built-in refund timer: if the key isn't delivered within one hour, the buyer can reclaim their payment automatically.

**Infinite sales.** Once deployed, the vending machine serves unlimited buyers. Each one gets a uniquely encrypted copy of the key — even if someone intercepted one buyer's encrypted key, they couldn't use it without that buyer's private key.

**Pennies, not dollars.** Here's the kicker: this doesn't run on Ethereum's main network, where a single transaction can cost $10-50. It runs on *Layer 2* networks — platforms like Arbitrum and Base that batch hundreds of transactions together before settling on Ethereum, inheriting its security at a fraction of the cost. On Base, the total cost of a purchase is about two cents. That's cheaper than a credit card transaction.

## The Elephant in the Room

No system is perfect, and CryptoVend has an honest limitation: the seller needs to be online.

When the buyer pays, the seller's computer must be running to detect the purchase and deliver the encrypted key. If the seller's computer is off, the buyer waits. After one hour, the buyer can trigger an automatic refund — so no money is lost, but the sale falls through.

This is inherent to the design: the encryption key exists only on the seller's computer, not on the blockchain. Storing it on the blockchain would make it visible to everyone (blockchain data is public), defeating the purpose.

In a future version, this could be solved with *threshold cryptography* — splitting the key into pieces distributed across a network of independent computers that collectively release it when the payment condition is met, with no single computer able to cheat or access the full key alone.

## The Math Behind the Magic

Three cryptographic primitives make CryptoVend possible:

**AES-256-GCM** encrypts the file. AES (Advanced Encryption Standard) is the same cipher used by governments and banks worldwide. The "256" means the key is 256 bits long — there are more possible keys than atoms in the observable universe. "GCM" (Galois/Counter Mode) adds authentication: if even a single bit of the encrypted file is altered, decryption fails. This prevents tampering.

**ECIES** (Elliptic Curve Integrated Encryption Scheme) handles the key delivery. It's based on the same elliptic curve mathematics that secures Bitcoin and Ethereum. The buyer and seller independently compute a shared secret using only their own private key and the other party's public key — a trick called Diffie-Hellman key exchange. This shared secret is used to encrypt the file key, ensuring only the intended buyer can decrypt it.

**Keccak-256** (the hash function used by Ethereum) provides the key commitment. A hash function turns any input into a fixed-size fingerprint. It's easy to compute the hash of a key, but computationally impossible to reverse — to find the key from its hash. By storing the hash on-chain at deployment, the seller commits to a specific key before any buyer appears.

All of this happens in your browser. No plugins, no downloads, no special software — just the Web Cryptography API that's built into every modern browser, and a lightweight open-source library for elliptic curve operations.

## What Could You Sell?

The system is file-agnostic. Some possibilities:

- **Research data** — a climate scientist sells a curated dataset to other researchers without going through a journal publisher
- **Software licenses** — an indie developer sells activation keys with cryptographic delivery guarantees
- **Digital art** — an artist sells high-resolution files directly to collectors
- **Educational content** — a teacher sells course materials without platform fees
- **Whistleblower documents** — a source sells evidence to a journalist, both remaining pseudonymous
- **Music** — a musician sells studio recordings at $2, keeping $1.98 instead of the $0.30 they'd get from streaming

The minimum viable price point on Layer 2 is about $1 — below that, even the two-cent gas fee becomes a significant percentage. Above $1, the economics are strictly better than any centralized alternative.

## A Glimpse of Trustless Commerce

CryptoVend is a proof of concept, but it illustrates a broader principle: *programmable trust*. When the rules of a transaction can be expressed in code and enforced by a decentralized network, the need for trusted intermediaries diminishes. This doesn't mean intermediaries have no value — they provide curation, customer support, dispute resolution, and discoverability. But for the core transaction — money for file — the mathematics is sufficient.

The vending machine metaphor is apt. A physical vending machine doesn't require a shopkeeper. Its mechanism *is* the shopkeeper: insert coin, receive goods, no trust required. CryptoVend achieves the same thing in the digital realm, using cryptography instead of springs and levers.

The code is open. The math is auditable. The transaction is verifiable. And the whole thing fits in two HTML files.

---

*The CryptoVend project is open-source. The seller console, buyer page template, and smart contract are available at the project repository. The system runs on Arbitrum, Base, and Optimism Layer 2 networks, with testnet support for experimentation.*
