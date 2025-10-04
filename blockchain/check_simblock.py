# check_simblock.py
from simblock_integration import SimBlockIntegration


def diagnose_simblock():
    print("🔧 SimBlock Diagnostic Tool")
    print("=" * 50)

    simblock = SimBlockIntegration()
    simblock.check_simblock_requirements()

    print("\n🚀 Attempting to start SimBlock...")
    success = simblock.start_simblock_simulation()

    if success:
        print("🎉 SimBlock is working correctly!")
    else:
        print("❌ SimBlock needs setup. Using simulated mode.")


if __name__ == "__main__":
    diagnose_simblock()