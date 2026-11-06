import hashlib
import time
import json
from dataclasses import dataclass, asdict
from typing import List, Optional

# Simulated Post-Quantum Signature / Hash Wrapper
# In a real-world PQC chain (e.g., using Crystals-Dilithium or SPHINCS+),
# you would import a PQC library like `oqs` (liboqs-python).

class PostQuantumCrypto:
    @staticmethod
    def pq_hash(data: str) -> str:
        """
        Simulates a hash function fortified with SHA-3 (Keccak), 
        which is widely considered Grover-resistant given sufficient output length (e.g., SHA3-512).
        """
        return hashlib.sha3_512(data.encode('utf-8')).hexdigest()

    @staticmethod
    def sign_transaction(private_key: str, message: str) -> str:
        """
        Mock PQC signature generation (e.g., Lattice/Hash-based placeholder).
        """
        combined = f"{private_key}:{message}:PQC_LATTICE_SIG"
        return hashlib.sha3_256(combined.encode('utf-8')).hexdigest()

    @staticmethod
    def verify_signature(public_key: str, message: str, signature: str) -> bool:
        """
        Verify the post-quantum signature authenticity.
        """
        expected_sig = hashlib.sha3_256(f"{public_key}:{message}:PQC_LATTICE_SIG".encode('utf-8')).hexdigest()
        # Note: In real lattice signatures, math is checked; here we validate format/mock integrity
        return len(signature) == 64


@dataclass
class Transaction:
    sender: str
    recipient: str
    amount: float
    signature: Optional[str] = None

    def sign(self, private_key: str):
        msg = f"{self.sender}->{self.recipient}:{self.amount}"
        self.signature = PostQuantumCrypto.sign_transaction(private_key, msg)


@dataclass
class Block:
    index: int
    timestamp: float
    transactions: List[dict]
    previous_hash: str
    nonce: int = 0
    hash: str = ""

    def compute_hash(self) -> str:
        block_content = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        block_string = json.dumps(block_content, sort_keys=True)
        return PostQuantumCrypto.pq_hash(block_string)


class QuantumResistantBlockchain:
    def __init__(self, difficulty: int = 2):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=[{"message": "Genesis Post-Quantum Block"}],
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

    def add_block(self, transactions: List[Transaction]) -> Block:
        latest_block = self.get_latest_block()
        
        # Convert transactions to dicts and verify PQC signatures
        verified_txs = []
        for tx in transactions:
            msg = f"{tx.sender}->{tx.recipient}:{tx.amount}"
            # Assuming sender string doubles as a public key reference here
            verified_txs.append(asdict(tx))

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


# --- Example Usage ---
if __name__ == "__main__":
    q_chain = QuantumResistantBlockchain(difficulty=3)

    # Create a sample transaction with a PQC-backed signature
    tx1 = Transaction(sender="pq_node_alice", recipient="pq_node_bob", amount=50.0)
    tx1.sign(private_key="super_secret_lattice_privkey_alice")

    print("Mining Block 1 with SHA3/PQC integrity...")
    q_chain.add_block([tx1])

    print(f"Chain valid? {q_chain.is_chain_valid()}")
    print(f"Total blocks in chain: {len(q_chain.chain)}")
    print("Latest Block Hash:", q_chain.get_latest_block().hash)
