# blockchain.py - FIXED VERSION
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
    """
    Main Blockchain class that manages the entire blockchain network.

    Responsibilities:
    - Maintain chain of blocks
    - Manage pending transactions (mempool)
    - Handle mining and proof-of-work
    - Manage peer-to-peer network
    - Validate transactions and blocks
    """

    def __init__(self, difficulty: int = 4, reward: float = 1.0):
        """
        Initialize a new Blockchain.

        Args:
            difficulty (int): Mining difficulty (number of leading zeros in hash)
            reward (float): Mining reward for miners
        """
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
        """
        Get the most recent block in the chain.

        Returns:
            Block: The last block in the chain
        """
        return self.chain[-1]

    @staticmethod
    def is_valid_transaction_structure(tx: Transaction) -> bool:
        """
        Validate the structure of a transaction.

        Args:
            tx (Transaction): Transaction to validate

        Returns:
            bool: True if transaction structure is valid
        """
        # Check if amount is valid number
        if not isinstance(tx.amount, (int, float)):
            return False
        # Check if amount is positive
        if tx.amount <= 0:
            return False
        # Check if sender and receiver exist
        if not tx.sender or not tx.receiver:
            return False
        # Sender and receiver cannot be the same
        if tx.sender == tx.receiver:
            return False
        return True

    # ---------------------
    # Peer-to-Peer (P2P) Functions
    # ---------------------
    def new_transaction_from_dict(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new transaction received from a peer node into the mempool.

        Args:
            tx_data (Dict): Transaction data from peer

        Returns:
            Dict: Result of transaction addition
        """
        try:
            # Create Transaction object from dictionary
            new_tx = Transaction.from_dict(tx_data)
            # Validate transaction structure
            if not self.is_valid_transaction_structure(new_tx):
                return {"error": "Invalid transaction data"}
            # Add to mempool
            self.mempool.append(new_tx)
            return {"status": "ok", "message": "Transaction received"}
        except Exception as e:
            return {"error": f"Failed to add transaction: {e}"}

    def add_new_block(self, new_block: Block) -> bool:
        """
        Add a block received from a peer into our chain - IMPROVED VERSION.

        Args:
            new_block (Block): Block to add to chain

        Returns:
            bool: True if block was added successfully
        """
        # Validate block type
        if not isinstance(new_block, Block):
            print("Block rejected: Invalid block type")
            return False

        last_block = self.last_block()

        # Check if this block builds on our last block
        if new_block.previous_hash == last_block.hash:
            # Standard case: block continues our chain
            print(f"Block #{new_block.index} continues from our last block #{last_block.index}")

            # Validate proof-of-work
            if not self._valid_proof(new_block):
                print(f"Block rejected: Invalid proof-of-work")
                return False

            # Validate hash matches computed hash
            if new_block.hash != new_block.compute_hash():
                print(f"Block rejected: Hash mismatch")
                return False

            # Remove included transactions from mempool (except reward transactions)
            included_ids = {tx.id for tx in new_block.transactions if tx.sender != "SYSTEM"}
            self.mempool = [tx for tx in self.mempool if tx.id not in included_ids]

            # Add the block to our chain
            self.chain.append(new_block)
            print(f"✅ Block #{new_block.index} added successfully")
            return True

        else:
            # This block doesn't continue our chain - it might be a fork
            print(f"Block #{new_block.index} has different previous hash")
            print(f"Expected (block #{last_block.index}): {last_block.hash[:10]}...")
            print(f"Got: {new_block.previous_hash[:10]}...")

            # Check if this block connects to any earlier block in our chain
            for i, existing_block in enumerate(self.chain):
                if new_block.previous_hash == existing_block.hash:
                    print(f"Block connects to block #{existing_block.index} in our chain")

                    # This is a fork - we need to handle it properly
                    # For now, we'll reject forks to keep it simple
                    # In a real implementation, you'd check which chain is longer
                    print("Fork detected - rejecting for simplicity")
                    return False

            # Block doesn't connect to our chain at all
            print("Block rejected: Does not connect to our chain")
            return False

    def resolve_conflicts(self) -> bool:
        """
        Consensus Algorithm: Replace our chain with the longest valid chain among peers.

        Returns:
            bool: True if our chain was replaced
        """
        longest_chain = None
        max_length = len(self.chain)

        # Check all peers for longer chains
        for peer in list(self.peers):
            try:
                response = requests.get(f'{peer}/blocks', timeout=5)
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
            # For simplicity, clear mempool (in real systems we'd re-check missing transactions)
            self.mempool = []
            return True
        return False

    def validate_chain(self, chain_to_validate: List[Block]) -> bool:
        """
        Check if a given chain is valid.

        Args:
            chain_to_validate (List[Block]): Chain to validate

        Returns:
            bool: True if chain is valid
        """
        if not chain_to_validate:
            return False

        # First block (genesis) must be valid
        if not chain_to_validate[0].compute_hash().startswith('0' * self.difficulty):
            return False

        # Validate rest of the blocks
        for i in range(1, len(chain_to_validate)):
            curr = chain_to_validate[i]
            prev = chain_to_validate[i - 1]

            # Check block linkage
            if curr.previous_hash != prev.hash:
                return False
            # Check hash integrity
            if curr.hash != curr.compute_hash():
                return False
            # Check proof-of-work
            if not curr.hash.startswith('0' * self.difficulty):
                return False
        return True

    # ---------------------
    # Transactions
    # ---------------------
    def new_transaction(self, sender: str, receiver: str, amount: float) -> str:
        """
        Create a new transaction and add it to mempool.

        Args:
            sender (str): Sender's address
            receiver (str): Receiver's address
            amount (float): Transaction amount

        Returns:
            str: Transaction ID
        """
        # Create new transaction
        tx = Transaction(sender=sender, receiver=receiver, amount=amount)
        # Validate transaction structure
        if not self.is_valid_transaction_structure(tx):
            raise ValueError("Invalid transaction structure")
        # Add to mempool
        self.mempool.append(tx)
        return tx.id  # Return transaction ID

    # ---------------------
    # Proof-of-Work (PoW)
    # ---------------------
    def _valid_proof(self, block: Block) -> bool:
        """
        Check if block hash has required leading zeros (proof-of-work).

        Args:
            block (Block): Block to validate

        Returns:
            bool: True if proof is valid
        """
        return block.hash.startswith('0' * self.difficulty)

    def _proof_of_work(self, block: Block) -> Block:
        """
        Perform proof-of-work by finding a nonce that creates valid hash.

        Args:
            block (Block): Block to mine

        Returns:
            Block: Mined block with valid nonce
        """
        # Start with nonce 0
        block.nonce = 0
        computed = block.compute_hash()

        # Keep incrementing nonce until we find valid hash
        while not computed.startswith('0' * self.difficulty):
            block.nonce += 1
            computed = block.compute_hash()

        # Set the valid hash
        block.hash = computed
        return block

    def _mine_block_genesis(self, genesis_block: Block) -> Block:
        """
        Special case: mine the first (genesis) block.

        Args:
            genesis_block (Block): Genesis block to mine

        Returns:
            Block: Mined genesis block
        """
        if not self._valid_proof(genesis_block):
            return self._proof_of_work(genesis_block)
        return genesis_block

    # ---------------------
    # Mining
    # ---------------------
    def mine_pending_transactions(self, miner_address: str, max_txs_per_block: int = 5) -> Block:
        """
        Mine pending transactions into a new block.

        Args:
            miner_address (str): Address to receive mining reward
            max_txs_per_block (int): Maximum transactions per block

        Returns:
            Block: Newly mined block
        """
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

        # Perform proof-of-work (mining)
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
        """
        Validate the entire chain block by block.

        Returns:
            bool: True if chain is valid
        """
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]

            # Check hash integrity
            if curr.hash != curr.compute_hash():
                return False
            # Check block linkage
            if curr.previous_hash != prev.hash:
                return False
            # Check proof-of-work
            if not self._valid_proof(curr):
                return False
        return True


    def get_balances(self):
        """
        Calculate current wallet balances including attack scenarios
        """
        balances = {}

        # Process all transactions in the blockchain
        for block in self.chain:
            for tx in block.transactions:
                sender = tx.sender
                receiver = tx.receiver
                amount = tx.amount

                # Initialize wallets if not present
                if sender not in balances:
                    balances[sender] = 0
                if receiver not in balances:
                    balances[receiver] = 0

                # ✅ FIXED: Only deduct from sender if not SYSTEM (mining reward)
                if sender != "SYSTEM":
                    balances[sender] -= amount
                balances[receiver] += amount

        # ✅ Include attacker balances from recent attacks
        from main import RECENT_ATTACK_RESULTS
        if 'last_attack' in RECENT_ATTACK_RESULTS:
            attack_data = RECENT_ATTACK_RESULTS['last_attack']
            attacker = attack_data.get('attacker', 'RedHawk')
            amount = attack_data.get('amount', 0)
            attack_success = attack_data.get('result', {}).get('successful', False)

            # Initialize attacker wallet if not present
            if attacker not in balances:
                balances[attacker] = 0

            # ✅ If attack successful, attacker gains the amount
            if attack_success:
                balances[attacker] += amount
                # Find the victim (receiver in recent transactions) and deduct
                if self.chain:
                    last_block = self.chain[-1]
                    for tx in last_block.transactions:
                        if tx.sender != "SYSTEM" and tx.amount == amount:
                            victim = tx.receiver
                            if victim in balances:
                                balances[victim] -= amount
                            break

        # Remove SYSTEM from balances for display
        if "SYSTEM" in balances:
            del balances["SYSTEM"]

        return balances

    # ---------------------
    # Utilities
    # ---------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert chain and mempool into dictionary format (for APIs or saving).

        Returns:
            Dict: Blockchain data as dictionary
        """
        return {
            "chain": [blk.to_dict() for blk in self.chain],
            "mempool": [tx.to_dict() for tx in self.mempool],
            "difficulty": self.difficulty,
            "peers": list(self.peers),
            "miner_reward": self.miner_reward
        }

    def __repr__(self):
        """
        String representation of the blockchain.

        Returns:
            str: Human-readable blockchain description
        """
        return f"Blockchain(len={len(self.chain)} peers={len(self.peers)} mempool={len(self.mempool)})"