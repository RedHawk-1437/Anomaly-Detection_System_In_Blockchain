# [file name]: simblock_service.py - HYBRID REAL + MOCK SIMULATION
"""
Hybrid Blockchain Simulation Service
- First tries to run Real SimBlock simulation
- Falls back to Advanced Mock Simulation if Real SimBlock fails
- Provides seamless experience for the user
"""

import subprocess
import threading
import time
import os
import json
import random
import re
from datetime import datetime


class HybridSimBlockService:
    def __init__(self):
        # Simulation state
        self.process = None
        self.is_running = False
        self.simulation_thread = None
        self.using_real_simblock = False

        # File paths
        self.output_log = "data/simblock_output.txt"
        self.simblock_dir = "simblock"
        self.jar_path = "simblock/simulator/build/libs/simulator.jar"
        self.config_path = "simblock/simblock-config.json"

        # Blockchain data structure
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

        # Block tracking system
        self.block_status = {}
        self.attack_blocks = []
        self.block_history = []
        self.transaction_pool = []
        self.transaction_history = []

        # Ensure directories exist
        os.makedirs("data", exist_ok=True)
        self._ensure_config_file()

    def _ensure_config_file(self):
        """Ensure SimBlock configuration file exists"""
        if not os.path.exists(self.config_path):
            config = {
                "simulation": {
                    "endBlockHeight": 100,
                    "blockInterval": 30000,
                    "nodeCount": 50,
                    "regionAssigned": False,
                    "routingType": "NONE",
                    "latencyType": "CONSTANT",
                    "networkDelay": 100
                },
                "consensus": {
                    "type": "PROOF_OF_WORK",
                    "miningPower": 100,
                    "miningPowerDistribution": "NORMAL"
                }
            }

            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ Created SimBlock configuration file")

    def start_simulation(self, node_count=110):
        """
        Start blockchain simulation
        Priority: Real SimBlock -> Advanced Mock Simulation
        """
        if self.is_running:
            return {"status": "error", "message": "Simulation already running"}

        print(f"🚀 Starting Hybrid Blockchain Simulation...")

        # First try Real SimBlock
        real_result = self._start_real_simblock(node_count)

        if real_result["status"] == "success":
            self.using_real_simblock = True
            return real_result
        else:
            # Fallback to Advanced Mock Simulation
            print("🔄 Real SimBlock unavailable, starting Advanced Mock Simulation...")
            return self._start_advanced_mock(node_count)

    def _start_real_simblock(self, node_count):
        """
        Attempt to start Real SimBlock simulation
        Returns success or error with fallback message
        """
        try:
            # Check if SimBlock JAR exists
            if not os.path.exists(self.jar_path):
                return {
                    "status": "error",
                    "message": "Real SimBlock JAR not found",
                    "fallback_available": True
                }

            # Update configuration with node count
            self._update_simblock_config(node_count)

            print(f"🔧 Starting REAL SimBlock with {node_count} nodes...")

            # Start Real SimBlock process
            cmd = [
                'java', '-jar', self.jar_path,
                '-c', self.config_path,
                '-o', self.output_log
            ]

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            self.is_running = True
            self.using_real_simblock = True

            # Start output monitoring thread
            monitor_thread = threading.Thread(
                target=self._monitor_real_simblock,
                daemon=True
            )
            monitor_thread.start()

            return {
                "status": "success",
                "message": f"✅ Real SimBlock simulation started with {node_count} nodes!",
                "type": "real_simblock",
                "node_count": node_count
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Real SimBlock start failed: {str(e)}",
                "fallback_available": True
            }

    def _update_simblock_config(self, node_count):
        """Update SimBlock configuration with new node count"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)

            config["simulation"]["nodeCount"] = node_count

            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)

        except Exception as e:
            print(f"⚠️ Config update failed: {e}")

    def _monitor_real_simblock(self):
        """Monitor Real SimBlock output and parse blockchain data"""
        print("🔍 Monitoring Real SimBlock output...")

        start_time = time.time()
        real_simblock_failed = False

        while self.is_running and self.process:
            try:
                # Read stdout
                line = self.process.stdout.readline()
                if line:
                    line = line.strip()
                    self._parse_real_simblock_output(line)

                # Read stderr for errors
                err_line = self.process.stderr.readline()
                if err_line:
                    err_line = err_line.strip()
                    if err_line:
                        print(f"❌ SimBlock Error: {err_line}")

                        # Check if it's a critical error that requires fallback
                        if any(error_keyword in err_line.lower() for error_keyword in
                               ['exception', 'error', 'nullpointer', 'initializer']):
                            print("🚨 Critical SimBlock error detected - switching to mock simulation")
                            real_simblock_failed = True
                            break

                # Check if process finished unexpectedly
                if self.process.poll() is not None:
                    print("ℹ️ Real SimBlock process completed unexpectedly")
                    real_simblock_failed = True
                    break

                # Auto-stop after 3 minutes for demo
                if time.time() - start_time > 180:
                    print("⏰ Auto-stopping Real SimBlock after 3 minutes")
                    break

                time.sleep(0.5)

            except Exception as e:
                print(f"Real SimBlock monitor error: {e}")
                real_simblock_failed = True
                break

        # CRITICAL FIX: If Real SimBlock failed, automatically start mock simulation
        if real_simblock_failed and self.is_running:
            print("🔄 Real SimBlock failed - automatically starting Advanced Mock Simulation...")
            self._cleanup_real_simblock()
            self._start_advanced_mock(110)  # Use same node count

    def _cleanup_real_simblock(self):
        """Clean up Real SimBlock resources"""
        try:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)
            self.using_real_simblock = False
        except:
            pass

    def _parse_real_simblock_output(self, line):
        """
        Parse Real SimBlock output and extract blockchain data
        This is where we convert SimBlock output to our blockchain data structure
        """
        try:
            # Log all output for debugging
            if line:
                print(f"📦 Real SimBlock: {line}")

            # Parse block mining events
            if any(keyword in line.lower() for keyword in ['block', 'height', 'mined']):
                self._update_from_real_block(line)

            # Parse transaction events
            elif any(keyword in line.lower() for keyword in ['transaction', 'tx']):
                self._update_from_real_transaction(line)

            # Parse network events
            elif any(keyword in line.lower() for keyword in ['node', 'network']):
                self._update_from_real_network(line)

        except Exception as e:
            print(f"Output parse error: {e}")

    def _update_from_real_block(self, line):
        """Update blockchain data from Real SimBlock block event"""
        self.blockchain_data["blocks"] += 1
        current_block = self.blockchain_data["blocks"]

        # Extract block information from line (you can enhance this parsing)
        block_info = {
            "block_number": current_block,
            "timestamp": datetime.now().isoformat(),
            "transactions": random.randint(1, 8),  # Placeholder - parse from actual data
            "miner": f"node_{random.randint(1, self.blockchain_data['nodes'])}",
            "status": "normal",
            "hash": f"0x{random.getrandbits(256):064x}",
            "difficulty": self.blockchain_data["difficulty"] + (current_block * 1000000),
            "size": 1024 + (current_block * 100),
            "gas_used": 21000 + (random.randint(1, 8) * 100),
            "is_anomalous": False,
            "from_real_simblock": True
        }

        self.block_history.append(block_info)
        self.blockchain_data["last_block_time"] = datetime.now().isoformat()
        self.blockchain_data["transactions"] += block_info["transactions"]

        print(f"🔗 Real Block #{current_block} processed")

    def _update_from_real_transaction(self, line):
        """Update blockchain data from Real SimBlock transaction event"""
        self.blockchain_data["transactions"] += 1

        tx_data = {
            "tx_hash": f"0x{random.getrandbits(160):040x}",
            "block_number": self.blockchain_data["blocks"],
            "from_address": f"0x{random.getrandbits(160):040x}",
            "to_address": f"0x{random.getrandbits(160):040x}",
            "value_eth": round(random.uniform(0.001, 10.0), 6),
            "status": "confirmed",
            "timestamp": datetime.now().isoformat(),
            "from_real_simblock": True
        }

        self.transaction_history.append(tx_data)

    def _update_from_real_network(self, line):
        """Update network statistics from Real SimBlock output"""
        # Parse network information from SimBlock output
        # This can be enhanced with actual parsing logic
        pass

    def _start_advanced_mock(self, node_count):
        """
        Start Advanced Mock Simulation as fallback
        Provides realistic blockchain simulation when Real SimBlock is unavailable
        """
        print(f"🎮 Starting Advanced Mock Simulation with {node_count} nodes...")

        # Reset data for new session
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

        self.block_status = {}
        self.attack_blocks = []
        self.block_history = []
        self.transaction_pool = []
        self.transaction_history = []

        self.is_running = True
        self.using_real_simblock = False

        # Start mock simulation thread
        self.simulation_thread = threading.Thread(
            target=self._advanced_mock_simulation,
            args=(node_count,),
            daemon=True
        )
        self.simulation_thread.start()

        return {
            "status": "success",
            "message": f"✅ Advanced Mock Simulation started with {node_count} nodes!",
            "type": "advanced_mock",
            "node_count": node_count,
            "fallback_used": True
        }

    def _advanced_mock_simulation(self, node_count):
        """
        Advanced Mock Simulation implementation
        Provides realistic blockchain behavior with detailed metrics
        """
        print("🔄 Initializing Advanced Mock Simulation...")

        block_interval = 10  # seconds between blocks
        block_height = 0
        nodes_online = node_count

        # Simulation log
        with open(self.output_log, "w", encoding="utf-8") as f:
            f.write("=== Advanced Mock Simulation Started ===\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write(f"Network Size: {node_count} nodes\n")
            f.write("Consensus: Proof of Work\n\n")

        time.sleep(2)  # Initialization delay

        while self.is_running:
            try:
                # Mine new block
                block_height += 1
                mining_node = random.randint(1, node_count)
                block_hash = f"0x{random.randint(1000000, 9999999):x}"

                # Determine block status
                block_status = self.block_status.get(block_height, "normal")

                # Remove from active attack blocks if exists
                if block_height in self.attack_blocks:
                    self.attack_blocks.remove(block_height)

                # Update blockchain data with realistic values
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

                # Generate transaction data
                block_transactions = self._generate_transaction_data(block_height, transactions_in_block)

                # Save block to history
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
                    "is_anomalous": block_status != "normal",
                    "transactions_data": block_transactions,
                    "from_real_simblock": False
                }
                self.block_history.append(block_info)

                # Write to log
                with open(self.output_log, "a", encoding="utf-8") as f:
                    f.write(f"{block_hash}\n")
                    f.write(f"# STATUS: {block_status.upper()}\n")
                    f.write(f"# BLOCK: {block_height}, TRANSACTIONS: {transactions_in_block}\n")
                    f.write(f"# MINER: Node_{mining_node}, DIFFICULTY: {self.blockchain_data['difficulty']}\n")

                # Console output with status
                if block_status == "attack_success":
                    status_icon = "🔴"
                    print(
                        f"{status_icon} BLOCK #{block_height} - ATTACK SUCCESS! | Transactions: {transactions_in_block}")
                elif block_status == "attack_failed":
                    status_icon = "🟡"
                    print(
                        f"{status_icon} BLOCK #{block_height} - ATTACK FAILED! | Transactions: {transactions_in_block}")
                else:
                    status_icon = "🔗"
                    print(
                        f"{status_icon} Block #{block_height} mined by Node {mining_node} | Transactions: {transactions_in_block}")

                # Random network events
                if block_height % 5 == 0:
                    nodes_online += random.randint(-2, 3)
                    self.blockchain_data["nodes"] = max(50, min(150, nodes_online))
                    print(f"🖥️ Network update: {self.blockchain_data['nodes']} nodes online")

                time.sleep(block_interval)

            except Exception as e:
                print(f"Mock simulation error: {e}")
                break

        # Simulation ended
        with open(self.output_log, "a", encoding="utf-8") as f:
            f.write(f"\n=== Simulation Completed ===\n")
            f.write(f"Total Blocks: {block_height}\n")

        print("✅ Mock simulation thread stopped")
        self.is_running = False

    def _generate_transaction_data(self, block_number, transaction_count):
        """Generate realistic transaction data for a block"""
        transactions = []
        for i in range(transaction_count):
            value_eth = round(random.uniform(0.001, 10.0), 6)
            gas_price = random.randint(10, 100)
            gas_used = random.randint(21000, 100000)
            transaction_fee = round(gas_used * gas_price / 1e9, 8)

            transaction = {
                'tx_hash': f"0x{random.randint(1000000, 9999999):x}{block_number:04d}{i:03d}",
                'block_number': block_number,
                'from_address': f"0x{random.randint(1000, 9999):x}...{random.randint(1000, 9999):x}",
                'to_address': f"0x{random.randint(1000, 9999):x}...{random.randint(1000, 9999):x}",
                'value_eth': value_eth,
                'value_usd': round(value_eth * 3500, 2),
                'gas_price_gwei': gas_price,
                'gas_used': gas_used,
                'transaction_fee_eth': transaction_fee,
                'status': 'success' if random.random() > 0.05 else 'failed',
                'timestamp': datetime.now().isoformat()
            }
            transactions.append(transaction)
            self.transaction_history.append(transaction)
        return transactions

    def stop_simulation(self):
        """Stop current simulation (both Real and Mock)"""
        if not self.is_running:
            return {"status": "error", "message": "Simulation not running"}

        print("🛑 Stopping simulation...")
        self.is_running = False

        # Stop Real SimBlock process
        if self.using_real_simblock and self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                self.process.kill()

        # Log simulation stop
        with open(self.output_log, "a", encoding="utf-8") as f:
            f.write(f"\n=== Simulation Stopped at {datetime.now()} ===\n")

        return {"status": "success", "message": "Simulation stopped"}

    def get_status(self):
        """Get current simulation status"""
        return {
            "status": "running" if self.is_running else "stopped",
            "is_running": self.is_running,
            "using_real_simblock": self.using_real_simblock,
            "blockchain_data": self.blockchain_data,
            "total_blocks": self.blockchain_data["blocks"],
            "total_transactions": self.blockchain_data["transactions"],
            "simulation_type": "real_simblock" if self.using_real_simblock else "advanced_mock"
        }

    def mark_block_attack(self, block_number, attack_type, success):
        """Mark a block as under attack (for ML detection)"""
        status = "attack_success" if success else "attack_failed"
        self.block_status[block_number] = status
        if block_number not in self.attack_blocks:
            self.attack_blocks.append(block_number)

        print(f"🎯 Marking Block #{block_number} for {attack_type} - Success: {success}")
        return True

    def get_block_status(self, block_number):
        """Get status of specific block"""
        return self.block_status.get(block_number, "normal")

    def get_simulation_state(self):
        """Get complete simulation state for frontend"""
        return {
            "status": "running" if self.is_running else "stopped",
            "is_running": self.is_running,
            "using_real_simblock": self.using_real_simblock,
            "blockchain_data": self.blockchain_data,
            "has_data": self.blockchain_data["blocks"] > 0,
            "block_status": self.block_status,
            "current_attack_blocks": self.attack_blocks,
            "total_transactions": len(self.transaction_history),
            "simulation_type": "real_simblock" if self.using_real_simblock else "advanced_mock"
        }


# Global instance
simblock_service = HybridSimBlockService()