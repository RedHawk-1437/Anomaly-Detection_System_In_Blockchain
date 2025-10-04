# transaction.py
# This file defines the Transaction class used to represent financial transactions
# between participants in the blockchain network.


import time
import hashlib
import json
from typing import Dict, Any


class Transaction:
    """
    Represents a single transaction in the blockchain.

    A transaction records the transfer of coins from one wallet to another.
    Each transaction has a unique ID and is immutable once created.
    """

    def __init__(self, sender: str, receiver: str, amount: float, timestamp: int = None, txid: str = None):
        """
        Initialize a new Transaction.

        Args:
            sender (str): Wallet address of the sender
            receiver (str): Wallet address of the receiver
            amount (float): Amount of coins to transfer
            timestamp (int, optional): When transaction was created. Defaults to current time.
            txid (str, optional): Transaction ID. If not provided, will be generated.
        """
        # Sender's wallet address (who is sending coins)
        self.sender = sender

        # Receiver's wallet address (who is receiving coins)
        self.receiver = receiver

        # Amount of coins being transferred
        self.amount = float(amount)

        # When the transaction was created (Unix timestamp)
        self.timestamp = timestamp if timestamp is not None else int(time.time())

        # Unique transaction ID - if not provided, generate one based on content
        self.id = txid if txid else self._compute_hash()

    def _compute_hash(self) -> str:
        """
        Calculate a unique hash for this transaction based on its content.

        Returns:
            str: SHA-256 hash of the transaction data
        """
        # Create a dictionary with transaction information
        payload = {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp
        }

        # Convert to JSON string and encode to bytes
        tx_string = json.dumps(payload, sort_keys=True).encode()

        # Return SHA-256 hash of the transaction data
        return hashlib.sha256(tx_string).hexdigest()

    @staticmethod
    def from_dict(tx_data: Dict[str, Any]) -> 'Transaction':
        """
        Create a Transaction object from dictionary data.
        Used when receiving transactions from network or loading from storage.

        Args:
            tx_data (Dict): Dictionary containing transaction information

        Returns:
            Transaction: Reconstructed Transaction object
        """
        return Transaction(
            sender=tx_data['sender'],
            receiver=tx_data['receiver'],
            amount=tx_data['amount'],
            timestamp=tx_data.get('timestamp'),  # Use provided timestamp or None
            txid=tx_data.get('id')  # Use provided ID or None (will be generated)
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert transaction to dictionary for JSON serialization.
        Useful for sending over network or saving to file.

        Returns:
            Dict: Transaction data as dictionary
        """
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp
        }

    def __repr__(self):
        """
        String representation of the transaction for debugging.

        Returns:
            str: Human-readable transaction description
        """
        return f"Tx({self.sender[:6]}→{self.receiver[:6]} ${self.amount} id={self.id[:8]}...)"