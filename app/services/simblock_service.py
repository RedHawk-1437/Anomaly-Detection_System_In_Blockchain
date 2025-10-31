# [file name]: simblock_service.py

import subprocess
import threading
import time
import os
import re
import random
from datetime import datetime


class SimBlockService:
    def __init__(self):
        self.process = None
        self.is_running = False
        self.simulation_thread = None
        self.output_log = "data/simblock_output.txt"
        self.current_status = "stopped"
        self.blockchain_data = {
            "blocks": 0,
            "nodes": 100,
            "transactions": 0,
            "last_block_time": None,
            "mining_power": 15.6,
            "difficulty": 18500000000000,
            "block_time": 12.5,
            "hash_rate": 15.6,
            "total_size": 0,
            "total_gas_used": 0,
            "average_gas_limit": 30000000,
            "average_base_fee": 10
        }

        # NAYA: Block status tracking system
        self.block_status = {}  # Format: {block_number: "normal", "attack_success", "attack_failed"}
        self.attack_blocks = []  # List of blocks under attack
        self.block_history = []  # Complete block history with status

        os.makedirs("data", exist_ok=True)

    def start_simulation(self, node_count=100):
        """Advanced Mock Simulation - SimBlock Compatible"""
        if self.is_running:
            return {"status": "error", "message": "Simulation already running"}

        print(f"🚀 Starting Advanced Blockchain Simulation...")
        print(f"📊 Network: {node_count} nodes")

        # RESET data for new session
        self.blockchain_data = {
            "blocks": 0,
            "nodes": node_count,
            "transactions": 0,
            "last_block_time": datetime.now().isoformat(),
            "mining_power": 15.6,
            "difficulty": 18500000000000,
            "block_time": 12.5,
            "hash_rate": 15.6,
            "total_size": 0,
            "total_gas_used": 0,
            "average_gas_limit": 30000000,
            "average_base_fee": 10
        }

        # NAYA: Reset block status for new session
        self.block_status = {}
        self.attack_blocks = []
        self.block_history = []

        self.is_running = True
        self.current_status = "running"

        # Create realistic SimBlock-style log file
        with open(self.output_log, "w", encoding="utf-8") as f:
            f.write("=== Blockchain Simulation Started ===\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write(f"Network Size: {node_count} nodes\n")
            f.write("Consensus: Proof of Work\n")
            f.write("Mining Algorithm: SHA-256\n\n")

        # Start advanced simulation in a daemon thread
        self.simulation_thread = threading.Thread(
            target=self._advanced_simulation,
            args=(node_count,),
            daemon=True
        )
        self.simulation_thread.start()

        return {
            "status": "success",
            "message": f"✅ Advanced blockchain simulation started with {node_count} nodes!",
            "type": "advanced_mock",
            "features": ["Real-time blocks", "Node network", "Transaction simulation", "Mining difficulty"]
        }

    def _advanced_simulation(self, node_count):
        """Advanced simulation that mimics SimBlock output"""
        print("🔄 Initializing blockchain network...")

        block_interval = 10  # seconds between blocks
        block_height = 0
        nodes_online = node_count

        with open(self.output_log, "a", encoding="utf-8") as f:
            f.write("🔗 Genesis block created\n")
            f.write("⛏️  Mining started...\n\n")

        # Simulate network initialization
        time.sleep(2)

        while self.is_running:
            try:
                # Mine a new block
                block_height += 1
                mining_node = random.randint(1, node_count)
                block_hash = f"0x{random.randint(1000000, 9999999):x}"

                # NAYA: FIXED - Determine block status DIRECTLY from block_status
                block_status = self.block_status.get(block_height, "normal")

                # Remove from active attack blocks if exists
                if block_height in self.attack_blocks:
                    self.attack_blocks.remove(block_height)

                # Update blockchain data with REAL values
                transactions_in_block = random.randint(3, 8)
                self.blockchain_data["blocks"] = block_height
                self.blockchain_data["transactions"] += transactions_in_block
                self.blockchain_data["last_block_time"] = datetime.now().isoformat()
                self.blockchain_data["mining_power"] = 15.6 + (0.1 * block_height)
                self.blockchain_data["difficulty"] = 18500000000000 + (1000000000 * block_height)
                self.blockchain_data["hash_rate"] = 15.6 + (0.05 * block_height)
                self.blockchain_data["total_size"] += 1024 + (block_height * 100)
                self.blockchain_data["total_gas_used"] += 21000 + (transactions_in_block * 100)
                self.blockchain_data["average_base_fee"] = 10 + (block_height // 10)

                # NAYA: Save block to history with REAL data
                block_info = {
                    "block_number": block_height,
                    "status": block_status,
                    "transactions": transactions_in_block,
                    "miner": mining_node,
                    "timestamp": datetime.now().isoformat(),
                    "hash": block_hash,
                    "difficulty": self.blockchain_data["difficulty"],
                    "size": 1024 + (block_height * 100),
                    "gas_used": 21000 + (transactions_in_block * 100),
                    "gas_limit": 30000000,
                    "base_fee": 10 + (block_height // 10),
                    "is_anomalous": block_status != "normal"
                }
                self.block_history.append(block_info)

                # Write block to log (SimBlock format)
                with open(self.output_log, "a", encoding="utf-8") as f:
                    f.write(f"{block_hash}\n")
                    f.write(f"# STATUS: {block_status.upper()}\n")  # NAYA: Add status to log
                    f.write(f"# BLOCK: {block_height}, TRANSACTIONS: {transactions_in_block}\n")
                    f.write(f"# MINER: Node_{mining_node}, DIFFICULTY: {self.blockchain_data['difficulty']}\n")

                    # Simulate node propagation (SimBlock format)
                    for i in range(random.randint(5, 15)):
                        node_id = random.randint(1, node_count)
                        propagation_time = random.randint(0, 300)
                        f.write(f"{node_id},{propagation_time}\n")

                    f.write("\n")

                # NAYA: FIXED - Use ACTUAL block_status for console output
                if block_status == "attack_success":
                    status_icon = "🔴"
                    print(
                        f"{status_icon} BLOCK #{block_height} - SUCCESSFUL ATTACK DETECTED! | Transactions: {self.blockchain_data['transactions']} | Miner: Node_{mining_node}")
                elif block_status == "attack_failed":
                    status_icon = "🟡"
                    print(
                        f"{status_icon} BLOCK #{block_height} - ATTACK FAILED! | Transactions: {self.blockchain_data['transactions']} | Miner: Node_{mining_node}")
                else:
                    status_icon = "🔗"
                    print(
                        f"{status_icon} Block #{block_height} mined by Node {mining_node} | Status: NORMAL | Transactions: {self.blockchain_data['transactions']}")

                # Random network events
                if block_height % 5 == 0:
                    nodes_online += random.randint(-2, 3)
                    self.blockchain_data["nodes"] = max(50, min(150, nodes_online))
                    print(f"🖥️  Network update: {self.blockchain_data['nodes']} nodes online")

                # Wait for next block
                time.sleep(block_interval)

            except Exception as e:
                print(f"Simulation error: {e}")
                break

        # Simulation ended
        with open(self.output_log, "a", encoding="utf-8") as f:
            f.write(f"\n=== Simulation Completed ===\n")
            f.write(f"Total Blocks: {block_height}\n")
            f.write(f"Total Transactions: {self.blockchain_data['transactions']}\n")
            f.write(f"Final Network Size: {self.blockchain_data['nodes']} nodes\n")

        print("✅ Simulation thread stopped successfully")
        self.is_running = False
        self.current_status = "stopped"

    def mark_block_attack(self, block_number, attack_type, success):
        """NAYA: Mark a block as under attack"""
        status = "attack_success" if success else "attack_failed"
        self.block_status[block_number] = status
        if block_number not in self.attack_blocks:
            self.attack_blocks.append(block_number)

        print(f"🎯 Marking Block #{block_number} for {attack_type} - Success: {success}")
        return True

    def get_block_status(self, block_number):
        """NAYA: Get status of specific block"""
        return self.block_status.get(block_number, "normal")

    def get_blockchain_with_status(self):
        """NAYA: Get blockchain data with block status information"""
        return {
            "blockchain_data": self.blockchain_data,
            "block_status": self.block_status,
            "block_history": self.block_history[-20:],  # Last 20 blocks
            "current_attack_blocks": self.attack_blocks
        }

    def stop_simulation(self):
        """Simulation stop keren"""
        if not self.is_running:
            return {"status": "error", "message": "Simulation not running"}

        print("🛑 Stopping blockchain simulation...")
        self.is_running = False
        self.current_status = "stopped"

        # Wait a bit for the thread to finish gracefully
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=5.0)  # Wait up to 5 seconds

        with open(self.output_log, "a", encoding="utf-8") as f:
            f.write(f"\n=== Simulation Stopped at {datetime.now()} ===\n")

        print("✅ Simulation stopped successfully")
        return {"status": "success", "message": "Simulation stopped"}

    def get_status(self):
        """Get current simulation status"""
        return {
            "status": self.current_status,
            "is_running": self.is_running,
            "blockchain_data": self.blockchain_data
        }

    def get_simulation_state(self):
        """Get complete simulation state for frontend"""
        return {
            "status": self.current_status,
            "is_running": self.is_running,
            "blockchain_data": self.blockchain_data,
            "has_data": self.blockchain_data["blocks"] > 0,
            # NAYA: Add block status information
            "block_status": self.block_status,
            "current_attack_blocks": self.attack_blocks
        }

    def get_latest_logs(self, lines=10):
        """Get latest simulation logs"""
        try:
            with open(self.output_log, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
                return "".join(all_lines[-lines:])
        except:
            return "No logs available yet."


# Global instance
simblock_service = SimBlockService()