# test_hybrid_fixed.py
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.simblock_service import simblock_service


def test_hybrid_with_fallback():
    """Test hybrid simulation with automatic fallback"""

    print("🧪 HYBRID SIMULATION WITH FALLBACK TEST")
    print("=" * 50)

    # Test 1: Check service initialization
    print("1. ✅ Service Initialization Check:")
    print(f"   - Real SimBlock available: {os.path.exists(simblock_service.jar_path)}")

    # Test 2: Start simulation (will try Real SimBlock first)
    print("\n2. 🚀 Starting Hybrid Simulation...")
    result = simblock_service.start_simulation(node_count=50)

    print(f"   - Initial Status: {result['status']}")
    print(f"   - Initial Type: {result.get('type', 'unknown')}")

    # Test 3: Monitor for fallback
    print("\n3. 🔍 Monitoring for Automatic Fallback...")

    simulation_switched = False

    for i in range(40):  # Monitor for 40 seconds
        status = simblock_service.get_status()
        current_type = status['simulation_type']
        blocks = status['blockchain_data']['blocks']
        transactions = status['blockchain_data']['transactions']

        print(f"   [{i + 1}/40] Type: {current_type} | Blocks: {blocks} | Transactions: {transactions}")

        # Check if simulation switched from real to mock
        if i > 5 and current_type == 'advanced_mock' and not simulation_switched:
            simulation_switched = True
            print("   ✅ SUCCESS: Automatic fallback to Mock Simulation detected!")

        # Simulate attacks for ML testing
        if blocks > 0 and i % 5 == 0:
            simblock_service.mark_block_attack(blocks, "51_percent", True)
            print(f"   🎯 Marked Block #{blocks} for attack testing")

        time.sleep(1)

        # Stop if we have good progress with mock
        if blocks >= 10 and current_type == 'advanced_mock':
            print("   ✅ Mock simulation working perfectly - stopping test")
            break

    # Test 4: Final analysis
    print("\n4. 📊 Final Analysis:")
    final_status = simblock_service.get_status()

    print(f"   - Final Simulation Type: {final_status['simulation_type']}")
    print(f"   - Total Blocks Mined: {final_status['blockchain_data']['blocks']}")
    print(f"   - Total Transactions: {final_status['blockchain_data']['transactions']}")
    print(f"   - Simulation Running: {final_status['is_running']}")

    if final_status['blockchain_data']['blocks'] > 0:
        print("   ✅ SUCCESS: Blockchain simulation is working!")
    else:
        print("   ❌ ISSUE: No blocks were mined")

    # Test 5: Clean stop
    print("\n5. 🛑 Stopping Simulation...")
    stop_result = simblock_service.stop_simulation()
    print(f"   - Stop Result: {stop_result['message']}")


if __name__ == "__main__":
    test_hybrid_with_fallback()