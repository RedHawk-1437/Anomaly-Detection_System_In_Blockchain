# test_suite.py - FIXED VERSION WITH CONTINUOUS TESTING LOOP
# Updated to work with your blockchain project structure and enhanced features

import requests
import time
import json
import sys
import random
from datetime import datetime

# Base URL for the blockchain node
BASE_URL = "http://127.0.0.1:5000"


class BlockchainTestSuite:
    """
    Comprehensive test suite for the Blockchain Anomaly Detection System
    Synchronized with current project structure and enhanced features
    """

    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.test_results = []
        self.attack_config = {
            'successProbability': 0.7,
            'attackerHashPower': 40,
            'forceSuccess': False,
            'forceFailure': False
        }

    def log_test(self, test_name, success, message="", data=None):
        """Log test results with timestamps"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "test": test_name,
            "success": success,
            "message": message,
            "data": data
        }
        self.test_results.append(result)

        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}: {message}")
        if data and not success:
            print(f"   Data: {data}")
        return success

    def test_connection(self):
        """Test basic connection to the blockchain node"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            success = response.status_code == 200
            return self.log_test(
                "Connection Test",
                success,
                f"Status: {response.status_code}" if success else "Failed to connect"
            )
        except Exception as e:
            return self.log_test("Connection Test", False, f"Error: {str(e)}")

    def test_blockchain_endpoints(self):
        """Test all core blockchain endpoints"""
        endpoints = [
            ("/api/chain", "GET", "Get Blockchain"),
            ("/api/balances", "GET", "Get Balances"),
            ("/api/balances/detailed", "GET", "Get Detailed Balances"),
        ]

        all_success = True
        for endpoint, method, test_name in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", timeout=10)

                success = response.status_code == 200
                all_success = all_success and success

                self.log_test(
                    f"Endpoint: {test_name}",
                    success,
                    f"Status: {response.status_code}",
                    response.json() if success else None
                )

            except Exception as e:
                all_success = False
                self.log_test(f"Endpoint: {test_name}", False, f"Error: {str(e)}")

        return all_success

    def test_transaction_creation(self):
        """Test creating new transactions"""
        try:
            # Create test transaction
            tx_data = {
                "sender": "TestUser1",
                "receiver": "TestUser2",
                "amount": 5.0
            }

            response = requests.post(
                f"{self.base_url}/api/tx/new",
                json=tx_data,
                timeout=10
            )

            success = response.status_code == 200
            response_data = response.json() if success else None

            return self.log_test(
                "Transaction Creation",
                success,
                f"Transaction ID: {response_data.get('txid', 'N/A')}" if success else f"Status: {response.status_code}",
                response_data
            )

        except Exception as e:
            return self.log_test("Transaction Creation", False, f"Error: {str(e)}")

    def test_mining(self):
        """Test block mining functionality"""
        try:
            mine_data = {
                "miner": "TestMiner"
            }

            response = requests.post(
                f"{self.base_url}/api/mine",
                json=mine_data,
                timeout=30  # Longer timeout for mining
            )

            success = response.status_code == 200
            response_data = response.json() if success else None

            return self.log_test(
                "Block Mining",
                success,
                f"Block Index: {response_data.get('block', {}).get('index', 'N/A')}" if success else f"Status: {response.status_code}",
                response_data
            )

        except Exception as e:
            return self.log_test("Block Mining", False, f"Error: {str(e)}")

    def test_attack_simulation(self):
        """Test double-spending attack simulation"""
        try:
            attack_data = {
                "attacker": "TestAttacker",
                "blocks": 1,
                "amount": 10.0,
                "frontend_config": self.attack_config
            }

            response = requests.post(
                f"{self.base_url}/api/attack/run",
                json=attack_data,
                timeout=20
            )

            success = response.status_code == 200
            response_data = response.json() if success else None

            attack_result = "SUCCESS" if response_data.get('successful', False) else "FAILED"

            return self.log_test(
                "Attack Simulation",
                success,
                f"Attack Result: {attack_result}, Probability: {response_data.get('success_probability', 0):.1f}%" if success else f"Status: {response.status_code}",
                response_data
            )

        except Exception as e:
            return self.log_test("Attack Simulation", False, f"Error: {str(e)}")

    def test_chart_endpoints(self):
        """Test all chart data endpoints"""
        chart_endpoints = [
            "/api/charts/blockchain-growth",
            "/api/charts/balance-distribution",
            "/api/charts/mining-analysis",
            "/api/charts/network-activity",
            "/api/charts/simblock-analysis"
        ]

        all_success = True
        for endpoint in chart_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                success = response.status_code == 200
                all_success = all_success and success

                chart_name = endpoint.split("/")[-1].replace("-", " ").title()
                self.log_test(
                    f"Chart: {chart_name}",
                    success,
                    f"Data Points: {len(response.json().get('labels', []))}" if success else f"Status: {response.status_code}"
                )

            except Exception as e:
                all_success = False
                self.log_test(f"Chart: {endpoint}", False, f"Error: {str(e)}")

        return all_success

    def test_simblock_integration(self):
        """Test SimBlock integration endpoints"""
        # FIXED: Corrected variable name from 'endpoints' to 'simblock_endpoints'
        simblock_endpoints = [
            ("/api/simblock/network", "GET", "Network Status"),
            ("/api/simblock/start", "POST", "Start Simulation"),
        ]

        all_success = True
        for endpoint, method, test_name in simblock_endpoints:  # FIXED: Changed 'endpoints' to 'simblock_endpoints'
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                else:
                    # For POST endpoints, send empty JSON
                    response = requests.post(f"{self.base_url}{endpoint}", json={}, timeout=10)

                # Consider 200 or 201 as success
                success = response.status_code in [200, 201]
                all_success = all_success and success

                self.log_test(
                    f"SimBlock: {test_name}",
                    success,
                    f"Status: {response.status_code}",
                    response.json() if success else None
                )

            except Exception as e:
                all_success = False
                self.log_test(f"SimBlock: {test_name}", False, f"Error: {str(e)}")

        return all_success

    def test_pdf_report_generation(self):
        """Test PDF report generation"""
        try:
            response = requests.get(f"{self.base_url}/api/report/pdf", timeout=60)
            success = response.status_code == 200

            return self.log_test(
                "PDF Report Generation",
                success,
                f"File Size: {len(response.content)} bytes" if success else f"Status: {response.status_code}"
            )

        except Exception as e:
            return self.log_test("PDF Report Generation", False, f"Error: {str(e)}")

    def test_network_management(self):
        """Test network management endpoints"""
        try:
            # Test adding a peer
            peer_data = {
                "address": "http://127.0.0.1:5001"
            }

            response = requests.post(
                f"{self.base_url}/peers",
                json=peer_data,
                timeout=10
            )

            success = response.status_code in [200, 201]

            return self.log_test(
                "Network Management",
                success,
                f"Peers: {len(response.json().get('peers', []))}" if success else f"Status: {response.status_code}",
                response.json() if success else None
            )

        except Exception as e:
            return self.log_test("Network Management", False, f"Error: {str(e)}")

    def test_consensus_mechanism(self):
        """Test blockchain consensus mechanism"""
        try:
            response = requests.get(f"{self.base_url}/consensus", timeout=10)
            success = response.status_code == 200

            return self.log_test(
                "Consensus Mechanism",
                success,
                f"Status: {response.status_code}",
                response.json() if success else None
            )

        except Exception as e:
            return self.log_test("Consensus Mechanism", False, f"Error: {str(e)}")

    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive Blockchain Test Suite")
        print("=" * 60)

        tests = [
            ("Connection Test", self.test_connection),
            ("Blockchain Endpoints", self.test_blockchain_endpoints),
            ("Transaction Test", self.test_transaction_creation),
            ("Mining Test", self.test_mining),
            ("Chart Endpoints", self.test_chart_endpoints),
            ("SimBlock Integration", self.test_simblock_integration),
            ("Attack Simulation", self.test_attack_simulation),
            ("Network Management", self.test_network_management),
            ("Consensus Test", self.test_consensus_mechanism),
            ("PDF Report", self.test_pdf_report_generation),
        ]

        all_success = True
        for test_name, test_func in tests:
            print(f"\n🔧 Running {test_name}...")
            success = test_func()
            all_success = all_success and success
            time.sleep(1)  # Brief pause between tests

        return all_success

    def run_continuous_testing(self, interval_seconds=30, max_iterations=None):
        """
        Run continuous testing in a loop

        Args:
            interval_seconds: Time between test cycles (default: 30 seconds)
            max_iterations: Maximum number of test cycles (None for infinite)
        """
        print("🔄 Starting Continuous Testing Mode")
        print(f"⏰ Test interval: {interval_seconds} seconds")
        print(f"🔁 Max iterations: {max_iterations if max_iterations else 'Infinite'}")
        print("Press Ctrl+C to stop testing")
        print("=" * 60)

        iteration = 0
        try:
            while True:
                iteration += 1
                print(f"\n📊 TEST CYCLE {iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 50)

                # Run comprehensive test
                success = self.run_comprehensive_test()

                # Print summary for this cycle
                total_tests = len(self.test_results)
                passed_tests = sum(1 for result in self.test_results if result['success'])

                print(f"\n📈 Cycle {iteration} Summary: {passed_tests}/{total_tests} tests passed")

                # Check if we should stop
                if max_iterations and iteration >= max_iterations:
                    print(f"\n✅ Completed {max_iterations} test cycles. Stopping.")
                    break

                # Wait for next cycle
                if iteration < (max_iterations if max_iterations else float('inf')):
                    print(f"\n⏳ Waiting {interval_seconds} seconds for next test cycle...")
                    time.sleep(interval_seconds)

        except KeyboardInterrupt:
            print(f"\n🛑 Testing interrupted by user after {iteration} cycles")

        return self.generate_final_report()

    def generate_final_report(self):
        """Generate a final test report"""
        print("\n" + "=" * 60)
        print("📊 FINAL TEST REPORT")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests

        # Group by test cycle
        cycles = {}
        for result in self.test_results:
            cycle_time = result['timestamp'][:16]  # Group by minute
            if cycle_time not in cycles:
                cycles[cycle_time] = []
            cycles[cycle_time].append(result)

        print(f"Total Test Cycles: {len(cycles)}")
        print(f"Total Tests Run: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Success Rate: {(passed_tests / total_tests) * 100:.1f}%")

        # Show recent failures
        recent_failures = [r for r in self.test_results[-20:] if not r['success']]
        if recent_failures:
            print(f"\n🔍 Recent Failures (last 20 tests):")
            for failure in recent_failures[-5:]:  # Show last 5 failures
                print(f"   ❌ {failure['test']}: {failure['message']}")

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests) * 100,
            "test_cycles": len(cycles)
        }


def main():
    """Main function to run the test suite"""
    import argparse

    parser = argparse.ArgumentParser(description='Blockchain Test Suite')
    parser.add_argument('--url', default=BASE_URL, help='Blockchain node URL')
    parser.add_argument('--single', action='store_true', help='Run single test cycle')
    parser.add_argument('--continuous', action='store_true', help='Run continuous testing')
    parser.add_argument('--interval', type=int, default=30, help='Test interval in seconds (continuous mode)')
    parser.add_argument('--iterations', type=int, help='Number of test iterations')

    args = parser.parse_args()

    test_suite = BlockchainTestSuite(base_url=args.url)

    if args.continuous:
        # Continuous testing mode
        test_suite.run_continuous_testing(
            interval_seconds=args.interval,
            max_iterations=args.iterations
        )
    else:
        # Single test cycle
        success = test_suite.run_comprehensive_test()
        report = test_suite.generate_final_report()

        if success:
            print("\n🎉 All tests completed successfully!")
        else:
            print("\n⚠️ Some tests failed. Check the report above.")
            sys.exit(1)


# Quick test function for immediate use
def quick_test():
    """Run a quick test without command line arguments"""
    test_suite = BlockchainTestSuite()
    print("🔧 Running Quick Test...")
    test_suite.run_comprehensive_test()
    test_suite.generate_final_report()


if __name__ == "__main__":
    # If no arguments, run in continuous mode with default settings
    if len(sys.argv) == 1:
        test_suite = BlockchainTestSuite()
        print("🔄 Starting default continuous testing (30s interval, 5 iterations)")
        test_suite.run_continuous_testing(interval_seconds=30, max_iterations=5)
    else:
        main()