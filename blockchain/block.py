# block.py
# This file defines the Block class used in the blockchain system.
# A Block stores transactions, its own hash, and links to the previous block.

import json
import hashlib
from typing import List, Dict, Any
from .transaction import Transaction   # Import Transaction class to store transactions inside blocks


class Block:
    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str, timestamp: int = None, nonce: int = 0):
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

    # Method to recreate a Block object from dictionary data
    @staticmethod
    def from_dict(block_data: Dict[str, Any]) -> 'Block':
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

    # Method to calculate the block's hash
    def compute_hash(self) -> str:
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

    # Convert block object into a dictionary (useful for sending over network or saving)
    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [t.to_dict() for t in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }

    # String representation of the block (for debugging/printing)
    def __repr__(self):
        return f"Block(idx={self.index} txs={len(self.transactions)} nonce={self.nonce} hash={self.hash[:10]}...)"
