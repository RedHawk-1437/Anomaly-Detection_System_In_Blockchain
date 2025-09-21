# blockchain.py
# This file defines the Blockchain class which handles the chain of blocks,
# transactions, mining, and peer-to-peer communication.

import time
import requests
import json
from typing import List, Dict, Any
from urllib.parse import urlparse
from .block import Block
from .transaction import Transaction


class Blockchain:
    def __init__(self, difficulty: int = 4, reward: float = 1.0):
        # The actual chain (list of blocks)
        self.chain: List[Block] = []

        # Temporary pool of transactions waiting to be mined
        self.mempool: List[Transaction] = []

        # Mining difficulty (number of leading zeros in hash)
        self.difficulty = int(difficulty)

        # Reward given to the miner when they mine a block
        self.miner_reward = float(reward)

        # Set of peer nodes (other blockchains in the network)
        self.peers = set()

        # Create the first block in the blockchain (Genesis Block)
        genesis = Block(index=0, transactions=[], previous_hash="0", timestamp=int(time.time()), nonce=0)

        # Mine the genesis block to make sure it matches the proof-of-work rule
        genesis = self._mine_block_genesis(genesis)

        # Add genesis block to the chain
        self.chain.append(genesis)

    # ---------------------
    # Core helpers
    # ---------------------
    def last_block(self) -> Block:
        # Return the most recent block in the chain
        return self.chain[-1]

    @staticmethod
    def is_valid_transaction_structure(tx: Transaction) -> bool:
        # Check if a transaction has a valid structure
        if not isinstance(tx.amount, (int, float)):
            return False
        if tx.amount <= 0:
            return False
        if not tx.sender or not tx.receiver:
            return False
        if tx.sender == tx.receiver:  # Sender and receiver cannot be the same
            return False
        return True

    # ---------------------
    # Peer-to-Peer (P2P) Functions
    # ---------------------
    def new_transaction_from_dict(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        # Add a new transaction received from a peer node into the mempool
        try:
            new_tx = Transaction.from_dict(tx_data)
            if not self.is_valid_transaction_structure(new_tx):
                return {"error": "Invalid transaction data"}
            self.mempool.append(new_tx)
            return {"status": "ok", "message": "Transaction received"}
        except Exception as e:
            return {"error": f"Failed to add transaction: {e}"}

    def add_new_block(self, new_block: Block) -> bool:
        # Add a block received from a peer into our chain
        last_block = self.last_block()

        # Block must link correctly to the last block
        if new_block.previous_hash != last_block.hash:
            return False

        # Block must pass proof-of-work
        if not self._valid_proof(new_block):
            return False

        # Remove included transactions from our mempool (to avoid duplicates)
        included_ids = {tx.id for tx in new_block.transactions if tx.sender != "SYSTEM"}
        self.mempool = [tx for tx in self.mempool if tx.id not in included_ids]

        # Finally, add the block
        self.chain.append(new_block)
        return True

    def resolve_conflicts(self) -> bool:
        # Consensus Algorithm: Replace our chain with the longest valid chain among peers
        longest_chain = None
        max_length = len(self.chain)

        for peer in list(self.peers):
            try:
                response = requests.get(f'{peer}/blocks')
                if response.status_code == 200:
                    data = response.json()

                    # Convert peer's blocks into Block objects
                    peer_chain = [Block.from_dict(b) for b in data['chain']]
                    peer_length = len(peer_chain)

                    # Check if their chain is longer and valid
                    if peer_length > max_length and self.validate_chain(peer_chain):
                        max_length = peer_length
                        longest_chain = peer_chain
            except Exception as e:
                print(f"Error fetching chain from {peer}: {e}")
                continue

        # If a longer valid chain is found, replace ours
        if longest_chain:
            self.chain = longest_chain
            # For simplicity, clear mempool (in real systems we’d re-check missing transactions)
            self.mempool = []
            return True
        return False

    def validate_chain(self, chain_to_validate: List[Block]) -> bool:
        # Check if a given chain is valid
        if not chain_to_validate:
            return False

        # First block (genesis) must be valid
        if not chain_to_validate[0].compute_hash().startswith('0' * self.difficulty):
            return False

        # Validate rest of the blocks
        for i in range(1, len(chain_to_validate)):
            curr = chain_to_validate[i]
            prev = chain_to_validate[i - 1]

            if curr.previous_hash != prev.hash:
                return False
            if curr.hash != curr.compute_hash():
                return False
            if not curr.hash.startswith('0' * self.difficulty):
                return False
        return True

    # ---------------------
    # Transactions
    # ---------------------
    def new_transaction(self, sender: str, receiver: str, amount: float) -> str:
        # Create a new transaction and add it to mempool
        tx = Transaction(sender=sender, receiver=receiver, amount=amount)
        if not self.is_valid_transaction_structure(tx):
            raise ValueError("Invalid transaction structure")
        self.mempool.append(tx)
        return tx.id  # Return transaction ID

    # ---------------------
    # Proof-of-Work (PoW)
    # ---------------------
    def _valid_proof(self, block: Block) -> bool:
        # Check if block hash has required leading zeros
        return block.hash.startswith('0' * self.difficulty)

    def _proof_of_work(self, block: Block) -> Block:
        # Keep changing nonce until block hash starts with required zeros
        block.nonce = 0
        computed = block.compute_hash()
        while not computed.startswith('0' * self.difficulty):
            block.nonce += 1
            computed = block.compute_hash()
        block.hash = computed
        return block

    def _mine_block_genesis(self, genesis_block: Block) -> Block:
        # Special case: mine the first (genesis) block
        if not self._valid_proof(genesis_block):
            return self._proof_of_work(genesis_block)
        return genesis_block

    # ---------------------
    # Mining
    # ---------------------
    def mine_pending_transactions(self, miner_address: str, max_txs_per_block: int = 5) -> Block:
        # Select transactions to include in block (limit per block)
        if not self.mempool:
            txs_to_mine = []
        else:
            txs_to_mine = self.mempool[:max_txs_per_block]

        # Add mining reward transaction
        reward_tx = Transaction(sender="SYSTEM", receiver=miner_address, amount=self.miner_reward)
        txs_to_mine.append(reward_tx)

        # Create new block
        new_index = self.last_block().index + 1
        new_block = Block(index=new_index, transactions=txs_to_mine, previous_hash=self.last_block().hash, nonce=0)

        # Perform proof-of-work
        mined = self._proof_of_work(new_block)

        # Add block to chain
        self.chain.append(mined)

        # Remove mined transactions from mempool (excluding reward tx)
        included_ids = {tx.id for tx in txs_to_mine if tx.sender != "SYSTEM"}
        self.mempool = [tx for tx in self.mempool if tx.id not in included_ids]

        return mined

    # ---------------------
    # Validation & Ledger
    # ---------------------
    def is_chain_valid(self) -> bool:
        # Validate the entire chain block by block
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]

            if curr.hash != curr.compute_hash():
                return False
            if curr.previous_hash != prev.hash:
                return False
            if not self._valid_proof(curr):
                return False
        return True

    def get_balances(self) -> Dict[str, float]:
        # Calculate balances for each participant
        balances: Dict[str, float] = {}
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender != "SYSTEM":  # SYSTEM tx means mining reward
                    balances[tx.sender] = balances.get(tx.sender, 0.0) - tx.amount
                balances[tx.receiver] = balances.get(tx.receiver, 0.0) + tx.amount
        return balances

    # ---------------------
    # Utilities
    # ---------------------
    def to_dict(self) -> Dict[str, Any]:
        # Convert chain and mempool into dictionary format (for APIs or saving)
        return {
            "chain": [blk.to_dict() for blk in self.chain],
            "mempool": [tx.to_dict() for tx in self.mempool],
            "difficulty": self.difficulty
        }


# Quick demo when this file is run directly
if __name__ == "__main__":
    print("Quick local demo of blockchain package")
    bc = Blockchain(difficulty=3)
    print("Genesis:", bc.last_block())
    bc.new_transaction("Alice", "Bob", 5)
    bc.new_transaction("Bob", "Charlie", 2)
    print("Mining block...")
    bc.mine_pending_transactions(miner_address="Miner1")
    print("Chain valid:", bc.is_chain_valid())
    print("Balances:", bc.get_balances())
