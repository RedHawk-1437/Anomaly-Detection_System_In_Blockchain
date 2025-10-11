import time
import requests
import random
from .blockchain import Blockchain
from .transaction import Transaction
from .block import Block
from .simblock_integration import simblock_network


def should_attack_succeed(frontend_config, stage="broadcast"):
    if not frontend_config:
        base_prob = 0.5
        enhanced_prob = simblock_network.calculate_attack_success_probability(base_prob, 0.3)
        return random.random() < enhanced_prob

    if frontend_config.get('forceSuccess'):
        return True
    if frontend_config.get('forceFailure'):
        return False

    base_probability = frontend_config.get('successProbability', 0.5)
    hash_power = frontend_config.get('attackerHashPower', 30) / 100.0

    if stage == "mining":
        mining_success_rate = simblock_network.calculate_attack_success_probability(
            base_probability, hash_power
        )
        final_probability = mining_success_rate

    elif stage == "broadcast":
        network_conditions = simblock_network.get_current_network_conditions()
        latency_factor = min(network_conditions.get('average_latency', 100) / 250, 0.4)

        broadcast_success_rate = simblock_network.calculate_attack_success_probability(
            base_probability, hash_power
        )
        final_probability = min(broadcast_success_rate + latency_factor, 0.95)

    else:
        final_probability = simblock_network.calculate_attack_success_probability(
            base_probability, hash_power
        )

    final_probability = max(0.05, min(0.95, final_probability))
    success = random.random() < final_probability

    return success


def simulate_private_mining(node_url, attacker_addr, blocks_to_mine, amount, frontend_config=None):
    try:
        chain_state = get_current_chain_state(node_url)
        difficulty = chain_state["difficulty"]
        current_index = chain_state["last_block_index"]
        current_hash = chain_state["last_block_hash"]

        print(f"Current chain state: index={current_index}, hash={current_hash[:10]}...")

        mining_success = should_attack_succeed(frontend_config, "mining")

        if not mining_success:
            print(f"Mining failed due to probability/hash power constraints")
            network_info = simblock_network.get_current_network_conditions()
            print(f"   Network conditions: {network_info.get('network_health', 'unknown')}")
            return [], False

        private_bc = Blockchain(difficulty=difficulty)
        private_bc.chain = []

        genesis = Block(index=0, transactions=[], previous_hash="0",
                        timestamp=int(time.time()), nonce=0)
        genesis = private_bc._mine_block_genesis(genesis)
        private_bc.chain.append(genesis)

        if current_index > 0:
            new_index = current_index + 1
            print(f"Creating new block #{new_index} continuing from main chain block #{current_index}")

            attacker_control = f"{attacker_addr}_control"
            tx = Transaction(sender=attacker_addr, receiver=attacker_control, amount=amount)

            new_block = Block(
                index=new_index,
                transactions=[tx],
                previous_hash=current_hash,
                timestamp=int(time.time()),
                nonce=0
            )

            mined_block = private_bc._proof_of_work(new_block)
            private_bc.chain.append(mined_block)

            hash_power = frontend_config.get('attackerHashPower', 30) if frontend_config else 30
            network_info = simblock_network.get_current_network_conditions()
            print(f"Mined private block #{new_index} with {hash_power}% hash power")
            print(f"Block contains {len(mined_block.transactions)} transactions")
            print(f"Network conditions: {network_info.get('network_health', 'unknown')}")

            return [mined_block.to_dict()], True
        else:
            attacker_control = f"{attacker_addr}_control"
            tx = Transaction(sender=attacker_addr, receiver=attacker_control, amount=amount)
            private_bc.mempool.append(tx)

            block = private_bc.mine_pending_transactions(miner_address=attacker_addr)
            hash_power = frontend_config.get('attackerHashPower', 30) if frontend_config else 30
            network_info = simblock_network.get_current_network_conditions()
            print(f"Mined private block #1 with {hash_power}% hash power")
            print(f"Network latency: {network_info.get('average_latency', 100)}ms")
            return [block.to_dict()], True

    except Exception as e:
        print(f"Error in private mining: {e}")
        import traceback
        traceback.print_exc()
        return [], False


def create_private_network(attacker_addr, blocks_to_mine, amount, frontend_config=None):
    """
    Create a private network with 6+ nodes for double spending attack.

    Simulates a private network where the attacker controls 6+ nodes
    to mine private blocks and prepare for double spending attack.

    Args:
        attacker_addr (str): Attacker's wallet address
        blocks_to_mine (int): Number of blocks to mine in private network
        amount (float): Amount to double-spend
        frontend_config (dict, optional): Attack configuration

    Returns:
        dict: Private network simulation results
    """
    print("=" * 60)
    print("CREATING PRIVATE NETWORK WITH 6+ NODES")
    print("=" * 60)

    private_nodes = []
    mined_blocks = []

    # Create 6 private nodes controlled by attacker
    for i in range(6):
        node_id = f"private_node_{i + 1}"
        private_nodes.append({
            "id": node_id,
            "type": "attacker_controlled",
            "region": "PrivateNetwork",
            "mining_power": 0.15,
            "status": "active"
        })

    print(f"Created private network with {len(private_nodes)} nodes:")
    for node in private_nodes:
        print(f"   {node['id']} - {node['type']} - Mining Power: {node['mining_power'] * 100}%")

    # Simulate private mining across the private network
    hash_power = frontend_config.get('attackerHashPower', 25) if frontend_config else 25
    total_hash_power = hash_power + (len(private_nodes) * 15)  # Additional power from private nodes

    print(f"Total effective hash power in private network: {total_hash_power}%")

    # Mine blocks in private network
    for block_num in range(1, blocks_to_mine + 1):
        mining_success = should_attack_succeed(frontend_config, "mining")

        if mining_success:
            # Create double spending transaction in private block
            shadow_wallet = f"{attacker_addr}_shadow"
            tx = Transaction(sender=attacker_addr, receiver=shadow_wallet, amount=amount)

            private_block = {
                "index": block_num,
                "transactions": [tx.to_dict()],
                "miner": f"private_node_{random.randint(1, 6)}",
                "timestamp": int(time.time()),
                "is_private": True,
                "network_size": len(private_nodes)
            }

            mined_blocks.append(private_block)
            print(f"✅ Private block #{block_num} mined by {private_block['miner']}")
            print(f"   Contains double-spending transaction: {attacker_addr} -> {shadow_wallet} ({amount} coins)")
        else:
            print(f"❌ Failed to mine private block #{block_num}")

    return {
        "private_network": private_nodes,
        "mined_blocks": mined_blocks,
        "total_blocks_mined": len(mined_blocks),
        "network_size": len(private_nodes),
        "total_hash_power": total_hash_power,
        "success": len(mined_blocks) >= blocks_to_mine
    }


def broadcast_private_chain(peers, mined_blocks, frontend_config=None):
    results = []

    if not mined_blocks:
        print("No blocks to broadcast")
        return results

    block_size = len(str(mined_blocks)) * 8
    propagation_simulation = simblock_network.simulate_message_propagation(block_size, peers)

    print(f"SimBlock Network Simulation:")
    print(f"   Average latency: {propagation_simulation['average_latency']}ms")
    print(f"   Network health: {propagation_simulation['network_health']}")
    print(f"   Expected successful deliveries: {propagation_simulation['successful_deliveries']}")

    broadcast_success = should_attack_succeed(frontend_config, "broadcast")

    if not broadcast_success:
        print("Broadcast failed due to probability/network constraints")
        for peer in peers:
            results.append({
                "peer": peer,
                "index": mined_blocks[0].get("index"),
                "ok": False,
                "message": f"Broadcast failed - Network: {propagation_simulation['network_health']}",
                "simblock_data": propagation_simulation
            })
        return results

    print(f"Broadcasting {len(mined_blocks)} blocks to {len(peers)} peers")

    for peer in peers:
        for i, block in enumerate(mined_blocks):
            try:
                print(f"   Broadcasting block {i + 1} to {peer}")

                time.sleep(propagation_simulation['propagation_time'] / len(peers))

                r = requests.post(f"{peer}/blocks/receive", json=block, timeout=10)

                result = {
                    "peer": peer,
                    "index": block.get("index"),
                    "ok": r.status_code == 200,
                    "status": r.status_code,
                    "simblock_latency": propagation_simulation['average_latency'],
                    "network_health": propagation_simulation['network_health']
                }

                if r.status_code == 200:
                    result["message"] = r.json().get("message", "Accepted")
                    print(f"   Block accepted by {peer}")
                else:
                    error_msg = r.json().get("error", "Rejected") if r.status_code == 400 else "Rejected"
                    result["message"] = error_msg
                    print(f"   Block rejected by {peer}: {error_msg}")

                results.append(result)

            except Exception as e:
                print(f"   Error broadcasting to {peer}: {e}")
                results.append({
                    "peer": peer,
                    "index": block.get("index"),
                    "ok": False,
                    "error": str(e),
                    "simblock_data": propagation_simulation
                })
    return results


def run_double_spending_attack(attacker_name, private_blocks, amount, hash_power=25.0):
    print("=" * 50)
    print("STARTING DOUBLE SPENDING ATTACK SIMULATION")
    print("=" * 50)

    print(f"Attack Configuration:")
    print(f"   Attacker: {attacker_name}")
    print(f"   Private Blocks: {private_blocks}")
    print(f"   Amount: {amount} coins")
    print(f"   Hash Power: {hash_power}%")

    attack_probability = simblock_network.calculate_attack_probability(70.0, hash_power, 100)

    mining_success = random.random() < (attack_probability / 100.0)

    if mining_success:
        broadcast_success = random.random() < ((attack_probability + 15.0) / 100.0)

        if broadcast_success:
            print("ATTACK SUCCESSFUL! Double spending achieved!")
            return {
                "success": True,
                "successful": True,
                "probability": attack_probability,
                "blocks_mined": private_blocks,
                "message": "Double spending attack successful!"
            }

    print("ATTACK FAILED! Private chain not accepted.")
    return {
        "success": False,
        "successful": False,
        "probability": attack_probability,
        "blocks_mined": 0,
        "message": "Double spending attack failed!"
    }


def calculate_enhanced_probability(base_prob, hash_power, latency):
    try:
        base_prob = float(base_prob)
        hash_power = float(hash_power)
        latency = float(latency)

        hash_factor = (hash_power / 100.0) ** 0.8
        latency_factor = max(0.5, 1.0 - (latency / 1000.0))
        base_factor = base_prob / 100.0
        gradle_boost = 1.05

        final_probability = base_factor * hash_factor * latency_factor * gradle_boost * 100
        final_probability = max(5.0, min(95.0, final_probability))

        return final_probability

    except Exception as e:
        print(f"Enhanced probability calculation error: {e}")
        return min(90.0, base_prob * (hash_power / 100.0))


def run_attack(node_url, peers, attacker_addr, blocks=1, amount=10.0, frontend_config=None):
    try:
        print("\n" + "=" * 50)
        print("STARTING ATTACK SIMULATION")
        print("=" * 50)

        if frontend_config is None:
            frontend_config = {}

        hash_power = frontend_config.get('hash_power', 30)
        force_success = frontend_config.get('force_success', False)
        force_failure = frontend_config.get('force_failure', False)

        print(f"Configuration:")
        print(f"   Attacker: {attacker_addr}")
        print(f"   Blocks: {blocks}")
        print(f"   Amount: {amount}")
        print(f"   Hash Power: {hash_power}%")
        print(f"   Force Success: {force_success}")
        print(f"   Force Failure: {force_failure}")

        if force_success:
            print("FORCE SUCCESS MODE - Attack will succeed")
            return {
                "successful": True,
                "success": True,
                "success_rate": 1.0,
                "blocks_mined": blocks,
                "message": "Double spending attack successful (FORCED SUCCESS MODE)!",
                "steps": [
                    {"action": "force_success", "result": True},
                    {"action": "mining", "mining_success": True},
                    {"action": "broadcast", "result": True}
                ],
                "hash_power": hash_power,
                "success_probability": 100.0
            }

        if force_failure:
            print("FORCE FAILURE MODE - Attack will fail")
            return {
                "successful": False,
                "success": False,
                "success_rate": 0.0,
                "blocks_mined": 0,
                "message": "Double spending attack failed (FORCED FAILURE MODE)!",
                "steps": [
                    {"action": "force_failure", "result": False}
                ],
                "hash_power": hash_power,
                "success_probability": 0.0
            }

        print("RANDOM MODE - Using Improved Probability Formula")
        print("=" * 50)

        base_prob = frontend_config.get('success_probability', 50.0)
        enhanced_prob = calculate_enhanced_probability(base_prob, hash_power, 100)

        import random
        attack_success = random.random() < (enhanced_prob / 100)

        if attack_success:
            print("ATTACK SUCCESSFUL! Double spending achieved!")
            return {
                "successful": True,
                "success": True,
                "success_rate": enhanced_prob / 100,
                "blocks_mined": blocks,
                "message": "Double spending attack successful with improved probability!",
                "steps": [
                    {"action": "improved_probability", "result": True},
                    {"action": "mining", "mining_success": True},
                    {"action": "broadcast", "result": True}
                ],
                "hash_power": hash_power,
                "success_probability": enhanced_prob
            }
        else:
            print("ATTACK FAILED! Private chain not accepted.")
            return {
                "successful": False,
                "success": False,
                "success_rate": enhanced_prob / 100,
                "blocks_mined": 0,
                "message": "Double spending attack failed!",
                "steps": [
                    {"action": "improved_probability", "result": False},
                    {"action": "mining", "mining_success": False}
                ],
                "hash_power": hash_power,
                "success_probability": enhanced_prob
            }

    except Exception as e:
        print(f"Attack simulation error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "successful": False,
            "success": False,
            "success_rate": 0,
            "blocks_mined": 0,
            "message": f"Attack simulation failed: {str(e)}",
            "steps": [{"action": "error", "error": str(e)}],
            "hash_power": hash_power if 'hash_power' in locals() else 0,
            "success_probability": 0
        }


def get_current_chain_state(node_url):
    try:
        r = requests.get(f"{node_url}/api/chain", timeout=10)
        r.raise_for_status()
        data = r.json()
        chain = data.get("chain", [])
        if chain:
            last_block = chain[-1]
            return {
                "last_block_hash": last_block.get("hash"),
                "last_block_index": last_block.get("index"),
                "difficulty": data.get("difficulty", 3),
                "chain_length": len(chain)
            }
        return {"last_block_hash": "0", "last_block_index": 0, "difficulty": 3, "chain_length": 1}
    except Exception as e:
        print(f"Error getting chain state: {e}")
        return {"last_block_hash": "0", "last_block_index": 0, "difficulty": 3, "chain_length": 1}


def prepare_honest_tx(node_url, sender, receiver, amount):
    try:
        r = requests.post(
            f"{node_url}/api/tx/new",
            json={"sender": sender, "receiver": receiver, "amount": amount},
            timeout=10
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error preparing honest transaction: {e}")
        raise


def simulate_network_partition(peers, partition_ratio=0.5, frontend_config=None):
    print(f"Simulating network partition attack (ratio: {partition_ratio})")

    partition_success = should_attack_succeed(frontend_config, "partition")

    if not partition_success:
        print("Network partition failed due to probability constraints")
        return {
            "successful": False,
            "partitioned_peers": [],
            "remaining_peers": peers,
            "message": "Partition attack failed"
        }

    num_isolated = max(1, int(len(peers) * partition_ratio))
    partitioned_peers = random.sample(peers, num_isolated)
    remaining_peers = [peer for peer in peers if peer not in partitioned_peers]

    print(f"Network partition successful:")
    print(f"   Isolated peers: {len(partitioned_peers)}")
    print(f"   Remaining peers: {len(remaining_peers)}")

    return {
        "successful": True,
        "partitioned_peers": partitioned_peers,
        "remaining_peers": remaining_peers,
        "partition_ratio": partition_ratio,
        "simblock_data": simblock_network.get_current_network_conditions()
    }


def analyze_attack_patterns(attack_logs):
    if not attack_logs:
        return {"message": "No attack logs to analyze"}

    successful_attacks = [log for log in attack_logs if log.get('successful')]
    failed_attacks = [log for log in attack_logs if not log.get('successful')]

    total_attacks = len(attack_logs)
    success_rate = len(successful_attacks) / total_attacks if total_attacks > 0 else 0

    avg_hash_power = 0
    avg_success_prob = 0
    avg_network_latency = 0

    for log in attack_logs:
        config = log.get('frontend_config', {})
        avg_hash_power += config.get('attackerHashPower', 30)
        avg_success_prob += config.get('successProbability', 0.5)

        network_cond = log.get('simblock_network_conditions', {})
        avg_network_latency += network_cond.get('average_latency', 100)

    avg_hash_power /= total_attacks
    avg_success_prob /= total_attacks
    avg_network_latency /= total_attacks

    recommendations = []
    if success_rate < 0.3:
        recommendations.append("Consider increasing hash power above 40%")
        recommendations.append("Wait for higher network latency conditions")
        recommendations.append("Try partitioning the network first")
    elif success_rate > 0.7:
        recommendations.append("Current strategy is effective")
        recommendations.append("Consider reducing hash power to save resources")

    return {
        "total_attacks_analyzed": total_attacks,
        "overall_success_rate": success_rate,
        "successful_attacks": len(successful_attacks),
        "failed_attacks": len(failed_attacks),
        "average_hash_power": avg_hash_power,
        "average_success_probability": avg_success_prob,
        "average_network_latency": avg_network_latency,
        "recommendations": recommendations,
        "optimal_conditions": {
            "hash_power": "40-60%",
            "network_latency": ">200ms",
            "success_probability": ">0.7"
        }
    }