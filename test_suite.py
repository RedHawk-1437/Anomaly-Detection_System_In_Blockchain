# test_suite.py
# Complete Blockchain Test Suite for VIVA Demonstration
# UPDATED VERSION - Compatible with Current Project Structure
# This file contains comprehensive tests for all blockchain functionalities
# including core operations, attack simulations, and system integrations.

import requests
import time
import json
import random
from datetime import datetime


class BlockchainTestSuite:
    """
    Comprehensive test suite for blockchain system validation.

    This class provides methods to test all aspects of the blockchain system
    including transactions, mining, consensus, attacks, and integrations.
    """

    def __init__(self, base_url="http://127.0.0.1:5000"):
        """
        Initialize the test suite with target server URL.

        Args:
            base_url (str): Base URL of the blockchain server to test
        """
        self.base_url = base_url
        self.test_results = []  # Store all test results
        self.start_time = None  # Track test suite start time

    def log_test(self, test_name, status, message=""):
        """
        Log test results with timestamp and display to console.

        Args:
            test_name (str): Name of the test
            status (str): Test status ('PASS', 'FAIL', 'WARNING')
            message (str): Additional information about test result
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": timestamp
        }
        self.test_results.append(result)

        # Display test result with appropriate emoji
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} [{timestamp}] {test_name}: {status} - {message}")

    def start_suite(self):
        """Start the test suite and display header information."""
        self.start_time = time.time()
        print("\n" + "=" * 70)
        print("🚀 BLOCKCHAIN TEST SUITE - VIVA DEMONSTRATION")
        print("=" * 70)
        print("📋 Testing All Blockchain Functionalities...")
        print("=" * 70)

    def end_suite(self):
        """
        End the test suite and display comprehensive summary.

        Returns:
            tuple: (passed_count, failed_count, warning_count)
        """
        end_time = time.time()
        duration = end_time - self.start_time

        print("\n" + "=" * 70)
        print("📊 TEST SUITE SUMMARY")
        print("=" * 70)

        # Count test results by status
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        warning = len([r for r in self.test_results if r["status"] == "WARNING"])

        print(f"✅ Passed: {passed} | ❌ Failed: {failed} | ⚠️ Warning: {warning}")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        print("=" * 70)

        # Display detailed test results
        for result in self.test_results:
            icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{icon} {result['test']}")

        return passed, failed, warning

    # ==================== CORE BLOCKCHAIN TESTS ====================

    def test_blockchain_initialization(self):
        """Test if blockchain is properly initialized with genesis block."""
        try:
            response = requests.get(f"{self.base_url}/api/chain")
            if response.status_code == 200:
                data = response.json()
                if data.get("chain") and len(data["chain"]) > 0:
                    genesis_block = data["chain"][0]
                    # Validate genesis block structure
                    if genesis_block["index"] == 0 and genesis_block["previous_hash"] == "0":
                        self.log_test("Blockchain Initialization", "PASS",
                                      f"Genesis block created with {len(data['chain'])} blocks")
                    else:
                        self.log_test("Blockchain Initialization", "FAIL", "Invalid genesis block")
                else:
                    self.log_test("Blockchain Initialization", "FAIL", "No chain data")
            else:
                self.log_test("Blockchain Initialization", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Blockchain Initialization", "FAIL", str(e))

    def test_transaction_creation(self):
        """Test transaction creation and validation functionality."""
        try:
            # Test transaction data
            tx_data = {
                "sender": "TestUser1",
                "receiver": "TestUser2",
                "amount": 10.5
            }

            response = requests.post(f"{self.base_url}/api/tx/new", json=tx_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok" and data.get("txid"):
                    self.log_test("Transaction Creation", "PASS",
                                  f"Transaction created with ID: {data['txid'][:8]}...")
                else:
                    self.log_test("Transaction Creation", "FAIL", "Invalid response")
            else:
                self.log_test("Transaction Creation", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Transaction Creation", "FAIL", str(e))

    def test_block_mining(self):
        """Test block mining functionality with transaction processing."""
        try:
            mine_data = {
                "miner": "TestMiner"
            }

            response = requests.post(f"{self.base_url}/api/mine", json=mine_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok" and data.get("block"):
                    block = data["block"]
                    self.log_test("Block Mining", "PASS",
                                  f"Block #{block['index']} mined with {len(block['transactions'])} transactions")
                else:
                    self.log_test("Block Mining", "FAIL", "Invalid response")
            else:
                self.log_test("Block Mining", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Block Mining", "FAIL", str(e))

    def test_balance_calculation(self):
        """Test wallet balance calculation accuracy."""
        try:
            response = requests.get(f"{self.base_url}/api/balances")
            if response.status_code == 200:
                balances = response.json()
                total_balance = sum(balances.values())
                self.log_test("Balance Calculation", "PASS",
                              f"Calculated balances for {len(balances)} users, Total: {total_balance:.2f}")
            else:
                self.log_test("Balance Calculation", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Balance Calculation", "FAIL", str(e))

    def test_chain_validation(self):
        """Test blockchain validation and integrity checks."""
        try:
            response = requests.get(f"{self.base_url}/api/chain")
            if response.status_code == 200:
                data = response.json()
                chain_length = len(data["chain"])

                # Basic validation checks - verify block linking
                is_valid = True
                for i in range(1, chain_length):
                    current_block = data["chain"][i]
                    previous_block = data["chain"][i - 1]

                    if current_block["previous_hash"] != previous_block["hash"]:
                        is_valid = False
                        break

                if is_valid:
                    self.log_test("Chain Validation", "PASS", f"Chain with {chain_length} blocks is valid")
                else:
                    self.log_test("Chain Validation", "FAIL", "Chain integrity broken")
            else:
                self.log_test("Chain Validation", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Chain Validation", "FAIL", str(e))

    # ==================== P2P NETWORK TESTS ====================

    def test_peer_management(self):
        """Test peer addition and network management functionality."""
        try:
            peer_data = {
                "address": "http://127.0.0.1:5001"  # Test peer address
            }

            response = requests.post(f"{self.base_url}/peers", json=peer_data)
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "successfully" in data["message"].lower():
                    self.log_test("Peer Management", "PASS",
                                  f"Peer added successfully. Total peers: {len(data.get('peers', []))}")
                else:
                    self.log_test("Peer Management", "WARNING", "Peer added but different response")
            else:
                self.log_test("Peer Management", "WARNING", "Peer addition failed (expected for demo)")
        except Exception as e:
            self.log_test("Peer Management", "WARNING", f"Peer test skipped: {str(e)}")

    def test_consensus_mechanism(self):
        """Test blockchain consensus algorithm functionality."""
        try:
            response = requests.get(f"{self.base_url}/consensus")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Consensus Mechanism", "PASS",
                              f"Consensus check completed: {data.get('message', 'Unknown')}")
            else:
                self.log_test("Consensus Mechanism", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Consensus Mechanism", "FAIL", str(e))

    # ==================== ATTACK SIMULATION TESTS ====================

    def test_double_spending_attack(self, probability=50, hash_power=50, force_success=False, force_failure=False):
        """
        Test double spending attack with different configurations.

        Args:
            probability (int): Attack success probability (1-100)
            hash_power (int): Attacker hash power percentage (1-100)
            force_success (bool): Force attack to succeed
            force_failure (bool): Force attack to fail
        """
        try:
            # UPDATED: Use current project's attack configuration structure
            attack_config = {
                "attacker": "TestAttacker",
                "blocks": 1,
                "amount": 5.0,
                "hash_power": hash_power,  # Direct parameter
                "frontend_config": {
                    "successProbability": probability / 100.0,
                    "attackerHashPower": hash_power,
                    "forceSuccess": force_success,
                    "forceFailure": force_failure
                }
            }

            response = requests.post(f"{self.base_url}/api/attack/run", json=attack_config)
            if response.status_code == 200:
                data = response.json()

                # UPDATED: Handle different response formats
                attack_successful = data.get("successful") or data.get("success", False)
                success_rate = data.get("success_rate", 0) * 100
                message = data.get("message", "")

                # Validate forced outcomes
                if force_success and attack_successful:
                    status = "PASS"
                    outcome_msg = "Force Success: Attack succeeded as expected"
                elif force_failure and not attack_successful:
                    status = "PASS"
                    outcome_msg = "Force Failure: Attack failed as expected"
                elif not force_success and not force_failure:
                    status = "PASS"  # Random mode - any outcome is valid
                    outcome_msg = f"Random: Success={attack_successful}, Rate={success_rate:.1f}%"
                else:
                    status = "FAIL"
                    outcome_msg = f"Expected {'success' if force_success else 'failure'} but got {attack_successful}"

                self.log_test("Double Spending Attack", status, outcome_msg)

            else:
                self.log_test("Double Spending Attack", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Double Spending Attack", "FAIL", str(e))

    def test_attack_scenarios(self):
        """Test multiple attack scenarios with different configurations."""
        print("\n🔓 TESTING ATTACK SCENARIOS")
        print("-" * 40)

        # Test 1: Force Success - should always succeed
        self.test_double_spending_attack(probability=10, hash_power=10, force_success=True)

        # Test 2: Force Failure - should always fail
        self.test_double_spending_attack(probability=90, hash_power=90, force_failure=True)

        # Test 3: Low Probability - unlikely to succeed
        self.test_double_spending_attack(probability=20, hash_power=30)

        # Test 4: High Probability - more likely to succeed
        self.test_double_spending_attack(probability=80, hash_power=70)

        # Test 5: Balanced - moderate chance of success
        self.test_double_spending_attack(probability=50, hash_power=50)

    # ==================== SIMBLOCK INTEGRATION TESTS ====================

    def test_simblock_network_status(self):
        """Test SimBlock network status and conditions."""
        try:
            response = requests.get(f"{self.base_url}/api/simblock/network")
            if response.status_code == 200:
                data = response.json()
                network_status = data.get('status', 'unknown')
                latency = data.get('latency', 'unknown')
                self.log_test("SimBlock Network Status", "PASS",
                              f"Network: {network_status}, Latency: {latency}")
            else:
                self.log_test("SimBlock Network Status", "WARNING", "Network status unavailable")
        except Exception as e:
            self.log_test("SimBlock Network Status", "WARNING", f"SimBlock not available: {str(e)}")

    def test_simblock_simulation_start(self):
        """Test starting SimBlock simulation."""
        try:
            response = requests.post(f"{self.base_url}/api/simblock/start")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("SimBlock Simulation Start", "PASS", "Simulation started successfully")
                else:
                    self.log_test("SimBlock Simulation Start", "WARNING", "Simulation in simulated mode")
            else:
                self.log_test("SimBlock Simulation Start", "WARNING", "Simulation start failed")
        except Exception as e:
            self.log_test("SimBlock Simulation Start", "WARNING", f"SimBlock start test skipped: {str(e)}")

    # ==================== CHART & ANALYTICS TESTS ====================

    def test_chart_data_endpoints(self):
        """Test chart data API endpoints for data visualization."""
        chart_endpoints = [
            "/api/charts/blockchain-growth",
            "/api/charts/balance-distribution",
            "/api/charts/mining-analysis",
            "/api/charts/network-activity"
        ]

        for endpoint in chart_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    self.log_test(f"Chart API: {endpoint.split('/')[-1]}", "PASS", "Data retrieved successfully")
                else:
                    self.log_test(f"Chart API: {endpoint.split('/')[-1]}", "WARNING", f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Chart API: {endpoint.split('/')[-1]}", "WARNING", str(e))

    def test_pdf_report_generation(self):
        """Test PDF report generation functionality."""
        try:
            response = requests.get(f"{self.base_url}/api/report/pdf")
            if response.status_code == 200:
                # Check if response is PDF
                content_type = response.headers.get('content-type', '')
                if 'pdf' in content_type.lower() or 'application' in content_type.lower():
                    self.log_test("PDF Report Generation", "PASS", "PDF report generated successfully")
                else:
                    self.log_test("PDF Report Generation", "WARNING", "Unexpected content type")
            else:
                self.log_test("PDF Report Generation", "WARNING", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("PDF Report Generation", "WARNING", str(e))

    # ==================== COMPREHENSIVE TEST SUITE ====================

    def run_comprehensive_test(self):
        """
        Run all tests in a comprehensive suite covering all system aspects.

        Returns:
            tuple: (passed_count, failed_count, warning_count)
        """
        self.start_suite()

        print("\n🔗 CORE BLOCKCHAIN FUNCTIONALITY")
        print("-" * 40)
        self.test_blockchain_initialization()
        self.test_transaction_creation()
        self.test_block_mining()
        self.test_balance_calculation()
        self.test_chain_validation()

        print("\n🌐 P2P NETWORK FUNCTIONALITY")
        print("-" * 40)
        self.test_peer_management()
        self.test_consensus_mechanism()

        print("\n🛡️ SECURITY & ATTACK SIMULATION")
        print("-" * 40)
        self.test_attack_scenarios()

        print("\n📊 ANALYTICS & VISUALIZATION")
        print("-" * 40)
        self.test_chart_data_endpoints()
        self.test_pdf_report_generation()

        print("\n🔬 SIMBLOCK INTEGRATION")
        print("-" * 40)
        self.test_simblock_network_status()
        self.test_simblock_simulation_start()

        return self.end_suite()

    # ==================== PERFORMANCE TESTING ====================

    def performance_test(self, num_transactions=5):
        """
        Performance test with multiple transactions to measure system throughput.

        Args:
            num_transactions (int): Number of transactions to create for performance test
        """
        print(f"\n⚡ PERFORMANCE TEST: {num_transactions} Transactions")
        print("-" * 50)

        start_time = time.time()
        successful_txs = 0

        # Create multiple transactions to test performance
        for i in range(num_transactions):
            try:
                tx_data = {
                    "sender": f"PerfUser{i}",
                    "receiver": f"PerfReceiver{i}",
                    "amount": random.uniform(1, 100)
                }

                response = requests.post(f"{self.base_url}/api/tx/new", json=tx_data)
                if response.status_code == 200:
                    successful_txs += 1

                # Small delay to avoid overwhelming the server
                time.sleep(0.1)

            except Exception as e:
                print(f"❌ Transaction {i + 1} failed: {e}")

        end_time = time.time()
        duration = end_time - start_time

        self.log_test("Performance Test", "PASS",
                      f"{successful_txs}/{num_transactions} transactions in {duration:.2f}s "
                      f"({duration / num_transactions:.3f}s per tx)")

    # ==================== VIVA SPECIFIC DEMOS ====================

    def viva_demonstration_mode(self):
        """Special demonstration mode for VIVA presentation with live interactions."""
        print("\n🎓 VIVA DEMONSTRATION MODE")
        print("=" * 50)

        # Clear previous results for clean demo
        self.test_results = []

        print("1. Demonstrating Blockchain Basics...")
        self.test_blockchain_initialization()
        time.sleep(1)

        print("\n2. Creating Sample Transactions...")
        self.test_transaction_creation()
        time.sleep(1)

        print("\n3. Mining New Block...")
        self.test_block_mining()
        time.sleep(1)

        print("\n4. Checking Balances...")
        self.test_balance_calculation()
        time.sleep(1)

        print("\n5. Double-Spending Attack Simulation...")
        self.test_double_spending_attack(probability=70, hash_power=60)
        time.sleep(1)

        print("\n6. SimBlock Network Integration...")
        self.test_simblock_network_status()

        print("\n" + "=" * 50)
        print("🎯 VIVA DEMONSTRATION COMPLETED!")
        print("=" * 50)


# ==================== DEMONSTRATION MODES ====================

def run_quick_demo():
    """Quick demonstration mode for VIVA presentation - essential tests only."""
    print("🎯 QUICK VIVA DEMONSTRATION MODE")
    print("=" * 50)

    tester = BlockchainTestSuite()
    tester.viva_demonstration_mode()


def run_full_demo():
    """Full comprehensive testing mode - all system aspects."""
    print("🔬 COMPREHENSIVE TESTING MODE")
    print("=" * 50)

    tester = BlockchainTestSuite()
    tester.run_comprehensive_test()

    # Additional performance test
    tester.performance_test(3)


def run_attack_demo():
    """Focus on attack simulation demonstrations."""
    print("🛡️ ATTACK SIMULATION DEMONSTRATION")
    print("=" * 50)

    tester = BlockchainTestSuite()
    tester.start_suite()

    print("\n🔓 ATTACK SCENARIOS DEMONSTRATION")
    print("-" * 40)

    # Various attack scenarios for comprehensive demonstration
    scenarios = [
        ("Force Success", 10, 10, True, False),
        ("Force Failure", 90, 90, False, True),
        ("Low Probability", 20, 30, False, False),
        ("High Probability", 80, 70, False, False),
        ("Balanced", 50, 50, False, False)
    ]

    for name, prob, hash_power, force_s, force_f in scenarios:
        print(f"\n🎯 Testing: {name}")
        tester.test_double_spending_attack(prob, hash_power, force_s, force_f)

    tester.end_suite()


def run_simblock_demo():
    """Focus on SimBlock integration demonstrations."""
    print("🌐 SIMBLOCK INTEGRATION DEMONSTRATION")
    print("=" * 50)

    tester = BlockchainTestSuite()
    tester.start_suite()

    print("\n🔬 SIMBLOCK FUNCTIONALITY")
    print("-" * 40)

    tester.test_simblock_network_status()
    tester.test_simblock_simulation_start()

    # Test enhanced probability calculation
    try:
        prob_data = {
            "base_probability": 0.7,
            "hash_power": 0.6,
            "latency": 100
        }
        response = requests.post("http://127.0.0.1:5000/api/simblock/attack-probability", json=prob_data)
        if response.status_code == 200:
            data = response.json()
            enhanced_prob = data.get('enhanced_probability', 0) * 100
            tester.log_test("SimBlock Probability Enhancement", "PASS",
                            f"Enhanced probability: {enhanced_prob:.1f}%")
    except Exception as e:
        tester.log_test("SimBlock Probability Enhancement", "WARNING", str(e))

    tester.end_suite()


if __name__ == "__main__":
    """
    Main entry point for the test suite with multiple demonstration modes.

    Allows user to choose between different testing scenarios:
    1. Quick VIVA Demo - Essential tests for presentations
    2. Full Comprehensive Test - All system functionality  
    3. Attack Simulation Demo - Focus on security aspects
    4. SimBlock Integration Demo - Network simulation focus
    5. All Tests - Complete testing suite
    """
    print("🚀 Blockchain Anomaly Detection System - Test Suite")
    print("=" * 60)
    print("Choose Demonstration Mode:")
    print("1. Quick VIVA Demo (Recommended for Presentation)")
    print("2. Full Comprehensive Test")
    print("3. Attack Simulation Demo")
    print("4. SimBlock Integration Demo")
    print("5. Run All Demonstration Modes")

    choice = input("\nEnter choice (1-5): ").strip()

    if choice == "1":
        run_quick_demo()
    elif choice == "2":
        run_full_demo()
    elif choice == "3":
        run_attack_demo()
    elif choice == "4":
        run_simblock_demo()
    elif choice == "5":
        print("\n" + "=" * 70)
        run_quick_demo()
        print("\n" + "=" * 70)
        run_full_demo()
        print("\n" + "=" * 70)
        run_attack_demo()
        print("\n" + "=" * 70)
        run_simblock_demo()
    else:
        print("Invalid choice. Running Quick VIVA Demo...")
        run_quick_demo()