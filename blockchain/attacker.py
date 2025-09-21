# attacker.py
# This file contains attacker functions for simulating a double-spending attack.
# It does not start servers — instead, it only returns Python dictionary results.

import time
import requests
from .blockchain import Blockchain   # Import Blockchain class to create a private chain
from .transaction import Transaction # Import Transaction class to create fake transactions


# Function to get the difficulty level of a node's blockchain
def get_node_difficulty(node_url):
    try:
        # Send GET request to a node's /api/chain endpoint
        r = requests.get(f"{node_url}/api/chain", timeout=5)
        # Extract difficulty from the response, default to 3 if not found
        return int(r.json().get("difficulty", 3))
    except Exception:
        # If request fails, return default difficulty = 3
        return 3


# Function to prepare and send a real (honest) transaction to the network
def prepare_honest_tx(node_url, sender, receiver, amount):
    # Send POST request to create and broadcast a new transaction
    r = requests.post(
        f"{node_url}/api/tx/new",
        json={"sender": sender, "receiver": receiver, "amount": amount},
        timeout=5
    )
    # If the transaction fails, raise an error
    r.raise_for_status()
    # Return transaction data as JSON (contains txid and details)
    return r.json()


# Function to simulate private mining for the attacker
def simulate_private_mining(node_url, attacker_addr, blocks_to_mine, amount):
    # First, get the network difficulty from the node
    difficulty = get_node_difficulty(node_url)

    # Create a new private blockchain with the same difficulty
    private_bc = Blockchain(difficulty=difficulty)

    # Attacker creates a fake double-spending transaction
    attacker_control = f"{attacker_addr}_control"  # fake receiver controlled by attacker
    tx = Transaction(sender=attacker_addr, receiver=attacker_control, amount=amount)

    # Add the fake transaction to the private blockchain's mempool
    private_bc.mempool.append(tx)

    mined = []  # list to store mined block data

    # Mine the requested number of private blocks
    for i in range(max(1, int(blocks_to_mine))):
        # Mine pending transactions and reward the attacker
        b = private_bc.mine_pending_transactions(miner_address=attacker_addr)
        # Convert block object into dictionary for easier sharing
        mined.append(b.to_dict())

    # Return the list of mined private blocks
    return mined


# Function to broadcast the attacker's private blocks to other peers
def broadcast_private_chain(peers, mined_blocks):
    results = []  # to store peer responses

    # Loop through all peers
    for peer in peers:
        # Send each mined block to the peer
        for b in mined_blocks:
            try:
                # POST request to /blocks/receive endpoint of peer
                r = requests.post(f"{peer}/blocks/receive", json=b, timeout=5)
                # Save result of sending (success or failure)
                results.append({
                    "peer": peer,
                    "index": b.get("index"),
                    "ok": r.status_code == 200,
                    "status": r.status_code
                })
            except Exception as e:
                # If sending fails, save error message
                results.append({
                    "peer": peer,
                    "index": b.get("index"),
                    "ok": False,
                    "error": str(e)
                })
    return results


# Main function that runs the whole attack step by step
def run_attack(node_url="http://127.0.0.1:5000", peers=None, attacker_addr="Attacker", blocks=1, amount=5.0):
    # If no peers provided, use only the main node
    peers = peers or [node_url]
    out = {"steps": []}  # Dictionary to store all steps and results

    # Step 1: Broadcast a normal honest transaction to a merchant
    try:
        honest_tx = prepare_honest_tx(node_url, attacker_addr, "Merchant", amount)
        out["steps"].append({"action": "broadcast_honest_tx", "result": honest_tx})
    except Exception as e:
        # If transaction fails, stop and return the error
        out["steps"].append({"action": "broadcast_honest_tx", "error": str(e)})
        return out

    # Step 2: Privately mine blocks containing a fake (double-spending) transaction
    try:
        mined = simulate_private_mining(node_url, attacker_addr, blocks_to_mine=blocks, amount=amount)
        out["steps"].append({"action": "private_mined_blocks", "count": len(mined)})
    except Exception as e:
        out["steps"].append({"action": "private_mining_failed", "error": str(e)})
        return out

    # Step 3: Broadcast private (fake) chain blocks to peers
    try:
        broadcast_res = broadcast_private_chain(peers, mined)
        out["steps"].append({"action": "broadcast_private_blocks", "results": broadcast_res})
    except Exception as e:
        out["steps"].append({"action": "broadcast_failed", "error": str(e)})
        return out

    # Step 4: Ask peers to run consensus (replace chain if attacker's chain is longer)
    consensus = []
    for p in peers:
        try:
            # Send GET request to peer's consensus endpoint
            r = requests.get(f"{p}/consensus", timeout=5)
            consensus.append({
                "peer": p,
                "status": r.status_code,
                "body": r.json()
            })
        except Exception as e:
            # If consensus fails for a peer, log the error
            consensus.append({"peer": p, "error": str(e)})

    out["steps"].append({"action": "consensus_results", "results": consensus})

    # Return all steps (honest tx, private mining, broadcasting, consensus)
    return out
