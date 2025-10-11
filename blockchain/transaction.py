# Import required libraries for transaction functionality
import time
import hashlib
import json
import uuid
from typing import Dict, Any


class Transaction:
    """
    Transaction Class for Blockchain Transactions

    Represents a single transaction in the blockchain with cryptographic
    integrity verification through hash computation.

    Attributes:
        sender: Sender's wallet address
        receiver: Receiver's wallet address
        amount: Transaction amount
        timestamp: Transaction creation time
        id: Unique transaction identifier (hash)
    """

    def __init__(self, sender: str, receiver: str, amount: float, timestamp: int = None, txid: str = None):
        """
        Initialize a new transaction

        Args:
            sender: Sender's wallet address
            receiver: Receiver's wallet address
            amount: Transaction amount
            timestamp: Optional custom timestamp (defaults to current time)
            txid: Optional custom transaction ID (defaults to computed hash)
        """
        self.sender = sender
        self.receiver = receiver
        self.amount = float(amount)
        self.timestamp = timestamp if timestamp is not None else int(time.time())
        self.id = txid if txid else self._compute_hash()

    def _compute_hash(self) -> str:
        """
        Compute SHA-256 hash of transaction data

        Creates a unique identifier for the transaction based on its contents.
        This ensures transaction integrity and prevents tampering.

        Returns:
            str: 64-character hexadecimal hash
        """
        # Create payload dictionary for hashing
        payload = {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp
        }
        # Convert to JSON string and compute hash
        tx_string = json.dumps(payload, sort_keys=True).encode()
        return hashlib.sha256(tx_string).hexdigest()

    @staticmethod
    def from_dict(tx_data: Dict[str, Any]) -> 'Transaction':
        """
        Create Transaction object from dictionary data

        Used for deserializing transaction data received from network
        or loaded from storage.

        Args:
            tx_data: Dictionary containing transaction data

        Returns:
            Transaction: Reconstructed Transaction object
        """
        return Transaction(
            sender=tx_data['sender'],
            receiver=tx_data['receiver'],
            amount=tx_data['amount'],
            timestamp=tx_data.get('timestamp'),
            txid=tx_data.get('id')
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert transaction to dictionary for serialization

        Prepares transaction data for network transmission or storage
        by converting all attributes to serializable format.

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
        """Human-readable string representation for debugging"""
        return f"Tx({self.sender[:6]}→{self.receiver[:6]} ${self.amount} id={self.id[:8]}...)"


class DoubleSpendTransaction:
    """
    Special transaction class for double spending attack demonstration.

    Creates two transactions with same timestamp - one to victim and one to attacker's shadow wallet.
    This demonstrates the core mechanism of double spending attacks in blockchain.
    """

    def __init__(self, attacker_addr: str, victim_addr: str, amount: float):
        """
        Initialize double spending transaction pair

        Args:
            attacker_addr: Attacker's wallet address
            victim_addr: Victim's wallet address
            amount: Amount to double spend
        """
        self.attacker_addr = attacker_addr
        self.victim_addr = victim_addr
        self.amount = float(amount)
        self.timestamp = int(time.time())  # Same timestamp for both transactions

        # Create the two double spending transactions
        self.honest_tx = self._create_honest_transaction()
        self.malicious_tx = self._create_malicious_transaction()

    def _create_honest_transaction(self) -> Transaction:
        """Create transaction to victim (honest transaction)"""
        return Transaction(
            sender=self.attacker_addr,
            receiver=self.victim_addr,
            amount=self.amount,
            timestamp=self.timestamp,
            txid=f"honest_{self.timestamp}_{uuid.uuid4().hex[:8]}"
        )

    def _create_malicious_transaction(self) -> Transaction:
        """Create transaction to attacker's shadow wallet (malicious transaction)"""
        shadow_wallet = f"{self.attacker_addr}_shadow"
        return Transaction(
            sender=self.attacker_addr,
            receiver=shadow_wallet,
            amount=self.amount,
            timestamp=self.timestamp,  # Same timestamp as honest transaction
            txid=f"malicious_{self.timestamp}_{uuid.uuid4().hex[:8]}"
        )

    def get_both_transactions(self) -> Dict[str, Transaction]:
        """Get both transactions for double spending attack"""
        return {
            "honest_to_victim": self.honest_tx,
            "malicious_to_shadow": self.malicious_tx
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert both transactions to dictionary for analysis"""
        return {
            "double_spend_attack": {
                "attacker": self.attacker_addr,
                "victim": self.victim_addr,
                "amount": self.amount,
                "timestamp": self.timestamp,
                "transactions": {
                    "honest_to_victim": self.honest_tx.to_dict(),
                    "malicious_to_shadow": self.malicious_tx.to_dict()
                }
            }
        }

    def __repr__(self):
        """Human-readable representation of double spend transaction"""
        return (f"DoubleSpend(attacker={self.attacker_addr[:6]}, "
                f"victim={self.victim_addr[:6]}, amount={self.amount}, "
                f"timestamp={self.timestamp})")


def create_double_spend_demonstration(attacker_addr: str, victim_addr: str, amount: float) -> Dict[str, Any]:
    """
    Create a complete double spending demonstration with both transactions.

    This function demonstrates the double spending attack scenario by creating
    two conflicting transactions and providing detailed analysis.

    Args:
        attacker_addr: Attacker's wallet address
        victim_addr: Victim's wallet address
        amount: Amount to double spend

    Returns:
        Dict with complete double spending demonstration data
    """
    print("=" * 60)
    print("DOUBLE SPENDING DEMONSTRATION")
    print("=" * 60)

    # Create double spend transaction pair
    double_spend = DoubleSpendTransaction(attacker_addr, victim_addr, amount)
    transactions = double_spend.get_both_transactions()

    # Display transaction details for educational purposes
    print("📋 Transaction Details:")
    print(f"   Attacker: {attacker_addr}")
    print(f"   Victim: {victim_addr}")
    print(f"   Amount: {amount} coins")
    print(f"   Timestamp: {double_spend.timestamp}")
    print()

    print("🔄 Double Spending Transactions:")
    print("   1. Honest Transaction (to Victim):")
    honest_tx = transactions["honest_to_victim"]
    print(f"      From: {honest_tx.sender}")
    print(f"      To: {honest_tx.receiver}")
    print(f"      Amount: {honest_tx.amount}")
    print(f"      TX ID: {honest_tx.id[:16]}...")
    print()

    print("   2. Malicious Transaction (to Shadow Wallet):")
    malicious_tx = transactions["malicious_to_shadow"]
    print(f"      From: {malicious_tx.sender}")
    print(f"      To: {malicious_tx.receiver}")
    print(f"      Amount: {malicious_tx.amount}")
    print(f"      TX ID: {malicious_tx.id[:16]}...")
    print()

    print("🔍 Double Spending Analysis:")
    print(f"   Same Sender: {honest_tx.sender == malicious_tx.sender}")
    print(f"   Same Amount: {honest_tx.amount == malicious_tx.amount}")
    print(f"   Same Timestamp: {honest_tx.timestamp == malicious_tx.timestamp}")
    print(f"   Different Receivers: {honest_tx.receiver != malicious_tx.receiver}")
    print()

    # Create comprehensive demonstration data structure
    demonstration_data = {
        "demonstration_type": "double_spending",
        "attack_scenario": "Attacker attempts to spend same coins twice",
        "timestamp": double_spend.timestamp,
        "participants": {
            "attacker": attacker_addr,
            "victim": victim_addr,
            "shadow_wallet": f"{attacker_addr}_shadow"
        },
        "transactions": {
            "transaction_1": {
                "type": "honest",
                "purpose": "Payment to victim for goods/services",
                "transaction": honest_tx.to_dict()
            },
            "transaction_2": {
                "type": "malicious",
                "purpose": "Double spend to attacker's shadow wallet",
                "transaction": malicious_tx.to_dict()
            }
        },
        "double_spend_indicators": {
            "same_sender": True,
            "same_amount": True,
            "same_timestamp": True,
            "different_receivers": True,
            "conflicting_transactions": True
        },
        "attack_workflow": [
            "1. Attacker sends honest transaction to victim",
            "2. Victim accepts payment and provides goods/services",
            "3. Attacker simultaneously sends malicious transaction to shadow wallet",
            "4. Attacker mines private blocks containing malicious transaction",
            "5. Attacker broadcasts longer private chain to overwrite honest transaction"
        ]
    }

    return demonstration_data


def validate_double_spend_transactions(tx1: Transaction, tx2: Transaction) -> Dict[str, Any]:
    """
    Validate if two transactions constitute a double spending attempt.

    This function analyzes two transactions to detect double spending patterns
    by comparing sender, amount, timestamp, and receiver addresses.

    Args:
        tx1: First transaction
        tx2: Second transaction

    Returns:
        Dict with validation results and analysis
    """
    analysis = {
        "is_double_spend": False,
        "reasons": [],
        "similarities": {},
        "differences": {}
    }

    # Check for double spend indicators
    if tx1.sender == tx2.sender:
        analysis["similarities"]["same_sender"] = True
        if tx1.amount == tx2.amount:
            analysis["similarities"]["same_amount"] = True
            if tx1.timestamp == tx2.timestamp:
                analysis["similarities"]["same_timestamp"] = True
                if tx1.receiver != tx2.receiver:
                    analysis["similarities"]["different_receivers"] = True
                    analysis["is_double_spend"] = True
                    analysis["reasons"].append("Same sender spending same amount to different receivers at same time")

    # Additional checks for transaction identity
    if tx1.id == tx2.id:
        analysis["is_double_spend"] = True
        analysis["reasons"].append("Same transaction ID")

    # Record differences for analysis
    analysis["differences"]["receivers"] = f"{tx1.receiver} vs {tx2.receiver}"
    analysis["differences"]["transaction_ids"] = f"{tx1.id[:8]}... vs {tx2.id[:8]}..."

    return analysis


def generate_double_spend_report(attacker_addr: str, victim_addr: str, amount: float) -> Dict[str, Any]:
    """
    Generate a comprehensive double spending report for analysis.

    Creates a complete report including demonstration, validation results,
    risk assessment, and recommendations for double spending prevention.

    Args:
        attacker_addr: Attacker's wallet address
        victim_addr: Victim's wallet address
        amount: Double spend amount

    Returns:
        Comprehensive double spending report
    """
    # Generate demonstration and validation data
    demonstration = create_double_spend_demonstration(attacker_addr, victim_addr, amount)
    double_spend = DoubleSpendTransaction(attacker_addr, victim_addr, amount)
    transactions = double_spend.get_both_transactions()

    validation = validate_double_spend_transactions(
        transactions["honest_to_victim"],
        transactions["malicious_to_shadow"]
    )

    # Create comprehensive report structure
    report = {
        "report_type": "double_spending_analysis",
        "generated_at": int(time.time()),
        "demonstration": demonstration,
        "validation_results": validation,
        "risk_assessment": {
            "risk_level": "HIGH" if validation["is_double_spend"] else "LOW",
            "vulnerability": "Double spending attack possible",
            "recommendations": [
                "Wait for multiple confirmations before accepting large payments",
                "Monitor for transactions with same sender and amount",
                "Implement double spend detection in transaction validation",
                "Use longer confirmation times for high-value transactions"
            ]
        },
        "transaction_analysis": {
            "total_transactions": 2,
            "conflicting_pairs": 1,
            "double_spend_detected": validation["is_double_spend"],
            "detection_confidence": "HIGH" if validation["is_double_spend"] else "LOW"
        }
    }

    return report