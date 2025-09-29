# attacker.py - FINAL OPTIMIZED VERSION
# Enhanced with realistic probability calculations

import time
import requests
import random
from .blockchain import Blockchain
from .transaction import Transaction
from .block import Block


def should_attack_succeed(frontend_config, stage="broadcast"):
    """
    Determine if attack should succeed based on configuration and probability calculations.

    Args:
        frontend_config (dict): Configuration from frontend with probability settings
        stage (str): Current attack stage ('mining', 'broadcast', etc.)

    Returns:
        bool: True if attack should succeed, False otherwise
    """
    # If no configuration provided, use default 50% chance
    if not frontend_config:
        return random.random() > 0.5  # Default 50% chance

    # Check force controls first - highest priority
    if frontend_config.get('forceSuccess'):
        print("🎯 Force SUCCESS enabled - attack will proceed")
        return True
    if frontend_config.get('forceFailure'):
        print("🚫 Force FAILURE enabled - attack will be prevented")
        return False

    # Get configuration values for probability calculation
    base_probability = frontend_config.get('successProbability', 0.5)
    hash_power = frontend_config.get('attackerHashPower', 30) / 100.0

    # Realistic probability calculations for different stages
    if stage == "mining":
        # Mining success depends 80% on hash power and 20% on luck
        mining_success_rate = hash_power * 0.8 + 0.2 * random.random()
        final_probability = mining_success_rate

    elif stage == "broadcast":
        # Broadcast success depends 70% on base probability and 30% on network conditions
        network_factor = 0.3 * random.random()
        broadcast_success_rate = base_probability * 0.7 + network_factor
        final_probability = min(broadcast_success_rate, 0.95)  # Cap at 95%

    else:
        # Overall attack success - balanced approach
        final_probability = (base_probability * 0.6 + hash_power * 0.4)

    # Ensure probability is within valid range (5% to 95%)
    final_probability = max(0.05, min(0.95, final_probability))

    # Determine success based on final probability
    success = random.random() < final_probability

    # Print detailed probability information for debugging
    print(f"🎲 {stage.upper()} probability calculation:")
    print(f"   Base probability: {base_probability:.1%}")
    print(f"   Hash power: {hash_power:.1%}")
    print(f"   Final probability: {final_probability:.1%}")
    print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")

    return success


def simulate_private_mining(node_url, attacker_addr, blocks_to_mine, amount, frontend_config=None):
    """
    Simulate private mining with hash power consideration.

    Args:
        node_url (str): URL of the target node
        attacker_addr (str): Attacker's wallet address
        blocks_to_mine (int): Number of blocks to mine privately
        amount (float): Amount to double-spend
        frontend_config (dict): Configuration for attack probability

    Returns:
        tuple: (list of mined blocks, mining success status)
    """
    try:
        # Get current state of the main blockchain
        chain_state = get_current_chain_state(node_url)
        difficulty = chain_state["difficulty"]
        current_index = chain_state["last_block_index"]
        current_hash = chain_state["last_block_hash"]

        print(f"Current chain state: index={current_index}, hash={current_hash[:10]}...")

        # Apply hash power limitation for mining stage
        mining_success = should_attack_succeed(frontend_config, "mining")

        if not mining_success:
            print(f"❌ Mining failed due to probability/hash power constraints")
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
            print(f"⛏️ Creating new block #{new_index} continuing from main chain block #{current_index}")

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

            # Print mining success information
            hash_power = frontend_config.get('attackerHashPower', 30) if frontend_config else 30
            print(f"✅ Mined private block #{new_index} with {hash_power}% hash power")
            print(f"📦 Block contains {len(mined_block.transactions)} transactions")

            return [mined_block.to_dict()], True
        else:
            # Genesis block case - create first block with transaction
            attacker_control = f"{attacker_addr}_control"
            tx = Transaction(sender=attacker_addr, receiver=attacker_control, amount=amount)
            private_bc.mempool.append(tx)

            # Mine the block with the transaction
            block = private_bc.mine_pending_transactions(miner_address=attacker_addr)
            hash_power = frontend_config.get('attackerHashPower', 30) if frontend_config else 30
            print(f"✅ Mined private block #1 with {hash_power}% hash power")
            return [block.to_dict()], True

    except Exception as e:
        print(f"💥 Error in private mining: {e}")
        import traceback
        traceback.print_exc()
        return [], False


def broadcast_private_chain(peers, mined_blocks, frontend_config=None):
    """
    Broadcast private chain to network peers with success probability.

    Args:
        peers (list): List of peer URLs to broadcast to
        mined_blocks (list): List of mined blocks to broadcast
        frontend_config (dict): Configuration for broadcast probability

    Returns:
        list: Results of broadcast attempts to each peer
    """
    results = []

    # Check if there are blocks to broadcast
    if not mined_blocks:
        print("❌ No blocks to broadcast")
        return results

    # Determine if broadcast should succeed based on probability
    broadcast_success = should_attack_succeed(frontend_config, "broadcast")

    if not broadcast_success:
        print("🎲 Broadcast failed due to probability constraints")
        # Create failure results for all peers
        for peer in peers:
            results.append({
                "peer": peer,
                "index": mined_blocks[0].get("index"),
                "ok": False,
                "message": "Broadcast failed due to probability constraints"
            })
        return results

    # Original broadcast logic - try to send blocks to all peers
    print(f"📡 Broadcasting {len(mined_blocks)} blocks to {len(peers)} peers")

    for peer in peers:
        for i, block in enumerate(mined_blocks):
            try:
                print(f"   📤 Broadcasting block {i + 1} to {peer}")
                # Send block to peer's receive endpoint
                r = requests.post(f"{peer}/blocks/receive", json=block, timeout=10)

                # Record the result
                result = {
                    "peer": peer,
                    "index": block.get("index"),
                    "ok": r.status_code == 200,
                    "status": r.status_code
                }

                if r.status_code == 200:
                    result["message"] = r.json().get("message", "Accepted")
                    print(f"   ✅ Block accepted by {peer}")
                else:
                    error_msg = r.json().get("error", "Rejected") if r.status_code == 400 else "Rejected"
                    result["message"] = error_msg
                    print(f"   ❌ Block rejected by {peer}: {error_msg}")

                results.append(result)

            except Exception as e:
                print(f"   💥 Error broadcasting to {peer}: {e}")
                results.append({
                    "peer": peer,
                    "index": block.get("index"),
                    "ok": False,
                    "error": str(e)
                })
    return results


def run_attack(node_url="http://127.0.0.1:5000", peers=None, attacker_addr="Attacker",
               blocks=1, amount=5.0, frontend_config=None):
    """
    Main function to run the double-spending attack with enhanced controls.

    Args:
        node_url (str): Target node URL
        peers (list): List of peer nodes
        attacker_addr (str): Attacker's address
        blocks (int): Number of blocks to mine
        amount (float): Amount to double-spend
        frontend_config (dict): Attack configuration

    Returns:
        dict: Detailed attack log with results
    """
    # Set default peers if none provided
    peers = peers or [node_url]

    # Initialize attack log
    attack_log = {
        "timestamp": time.time(),
        "attacker": attacker_addr,
        "blocks": blocks,
        "amount": amount,
        "frontend_config": frontend_config,
        "steps": []  # Will store each step of the attack
    }

    try:
        print(f"\n{'=' * 50}")
        print(f"🚀 STARTING ATTACK SIMULATION")
        print(f"{'=' * 50}")
        print(f"📋 Configuration:")
        print(f"   Attacker: {attacker_addr}")
        print(f"   Blocks to mine: {blocks}")
        print(f"   Amount: {amount} coins")
        print(f"   Peers: {len(peers)}")
        if frontend_config:
            print(f"   Probability: {frontend_config.get('successProbability', 0.5) * 100}%")
            print(f"   Hash Power: {frontend_config.get('attackerHashPower', 30)}%")
            print(f"   Force Success: {frontend_config.get('forceSuccess', False)}")
            print(f"   Force Failure: {frontend_config.get('forceFailure', False)}")
        print(f"{'=' * 50}")

        # Step 1: Broadcast honest transaction (to merchant)
        attack_log["steps"].append({"action": "starting_attack", "timestamp": time.time()})
        print("1️⃣ STEP 1: Starting attack preparation")

        honest_tx = prepare_honest_tx(node_url, attacker_addr, "Merchant", amount)
        attack_log["steps"].append({
            "action": "broadcast_honest_tx",
            "result": honest_tx,
            "timestamp": time.time()
        })
        print("2️⃣ STEP 2: Honest transaction broadcasted to merchant")

        # Step 2: Private mining with hash power consideration
        attack_log["steps"].append({"action": "starting_private_mining", "timestamp": time.time()})
        print("3️⃣ STEP 3: Starting private mining")

        # Mine blocks privately (double-spending chain)
        mined_blocks, mining_success = simulate_private_mining(
            node_url, attacker_addr, blocks_to_mine=blocks, amount=amount,
            frontend_config=frontend_config
        )

        attack_log["steps"].append({
            "action": "private_mined_blocks",
            "count": len(mined_blocks),
            "mining_success": mining_success,
            "timestamp": time.time()
        })
        print(f"4️⃣ STEP 4: Mining completed - {len(mined_blocks)} blocks mined")

        # Check if mining was successful
        if not mined_blocks:
            print("❌ ATTACK FAILED: No blocks were mined")
            attack_log["successful"] = False
            attack_log["success_rate"] = 0
            return attack_log

        # Step 3: Broadcast private chain with probability
        attack_log["steps"].append({"action": "broadcasting_private_chain", "timestamp": time.time()})
        print("5️⃣ STEP 5: Broadcasting private chain to network")

        # Try to broadcast the private chain to replace the main chain
        broadcast_results = broadcast_private_chain(peers, mined_blocks, frontend_config)
        attack_log["steps"].append({
            "action": "broadcast_private_blocks",
            "results": broadcast_results,
            "timestamp": time.time()
        })

        # Count successful broadcasts
        success_peers = [r for r in broadcast_results if r.get('ok')]
        print(f"6️⃣ STEP 6: Broadcast completed - {len(success_peers)}/{len(peers)} peers accepted")

        # Step 4: Consensus check
        attack_log["steps"].append({"action": "checking_consensus", "timestamp": time.time()})
        print("7️⃣ STEP 7: Checking network consensus")

        # Check consensus across all peers
        consensus_results = []
        for peer in peers:
            try:
                r = requests.get(f"{peer}/consensus", timeout=10)
                consensus_results.append({
                    "peer": peer,
                    "status": r.status_code,
                    "body": r.json()
                })
            except Exception as e:
                consensus_results.append({"peer": peer, "error": str(e)})

        attack_log["steps"].append({
            "action": "consensus_results",
            "results": consensus_results,
            "timestamp": time.time()
        })
        print("8️⃣ STEP 8: Consensus check completed")

        # Determine final attack success
        # Attack is successful if at least one peer accepted our chain
        attack_log["successful"] = len(success_peers) > 0
        attack_log["success_rate"] = len(success_peers) / len(peers) if peers else 0

        attack_log["steps"].append({
            "action": "attack_completed",
            "successful": attack_log["successful"],
            "success_rate": attack_log["success_rate"],
            "timestamp": time.time()
        })

        # Final result display
        print(f"\n{'=' * 50}")
        if attack_log['successful']:
            print(f"🎉 ATTACK SUCCESSFUL!")
            print(f"   Success rate: {attack_log['success_rate']:.1%}")
            print(f"   Double-spending achieved!")
        else:
            print(f"💥 ATTACK FAILED")
            print(f"   Success rate: {attack_log['success_rate']:.1%}")
            print(f"   Network prevented the attack")
        print(f"{'=' * 50}\n")

    except Exception as e:
        print(f"💥 CRITICAL ERROR: Attack failed with error: {e}")
        import traceback
        traceback.print_exc()
        attack_log["steps"].append({
            "action": "attack_failed",
            "error": str(e),
            "timestamp": time.time()
        })
        attack_log["successful"] = False
        attack_log["success_rate"] = 0

    return attack_log


# Helper functions (unchanged)
def get_current_chain_state(node_url):
    """
    Get the current chain state including the last block hash and index.

    Args:
        node_url (str): URL of the node to query

    Returns:
        dict: Chain state information
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

    Args:
        node_url (str): Node URL
        sender (str): Sender address
        receiver (str): Receiver address
        amount (float): Transaction amount

    Returns:
        dict: Transaction response
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