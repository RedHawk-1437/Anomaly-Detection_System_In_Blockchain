# transaction.py
# This file defines the Transaction class which is used
# to represent a transfer of value between two parties.

import time
import uuid
from typing import Dict, Any


class Transaction:
    def __init__(self, sender: str, receiver: str, amount: float, txid: str = None, timestamp: int = None):
        # Unique transaction ID (if not provided, generate using uuid4)
        self.id = txid or str(uuid.uuid4())

        # Who is sending the money/value
        self.sender = sender

        # Who is receiving the money/value
        self.receiver = receiver

        # Amount of money/value being transferred (always float)
        self.amount = float(amount)

        # When the transaction was created (use current time if not provided)
        self.timestamp = int(time.time()) if timestamp is None else int(timestamp)

    @staticmethod
    def from_dict(tx_data: Dict[str, Any]) -> 'Transaction':
        # Create a Transaction object from a dictionary (used when receiving data from peers)
        return Transaction(
            sender=tx_data['sender'],
            receiver=tx_data['receiver'],
            amount=tx_data['amount'],
            txid=tx_data['id'],
            timestamp=tx_data['timestamp']
        )

    def to_dict(self) -> Dict[str, Any]:
        # Convert a Transaction object into a dictionary (used for APIs or saving)
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp
        }

    def __repr__(self):
        # Friendly string representation of transaction (useful for debugging)
        return f"Transaction({self.sender}->{self.receiver} : {self.amount} id={self.id[:8]})"