pip install open-quantum-safe


import hashlib
import time
import json
import oqs
from dataclasses import dataclass, asdict
from typing import List, Optional

# Global Post-Quantum Digital Signature Setting
# ML-DSA-65 (formerly Dilithium3) provides NIST Level 3 security (equivalent to AES-192)
PQC_ALGORITHM = "ML-DSA-65" 

@dataclass
class Transaction:
    sender_public_key: bytes  # Public keys in PQC are large byte arrays
    recipient: str
    amount: float
    signature: Optional[bytes] = None

    def get_message_bytes(self) -> bytes:
        """Serializes transaction data consistently into bytes for signing/verifying."""
        # Hex encode the public key for clean string representation
        pub_key_hex = self.sender_public_key.hex()
        msg = f"{pub_key_hex}->{self.recipient}:{self.amount}"
        return msg.encode('utf-8')

    def sign(self, private_key: bytes):
        """Signs the transaction using the sender's ML-DSA private key."""
        with oqs.Signature(PQC_ALGORITHM) as signer:
            self.signature = signer.sign(self.get_message_bytes(), private_key)

    def to_dict(self) -> dict:
        """Converts data to a serializable dictionary, converting bytes to hex."""
        return {
            "sender_public_key": self.sender_public_key.hex(),
            "recipient": self.recipient,
            "amount": self.amount,
            "signature": self.signature.hex() if self.signature else None
        }


@dataclass
class Block:
    index: int
    timestamp: float
    transactions: List[dict]
    previous_hash: str
    nonce: int = 0
    hash: str = ""

    def compute_hash(self) -> str:
        """Uses Grover-resistant SHA3-512 to hash the block contents."""
        block_content = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        block_string = json.dumps(block_content, sort_keys=True)
        return hashlib.sha3_512(block_string.encode('utf-8')).hexdigest()


class QuantumResistantBlockchain:
    def __init__(self, difficulty: int = 2):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=[{"message": "Genesis Liboqs-Fortified Block"}],
            previous_hash="0" * 128
        )
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def proof_of_work(self, block: Block) -> int:
        block.nonce = 0
        computed_hash = block.compute_hash()
        prefix = '0' * self.difficulty
        while not computed_hash.startswith(prefix):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return block.nonce

    def add_block(self, transactions: List[Transaction]) -> Optional[Block]:
        latest_block = self.get_latest_block()
        verified_txs = []

        # Validate signatures using liboqs before adding to block
        for tx in transactions:
            if not tx.signature:
                print(f"[-] Transaction rejected: Missing PQC signature.")
                return None
                
            with oqs.Signature(PQC_ALGORITHM) as verifier:
                is_valid = verifier.verify(
                    tx.get_message_bytes(), 
                    tx.signature, 
                    tx.sender_public_key
                )
                if not is_valid:
                    print(f"[-] Transaction rejected: Invalid PQC signature.")
                    return None
            
            verified_txs.append(tx.to_dict())

        new_block = Block(
            index=latest_block.index + 1,
            timestamp=time.time(),
            transactions=verified_txs,
            previous_hash=latest_block.hash
        )
        
        self.proof_of_work(new_block)
        new_block.hash = new_block.compute_hash()
        self.chain.append(new_block)
        return new_block

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.compute_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True


# --- Runtime Simulation ---
if __name__ == "__main__":
    print(f"[+] Initializing Blockchain with {PQC_ALGORITHM} signature validation...")
    q_chain = QuantumResistantBlockchain(difficulty=3)

    # 1. Generate real post-quantum keys for Alice using ML-DSA-65
    with oqs.Signature(PQC_ALGORITHM) as signer:
        alice_public_key = signer.generate_keypair()
        alice_private_key = signer.export_secret_key()

    print(f"[+] Alice's PQC Public Key Generated (Length: {len(alice_public_key)} bytes)")

    # 2. Alice creates and signs a transaction to Bob
    tx1 = Transaction(
        sender_public_key=alice_public_key, 
        recipient="pq_node_bob", 
        amount=12.50
    )
    tx1.sign(alice_private_key)
    print("[+] Transaction successfully signed using lattice-based cryptography.")

    # 3. Add to blockchain (triggers real signature verification)
    print("[*] Mining Block 1...")
    mined_block = q_chain.add_block([tx1])

    if mined_block:
        print(f"[+] Block mined successfully! Nonce: {mined_block.nonce}")
        print(f"[+] Blockchain Validation Status: {q_chain.is_chain_valid()}")
        print(f"[+] Current Block Hash: {q_chain.get_latest_block().hash[:32]}...")
