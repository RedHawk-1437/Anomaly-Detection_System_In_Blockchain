"""
attacker.py - Blockchain Attack Simulation Module

This module provides comprehensive blockchain attack simulation capabilities
with realistic probability calculations and SimBlock network integration.
It implements various attack vectors including double spending, network
partitioning, and private mining attacks with configurable parameters.

Key Features:
- Double spending attack simulation with enhanced probability calculations
- Private mining with hash power considerations
- Network partition attack simulation
- Attack pattern analysis and statistics
- SimBlock network condition integration for realistic simulations
- Frontend configuration support for customizable attack parameters

The module serves as the core component for testing blockchain security
and analyzing attack success factors under different network conditions.
"""

import time
import requests
import random
from .blockchain import Blockchain
from .transaction import Transaction
from .block import Block
from .simblock_integration import simblock_network  # Import SimBlock integration


def should_attack_succeed(frontend_config, stage="broadcast"):
    """
    Determine if attack should succeed based on configuration and SimBlock network conditions.

    Evaluates attack success probability considering frontend configuration,
    network conditions from SimBlock, and the specific attack stage (mining,
    broadcast, etc.). Handles force success/failure modes and calculates
    realistic probabilities based on network factors.

    Args:
        frontend_config (dict): Configuration from frontend with probability settings.
            Expected keys:
            - forceSuccess (bool): Override to force attack success
            - forceFailure (bool): Override to force attack failure
            - successProbability (float): Base success probability (0.0-1.0)
            - attackerHashPower (float): Attacker's hash power percentage
        stage (str): Current attack stage. Options: 'mining', 'broadcast', 'partition'.
                   Defaults to 'broadcast'.

    Returns:
        bool: True if attack should succeed at this stage, False otherwise
    """
    # If no configuration provided, use SimBlock-enhanced default
    if not frontend_config:
        base_prob = 0.5
        enhanced_prob = simblock_network.calculate_attack_success_probability(base_prob, 0.3)
        return random.random() < enhanced_prob

    # Check force controls first - highest priority
    if frontend_config.get('forceSuccess'):
        print("Force SUCCESS enabled - attack will proceed")
        return True
    if frontend_config.get('forceFailure'):
        print("Force FAILURE enabled - attack will be prevented")
        return False

    # Get configuration values for probability calculation
    base_probability = frontend_config.get('successProbability', 0.5)
    hash_power = frontend_config.get('attackerHashPower', 30) / 100.0

    # Use SimBlock for enhanced probability calculations
    if stage == "mining":
        # Mining success depends on hash power and network conditions
        mining_success_rate = simblock_network.calculate_attack_success_probability(
            base_probability, hash_power
        )
        final_probability = mining_success_rate

    elif stage == "broadcast":
        # Broadcast success heavily depends on network conditions from SimBlock
        network_conditions = simblock_network.get_current_network_conditions()
        latency_factor = min(network_conditions.get('average_latency', 100) / 250, 0.4)

        broadcast_success_rate = simblock_network.calculate_attack_success_probability(
            base_probability, hash_power
        )
        final_probability = min(broadcast_success_rate + latency_factor, 0.95)

    else:
        # Overall attack success - use SimBlock enhanced calculation
        final_probability = simblock_network.calculate_attack_success_probability(
            base_probability, hash_power
        )

    # Ensure probability is within valid range (5% to 95%)
    final_probability = max(0.05, min(0.95, final_probability))

    # Determine success based on final probability
    success = random.random() < final_probability

    # Print detailed probability information for debugging
    network_info = simblock_network.get_current_network_conditions()
    print(f"{stage.upper()} probability calculation:")
    print(f"   Base probability: {base_probability:.1%}")
    print(f"   Hash power: {hash_power:.1%}")
    print(f"   Network latency: {network_info.get('average_latency', 100)}ms")
    print(f"   Final probability: {final_probability:.1%}")
    print(f"   Result: {'SUCCESS' if success else 'FAILED'}")

    return success


def simulate_private_mining(node_url, attacker_addr, blocks_to_mine, amount, frontend_config=None):
    """
    Simulate private mining with hash power consideration and SimBlock network awareness.

    Creates a private blockchain fork and mines blocks containing double-spending
    transactions. Considers hash power limitations and network conditions from
    SimBlock to determine mining success.

    Args:
        node_url (str): URL of the target node to query for current chain state
        attacker_addr (str): Attacker's wallet address for transaction creation
        blocks_to_mine (int): Number of blocks to mine privately in the fork
        amount (float): Amount to double-spend in the attack transaction
        frontend_config (dict, optional): Configuration for attack probability
                                        and hash power. Defaults to None.

    Returns:
        tuple: Contains two elements:
            - list: Dictionary representations of successfully mined blocks
            - bool: True if mining was successful, False otherwise
    """
    try:
        # Get current state of the main blockchain
        chain_state = get_current_chain_state(node_url)
        difficulty = chain_state["difficulty"]
        current_index = chain_state["last_block_index"]
        current_hash = chain_state["last_block_hash"]

        print(f"Current chain state: index={current_index}, hash={current_hash[:10]}...")

        # Apply hash power limitation with SimBlock network awareness
        mining_success = should_attack_succeed(frontend_config, "mining")

        if not mining_success:
            print(f"Mining failed due to probability/hash power constraints")
            # Get network conditions for debugging
            network_info = simblock_network.get_current_network_conditions()
            print(f"   Network conditions: {network_info.get('network_health', 'unknown')}")
            return [], False

        # Continue with mining logic if successful
        # Create a private blockchain for the attacker
        private_bc = Blockchain(difficulty=difficulty)
        private_bc.chain = []  # Start with empty chain

        # Create genesis block for private chain
        genesis = Block(index=0, transactions=[], previous_hash="0",
                        timestamp=int(time.time()), nonce=0)
        genesis = private_bc._mine_block_genesis(genesis)
        private_bc.chain.append(genesis)

        # If we're not at genesis, create new blocks
        if current_index > 0:
            new_index = current_index + 1
            print(f"Creating new block #{new_index} continuing from main chain block #{current_index}")

            # Create double-spending transaction
            # The attacker sends coins to themselves (double-spending)
            attacker_control = f"{attacker_addr}_control"
            tx = Transaction(sender=attacker_addr, receiver=attacker_control, amount=amount)

            # Create new block with the double-spending transaction
            new_block = Block(
                index=new_index,
                transactions=[tx],
                previous_hash=current_hash,  # Continue from main chain
                timestamp=int(time.time()),
                nonce=0
            )

            # Mine the block (proof of work)
            mined_block = private_bc._proof_of_work(new_block)
            private_bc.chain.append(mined_block)

            # Print mining success information with network context
            hash_power = frontend_config.get('attackerHashPower', 30) if frontend_config else 30
            network_info = simblock_network.get_current_network_conditions()
            print(f"Mined private block #{new_index} with {hash_power}% hash power")
            print(f"Block contains {len(mined_block.transactions)} transactions")
            print(f"Network conditions: {network_info.get('network_health', 'unknown')}")

            return [mined_block.to_dict()], True
        else:
            # Genesis block case - create first block with transaction
            attacker_control = f"{attacker_addr}_control"
            tx = Transaction(sender=attacker_addr, receiver=attacker_control, amount=amount)
            private_bc.mempool.append(tx)

            # Mine the block with the transaction
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


def broadcast_private_chain(peers, mined_blocks, frontend_config=None):
    """
    Broadcast private chain to network peers with SimBlock network simulation.

    Attempts to propagate privately mined blocks to network peers with
    realistic network simulation including latency, propagation delays,
    and success rates based on network conditions.

    Args:
        peers (list): List of peer URLs to broadcast the private chain to
        mined_blocks (list): List of mined block dictionaries to broadcast
        frontend_config (dict, optional): Configuration for broadcast probability
                                        and network factors. Defaults to None.

    Returns:
        list: List of dictionaries containing broadcast results for each peer.
              Each result contains:
              - peer (str): Peer URL
              - index (int): Block index
              - ok (bool): Whether broadcast was successful
              - status (int): HTTP status code if available
              - message (str): Response message from peer
              - simblock_latency (float): Network latency from simulation
              - network_health (str): Network health status
    """
    results = []

    # Check if there are blocks to broadcast
    if not mined_blocks:
        print("No blocks to broadcast")
        return results

    # Use SimBlock to simulate network propagation
    block_size = len(str(mined_blocks)) * 8  # Approximate block size in bits
    propagation_simulation = simblock_network.simulate_message_propagation(block_size, peers)

    print(f"SimBlock Network Simulation:")
    print(f"   Average latency: {propagation_simulation['average_latency']}ms")
    print(f"   Network health: {propagation_simulation['network_health']}")
    print(f"   Expected successful deliveries: {propagation_simulation['successful_deliveries']}")

    # Determine if broadcast should succeed based on network conditions
    broadcast_success = should_attack_succeed(frontend_config, "broadcast")

    if not broadcast_success:
        print("Broadcast failed due to probability/network constraints")
        # Create failure results for all peers
        for peer in peers:
            results.append({
                "peer": peer,
                "index": mined_blocks[0].get("index"),
                "ok": False,
                "message": f"Broadcast failed - Network: {propagation_simulation['network_health']}",
                "simblock_data": propagation_simulation
            })
        return results

    # Original broadcast logic enhanced with SimBlock data
    print(f"Broadcasting {len(mined_blocks)} blocks to {len(peers)} peers")

    for peer in peers:
        for i, block in enumerate(mined_blocks):
            try:
                print(f"   Broadcasting block {i + 1} to {peer}")

                # Add simulated network delay based on SimBlock
                time.sleep(propagation_simulation['propagation_time'] / len(peers))

                # Send block to peer's receive endpoint
                r = requests.post(f"{peer}/blocks/receive", json=block, timeout=10)

                # Record the result with SimBlock context
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


def run_double_spending_attack(attacker_name, private_blocks, amount, hash_power=50.0):
    """
    Simulate double spending attack - SimBlock integration compatible.

    Performs a simplified double spending attack simulation using SimBlock
    for probability calculations and network condition awareness. Compatible
    with both direct calls and SimBlock integration requirements.

    Args:
        attacker_name (str): Name identifier for the attacker
        private_blocks (int): Number of private blocks to attempt mining
        amount (float): Amount of coins to attempt double-spending
        hash_power (float, optional): Attacker's hash power percentage.
                                    Defaults to 50.0.

    Returns:
        dict: Attack simulation results containing:
            - success (bool): Overall attack success status
            - successful (bool): Compatibility alias for success
            - probability (float): Calculated attack probability percentage
            - blocks_mined (int): Number of blocks successfully mined
            - message (str): Descriptive result message
    """
    print("=" * 50)
    print("STARTING DOUBLE SPENDING ATTACK SIMULATION")
    print("=" * 50)

    print(f"Attack Configuration:")
    print(f"   Attacker: {attacker_name}")
    print(f"   Private Blocks: {private_blocks}")
    print(f"   Amount: {amount} coins")
    print(f"   Hash Power: {hash_power}%")

    # Calculate attack probability
    attack_probability = simblock_network.calculate_attack_probability(70.0, hash_power, 100)

    # Simulate mining
    mining_success = random.random() < (attack_probability / 100.0)

    # Simulate network propagation
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
    """
    Improved probability calculation with realistic ranges and balancing.

    Enhances basic probability calculations with realistic factors including
    hash power scaling, latency impact, and gradle simulation boost. Provides
    detailed breakdown for debugging and analysis.

    Args:
        base_prob (float): Base success probability percentage (0-100)
        hash_power (float): Attacker's hash power percentage (0-100)
        latency (float): Network latency in milliseconds

    Returns:
        float: Enhanced probability percentage value (5-95 range)
    """
    try:
        # Normalize inputs
        base_prob = float(base_prob)
        hash_power = float(hash_power)
        latency = float(latency)

        # Ensure base probability is reasonable (1-100%)
        base_prob = float(base_prob)

        # Better hash power scaling
        # Hash power should have stronger but realistic influence
        hash_factor = (hash_power / 100.0) ** 0.8

        # Better latency factor
        # Lower latency = better success, but not too extreme
        latency_factor = max(0.5, 1.0 - (latency / 1000.0))

        # Base probability scaling
        base_factor = base_prob / 100.0

        # Realistic gradle boost
        gradle_boost = 1.05

        # Final calculation with better balancing
        final_probability = base_factor * hash_factor * latency_factor * gradle_boost * 100

        # Ensure reasonable bounds (5% to 95%)
        final_probability = max(5.0, min(95.0, final_probability))

        print(f"Enhanced Probability Breakdown:")
        print(f"   Base: {base_prob:.1f}% -> Factor: {base_factor:.3f}")
        print(f"   Hash Power: {hash_power:.1f}% -> Factor: {hash_factor:.3f}")
        print(f"   Latency: {latency:.1f}ms -> Factor: {latency_factor:.3f}")
        print(f"   Gradle Boost: {gradle_boost}")
        print(f"   Final Probability: {final_probability:.1f}%")

        return final_probability

    except Exception as e:
        print(f"Enhanced probability calculation error: {e}")
        # Fallback to simple calculation
        return min(90.0, base_prob * (hash_power / 100.0))


def run_attack(node_url, peers, attacker_addr, blocks=1, amount=10.0, frontend_config=None):
    """
    Run comprehensive double-spending attack simulation with enhanced configuration.

    Orchestrates a complete double-spending attack including private mining,
    network broadcasting, and success probability calculations. Supports
    multiple operation modes including force success/failure and random
    mode with enhanced probability calculations.

    Args:
        node_url (str): Target node URL for chain state queries
        peers (list): List of peer URLs for network broadcasting
        attacker_addr (str): Attacker's wallet address for transactions
        blocks (int, optional): Number of blocks to mine privately. Defaults to 1.
        amount (float, optional): Amount to double-spend. Defaults to 10.0.
        frontend_config (dict, optional): Attack configuration parameters.
            Expected keys:
            - hash_power (float): Attacker's hash power percentage
            - force_success (bool): Force attack to succeed
            - force_failure (bool): Force attack to fail
            - success_probability (float): Base success probability

    Returns:
        dict: Comprehensive attack results containing:
            - successful (bool): Overall attack success status
            - success (bool): Compatibility alias for successful
            - success_rate (float): Calculated success probability (0.0-1.0)
            - blocks_mined (int): Number of blocks successfully mined
            - message (str): Descriptive result message
            - steps (list): Detailed step-by-step execution results
            - hash_power (float): Hash power used in attack
            - success_probability (float): Final success probability percentage
    """
    try:
        print("\n" + "=" * 50)
        print("STARTING ATTACK SIMULATION")
        print("=" * 50)

        # Safely get configuration values
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

        # Handle force success/failure first with proper checks
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

        # RANDOM MODE - Using improved probability
        print("RANDOM MODE - Using Improved Probability Formula")
        print("=" * 50)

        # Base probability from frontend
        base_prob = frontend_config.get('success_probability', 50.0)

        # Enhanced probability with improved formula
        enhanced_prob = calculate_enhanced_probability(base_prob, hash_power, 100)

        # Use enhanced probability for attack success
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
    """
    Get the current chain state including the last block hash and index.

    Queries the specified node for current blockchain state including
    the most recent block information, chain length, and difficulty.

    Args:
        node_url (str): URL of the node to query for chain state

    Returns:
        dict: Chain state information containing:
            - last_block_hash (str): Hash of the most recent block
            - last_block_index (int): Index of the most recent block
            - difficulty (int): Current mining difficulty
            - chain_length (int): Total number of blocks in chain
    """
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
    """
    Prepare and broadcast an honest transaction to the merchant.

    Creates and submits a legitimate transaction to the network as part
    of attack simulation setup. This represents the initial honest
    transaction that will be double-spent.

    Args:
        node_url (str): Node URL for transaction submission
        sender (str): Sender's wallet address
        receiver (str): Receiver's (merchant) wallet address
        amount (float): Transaction amount

    Returns:
        dict: Transaction response from the node

    Raises:
        Exception: If transaction submission fails
    """
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
    """
    Simulate a network partition attack where the attacker isolates part of the network.

    Models a network partitioning attack where the attacker attempts to
    isolate a portion of the network to gain advantage. Uses probability
    calculations and SimBlock network conditions for realistic simulation.

    Args:
        peers (list): List of all peer URLs in the network
        partition_ratio (float, optional): Ratio of network to isolate (0.0 to 1.0).
                                         Defaults to 0.5.
        frontend_config (dict, optional): Configuration for attack probability.
                                        Defaults to None.

    Returns:
        dict: Partition simulation results containing:
            - successful (bool): Whether partition attack succeeded
            - partitioned_peers (list): List of isolated peer URLs
            - remaining_peers (list): List of accessible peer URLs
            - partition_ratio (float): Requested partition ratio
            - simblock_data (dict): Network conditions from SimBlock
    """
    print(f"Simulating network partition attack (ratio: {partition_ratio})")

    # Determine if partition attack succeeds
    partition_success = should_attack_succeed(frontend_config, "partition")

    if not partition_success:
        print("Network partition failed due to probability constraints")
        return {
            "successful": False,
            "partitioned_peers": [],
            "remaining_peers": peers,
            "message": "Partition attack failed"
        }

    # Calculate number of peers to isolate
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
    """
    Analyze multiple attack logs to identify patterns and success factors.

    Processes historical attack data to extract statistics, identify
    successful strategies, and generate recommendations for future attacks.
    Provides insights into optimal attack conditions and parameters.

    Args:
        attack_logs (list): List of attack log dictionaries from previous simulations.
                          Each log should contain success status and configuration.

    Returns:
        dict: Comprehensive analysis results containing:
            - total_attacks_analyzed (int): Number of attacks processed
            - overall_success_rate (float): Aggregate success rate (0.0-1.0)
            - successful_attacks (int): Count of successful attacks
            - failed_attacks (int): Count of failed attacks
            - average_hash_power (float): Mean hash power across attacks
            - average_success_probability (float): Mean base success probability
            - average_network_latency (float): Mean network latency
            - recommendations (list): Strategic recommendations for improvement
            - optimal_conditions (dict): Identified optimal attack parameters
    """
    if not attack_logs:
        return {"message": "No attack logs to analyze"}

    successful_attacks = [log for log in attack_logs if log.get('successful')]
    failed_attacks = [log for log in attack_logs if not log.get('successful')]

    total_attacks = len(attack_logs)
    success_rate = len(successful_attacks) / total_attacks if total_attacks > 0 else 0

    # Calculate average hash power and success probability
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

    # Generate recommendations
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