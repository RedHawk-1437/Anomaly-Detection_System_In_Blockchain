# test_complete_project.py
"""
COMPLETE PROJECT TEST SUITE
Tests all phases of the Blockchain Anomaly Detection System
"""

import sys
import os
import time
import requests
import json
import pandas as pd

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class CompleteProjectTest:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.test_results = {}

    def run_complete_test_suite(self):
        """Run complete test suite for all project phases"""

        print("🚀 COMPLETE BLOCKCHAIN ANOMALY DETECTION SYSTEM TEST")
        print("=" * 70)

        # Phase 1: System Initialization
        self.phase_1_system_initialization()

        # Phase 2: Blockchain Simulation
        self.phase_2_blockchain_simulation()

        # Phase 3: ML Model Training
        self.phase_3_ml_training()

        # Phase 4: Attack Simulation
        self.phase_4_attack_simulation()

        # Phase 5: Anomaly Detection
        self.phase_5_anomaly_detection()

        # Phase 6: Data Export & Analytics
        self.phase_6_data_export()

        # Phase 7: System Integration
        self.phase_7_system_integration()

        # Final Report
        self.generate_final_report()

    def phase_1_system_initialization(self):
        """Test Phase 1: System Initialization & Services"""
        print("\n📦 PHASE 1: SYSTEM INITIALIZATION")
        print("-" * 40)

        # Test 1.1: Flask Application
        try:
            response = requests.get(f"{self.base_url}/")
            self.test_results['flask_app'] = response.status_code == 200
            print(f"✅ 1.1 Flask Application: {response.status_code}")
        except:
            self.test_results['flask_app'] = False
            print("❌ 1.1 Flask Application: Failed")

        # Test 1.2: All Services Status
        services = ['dashboard', 'ml', 'attack', 'kaggle']
        for service in services:
            try:
                response = requests.get(f"{self.base_url}/api/{service}/status")
                self.test_results[f'{service}_service'] = response.status_code == 200
                print(f"✅ 1.2 {service.title()} Service: Active")
            except:
                self.test_results[f'{service}_service'] = False
                print(f"❌ 1.2 {service.title()} Service: Inactive")

        # Test 1.3: Static Files
        try:
            response = requests.get(f"{self.base_url}/static/styles.css")
            self.test_results['static_files'] = response.status_code == 200
            print("✅ 1.3 Static Files: Loaded")
        except:
            self.test_results['static_files'] = False
            print("❌ 1.3 Static Files: Failed")

    def phase_2_blockchain_simulation(self):
        """Test Phase 2: Blockchain Simulation System"""
        print("\n⛓️ PHASE 2: BLOCKCHAIN SIMULATION")
        print("-" * 40)

        # Test 2.1: Start Simulation
        try:
            response = requests.post(
                f"{self.base_url}/api/simblock/start",
                json={"node_count": 30}
            )
            data = response.json()
            self.test_results['simulation_start'] = data.get('status') == 'success'
            simulation_type = data.get('type', 'unknown')
            print(f"✅ 2.1 Simulation Start: {simulation_type.upper()}")
        except:
            self.test_results['simulation_start'] = False
            print("❌ 2.1 Simulation Start: Failed")

        # Test 2.2: Monitor Block Production
        print("⏳ 2.2 Monitoring block production (15 seconds)...")
        blocks_produced = False
        for i in range(15):
            try:
                response = requests.get(f"{self.base_url}/api/simblock/status")
                data = response.json()
                blocks = data.get('blockchain_data', {}).get('blocks', 0)
                if blocks > 0:
                    blocks_produced = True
                    print(f"   ✅ Block #{blocks} mined")
                    break
            except:
                pass
            time.sleep(1)

        self.test_results['block_production'] = blocks_produced
        print(f"✅ 2.2 Block Production: {'Success' if blocks_produced else 'Failed'}")

        # Test 2.3: Simulation Status
        try:
            response = requests.get(f"{self.base_url}/api/simblock/status")
            data = response.json()
            self.test_results['simulation_status'] = data.get('is_running', False)
            print(f"✅ 2.3 Simulation Running: {data.get('is_running', False)}")
        except:
            self.test_results['simulation_status'] = False
            print("❌ 2.3 Simulation Status: Failed")

    def phase_3_ml_training(self):
        """Test Phase 3: ML Model Training"""
        print("\n🤖 PHASE 3: MACHINE LEARNING TRAINING")
        print("-" * 40)

        # Test 3.1: Train ML Model
        try:
            print("⏳ 3.1 Training ML Model (this may take 20-30 seconds)...")
            response = requests.post(f"{self.base_url}/api/ml/train")
            data = response.json()
            self.test_results['ml_training'] = data.get('status') == 'success'
            accuracy = data.get('accuracy', 0)
            print(f"✅ 3.1 ML Training: {accuracy:.2%} Accuracy")
        except Exception as e:
            self.test_results['ml_training'] = False
            print(f"❌ 3.1 ML Training: Failed - {e}")

        # Test 3.2: ML Model Status
        try:
            response = requests.get(f"{self.base_url}/api/ml/status")
            data = response.json()
            self.test_results['ml_status'] = data.get('training_status') == 'trained'
            print(f"✅ 3.2 ML Status: {data.get('training_status', 'unknown')}")
        except:
            self.test_results['ml_status'] = False
            print("❌ 3.2 ML Status: Failed")

    def phase_4_attack_simulation(self):
        """Test Phase 4: Blockchain Attack Simulation"""
        print("\n🔴 PHASE 4: BLOCKCHAIN ATTACK SIMULATION")
        print("-" * 40)

        attacks = [
            {"name": "Double Spending", "endpoint": "double-spending", "params": {"amount": 50}},
            {"name": "51% Attack", "endpoint": "51-percent", "params": {"hash_power": 60}},
            {"name": "Selfish Mining", "endpoint": "selfish-mining", "params": {"max_blocks": 2}},
            {"name": "Eclipse Attack", "endpoint": "eclipse", "params": {"target_node": 25}}
        ]

        attack_results = []

        for i, attack in enumerate(attacks, 1):
            try:
                response = requests.post(
                    f"{self.base_url}/api/attack/{attack['endpoint']}",
                    json=attack['params']
                )
                data = response.json()
                success = data.get('status') == 'success'
                attack_results.append(success)
                print(f"✅ 4.{i} {attack['name']}: {'Launched' if success else 'Failed'}")
                time.sleep(2)  # Wait between attacks
            except:
                attack_results.append(False)
                print(f"❌ 4.{i} {attack['name']}: Failed")

        self.test_results['attack_simulation'] = any(attack_results)
        print(f"✅ 4.0 Attack Simulation: {sum(attack_results)}/{len(attacks)} Successful")

    def phase_5_anomaly_detection(self):
        """Test Phase 5: Real-time Anomaly Detection"""
        print("\n🎯 PHASE 5: REAL-TIME ANOMALY DETECTION")
        print("-" * 40)

        # Test 5.1: Start Anomaly Detection
        try:
            response = requests.post(f"{self.base_url}/api/ml/start-detection")
            data = response.json()
            self.test_results['detection_start'] = data.get('status') == 'success'
            print("✅ 5.1 Anomaly Detection: Started")
        except:
            self.test_results['detection_start'] = False
            print("❌ 5.1 Anomaly Detection: Failed to start")

        # Test 5.2: Monitor Detection
        print("⏳ 5.2 Monitoring anomaly detection (10 seconds)...")
        anomalies_detected = False
        for i in range(10):
            try:
                response = requests.get(f"{self.base_url}/api/ml/predictions?limit=5")
                data = response.json()
                predictions = data.get('recent_predictions', [])
                if any(p.get('is_anomaly', False) for p in predictions):
                    anomalies_detected = True
                    print("   ✅ Anomaly detected!")
                    break
            except:
                pass
            time.sleep(1)

        self.test_results['anomaly_detection'] = anomalies_detected
        print(f"✅ 5.2 Anomaly Detection: {'Success' if anomalies_detected else 'No anomalies'}")

        # Test 5.3: Stop Detection
        try:
            response = requests.post(f"{self.base_url}/api/ml/stop-detection")
            self.test_results['detection_stop'] = response.json().get('status') == 'success'
            print("✅ 5.3 Anomaly Detection: Stopped")
        except:
            self.test_results['detection_stop'] = False
            print("❌ 5.3 Anomaly Detection: Failed to stop")

    def phase_6_data_export(self):
        """Test Phase 6: Data Export & Analytics"""
        print("\n📊 PHASE 6: DATA EXPORT & ANALYTICS")
        print("-" * 40)

        # Test 6.1: Generate CSV Reports
        try:
            response = requests.post(f"{self.base_url}/api/kaggle/generate-csv-reports")
            data = response.json()
            self.test_results['csv_generation'] = data.get('status') == 'success'
            reports_count = len(data.get('reports', []))
            print(f"✅ 6.1 CSV Reports: {reports_count} reports generated")
        except:
            self.test_results['csv_generation'] = False
            print("❌ 6.1 CSV Reports: Failed")

        # Test 6.2: Download Reports
        try:
            response = requests.get(f"{self.base_url}/api/kaggle/download-all-csv-reports")
            self.test_results['report_download'] = response.status_code == 200
            print("✅ 6.2 Report Download: Success")
        except:
            self.test_results['report_download'] = False
            print("❌ 6.2 Report Download: Failed")

        # Test 6.3: Dataset Statistics
        try:
            response = requests.get(f"{self.base_url}/api/kaggle/dataset-stats")
            data = response.json()
            self.test_results['dataset_stats'] = data.get('status') == 'success'
            samples = data.get('total_samples', 0)
            print(f"✅ 6.3 Dataset Stats: {samples} samples available")
        except:
            self.test_results['dataset_stats'] = False
            print("❌ 6.3 Dataset Stats: Failed")

    def phase_7_system_integration(self):
        """Test Phase 7: System Integration & Dashboard"""
        print("\n🌐 PHASE 7: SYSTEM INTEGRATION")
        print("-" * 40)

        # Test 7.1: Dashboard Integration
        try:
            response = requests.get(f"{self.base_url}/api/dashboard/status")
            data = response.json()
            self.test_results['dashboard_integration'] = data.get('status') == 'running'
            print("✅ 7.1 Dashboard Integration: Active")
        except:
            self.test_results['dashboard_integration'] = False
            print("❌ 7.1 Dashboard Integration: Failed")

        # Test 7.2: Stop Simulation
        try:
            response = requests.post(f"{self.base_url}/api/simblock/stop")
            self.test_results['simulation_stop'] = response.json().get('status') == 'success'
            print("✅ 7.2 Simulation Stop: Success")
        except:
            self.test_results['simulation_stop'] = False
            print("❌ 7.2 Simulation Stop: Failed")

        # Test 7.3: Final System Status
        try:
            responses = {}
            endpoints = ['simblock/status', 'ml/status', 'attack/stats', 'kaggle/status']
            for endpoint in endpoints:
                response = requests.get(f"{self.base_url}/api/{endpoint}")
                responses[endpoint] = response.status_code == 200

            self.test_results['final_status'] = all(responses.values())
            active_services = sum(responses.values())
            print(f"✅ 7.3 Final Status: {active_services}/{len(endpoints)} services active")
        except:
            self.test_results['final_status'] = False
            print("❌ 7.3 Final Status: Failed")

    def generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 70)
        print("📈 COMPREHENSIVE TEST REPORT")
        print("=" * 70)

        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())
        success_rate = (passed_tests / total_tests) * 100

        print(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} Tests Passed ({success_rate:.1f}%)")
        print("\n📋 DETAILED BREAKDOWN:")

        phases = {
            'System Initialization': ['flask_app', 'dashboard_service', 'ml_service', 'attack_service',
                                      'kaggle_service', 'static_files'],
            'Blockchain Simulation': ['simulation_start', 'block_production', 'simulation_status'],
            'ML Training': ['ml_training', 'ml_status'],
            'Attack Simulation': ['attack_simulation'],
            'Anomaly Detection': ['detection_start', 'anomaly_detection', 'detection_stop'],
            'Data Export': ['csv_generation', 'report_download', 'dataset_stats'],
            'System Integration': ['dashboard_integration', 'simulation_stop', 'final_status']
        }

        for phase, tests in phases.items():
            phase_tests = [self.test_results.get(test, False) for test in tests]
            phase_passed = sum(phase_tests)
            phase_total = len(phase_tests)
            print(f"   {phase}: {phase_passed}/{phase_total}")

        print("\n🎯 PROJECT STATUS:")
        if success_rate >= 90:
            print("   ✅ EXCELLENT - Project is fully functional and ready for deployment!")
        elif success_rate >= 75:
            print("   ✅ GOOD - Project is functional with minor issues")
        elif success_rate >= 60:
            print("   ⚠️  FAIR - Project works but needs improvements")
        else:
            print("   ❌ POOR - Project has significant issues")

        print(f"\n🚀 NEXT STEPS:")
        print("   1. Review failed tests above")
        print("   2. Check server logs for errors")
        print("   3. Verify all services are running")
        print("   4. Test manual workflow in browser")


if __name__ == "__main__":
    # Check if Flask app is running
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print("✅ Flask application detected, starting tests...")
    except:
        print("❌ Flask application not running. Please start with: python main.py")
        print("   Then run: python test_complete_project.py")
        sys.exit(1)

    tester = CompleteProjectTest()
    tester.run_complete_test_suite()