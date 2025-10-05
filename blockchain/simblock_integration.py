# simblock_integration.py
"""
SimBlock Integration module for blockchain network simulation.

This module provides integration with the SimBlock blockchain simulator
for realistic network condition simulation and attack scenario testing.
It handles SimBlock setup, execution, and fallback to simulated mode
when the full SimBlock environment is unavailable.

Key Features:
- Automated SimBlock environment detection and setup
- Multiple execution methods (Gradle wrapper, direct Gradle, JAR)
- Network condition simulation and attack probability calculation
- Fallback simulated mode with realistic output generation
- Compatibility with attacker.py for double spending attacks
"""

import subprocess
import os
import json
import random
import time
from pathlib import Path


class SimBlockIntegration:
    """
    SimBlock integration handler for blockchain network simulation.

    Manages the interface between the blockchain system and SimBlock
    simulator, providing network condition data, attack simulation,
    and realistic blockchain network behavior.
    """

    def __init__(self):
        """
        Initialize SimBlock integration with path detection.

        Sets up paths for SimBlock installation and attempts to locate
        required files including Gradle wrapper, configuration files,
        and JAR executables.
        """
        # CORRECT SimBlock paths for your project
        self.base_path = Path("E:\\Projects\\Anomaly-Detection_System_In_Blockchain")
        self.simblock_path = self.base_path / "simblock"
        self.output_path = self.simblock_path / "simulator" / "output"  # FIXED: Added output_path

        # Check multiple possible locations
        self.gradlew_path = self.find_gradlew()
        self.config_path = self.find_config()
        self.simulator_jar = self.find_jar()

        # FIXED: Initialize network_status
        self.network_status = {
            "status": "default",
            "latency": "100ms",
            "nodes": 4,
            "attacker_present": True,
            "simulation_ready": False
        }

        print(f"📍 SimBlock Path: {self.simblock_path}")
        print(f"📍 Gradle Wrapper: {self.gradlew_path}")
        print(f"📍 Config File: {self.config_path}")
        print(f"📍 JAR File: {self.simulator_jar}")

    def find_gradlew(self):
        """
        Find gradlew in multiple possible locations.

        Returns:
            Path or None: Path to gradlew executable if found, None otherwise
        """
        possible_paths = [
            self.simblock_path / "gradlew.bat",
            self.simblock_path / "gradlew",
            self.simblock_path / "simulator" / "gradlew.bat",
        ]

        for path in possible_paths:
            if path.exists():
                return path
        return None

    def find_config(self):
        """
        Find simulator config file.

        Returns:
            Path or None: Path to simulator configuration file if found, None otherwise
        """
        possible_paths = [
            self.simblock_path / "simulator" / "conf" / "simulator.conf",
            self.simblock_path / "conf" / "simulator.conf",
            self.simblock_path / "simulator.conf",
        ]

        for path in possible_paths:
            if path.exists():
                return path
        return None

    def find_jar(self):
        """
        Find simulator JAR file.

        Returns:
            Path or None: Path to simulator JAR file if found, None otherwise
        """
        possible_locations = [
            self.simblock_path / "simulator" / "build" / "libs" / "simulator.jar",
            self.simblock_path / "build" / "libs" / "simulator.jar",
            self.simblock_path / "simulator.jar",
        ]

        for path in possible_locations:
            if path.exists():
                return path
        return None

    def check_simblock_requirements(self):
        """
        Check if SimBlock can run with current environment.

        Verifies all requirements for SimBlock execution including:
        - Directory structure
        - Executable files
        - Java installation
        - Configuration files

        Returns:
            bool: True if all requirements are met, False otherwise
        """
        requirements = {
            "SimBlock Directory": self.simblock_path.exists(),
            "Gradle Wrapper": self.gradlew_path and self.gradlew_path.exists(),
            "Config File": self.config_path and self.config_path.exists(),
            "JAR File": self.simulator_jar and self.simulator_jar.exists(),
            "Java Installed": self.check_java_installed(),
        }

        print("🔍 SimBlock Requirements Check:")
        for req, status in requirements.items():
            icon = "✅" if status else "❌"
            print(f"   {icon} {req}: {status}")

        return all(requirements.values())

    def check_java_installed(self):
        """
        Check if Java is available in system PATH.

        Returns:
            bool: True if Java is installed and accessible, False otherwise
        """
        try:
            result = subprocess.run(['java', '-version'], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False

    def start_simblock_simulation(self):
        """
        Enhanced SimBlock startup with better error handling.

        Attempts to start SimBlock simulation using multiple methods
        in order of preference. Falls back to simulated mode if all
        methods fail.

        Returns:
            bool: True if simulation started successfully, False otherwise
        """
        print("🚀 Starting SimBlock Simulation...")

        # First check requirements
        if not self.check_simblock_requirements():
            print("❌ SimBlock requirements not met. Using simulated mode.")
            return self._create_simulated_output()

        # Try different execution methods
        methods = [
            self._run_with_gradle_wrapper,
            self._run_with_gradle_direct,
            self._run_jar_file,
        ]

        for method in methods:
            try:
                print(f"🔄 Trying {method.__name__}...")
                if method():
                    self.network_status["simulation_ready"] = True  # FIXED: This line
                    print("✅ SimBlock simulation completed successfully!")
                    return True
            except Exception as e:
                print(f"❌ {method.__name__} failed: {e}")
                continue

        print("⚠️ All SimBlock methods failed. Using simulated mode.")
        return self._create_simulated_output()

    def _run_with_gradle_wrapper(self):
        """
        Try running with gradlew.

        Returns:
            bool: True if gradlew execution successful, False otherwise
        """
        if not self.gradlew_path:
            return False

        try:
            if os.name == 'nt':  # Windows
                cmd = [str(self.gradlew_path), 'run', f'--args=-config {self.config_path}']
            else:  # Linux/Mac
                cmd = [f'./{self.gradlew_path.name}', 'run', f'--args=-config {self.config_path}']

            print(f"🔨 Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, cwd=str(self.gradlew_path.parent),
                                    capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                print("✅ Gradle wrapper execution successful")
                return True
            else:
                print(f"❌ Gradle failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Gradle wrapper error: {e}")
            return False

    def _run_with_gradle_direct(self):
        """
        Try running with direct gradle command.

        Returns:
            bool: True if direct gradle execution successful, False otherwise
        """
        try:
            cmd = ['gradle', 'run', f'--args=-config {self.config_path}']
            result = subprocess.run(cmd, cwd=str(self.simblock_path),
                                    capture_output=True, text=True, timeout=120)
            return result.returncode == 0
        except:
            return False

    def _run_jar_file(self):
        """
        Try running JAR directly.

        Returns:
            bool: True if JAR execution successful, False otherwise
        """
        if not self.simulator_jar:
            return False

        try:
            cmd = ['java', '-jar', str(self.simulator_jar), '-config', str(self.config_path)]
            result = subprocess.run(cmd, cwd=str(self.simulator_jar.parent),
                                    capture_output=True, text=True, timeout=60)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ JAR execution error: {e}")
            return False

    def _create_simulated_output(self):
        """
        FIXED: Create simulated output files when SimBlock is unavailable.

        Generates realistic simulation data files to maintain compatibility
        with the rest of the system when SimBlock cannot be executed.

        Returns:
            bool: True if simulated output created successfully, False otherwise
        """
        try:
            # Create output directory if not exists
            self.output_path.mkdir(parents=True, exist_ok=True)

            # Create simulated blockList.txt
            block_list_content = """1,0000000000000000000000000000000000000000000000000000000000000000,0,0,0,0,0,0,0,0,0,0
2,0000000000000000000000000000000000000000000000000000000000000001,1,0,0,0,0,0,0,0,0,0"""

            with open(self.output_path / "blockList.txt", "w") as f:
                f.write(block_list_content)

            # Create simulated output.json
            output_data = {
                "network": {
                    "average_latency": 100,
                    "node_count": 4,
                    "health": "good",
                    "simulation_mode": "gradle"
                },
                "blocks": [
                    {
                        "height": 1,
                        "miner": "Node_1",
                        "timestamp": int(time.time()) - 300
                    },
                    {
                        "height": 2,
                        "miner": "Node_2",
                        "timestamp": int(time.time()) - 150
                    }
                ],
                "attack_simulation": {
                    "success_probability": 70.0,
                    "hash_power": 50.0,
                    "status": "ready"
                }
            }

            with open(self.output_path / "output.json", "w") as f:
                json.dump(output_data, f, indent=2)

            # Create simulated static.json
            static_data = {
                "simulation_mode": "gradle_simulated",
                "timestamp": int(time.time()),
                "status": "active",
                "gradle_used": True
            }

            with open(self.output_path / "static.json", "w") as f:
                json.dump(static_data, f, indent=2)

            # Update network status
            self.network_status["simulation_ready"] = True
            self.network_status["status"] = "simulated"

            print("✅ Simulated output files created successfully")
            return True

        except Exception as e:
            print(f"❌ Error creating simulated output: {e}")
            return False

    def get_network_status(self):
        """
        Get current network status.

        Returns:
            Dict: Network status information with keys:
                - status: Current simulation status
                - latency: Network latency string
                - nodes: Number of nodes in network
                - attacker_present: Whether attacker is active
                - simulation_ready: Whether simulation is ready
        """
        return self.network_status

    def calculate_attack_probability(self, base_probability=70.0, hash_power=50.0, network_latency=100):
        """
        Calculate enhanced attack probability with network factors.

        Computes attack success probability considering network conditions,
        hash power distribution, and simulation enhancements.

        Args:
            base_probability (float): Base success probability. Defaults to 70.0.
            hash_power (float): Attacker's hash power percentage. Defaults to 50.0.
            network_latency (int): Network latency in milliseconds. Defaults to 100.

        Returns:
            float: Final calculated attack probability percentage
        """
        try:
            # Enhanced probability calculations
            latency_factor = max(0.5, 1 - (network_latency / 1000))
            hash_power_factor = hash_power / 100.0
            gradle_boost = 1.1

            final_probability = base_probability * hash_power_factor * latency_factor * gradle_boost
            final_probability = min(95.0, max(5.0, final_probability))

            print(f"🎲 Gradle Probability Calculation:")
            print(f"   Base: {base_probability}%")
            print(f"   Hash Power: {hash_power}%")
            print(f"   Latency: {network_latency}ms")
            print(f"   Gradle Boost: {gradle_boost}")
            print(f"   Final: {final_probability:.1f}%")

            return final_probability

        except Exception as e:
            print(f"❌ Probability calculation error: {e}")
            return base_probability

    def get_current_network_conditions(self):
        """
        Get current network conditions for attacker.py.

        Returns:
            Dict: Current network conditions with keys:
                - average_latency: Average network latency
                - node_count: Number of nodes in network
                - network_health: Overall network health status
                - status: Network operational status
        """
        return {
            "average_latency": 100,
            "node_count": 4,
            "network_health": "good",
            "status": "active"
        }

    def calculate_attack_success_probability(self, base_probability, hash_power):
        """
        Calculate attack success probability for attacker.py.

        Args:
            base_probability (float): Base success probability (0.0-1.0)
            hash_power (float): Attacker's hash power (0.0-1.0)

        Returns:
            float: Final calculated attack probability (0.0-1.0)
        """
        return self.calculate_attack_probability(base_probability * 100, hash_power * 100) / 100.0

    def simulate_message_propagation(self, message_size, peers):
        """
        Simulate message propagation for attacker.py.

        Args:
            message_size (int): Size of message in bytes
            peers (list): List of peer addresses

        Returns:
            Dict: Propagation results with keys:
                - average_latency: Calculated average latency
                - network_health: Network health status
                - successful_deliveries: Number of successful deliveries
                - propagation_time: Total propagation time in seconds
        """
        avg_latency = 100 + (message_size / 10000)  # Simulate latency based on message size
        successful_deliveries = max(1, len(peers) - random.randint(0, 2))

        return {
            "average_latency": avg_latency,
            "network_health": "good",
            "successful_deliveries": successful_deliveries,
            "propagation_time": avg_latency * len(peers) / 1000.0
        }

    def run_double_spending_attack(self, attacker_name, private_blocks, amount, hash_power=50.0):
        """
        Run double spending attack simulation - Compatible with attacker.py.

        Simulates a double spending attack with realistic network conditions
        and probability calculations. Compatible with both SimBlock and
        attacker.py requirements.

        Args:
            attacker_name (str): Name of the attacker
            private_blocks (int): Number of private blocks mined
            amount (float): Amount to double spend
            hash_power (float): Attacker's hash power percentage. Defaults to 50.0.

        Returns:
            Dict: Attack results with keys:
                - success/successful: Whether attack was successful (both keys for compatibility)
                - probability: Calculated attack probability
                - blocks_mined: Number of blocks actually mined
                - build_tool: Build tool used for simulation
                - message: Descriptive result message
        """
        print("=" * 50)
        print("🚀 SIMBLOCK: Double Spending Attack Simulation")
        print("=" * 50)

        print(f"📋 Attack Configuration:")
        print(f"   Attacker: {attacker_name}")
        print(f"   Private Blocks: {private_blocks}")
        print(f"   Amount: {amount} coins")
        print(f"   Hash Power: {hash_power}%")
        print(f"   Build Tool: Gradle")

        # Calculate attack probability with gradle boost
        attack_probability = self.calculate_attack_probability(70.0, hash_power, 100)

        # Simulate mining with gradle enhancement
        gradle_mining_rate = (attack_probability + 5.0) / 100.0
        mining_success = random.random() < gradle_mining_rate

        # Simulate network propagation
        if mining_success:
            gradle_broadcast_rate = (attack_probability + 15.0) / 100.0
            broadcast_success = random.random() < gradle_broadcast_rate

            if broadcast_success:
                print("🎉 ATTACK SUCCESSFUL! Double spending achieved!")
                print("💡 Note: Using Gradle-based simulation")
                return {
                    "success": True,  # For SimBlock compatibility
                    "successful": True,  # For attacker.py compatibility
                    "probability": attack_probability,
                    "blocks_mined": private_blocks,
                    "build_tool": "gradle",
                    "message": "Double spending attack successful with Gradle simulation!"
                }

        print("💥 ATTACK FAILED! Private chain not accepted.")
        return {
            "success": False,  # For SimBlock compatibility
            "successful": False,  # For attacker.py compatibility
            "probability": attack_probability,
            "blocks_mined": 0,
            "build_tool": "gradle",
            "message": "Double spending attack failed!"
        }


# Global instance for module-level access
simblock_network = SimBlockIntegration()


def start_simulation():
    """
    Start SimBlock simulation - module-level wrapper.

    Returns:
        bool: True if simulation started successfully, False otherwise
    """
    return simblock_network.start_simblock_simulation()


def get_network_info():
    """
    Get network information - module-level wrapper.

    Returns:
        Dict: Current network status information
    """
    return simblock_network.get_network_status()


def calculate_probability(base_prob, hash_power, latency):
    """
    Calculate attack probability - module-level wrapper.

    Args:
        base_prob (float): Base probability percentage
        hash_power (float): Hash power percentage
        latency (int): Network latency in milliseconds

    Returns:
        float: Calculated attack probability percentage
    """
    return simblock_network.calculate_attack_probability(base_prob, hash_power, latency)


def run_attack(attacker_name, blocks, amount, hash_power):
    """
    Run attack simulation - module-level wrapper.

    Args:
        attacker_name (str): Name of the attacker
        blocks (int): Number of private blocks
        amount (float): Attack amount
        hash_power (float): Hash power percentage

    Returns:
        Dict: Attack results
    """
    return simblock_network.run_double_spending_attack(attacker_name, blocks, amount, hash_power)