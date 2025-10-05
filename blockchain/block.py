# block.py
"""
Block module for the blockchain system.

This module defines the Block class which represents a single block in the blockchain.
Each block contains transactional data, cryptographic hashes for chain integrity,
and proof-of-work components. Blocks are linked together through cryptographic hashes
to form an immutable chain.

Key Features:
- Block creation and initialization
- Cryptographic hash computation using SHA-256
- Serialization to/from dictionary format for storage and transmission
- Transaction management within blocks
- Proof-of-work support through nonce values
"""

import json
import hashlib
from typing import List, Dict, Any
from .transaction import Transaction  # Import Transaction class to store transactions inside blocks


class Block:
    """
    Represents a single block in the blockchain.

    Each block contains:
    - Index (position in chain)
    - Timestamp (when created)
    - List of transactions
    - Previous block's hash (for chain linking)
    - Nonce (for proof-of-work)
    - Its own hash (calculated from contents)

    The block uses cryptographic hashing to maintain integrity and links to the
    previous block to form an immutable chain structure.
    """

    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str, timestamp: int = None,
                 nonce: int = 0):
        """
        Initialize a new Block.

        Args:
            index (int): Block number in the chain (starts from 0 for genesis block)
            transactions (List[Transaction]): List of transactions in this block
            previous_hash (str): Hash of the previous block in chain
            timestamp (int, optional): When block was created. Defaults to current time.
            nonce (int, optional): Number used in mining. Defaults to 0.
        """
        # Block number in the chain (starts from 0 for genesis block)
        self.index = index

        # Store the time block was created. If not given, use current system time
        self.timestamp = timestamp if timestamp is not None else int(__import__("time").time())

        # Copy the list of transactions (avoid modifying the original one)
        self.transactions = transactions[:]

        # Hash of the previous block (to link blocks together like a chain)
        self.previous_hash = previous_hash

        # Nonce is a number used in mining (proof of work)
        self.nonce = int(nonce)

        # Each block has its own unique hash based on its content
        self.hash = self.compute_hash()

    @staticmethod
    def from_dict(block_data: Dict[str, Any]) -> 'Block':
        """
        Create a Block object from dictionary data (used when receiving blocks from network).

        This method reconstructs a Block object from serialized dictionary data,
        typically received over the network or loaded from storage. It preserves
        the original hash without recalculation to maintain data integrity.

        Args:
            block_data (Dict): Dictionary containing block information with keys:
                - index: Block position in chain
                - transactions: List of transaction dictionaries
                - previous_hash: Hash of previous block
                - timestamp: Block creation time
                - nonce: Proof-of-work nonce value
                - hash: Block's cryptographic hash

        Returns:
            Block: Reconstructed Block object with original hash preserved
        """
        # Convert transaction data from dicts back into Transaction objects
        transactions = [Transaction.from_dict(tx_data) for tx_data in block_data['transactions']]

        # Create a Block using provided data
        block = Block(
            index=block_data['index'],
            transactions=transactions,
            previous_hash=block_data['previous_hash'],
            timestamp=block_data['timestamp'],
            nonce=block_data['nonce']
        )

        # Assign the hash directly (do not recalculate, to keep it same as original)
        block.hash = block_data['hash']
        return block

    def compute_hash(self) -> str:
        """
        Calculate the SHA-256 hash of the block's contents.

        The hash is computed from a JSON-serialized representation of the block's
        core data including index, timestamp, transactions, previous hash, and nonce.
        This hash serves as the block's unique identifier and integrity check.

        Returns:
            str: 64-character hexadecimal hash string representing the block's contents
        """
        # Create a dictionary with block information
        payload = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [t.to_dict() for t in self.transactions],  # convert transactions to dicts
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }

        # Convert payload to JSON string and encode into bytes
        block_string = json.dumps(payload, sort_keys=True).encode()

        # Return SHA-256 hash of the block string
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert block to dictionary for JSON serialization.

        This method prepares the block data for network transmission or storage
        by converting all attributes to a dictionary format. The resulting
        dictionary can be easily serialized to JSON.

        Returns:
            Dict: Block data as dictionary with keys:
                - index: Block position in chain
                - timestamp: Block creation time
                - transactions: List of transaction dictionaries
                - previous_hash: Hash of previous block
                - nonce: Proof-of-work nonce value
                - hash: Block's cryptographic hash
        """
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [t.to_dict() for t in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }

    def __repr__(self):
        """
        String representation of the block for debugging.

        Provides a concise, human-readable summary of the block's key attributes
        including index, transaction count, nonce, and a truncated hash for quick
        identification during debugging.

        Returns:
            str: Human-readable block description in format:
                 "Block(idx={index} txs={tx_count} nonce={nonce} hash={hash_prefix}...)"
        """
        return f"Block(idx={self.index} txs={len(self.transactions)} nonce={self.nonce} hash={self.hash[:10]}...)"