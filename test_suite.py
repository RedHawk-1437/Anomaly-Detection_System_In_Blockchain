"""
test_suite.py - Comprehensive Test Suite for Blockchain Anomaly Detection System
FIXED VERSION - Updated error handling test
"""

import unittest
import json
import time
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
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
    """Test Block class functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.transactions = [
            Transaction("Alice", "Bob", 10.0),
            Transaction("Bob", "Charlie", 5.0)
        ]
        self.block_data = {
            "index": 1,
            "transactions": self.transactions,
            "previous_hash": "0" * 64,
            "timestamp": int(time.time()),
            "nonce": 12345
        }

    def test_block_creation(self):
        """Test block creation with valid data"""
        block = Block(**self.block_data)

        self.assertEqual(block.index, 1)
        self.assertEqual(len(block.transactions), 2)
        self.assertEqual(block.previous_hash, "0" * 64)
        self.assertEqual(block.nonce, 12345)
        self.assertIsNotNone(block.hash)

    def test_block_hash_computation(self):
        """Test block hash computation"""
        block = Block(**self.block_data)
        computed_hash = block.compute_hash()

        self.assertEqual(block.hash, computed_hash)
        self.assertEqual(len(computed_hash), 64)  # SHA-256 hash length

    def test_block_to_dict(self):
        """Test block serialization to dictionary"""
        block = Block(**self.block_data)
        block_dict = block.to_dict()

        self.assertEqual(block_dict["index"], 1)
        self.assertEqual(len(block_dict["transactions"]), 2)
        self.assertEqual(block_dict["previous_hash"], "0" * 64)
        self.assertEqual(block_dict["nonce"], 12345)
        self.assertEqual(block_dict["hash"], block.hash)

    def test_block_from_dict(self):
        """Test block deserialization from dictionary"""
        block = Block(**self.block_data)
        block_dict = block.to_dict()

        reconstructed_block = Block.from_dict(block_dict)

        self.assertEqual(block.index, reconstructed_block.index)
        self.assertEqual(block.hash, reconstructed_block.hash)
        self.assertEqual(block.previous_hash, reconstructed_block.previous_hash)


class TestTransaction(unittest.TestCase):
    """Test Transaction class functionality"""

    def test_transaction_creation(self):
        """Test transaction creation with valid data"""
        tx = Transaction("Alice", "Bob", 10.0)

        self.assertEqual(tx.sender, "Alice")
        self.assertEqual(tx.receiver, "Bob")
        self.assertEqual(tx.amount, 10.0)
        self.assertIsNotNone(tx.id)
        self.assertIsNotNone(tx.timestamp)

    def test_transaction_hash_computation(self):
        """Test transaction hash computation"""
        tx1 = Transaction("Alice", "Bob", 10.0)
        tx2 = Transaction("Alice", "Bob", 10.0)

        # Same data should produce same hash if timestamps are same
        tx2.timestamp = tx1.timestamp
        self.assertEqual(tx1.id, tx2.id)

    def test_transaction_to_dict(self):
        """Test transaction serialization to dictionary"""
        tx = Transaction("Alice", "Bob", 10.0)
        tx_dict = tx.to_dict()

        self.assertEqual(tx_dict["sender"], "Alice")
        self.assertEqual(tx_dict["receiver"], "Bob")
        self.assertEqual(tx_dict["amount"], 10.0)
        self.assertEqual(tx_dict["id"], tx.id)

    def test_transaction_from_dict(self):
        """Test transaction deserialization from dictionary"""
        tx = Transaction("Alice", "Bob", 10.0)
        tx_dict = tx.to_dict()

        reconstructed_tx = Transaction.from_dict(tx_dict)

        self.assertEqual(tx.sender, reconstructed_tx.sender)
        self.assertEqual(tx.receiver, reconstructed_tx.receiver)
        self.assertEqual(tx.amount, reconstructed_tx.amount)
        self.assertEqual(tx.id, reconstructed_tx.id)


class TestDoubleSpendTransaction(unittest.TestCase):
    """Test DoubleSpendTransaction class functionality"""

    def test_double_spend_creation(self):
        """Test double spend transaction creation"""
        double_spend = DoubleSpendTransaction("Attacker", "Victim", 15.0)

        self.assertEqual(double_spend.attacker_addr, "Attacker")
        self.assertEqual(double_spend.victim_addr, "Victim")
        self.assertEqual(double_spend.amount, 15.0)
        self.assertIsNotNone(double_spend.timestamp)

    def test_double_spend_transactions(self):
        """Test both transactions in double spend"""
        double_spend = DoubleSpendTransaction("Attacker", "Victim", 15.0)
        transactions = double_spend.get_both_transactions()

        self.assertIn("honest_to_victim", transactions)
        self.assertIn("malicious_to_shadow", transactions)

        honest_tx = transactions["honest_to_victim"]
        malicious_tx = transactions["malicious_to_shadow"]

        self.assertEqual(honest_tx.sender, "Attacker")
        self.assertEqual(honest_tx.receiver, "Victim")
        self.assertEqual(malicious_tx.sender, "Attacker")
        self.assertEqual(malicious_tx.receiver, "Attacker_shadow")
        self.assertEqual(honest_tx.amount, 15.0)
        self.assertEqual(malicious_tx.amount, 15.0)
        self.assertEqual(honest_tx.timestamp, malicious_tx.timestamp)


class TestBlockchain(unittest.TestCase):
    """Test Blockchain class functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.blockchain = Blockchain(difficulty=2, reward=1.0)

    def test_blockchain_initialization(self):
        """Test blockchain initialization"""
        self.assertEqual(len(self.blockchain.chain), 1)  # Genesis block
        self.assertEqual(len(self.blockchain.mempool), 0)
        self.assertEqual(self.blockchain.difficulty, 2)
        self.assertEqual(self.blockchain.miner_reward, 1.0)

    def test_genesis_block(self):
        """Test genesis block creation"""
        genesis_block = self.blockchain.chain[0]

        self.assertEqual(genesis_block.index, 0)
        self.assertEqual(len(genesis_block.transactions), 0)
        self.assertEqual(genesis_block.previous_hash, "0")
        self.assertTrue(genesis_block.hash.startswith('0' * 2))  # Proof of work

    def test_new_transaction(self):
        """Test adding new transaction"""
        tx_id = self.blockchain.new_transaction("Alice", "Bob", 10.0)

        self.assertIsNotNone(tx_id)
        self.assertEqual(len(self.blockchain.mempool), 1)
        self.assertEqual(self.blockchain.mempool[0].sender, "Alice")
        self.assertEqual(self.blockchain.mempool[0].receiver, "Bob")
        self.assertEqual(self.blockchain.mempool[0].amount, 10.0)

    def test_mine_pending_transactions(self):
        """Test mining pending transactions"""
        # Add some transactions
        self.blockchain.new_transaction("Alice", "Bob", 10.0)
        self.blockchain.new_transaction("Bob", "Charlie", 5.0)

        # Mine block
        block = self.blockchain.mine_pending_transactions("Miner1")

        self.assertEqual(block.index, 1)
        self.assertEqual(len(block.transactions), 3)  # 2 transactions + reward
        self.assertTrue(block.hash.startswith('0' * 2))  # Proof of work
        self.assertEqual(len(self.blockchain.mempool), 0)  # Mempool cleared

    def test_chain_validation(self):
        """Test blockchain validation"""
        # Add some blocks
        self.blockchain.new_transaction("Alice", "Bob", 10.0)
        self.blockchain.mine_pending_transactions("Miner1")

        self.assertTrue(self.blockchain.is_chain_valid())

    def test_add_new_block(self):
        """Test adding new block to chain"""
        # Create a valid block
        transactions = [Transaction("Alice", "Bob", 10.0)]
        new_block = Block(
            index=1,
            transactions=transactions,
            previous_hash=self.blockchain.last_block().hash,
            timestamp=int(time.time()),
            nonce=0
        )

        # Mine the block
        mined_block = self.blockchain._proof_of_work(new_block)

        # Add to chain
        success = self.blockchain.add_new_block(mined_block)

        self.assertTrue(success)
        self.assertEqual(len(self.blockchain.chain), 2)

    def test_double_spend_detection(self):
        """Test double spending detection"""
        # Create a block with double spend attempt
        transactions = [
            Transaction("Alice", "Bob", 10.0),
            Transaction("Alice", "Charlie", 10.0)  # Same sender, same amount
        ]

        new_block = Block(
            index=1,
            transactions=transactions,
            previous_hash=self.blockchain.last_block().hash,
            timestamp=int(time.time()),
            nonce=0
        )

        mined_block = self.blockchain._proof_of_work(new_block)

        # Should detect double spend
        has_double_spend = self.blockchain._has_double_spend(transactions)
        self.assertTrue(has_double_spend)


class TestAttackSimulation(unittest.TestCase):
    """Test attack simulation functionality"""

    def setUp(self):
        """Set up test fixtures"""
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
        """Test successful attack simulation"""
        # Mock the chain state response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "chain": [{"index": 0, "hash": "0" * 64}],
            "difficulty": 3
        }
        mock_requests.get.return_value = mock_response

        # Test with force success
        config = self.frontend_config.copy()
        config["force_success"] = True

        result = run_attack(
            node_url=self.node_url,
            peers=[],
            attacker_addr=self.attacker_addr,
            blocks=1,
            amount=10.0,
            frontend_config=config
        )

        self.assertTrue(result["successful"])
        self.assertTrue(result["success"])
        self.assertEqual(result["success_rate"], 1.0)

    @patch('blockchain.attacker.requests')
    def test_run_attack_failure(self, mock_requests):
        """Test failed attack simulation"""
        # Mock the chain state response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "chain": [{"index": 0, "hash": "0" * 64}],
            "difficulty": 3
        }
        mock_requests.get.return_value = mock_response

        # Test with force failure
        config = self.frontend_config.copy()
        config["force_failure"] = True

        result = run_attack(
            node_url=self.node_url,
            peers=[],
            attacker_addr=self.attacker_addr,
            blocks=1,
            amount=10.0,
            frontend_config=config
        )

        self.assertFalse(result["successful"])
        self.assertFalse(result["success"])
        self.assertEqual(result["success_rate"], 0.0)

    def test_create_private_network(self):
        """Test private network creation"""
        network_data = create_private_network(
            attacker_addr=self.attacker_addr,
            blocks_to_mine=2,
            amount=15.0,
            frontend_config=self.frontend_config
        )

        self.assertIn("private_network", network_data)
        self.assertIn("mined_blocks", network_data)
        self.assertIn("network_size", network_data)
        self.assertGreaterEqual(network_data["network_size"], 6)
        self.assertIn("total_hash_power", network_data)

    def test_run_double_spending_attack(self):
        """Test double spending attack execution"""
        result = run_double_spending_attack(
            attacker_name="TestAttacker",
            private_blocks=2,
            amount=20.0,
            hash_power=25.0
        )

        self.assertIn("success", result)
        self.assertIn("successful", result)
        self.assertIn("probability", result)
        self.assertIn("blocks_mined", result)
        self.assertIn("message", result)


class TestSimBlockIntegration(unittest.TestCase):
    """Test SimBlock integration functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.simblock = SimBlockIntegration()

    def test_simblock_initialization(self):
        """Test SimBlock integration initialization"""
        self.assertIsNotNone(self.simblock.base_path)
        self.assertIsInstance(self.simblock.network_status, dict)
        self.assertIn("status", self.simblock.network_status)
        self.assertIn("nodes", self.simblock.network_status)

    def test_calculate_attack_probability(self):
        """Test attack probability calculation"""
        probability = self.simblock.calculate_attack_probability(
            base_probability=70.0,
            hash_power=25.0,
            network_latency=100
        )

        self.assertIsInstance(probability, float)
        self.assertGreaterEqual(probability, 5.0)
        self.assertLessEqual(probability, 95.0)

    def test_get_network_conditions(self):
        """Test network conditions retrieval"""
        conditions = self.simblock.get_current_network_conditions()

        self.assertIsInstance(conditions, dict)
        self.assertIn("average_latency", conditions)
        self.assertIn("node_count", conditions)
        self.assertIn("network_health", conditions)

    def test_simulate_message_propagation(self):
        """Test message propagation simulation"""
        propagation_data = self.simblock.simulate_message_propagation(
            message_size=1000,
            peers=["peer1", "peer2", "peer3"]
        )

        self.assertIsInstance(propagation_data, dict)
        self.assertIn("average_latency", propagation_data)
        self.assertIn("network_health", propagation_data)
        self.assertIn("successful_deliveries", propagation_data)
        self.assertIn("propagation_time", propagation_data)


class TestCSVReportGeneration(unittest.TestCase):
    """Test CSV report generation functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.blockchain = Blockchain(difficulty=2, reward=1.0)

        # Add some test data
        self.blockchain.new_transaction("Alice", "Bob", 10.0)
        self.blockchain.new_transaction("Bob", "Charlie", 5.0)
        self.blockchain.mine_pending_transactions("Miner1")

    def test_blockchain_data_export(self):
        """Test blockchain data export functionality"""
        chain_data = self.blockchain.to_dict()

        self.assertIsInstance(chain_data, dict)
        self.assertIn("chain", chain_data)
        self.assertIn("mempool", chain_data)
        self.assertIn("difficulty", chain_data)
        self.assertIn("peers", chain_data)

    def test_balance_calculation(self):
        """Test balance calculation"""
        balances = self.blockchain.get_balances()

        self.assertIsInstance(balances, dict)
        # SYSTEM account should be removed from balances
        self.assertNotIn("SYSTEM", balances)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""

    def test_end_to_end_blockchain_operations(self):
        """Test complete blockchain operations flow"""
        # Initialize blockchain
        blockchain = Blockchain(difficulty=2, reward=1.0)

        # Create transactions
        tx1_id = blockchain.new_transaction("Alice", "Bob", 10.0)
        tx2_id = blockchain.new_transaction("Bob", "Charlie", 5.0)

        self.assertEqual(len(blockchain.mempool), 2)

        # Mine block
        block = blockchain.mine_pending_transactions("Miner1")

        self.assertEqual(block.index, 1)
        self.assertEqual(len(block.transactions), 3)  # 2 transactions + reward
        self.assertEqual(len(blockchain.mempool), 0)

        # Verify chain validity
        self.assertTrue(blockchain.is_chain_valid())

        # Check balances
        balances = blockchain.get_balances()
        self.assertIn("Bob", balances)
        self.assertIn("Charlie", balances)

    @patch('blockchain.attacker.requests')
    def test_attack_simulation_integration(self, mock_requests):
        """Test integrated attack simulation"""
        # Mock network responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "chain": [{"index": 0, "hash": "0" * 64}],
            "difficulty": 3
        }
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response

        # Run attack simulation
        result = run_attack(
            node_url="http://127.0.0.1:5000",
            peers=[],
            attacker_addr="IntegrationTestAttacker",
            blocks=1,
            amount=15.0,
            frontend_config={"force_success": True}
        )

        self.assertTrue(result["successful"])
        self.assertIn("steps", result)
        self.assertIn("success_probability", result)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in various components"""

    def test_invalid_transaction(self):
        """Test handling of invalid transactions"""
        blockchain = Blockchain()

        # Test invalid amount
        with self.assertRaises(ValueError):
            blockchain.new_transaction("Alice", "Bob", -10.0)

    def test_invalid_block_addition(self):
        """Test handling of invalid block addition"""
        blockchain = Blockchain()

        # Create invalid block (wrong previous hash)
        invalid_block = Block(
            index=1,
            transactions=[],
            previous_hash="invalid_hash",
            timestamp=int(time.time()),
            nonce=0
        )

        success = blockchain.add_new_block(invalid_block)
        self.assertFalse(success)

    @patch('blockchain.attacker.requests')
    def test_network_failure_handling(self, mock_requests):
        """Test handling of network failures - FIXED VERSION"""
        # Mock network failure for get_current_chain_state
        mock_requests.get.side_effect = Exception("Network error")

        result = run_attack(
            node_url="http://127.0.0.1:5000",
            peers=[],
            attacker_addr="TestAttacker",
            blocks=1,
            amount=10.0,
            frontend_config={}
        )

        # The attack should handle the network error gracefully
        self.assertFalse(result["successful"])
        self.assertIn("message", result)
        # Check that we get a proper error response structure
        self.assertIn("success", result)
        self.assertIn("success_rate", result)


class TestPerformance(unittest.TestCase):
    """Performance tests for critical operations"""

    def test_block_mining_performance(self):
        """Test block mining performance"""
        blockchain = Blockchain(difficulty=2)  # Lower difficulty for faster tests

        # Add transactions
        for i in range(5):
            blockchain.new_transaction(f"Sender{i}", f"Receiver{i}", 1.0)

        # Time the mining operation
        start_time = time.time()
        block = blockchain.mine_pending_transactions("PerformanceTestMiner")
        end_time = time.time()

        mining_time = end_time - start_time

        # Mining should complete in reasonable time (adjust threshold as needed)
        self.assertLess(mining_time, 10.0)  # 10 seconds maximum
        self.assertEqual(block.index, 1)
        self.assertEqual(len(block.transactions), 6)  # 5 transactions + reward

    def test_chain_validation_performance(self):
        """Test chain validation performance"""
        blockchain = Blockchain(difficulty=2)

        # Add multiple blocks
        for i in range(3):
            for j in range(3):
                blockchain.new_transaction(f"Sender{i}_{j}", f"Receiver{i}_{j}", 1.0)
            blockchain.mine_pending_transactions(f"Miner{i}")

        # Time the validation operation
        start_time = time.time()
        is_valid = blockchain.is_chain_valid()
        end_time = time.time()

        validation_time = end_time - start_time

        self.assertTrue(is_valid)
        self.assertLess(validation_time, 1.0)  # 1 second maximum


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_empty_blockchain(self):
        """Test operations on empty blockchain"""
        blockchain = Blockchain()

        # Should have genesis block
        self.assertEqual(len(blockchain.chain), 1)
        self.assertTrue(blockchain.is_chain_valid())

    def test_large_transaction_amount(self):
        """Test handling of large transaction amounts"""
        blockchain = Blockchain()

        # Large amount should be handled
        tx_id = blockchain.new_transaction("RichUser", "Recipient", 1000000.0)
        self.assertIsNotNone(tx_id)

    def test_same_sender_receiver(self):
        """Test transaction with same sender and receiver"""
        blockchain = Blockchain()

        # This should be invalid based on your validation
        with self.assertRaises(ValueError):
            blockchain.new_transaction("Alice", "Alice", 10.0)

    def test_zero_amount_transaction(self):
        """Test transaction with zero amount"""
        blockchain = Blockchain()

        # Zero amount should be invalid
        with self.assertRaises(ValueError):
            blockchain.new_transaction("Alice", "Bob", 0.0)


def run_all_tests():
    """Run all test suites and return results"""
    # Create test loader and suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
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

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    print("🚀 Starting Comprehensive Blockchain Test Suite...")
    print("=" * 70)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("=" * 70)
    print(f"📊 TEST SUMMARY:")
    print(f"   Tests Run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        # Print failure details
        for failure in result.failures:
            print(f"\n❌ FAILED: {failure[0]}")
            print(f"   Error: {failure[1]}")
        for error in result.errors:
            print(f"\n💥 ERROR: {error[0]}")
            print(f"   Error: {error[1]}")
        return False


if __name__ == "__main__":
    # Run all tests
    success = run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)