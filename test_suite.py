"""
test_suite.py - Comprehensive Test Suite for Blockchain Anomaly Detection System
FIXED VERSION - Updated error handling test

This test suite validates all components of the Blockchain Anomaly Detection System.
It includes unit tests, integration tests, and performance tests to ensure system reliability.
"""

import unittest
import json
import time
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add the project directory to Python path to import project modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules for testing
from blockchain.blockchain import Blockchain
from blockchain.block import Block
from blockchain.transaction import Transaction, DoubleSpendTransaction
from blockchain.attacker import (
    run_attack,
    simulate_private_mining,
    create_private_network,
    run_double_spending_attack
)
from blockchain.simblock_integration import SimBlockIntegration


class TestBlock(unittest.TestCase):
    """
    Test cases for the Block class functionality.

    This class tests block creation, hash computation, serialization,
    and deserialization to ensure blocks work correctly in the blockchain.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.

        Creates sample transactions and block data that will be used
        in multiple test cases.
        """
        # Create sample transactions for testing
        self.transactions = [
            Transaction("Alice", "Bob", 10.0),
            Transaction("Bob", "Charlie", 5.0)
        ]

        # Create sample block data with realistic values
        self.block_data = {
            "index": 1,
            "transactions": self.transactions,
            "previous_hash": "0" * 64,  # Simulate previous block hash
            "timestamp": int(time.time()),  # Current timestamp
            "nonce": 12345  # Sample nonce for proof of work
        }

    def test_block_creation(self):
        """Test that a block can be created with valid data."""
        # Create block using sample data
        block = Block(**self.block_data)

        # Verify all block properties are set correctly
        self.assertEqual(block.index, 1)
        self.assertEqual(len(block.transactions), 2)
        self.assertEqual(block.previous_hash, "0" * 64)
        self.assertEqual(block.nonce, 12345)
        self.assertIsNotNone(block.hash)  # Hash should be automatically computed

    def test_block_hash_computation(self):
        """Test that block hash computation is correct and consistent."""
        # Create a block and compute its hash
        block = Block(**self.block_data)
        computed_hash = block.compute_hash()

        # Verify the computed hash matches the block's hash
        self.assertEqual(block.hash, computed_hash)
        # Verify hash is proper SHA-256 format (64 characters)
        self.assertEqual(len(computed_hash), 64)

    def test_block_to_dict(self):
        """Test that a block can be properly serialized to a dictionary."""
        # Create block and convert to dictionary
        block = Block(**self.block_data)
        block_dict = block.to_dict()

        # Verify all important data is preserved in serialization
        self.assertEqual(block_dict["index"], 1)
        self.assertEqual(len(block_dict["transactions"]), 2)
        self.assertEqual(block_dict["previous_hash"], "0" * 64)
        self.assertEqual(block_dict["nonce"], 12345)
        self.assertEqual(block_dict["hash"], block.hash)

    def test_block_from_dict(self):
        """Test that a block can be properly deserialized from a dictionary."""
        # Create original block and serialize it
        block = Block(**self.block_data)
        block_dict = block.to_dict()

        # Reconstruct block from dictionary
        reconstructed_block = Block.from_dict(block_dict)

        # Verify reconstructed block matches original
        self.assertEqual(block.index, reconstructed_block.index)
        self.assertEqual(block.hash, reconstructed_block.hash)
        self.assertEqual(block.previous_hash, reconstructed_block.previous_hash)


class TestTransaction(unittest.TestCase):
    """
    Test cases for the Transaction class functionality.

    Tests transaction creation, hash computation, serialization,
    and validation of transaction properties.
    """

    def test_transaction_creation(self):
        """Test that transactions are created with correct properties."""
        # Create a sample transaction
        tx = Transaction("Alice", "Bob", 10.0)

        # Verify transaction properties
        self.assertEqual(tx.sender, "Alice")
        self.assertEqual(tx.receiver, "Bob")
        self.assertEqual(tx.amount, 10.0)
        self.assertIsNotNone(tx.id)  # ID should be automatically generated
        self.assertIsNotNone(tx.timestamp)  # Timestamp should be set

    def test_transaction_hash_computation(self):
        """Test that transaction IDs (hashes) are computed consistently."""
        # Create two identical transactions
        tx1 = Transaction("Alice", "Bob", 10.0)
        tx2 = Transaction("Alice", "Bob", 10.0)

        # Make timestamps identical to ensure same hash
        tx2.timestamp = tx1.timestamp

        # Both transactions should have same ID if data is identical
        self.assertEqual(tx1.id, tx2.id)

    def test_transaction_to_dict(self):
        """Test transaction serialization to dictionary format."""
        # Create transaction and serialize it
        tx = Transaction("Alice", "Bob", 10.0)
        tx_dict = tx.to_dict()

        # Verify all data is correctly serialized
        self.assertEqual(tx_dict["sender"], "Alice")
        self.assertEqual(tx_dict["receiver"], "Bob")
        self.assertEqual(tx_dict["amount"], 10.0)
        self.assertEqual(tx_dict["id"], tx.id)

    def test_transaction_from_dict(self):
        """Test transaction deserialization from dictionary format."""
        # Create original transaction and serialize it
        tx = Transaction("Alice", "Bob", 10.0)
        tx_dict = tx.to_dict()

        # Reconstruct transaction from dictionary
        reconstructed_tx = Transaction.from_dict(tx_dict)

        # Verify reconstructed transaction matches original
        self.assertEqual(tx.sender, reconstructed_tx.sender)
        self.assertEqual(tx.receiver, reconstructed_tx.receiver)
        self.assertEqual(tx.amount, reconstructed_tx.amount)
        self.assertEqual(tx.id, reconstructed_tx.id)


class TestDoubleSpendTransaction(unittest.TestCase):
    """
    Test cases for DoubleSpendTransaction class.

    Tests the functionality of double-spend transactions which are
    crucial for simulating blockchain attacks.
    """

    def test_double_spend_creation(self):
        """Test that double-spend transactions are created correctly."""
        # Create a double-spend transaction
        double_spend = DoubleSpendTransaction("Attacker", "Victim", 15.0)

        # Verify double-spend transaction properties
        self.assertEqual(double_spend.attacker_addr, "Attacker")
        self.assertEqual(double_spend.victim_addr, "Victim")
        self.assertEqual(double_spend.amount, 15.0)
        self.assertIsNotNone(double_spend.timestamp)

    def test_double_spend_transactions(self):
        """Test that both transactions in a double-spend are generated correctly."""
        # Create double-spend and get both transactions
        double_spend = DoubleSpendTransaction("Attacker", "Victim", 15.0)
        transactions = double_spend.get_both_transactions()

        # Verify both transaction types exist
        self.assertIn("honest_to_victim", transactions)
        self.assertIn("malicious_to_shadow", transactions)

        # Extract both transactions
        honest_tx = transactions["honest_to_victim"]
        malicious_tx = transactions["malicious_to_shadow"]

        # Verify transaction details
        self.assertEqual(honest_tx.sender, "Attacker")
        self.assertEqual(honest_tx.receiver, "Victim")
        self.assertEqual(malicious_tx.sender, "Attacker")
        self.assertEqual(malicious_tx.receiver, "Attacker_shadow")  # Shadow address
        self.assertEqual(honest_tx.amount, 15.0)
        self.assertEqual(malicious_tx.amount, 15.0)
        # Both transactions should have same timestamp
        self.assertEqual(honest_tx.timestamp, malicious_tx.timestamp)


class TestBlockchain(unittest.TestCase):
    """
    Test cases for the Blockchain class core functionality.

    Tests blockchain initialization, block mining, transaction processing,
    chain validation, and double-spend detection.
    """

    def setUp(self):
        """Set up a fresh blockchain instance before each test."""
        # Create blockchain with custom difficulty and reward
        self.blockchain = Blockchain(difficulty=2, reward=1.0)

    def test_blockchain_initialization(self):
        """Test that blockchain initializes with correct default values."""
        # Verify initial blockchain state
        self.assertEqual(len(self.blockchain.chain), 1)  # Should have genesis block
        self.assertEqual(len(self.blockchain.mempool), 0)  # Mempool should be empty
        self.assertEqual(self.blockchain.difficulty, 2)  # Custom difficulty
        self.assertEqual(self.blockchain.miner_reward, 1.0)  # Custom reward

    def test_genesis_block(self):
        """Test that the genesis block is created with correct properties."""
        # Get the genesis block (first block in chain)
        genesis_block = self.blockchain.chain[0]

        # Verify genesis block properties
        self.assertEqual(genesis_block.index, 0)  # First block has index 0
        self.assertEqual(len(genesis_block.transactions), 0)  # No transactions
        self.assertEqual(genesis_block.previous_hash, "0")  # Special previous hash
        # Genesis block should satisfy proof of work
        self.assertTrue(genesis_block.hash.startswith('0' * 2))

    def test_new_transaction(self):
        """Test adding new transactions to the mempool."""
        # Add a transaction to the blockchain
        tx_id = self.blockchain.new_transaction("Alice", "Bob", 10.0)

        # Verify transaction was added correctly
        self.assertIsNotNone(tx_id)  # Should return transaction ID
        self.assertEqual(len(self.blockchain.mempool), 1)  # Mempool should have 1 transaction
        # Verify transaction details in mempool
        self.assertEqual(self.blockchain.mempool[0].sender, "Alice")
        self.assertEqual(self.blockchain.mempool[0].receiver, "Bob")
        self.assertEqual(self.blockchain.mempool[0].amount, 10.0)

    def test_mine_pending_transactions(self):
        """Test mining pending transactions into a new block."""
        # Add sample transactions to mempool
        self.blockchain.new_transaction("Alice", "Bob", 10.0)
        self.blockchain.new_transaction("Bob", "Charlie", 5.0)

        # Mine the pending transactions
        block = self.blockchain.mine_pending_transactions("Miner1")

        # Verify the mined block
        self.assertEqual(block.index, 1)  # Should be second block (after genesis)
        # Should have 3 transactions: 2 original + 1 miner reward
        self.assertEqual(len(block.transactions), 3)
        self.assertTrue(block.hash.startswith('0' * 2))  # Should satisfy proof of work
        self.assertEqual(len(self.blockchain.mempool), 0)  # Mempool should be cleared

    def test_chain_validation(self):
        """Test that the blockchain validation works correctly."""
        # Add some transactions and mine a block
        self.blockchain.new_transaction("Alice", "Bob", 10.0)
        self.blockchain.mine_pending_transactions("Miner1")

        # The chain should be valid after mining
        self.assertTrue(self.blockchain.is_chain_valid())

    def test_add_new_block(self):
        """Test adding a new valid block to the blockchain."""
        # Create a new block with sample transaction
        transactions = [Transaction("Alice", "Bob", 10.0)]
        new_block = Block(
            index=1,
            transactions=transactions,
            previous_hash=self.blockchain.last_block().hash,  # Link to previous block
            timestamp=int(time.time()),
            nonce=0  # Will be updated during mining
        )

        # Mine the block (perform proof of work)
        mined_block = self.blockchain._proof_of_work(new_block)

        # Add the mined block to the chain
        success = self.blockchain.add_new_block(mined_block)

        # Verify block was added successfully
        self.assertTrue(success)
        self.assertEqual(len(self.blockchain.chain), 2)  # Should now have 2 blocks

    def test_double_spend_detection(self):
        """Test that double spending attempts are detected."""
        # Create transactions that represent a double spend attempt
        transactions = [
            Transaction("Alice", "Bob", 10.0),
            Transaction("Alice", "Charlie", 10.0)  # Same sender, same amount = double spend
        ]

        # Create a block with the double spend transactions
        new_block = Block(
            index=1,
            transactions=transactions,
            previous_hash=self.blockchain.last_block().hash,
            timestamp=int(time.time()),
            nonce=0
        )

        # Mine the block
        mined_block = self.blockchain._proof_of_work(new_block)

        # The system should detect the double spend
        has_double_spend = self.blockchain._has_double_spend(transactions)
        self.assertTrue(has_double_spend)


class TestAttackSimulation(unittest.TestCase):
    """
    Test cases for attack simulation functionality.

    Tests various blockchain attacks including double spending
    and private mining attacks.
    """

    def setUp(self):
        """Set up test fixtures for attack simulation tests."""
        # Configuration for attack simulations
        self.node_url = "http://127.0.0.1:5000"
        self.attacker_addr = "TestAttacker"
        self.frontend_config = {
            "hash_power": 30,
            "success_probability": 50.0,
            "force_success": False,
            "force_failure": False
        }

    @patch('blockchain.attacker.requests')
    def test_run_attack_success(self, mock_requests):
        """Test successful attack simulation with mocked network."""
        # Mock the blockchain node response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "chain": [{"index": 0, "hash": "0" * 64}],  # Genesis block
            "difficulty": 3
        }
        mock_requests.get.return_value = mock_response

        # Configure test for forced success
        config = self.frontend_config.copy()
        config["force_success"] = True

        # Run the attack simulation
        result = run_attack(
            node_url=self.node_url,
            peers=[],
            attacker_addr=self.attacker_addr,
            blocks=1,
            amount=10.0,
            frontend_config=config
        )

        # Verify attack was successful
        self.assertTrue(result["successful"])
        self.assertTrue(result["success"])
        self.assertEqual(result["success_rate"], 1.0)  # 100% success rate

    @patch('blockchain.attacker.requests')
    def test_run_attack_failure(self, mock_requests):
        """Test failed attack simulation with mocked network."""
        # Mock the blockchain node response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "chain": [{"index": 0, "hash": "0" * 64}],  # Genesis block
            "difficulty": 3
        }
        mock_requests.get.return_value = mock_response

        # Configure test for forced failure
        config = self.frontend_config.copy()
        config["force_failure"] = True

        # Run the attack simulation
        result = run_attack(
            node_url=self.node_url,
            peers=[],
            attacker_addr=self.attacker_addr,
            blocks=1,
            amount=10.0,
            frontend_config=config
        )

        # Verify attack failed as expected
        self.assertFalse(result["successful"])
        self.assertFalse(result["success"])
        self.assertEqual(result["success_rate"], 0.0)  # 0% success rate

    def test_create_private_network(self):
        """Test creation of a private network for attack simulation."""
        # Create a private network for attack
        network_data = create_private_network(
            attacker_addr=self.attacker_addr,
            blocks_to_mine=2,
            amount=15.0,
            frontend_config=self.frontend_config
        )

        # Verify private network was created with expected properties
        self.assertIn("private_network", network_data)
        self.assertIn("mined_blocks", network_data)
        self.assertIn("network_size", network_data)
        self.assertGreaterEqual(network_data["network_size"], 6)  # Minimum network size
        self.assertIn("total_hash_power", network_data)

    def test_run_double_spending_attack(self):
        """Test execution of a double spending attack."""
        # Run double spending attack simulation
        result = run_double_spending_attack(
            attacker_name="TestAttacker",
            private_blocks=2,
            amount=20.0,
            hash_power=25.0
        )

        # Verify attack result structure
        self.assertIn("success", result)
        self.assertIn("successful", result)
        self.assertIn("probability", result)  # Success probability
        self.assertIn("blocks_mined", result)  # Number of blocks mined
        self.assertIn("message", result)  # Result description


class TestSimBlockIntegration(unittest.TestCase):
    """
    Test cases for SimBlock integration functionality.

    Tests the integration with SimBlock simulator for realistic
    blockchain network simulations.
    """

    def setUp(self):
        """Set up SimBlock integration instance for testing."""
        self.simblock = SimBlockIntegration()

    def test_simblock_initialization(self):
        """Test that SimBlock integration initializes correctly."""
        # Verify SimBlock instance was created properly
        self.assertIsNotNone(self.simblock.base_path)
        self.assertIsInstance(self.simblock.network_status, dict)
        self.assertIn("status", self.simblock.network_status)
        self.assertIn("nodes", self.simblock.network_status)

    def test_calculate_attack_probability(self):
        """Test attack probability calculation with network factors."""
        # Calculate attack probability with various factors
        probability = self.simblock.calculate_attack_probability(
            base_probability=70.0,
            hash_power=25.0,
            network_latency=100
        )

        # Verify probability is within reasonable bounds
        self.assertIsInstance(probability, float)
        self.assertGreaterEqual(probability, 5.0)  # At least 5%
        self.assertLessEqual(probability, 95.0)  # At most 95%

    def test_get_network_conditions(self):
        """Test retrieval of current network conditions from SimBlock."""
        # Get current network conditions
        conditions = self.simblock.get_current_network_conditions()

        # Verify conditions data structure
        self.assertIsInstance(conditions, dict)
        self.assertIn("average_latency", conditions)
        self.assertIn("node_count", conditions)
        self.assertIn("network_health", conditions)

    def test_simulate_message_propagation(self):
        """Test simulation of message propagation across network."""
        # Simulate message propagation to multiple peers
        propagation_data = self.simblock.simulate_message_propagation(
            message_size=1000,
            peers=["peer1", "peer2", "peer3"]
        )

        # Verify propagation data structure
        self.assertIsInstance(propagation_data, dict)
        self.assertIn("average_latency", propagation_data)
        self.assertIn("network_health", propagation_data)
        self.assertIn("successful_deliveries", propagation_data)
        self.assertIn("propagation_time", propagation_data)


class TestCSVReportGeneration(unittest.TestCase):
    """
    Test cases for CSV report generation functionality.

    Tests data export and balance calculation for reporting purposes.
    """

    def setUp(self):
        """Set up blockchain with sample data for report testing."""
        self.blockchain = Blockchain(difficulty=2, reward=1.0)

        # Add sample transactions and mine a block
        self.blockchain.new_transaction("Alice", "Bob", 10.0)
        self.blockchain.new_transaction("Bob", "Charlie", 5.0)
        self.blockchain.mine_pending_transactions("Miner1")

    def test_blockchain_data_export(self):
        """Test that blockchain data can be exported for reporting."""
        # Export blockchain data to dictionary format
        chain_data = self.blockchain.to_dict()

        # Verify exported data structure
        self.assertIsInstance(chain_data, dict)
        self.assertIn("chain", chain_data)  # Blockchain data
        self.assertIn("mempool", chain_data)  # Pending transactions
        self.assertIn("difficulty", chain_data)  # Current difficulty
        self.assertIn("peers", chain_data)  # Network peers

    def test_balance_calculation(self):
        """Test that account balances are calculated correctly."""
        # Calculate balances for all accounts
        balances = self.blockchain.get_balances()

        # Verify balances structure
        self.assertIsInstance(balances, dict)
        # SYSTEM account (miner rewards) should not appear in public balances
        self.assertNotIn("SYSTEM", balances)


class TestIntegration(unittest.TestCase):
    """
    Integration tests for the complete blockchain system.

    Tests end-to-end workflows and system integration.
    """

    def test_end_to_end_blockchain_operations(self):
        """Test complete blockchain operations from transaction to mining."""
        # Initialize a new blockchain
        blockchain = Blockchain(difficulty=2, reward=1.0)

        # Create and add transactions
        tx1_id = blockchain.new_transaction("Alice", "Bob", 10.0)
        tx2_id = blockchain.new_transaction("Bob", "Charlie", 5.0)

        # Verify transactions are in mempool
        self.assertEqual(len(blockchain.mempool), 2)

        # Mine the pending transactions
        block = blockchain.mine_pending_transactions("Miner1")

        # Verify the mined block
        self.assertEqual(block.index, 1)  # Second block (after genesis)
        # 2 transactions + 1 miner reward = 3 total
        self.assertEqual(len(block.transactions), 3)
        self.assertEqual(len(blockchain.mempool), 0)  # Mempool should be empty

        # Verify the entire chain is valid
        self.assertTrue(blockchain.is_chain_valid())

        # Check that balances are calculated correctly
        balances = blockchain.get_balances()
        self.assertIn("Bob", balances)  # Bob should have balance
        self.assertIn("Charlie", balances)  # Charlie should have balance

    @patch('blockchain.attacker.requests')
    def test_attack_simulation_integration(self, mock_requests):
        """Test integrated attack simulation with mocked network."""
        # Mock network responses for attack simulation
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "chain": [{"index": 0, "hash": "0" * 64}],  # Genesis block
            "difficulty": 3
        }
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response

        # Run integrated attack simulation
        result = run_attack(
            node_url="http://127.0.0.1:5000",
            peers=[],
            attacker_addr="IntegrationTestAttacker",
            blocks=1,
            amount=15.0,
            frontend_config={"force_success": True}  # Force success for test
        )

        # Verify attack simulation completed
        self.assertTrue(result["successful"])
        self.assertIn("steps", result)  # Attack steps taken
        self.assertIn("success_probability", result)  # Calculated probability


class TestErrorHandling(unittest.TestCase):
    """
    Test cases for error handling in various components.

    Ensures the system handles invalid inputs and edge cases gracefully.
    """

    def test_invalid_transaction(self):
        """Test handling of invalid transaction parameters."""
        blockchain = Blockchain()

        # Test that negative amount raises ValueError
        with self.assertRaises(ValueError):
            blockchain.new_transaction("Alice", "Bob", -10.0)

    def test_invalid_block_addition(self):
        """Test handling of invalid block addition attempts."""
        blockchain = Blockchain()

        # Create a block with invalid previous hash
        invalid_block = Block(
            index=1,
            transactions=[],
            previous_hash="invalid_hash",  # This won't match actual previous hash
            timestamp=int(time.time()),
            nonce=0
        )

        # Adding invalid block should fail
        success = blockchain.add_new_block(invalid_block)
        self.assertFalse(success)

    @patch('blockchain.attacker.requests')
    def test_network_failure_handling(self, mock_requests):
        """Test graceful handling of network failures during attacks."""
        # Mock network failure by raising exception
        mock_requests.get.side_effect = Exception("Network error")

        # Run attack simulation with network failure
        result = run_attack(
            node_url="http://127.0.0.1:5000",
            peers=[],
            attacker_addr="TestAttacker",
            blocks=1,
            amount=10.0,
            frontend_config={}
        )

        # System should handle network error gracefully
        self.assertFalse(result["successful"])
        self.assertIn("message", result)  # Error message should be included
        # Verify proper error response structure
        self.assertIn("success", result)
        self.assertIn("success_rate", result)


class TestPerformance(unittest.TestCase):
    """
    Performance tests for critical blockchain operations.

    Ensures that key operations complete within acceptable time limits.
    """

    def test_block_mining_performance(self):
        """Test that block mining completes in reasonable time."""
        # Use lower difficulty for faster testing
        blockchain = Blockchain(difficulty=2)

        # Add multiple transactions to mine
        for i in range(5):
            blockchain.new_transaction(f"Sender{i}", f"Receiver{i}", 1.0)

        # Time the mining operation
        start_time = time.time()
        block = blockchain.mine_pending_transactions("PerformanceTestMiner")
        end_time = time.time()

        mining_time = end_time - start_time

        # Mining should complete within acceptable time (adjust as needed)
        self.assertLess(mining_time, 10.0)  # 10 seconds maximum for this test
        self.assertEqual(block.index, 1)  # Should be second block
        # 5 transactions + 1 miner reward = 6 total
        self.assertEqual(len(block.transactions), 6)

    def test_chain_validation_performance(self):
        """Test that chain validation is efficient even with multiple blocks."""
        blockchain = Blockchain(difficulty=2)

        # Create a blockchain with multiple blocks
        for i in range(3):
            # Add multiple transactions per block
            for j in range(3):
                blockchain.new_transaction(f"Sender{i}_{j}", f"Receiver{i}_{j}", 1.0)
            blockchain.mine_pending_transactions(f"Miner{i}")

        # Time the validation operation
        start_time = time.time()
        is_valid = blockchain.is_chain_valid()
        end_time = time.time()

        validation_time = end_time - start_time

        # Chain should be valid and validation should be fast
        self.assertTrue(is_valid)
        self.assertLess(validation_time, 1.0)  # 1 second maximum for validation


class TestEdgeCases(unittest.TestCase):
    """
    Test edge cases and boundary conditions.

    Tests unusual scenarios and invalid inputs to ensure system robustness.
    """

    def test_empty_blockchain(self):
        """Test operations on a newly created empty blockchain."""
        blockchain = Blockchain()

        # New blockchain should have genesis block only
        self.assertEqual(len(blockchain.chain), 1)
        # Empty chain should always be valid
        self.assertTrue(blockchain.is_chain_valid())

    def test_large_transaction_amount(self):
        """Test handling of very large transaction amounts."""
        blockchain = Blockchain()

        # Large amount should be handled without issues
        tx_id = blockchain.new_transaction("RichUser", "Recipient", 1000000.0)
        self.assertIsNotNone(tx_id)

    def test_same_sender_receiver(self):
        """Test transaction validation with same sender and receiver."""
        blockchain = Blockchain()

        # Transaction to self should be invalid
        with self.assertRaises(ValueError):
            blockchain.new_transaction("Alice", "Alice", 10.0)

    def test_zero_amount_transaction(self):
        """Test that zero amount transactions are rejected."""
        blockchain = Blockchain()

        # Zero amount transactions should be invalid
        with self.assertRaises(ValueError):
            blockchain.new_transaction("Alice", "Bob", 0.0)


def run_all_tests():
    """
    Run all test suites and display comprehensive results.

    Returns:
        bool: True if all tests passed, False otherwise
    """
    # Create test loader and comprehensive test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Define all test classes to include
    test_classes = [
        TestBlock,
        TestTransaction,
        TestDoubleSpendTransaction,
        TestBlockchain,
        TestAttackSimulation,
        TestSimBlockIntegration,
        TestCSVReportGeneration,
        TestIntegration,
        TestErrorHandling,
        TestPerformance,
        TestEdgeCases
    ]

    # Add all test classes to the suite
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Display test execution header
    print("🚀 Starting Comprehensive Blockchain Test Suite...")
    print("=" * 70)

    # Run all tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Display comprehensive test summary
    print("=" * 70)
    print(f"📊 TEST SUMMARY:")
    print(f"   Tests Run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Skipped: {len(result.skipped)}")

    # Display final result
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        # Display detailed failure information
        for failure in result.failures:
            print(f"\n❌ FAILED: {failure[0]}")
            print(f"   Error: {failure[1]}")
        for error in result.errors:
            print(f"\n💥 ERROR: {error[0]}")
            print(f"   Error: {error[1]}")
        return False


if __name__ == "__main__":
    """
    Main execution point for running the test suite.

    When run directly, executes all tests and exits with appropriate status code.
    """
    # Run all tests and get success status
    success = run_all_tests()

    # Exit with code 0 for success, 1 for failure
    sys.exit(0 if success else 1)