# [file name]: attack_service.py

import threading
import time
import random
import json
import os
from datetime import datetime
from enum import Enum


class AttackType(Enum):
    DOUBLE_SPENDING = "double_spending"
    FIFTY_ONE_PERCENT = "51_percent"
    SELFISH_MINING = "selfish_mining"
    ECLIPSE_ATTACK = "eclipse_attack"


class AttackService:
    def __init__(self, simblock_service):
        self.simblock_service = simblock_service
        self.active_attacks = {}
        self.attack_log = "data/attack_logs.json"
        self.attack_stats = {
            "total_attacks": 0,
            "successful_attacks": 0,
            "failed_attacks": 0
        }

        # Initialize attack log file
        self._init_attack_log()

    def _init_attack_log(self):
        """Initialize attack log file"""
        try:
            with open(self.attack_log, 'w') as f:
                json.dump({
                    "attack_history": [],
                    "statistics": self.attack_stats,
                    "created_at": datetime.now().isoformat()
                }, f, indent=2)
        except:
            pass

    def start_attack(self, attack_type, parameters=None):
        """Start a blockchain attack"""
        print(f"🔴 ATTACK START REQUEST: {attack_type.value}")

        # FIX: Check if simulation is running properly
        if not hasattr(self.simblock_service, 'is_running') or not self.simblock_service.is_running:
            error_msg = "Blockchain simulation not running. Please start simulation first."
            print(f"❌ {error_msg}")
            return {"status": "error", "message": error_msg}

        attack_id = f"{attack_type.value}_{int(time.time())}"

        # Get current block number for attack targeting
        current_block = self.simblock_service.blockchain_data["blocks"]
        target_block = current_block + 1  # FIXED: Target NEXT block

        attack_data = {
            "id": attack_id,
            "type": attack_type.value,
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "parameters": parameters or {},
            "target_block": target_block,  # NAYA: Store target block
            "results": {}
        }

        self.active_attacks[attack_id] = attack_data
        self.attack_stats["total_attacks"] += 1

        print(f"🎯 Starting {attack_type.value.replace('_', ' ').title()} on Block #{target_block}...")

        # Start attack in separate thread
        if attack_type == AttackType.DOUBLE_SPENDING:
            thread = threading.Thread(target=self._double_spending_attack, args=(attack_id, parameters, target_block))
        elif attack_type == AttackType.FIFTY_ONE_PERCENT:
            thread = threading.Thread(target=self._fifty_one_percent_attack, args=(attack_id, parameters, target_block))
        elif attack_type == AttackType.SELFISH_MINING:
            thread = threading.Thread(target=self._selfish_mining_attack, args=(attack_id, parameters, target_block))
        elif attack_type == AttackType.ECLIPSE_ATTACK:
            thread = threading.Thread(target=self._eclipse_attack, args=(attack_id, parameters, target_block))

        thread.daemon = True
        thread.start()

        self._log_attack(attack_data)

        return {
            "status": "success",
            "message": f"{attack_type.value.replace('_', ' ').title()} started on Block #{target_block}!",
            "attack_id": attack_id,
            "target_block": target_block
        }

    def _double_spending_attack(self, attack_id, parameters, target_block):
        """Double Spending Attack Implementation"""
        print(f"💸 Double Spending Attack: Targeting Block #{target_block}...")

        attack_data = self.active_attacks[attack_id]

        try:
            # Simulate double spending scenario
            victim_amount = parameters.get('amount', 100)
            attacker_nodes = parameters.get('attacker_nodes', 5)

            # Step 1: Create legitimate transaction
            time.sleep(1)
            attack_data["results"]["legitimate_tx"] = {
                "tx_id": f"tx_legit_{int(time.time())}",
                "amount": victim_amount,
                "recipient": "Victim_Wallet",
                "timestamp": datetime.now().isoformat()
            }

            print(f"💸 Legitimate transaction created: {victim_amount} coins to Victim")

            # Step 2: Create conflicting transaction
            time.sleep(1)
            attack_data["results"]["malicious_tx"] = {
                "tx_id": f"tx_mal_{int(time.time())}",
                "amount": victim_amount,
                "recipient": "Attacker_Shadow_Wallet",
                "timestamp": datetime.now().isoformat()
            }

            print(f"🕵️‍♂️ Malicious transaction created: {victim_amount} coins to Shadow Wallet")

            # Step 3: Try to get both transactions confirmed
            success = random.random() > 0.3  # 70% success rate

            # Mark the target block with attack result
            self.simblock_service.mark_block_attack(target_block, "double_spending", success)

            if success:
                attack_data["results"]["success"] = True
                attack_data["results"]["method"] = "Race Attack"
                attack_data["status"] = "success"
                self.attack_stats["successful_attacks"] += 1
                print(f"✅ Double Spending Attack SUCCESSFUL on Block #{target_block}!")
            else:
                attack_data["results"]["success"] = False
                attack_data["results"]["detected_by"] = "Network Consensus"
                attack_data["status"] = "failed"
                self.attack_stats["failed_attacks"] += 1
                print(f"❌ Double Spending Attack FAILED on Block #{target_block}!")

            attack_data["end_time"] = datetime.now().isoformat()
            self._log_attack(attack_data)

            # Remove from active attacks after completion
            time.sleep(2)
            if attack_id in self.active_attacks:
                del self.active_attacks[attack_id]

        except Exception as e:
            attack_data["status"] = "error"
            attack_data["error"] = str(e)
            self._log_attack(attack_data)

    def _fifty_one_percent_attack(self, attack_id, parameters, target_block):
        """51% Attack Implementation """
        print(f"⚡ 51% Attack: Targeting Block #{target_block}...")

        attack_data = self.active_attacks[attack_id]

        try:
            hash_power = parameters.get('hash_power', 55)
            duration = parameters.get('duration', 20)

            attack_data["results"]["hash_power"] = hash_power
            attack_data["results"]["duration"] = duration

            print(f"⛏️  Attacker hash power: {hash_power}%")

            # Determine success based on hash power
            success = hash_power > 50 and random.random() > 0.2

            # Mark the target block with attack result
            self.simblock_service.mark_block_attack(target_block, "51_percent", success)

            attack_data["results"]["success"] = success

            if success:
                attack_data["status"] = "success"
                self.attack_stats["successful_attacks"] += 1
                print(f"✅ 51% Attack SUCCESSFUL on Block #{target_block}! Network controlled!")
            else:
                attack_data["status"] = "failed"
                self.attack_stats["failed_attacks"] += 1
                print(f"❌ 51% Attack FAILED on Block #{target_block}! Insufficient hash power!")

            attack_data["end_time"] = datetime.now().isoformat()
            self._log_attack(attack_data)

            # Remove from active attacks after completion
            time.sleep(2)
            if attack_id in self.active_attacks:
                del self.active_attacks[attack_id]

        except Exception as e:
            attack_data["status"] = "error"
            attack_data["error"] = str(e)
            self._log_attack(attack_data)

    def _selfish_mining_attack(self, attack_id, parameters, target_block):
        """Selfish Mining Attack Implementation """
        print(f"🤫 Selfish Mining: Targeting Block #{target_block}...")

        attack_data = self.active_attacks[attack_id]

        try:
            secret_blocks = 0
            max_secret_blocks = parameters.get('max_blocks', 2)

            attack_data["results"]["strategy"] = "Withhold blocks and release strategically"

            # Simulate selfish mining
            for i in range(3):
                if not self.simblock_service.is_running:
                    break

                time.sleep(3)

                # Decide whether to publish or withhold
                if secret_blocks < max_secret_blocks and random.random() > 0.4:
                    secret_blocks += 1
                    print(
                        f"🕵️‍♂️ Secretly mined block #{self.simblock_service.blockchain_data['blocks'] + secret_blocks} (Total secret: {secret_blocks})")
                else:
                    if secret_blocks > 0:
                        print(f"📤 Releasing {secret_blocks} secret blocks to network!")
                        attack_data["results"]["blocks_withheld"] = secret_blocks
                        secret_blocks = 0

            success = secret_blocks > 0 or random.random() > 0.5

            # Mark the target block with attack result
            self.simblock_service.mark_block_attack(target_block, "selfish_mining", success)

            attack_data["results"]["success"] = success

            if success:
                attack_data["status"] = "success"
                self.attack_stats["successful_attacks"] += 1
                print(f"✅ Selfish Mining SUCCESSFUL on Block #{target_block}! Revenue increased!")
            else:
                attack_data["status"] = "failed"
                self.attack_stats["failed_attacks"] += 1
                print(f"❌ Selfish Mining FAILED on Block #{target_block}! No advantage gained!")

            attack_data["end_time"] = datetime.now().isoformat()
            self._log_attack(attack_data)

            # Remove from active attacks after completion
            time.sleep(2)
            if attack_id in self.active_attacks:
                del self.active_attacks[attack_id]

        except Exception as e:
            attack_data["status"] = "error"
            attack_data["error"] = str(e)
            self._log_attack(attack_data)

    def _eclipse_attack(self, attack_id, parameters, target_block):
        """Eclipse Attack Implementation """
        print(f"🌑 Eclipse Attack: Targeting Block #{target_block}...")

        attack_data = self.active_attacks[attack_id]

        try:
            target_node = parameters.get('target_node', 25)
            attacker_nodes = parameters.get('attacker_nodes', 8)
            isolation_time = parameters.get('isolation_time', 15)

            attack_data["results"]["target_node"] = target_node
            attack_data["results"]["attacker_nodes"] = attacker_nodes

            print(f"🎯 Targeting Node {target_node} with {attacker_nodes} attacker nodes")

            # Check if attack was successful
            success = random.random() > 0.2  # 80% success rate

            # Mark the target block with attack result
            self.simblock_service.mark_block_attack(target_block, "eclipse_attack", success)

            attack_data["results"]["success"] = success

            if success:
                attack_data["status"] = "success"
                self.attack_stats["successful_attacks"] += 1
                print(f"✅ Eclipse Attack SUCCESSFUL on Block #{target_block}! Node {target_node} completely isolated!")
            else:
                attack_data["status"] = "failed"
                self.attack_stats["failed_attacks"] += 1
                print(f"❌ Eclipse Attack FAILED on Block #{target_block}! Node {target_node} reconnected!")

            attack_data["end_time"] = datetime.now().isoformat()
            self._log_attack(attack_data)

            # Remove from active attacks after completion
            time.sleep(2)
            if attack_id in self.active_attacks:
                del self.active_attacks[attack_id]

        except Exception as e:
            attack_data["status"] = "error"
            attack_data["error"] = str(e)
            self._log_attack(attack_data)

    def _log_attack(self, attack_data):
        """Log attack data to file"""
        try:
            os.makedirs("data", exist_ok=True)

            clean_data = {}

            for key, value in attack_data.items():
                if key == 'parameters' and isinstance(value, dict):
                    clean_data[key] = {}
                    for param_key, param_value in value.items():
                        if hasattr(param_value, 'item'):
                            clean_data[key][param_key] = param_value.item()
                        elif isinstance(param_value, (int, float, str, bool, type(None))):
                            clean_data[key][param_key] = param_value
                        else:
                            clean_data[key][param_key] = str(param_value)
                elif hasattr(value, 'item'):
                    clean_data[key] = value.item()
                elif isinstance(value, (int, float, str, bool, type(None), dict, list)):
                    clean_data[key] = value
                else:
                    clean_data[key] = str(value)

            if os.path.exists(self.attack_log):
                try:
                    with open(self.attack_log, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except:
                    data = {
                        "attack_history": [],
                        "statistics": self.attack_stats,
                        "created_at": datetime.now().isoformat()
                    }
            else:
                data = {
                    "attack_history": [],
                    "statistics": self.attack_stats,
                    "created_at": datetime.now().isoformat()
                }

            data["attack_history"].append(clean_data)
            data["statistics"] = {
                "total_attacks": int(self.attack_stats["total_attacks"]),
                "successful_attacks": int(self.attack_stats["successful_attacks"]),
                "failed_attacks": int(self.attack_stats["failed_attacks"])
            }
            data["updated_at"] = datetime.now().isoformat()

            with open(self.attack_log, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Error logging attack: {e}")

    def get_active_attacks(self):
        """Get currently running attacks"""
        return list(self.active_attacks.values())

    def get_attack_stats(self):
        """Get attack statistics"""
        return self.attack_stats

    def stop_attack(self, attack_id):
        """Stop a specific attack"""
        if attack_id in self.active_attacks:
            self.active_attacks[attack_id]["status"] = "stopped"
            self.active_attacks[attack_id]["end_time"] = datetime.now().isoformat()
            self._log_attack(self.active_attacks[attack_id])
            del self.active_attacks[attack_id]
            return {"status": "success", "message": "Attack stopped"}
        return {"status": "error", "message": "Attack not found"}