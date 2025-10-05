# check_simblock.py
"""
SimBlock Diagnostic Tool module.

This module provides diagnostic functionality for checking SimBlock integration
and requirements. It helps identify setup issues and verifies that the
SimBlock simulation environment is properly configured.

The diagnostic tool checks for required files, Java installation, and
attempts to start the SimBlock simulation to verify operational status.
"""

from simblock_integration import SimBlockIntegration


def diagnose_simblock():
    """
    Run comprehensive diagnostic checks on SimBlock integration.

    Performs a complete diagnostic of the SimBlock environment including:
    - Requirement verification
    - File system checks
    - Java installation validation
    - Simulation startup test

    Results are printed to console with clear status indicators.
    """
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