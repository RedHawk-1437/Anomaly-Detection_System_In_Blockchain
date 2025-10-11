# Import required libraries for blockchain functionality
import time
import requests
import json
from typing import List, Dict, Any
from urllib.parse import urlparse
from .block import Block
from .transaction import Transaction


class Blockchain:
    """
    Main Blockchain class implementing core blockchain functionality.

    This class represents a complete blockchain system with features including:
    - Block creation and mining
    - Transaction management
    - Proof-of-work consensus
    - Peer-to-peer network support
    - Double spending detection
    - Private network simulation for attack testing
    """

    def __init__(self, difficulty: int = 4, reward: float = 1.0):
        """
        Initialize a new blockchain with genesis block.

        Args:
            difficulty (int): Mining difficulty (number of leading zeros required in hash)
            reward (float): Mining reward for successful block mining
        """
        # Core blockchain data structures
        self.chain: List[Block] = []  # List of blocks forming the blockchain
        self.mempool: List[Transaction] = []  # Pending transactions waiting to be mined
        self.difficulty = int(difficulty)  # Mining difficulty level
        self.miner_reward = float(reward)  # Reward for mining a block
        self.peers = set()  # Set of peer nodes in the network

        # Security and attack simulation components
        self.private_networks = {}  # Track private networks for double spending attacks
        self.double_spend_transactions = []  # Record detected double spending attempts

        # Create and mine the genesis block (first block in chain)
        genesis = Block(index=0, transactions=[], previous_hash="0", timestamp=int(time.time()), nonce=0)
        genesis = self._mine_block_genesis(genesis)
        self.chain.append(genesis)

    def last_block(self) -> Block:
        """Get the most recent block in the blockchain"""
        return self.chain[-1]

    @staticmethod
    def is_valid_transaction_structure(tx: Transaction) -> bool:
        """
        Validate transaction structure and data integrity.

        Args:
            tx (Transaction): Transaction object to validate

        Returns:
            bool: True if transaction structure is valid
        """
        # Check amount is numeric and positive
        if not isinstance(tx.amount, (int, float)):
            return False
        if tx.amount <= 0:
            return False

        # Check sender and receiver addresses exist
        if not tx.sender or not tx.receiver:
            return False

        # Prevent self-transactions
        if tx.sender == tx.receiver:
            return False

        return True

    def new_transaction_from_dict(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create and add new transaction from dictionary data.

        Args:
            tx_data (Dict): Transaction data in dictionary format

        Returns:
            Dict: Operation result with status/error message
        """
        try:
            # Convert dictionary to Transaction object
            new_tx = Transaction.from_dict(tx_data)

            # Validate transaction structure
            if not self.is_valid_transaction_structure(new_tx):
                return {"error": "Invalid transaction data"}

            # Add to mempool for mining
            self.mempool.append(new_tx)
            return {"status": "ok", "message": "Transaction received"}

        except Exception as e:
            return {"error": f"Failed to add transaction: {e}"}

    def add_new_block(self, new_block: Block) -> bool:
        """
        Add a new block to the blockchain after validation.

        Performs comprehensive validation including:
        - Block type and structure
        - Chain continuity (previous hash matching)
        - Proof-of-work validity
        - Hash integrity
        - Double spending detection

        Args:
            new_block (Block): Block to add to chain

        Returns:
            bool: True if block was successfully added
        """
        # Validate block type
        if not isinstance(new_block, Block):
            print("Block rejected: Invalid block type")
            return False

        last_block = self.last_block()

        # Check chain continuity
        if new_block.previous_hash == last_block.hash:
            print(f"Block #{new_block.index} continues from our last block #{last_block.index}")

            # Validate proof-of-work
            if not self._valid_proof(new_block):
                print(f"Block rejected: Invalid proof-of-work")
                return False

            # Verify hash integrity
            if new_block.hash != new_block.compute_hash():
                print(f"Block rejected: Hash mismatch")
                return False

            # Check for double spending in transactions
            if self._has_double_spend(new_block.transactions):
                print(f"Block rejected: Contains double spend transactions")
                return False

            # Remove included transactions from mempool
            included_ids = {tx.id for tx in new_block.transactions if tx.sender != "SYSTEM"}
            self.mempool = [tx for tx in self.mempool if tx.id not in included_ids]

            # Add block to chain
            self.chain.append(new_block)
            print(f"✅ Block #{new_block.index} added successfully")
            return True

        else:
            # Handle chain forks
            print(f"Block #{new_block.index} has different previous hash")
            print(f"Expected (block #{last_block.index}): {last_block.hash[:10]}...")
            print(f"Got: {new_block.previous_hash[:10]}...")

            # Check if block connects to any point in our chain
            for i, existing_block in enumerate(self.chain):
                if new_block.previous_hash == existing_block.hash:
                    print(f"Block connects to block #{existing_block.index} in our chain")
                    print("Fork detected - rejecting for simplicity")
                    return False

            print("Block rejected: Does not connect to our chain")
            return False

    def _has_double_spend(self, transactions: List[Transaction]) -> bool:
        """
        Check if block contains double spend transactions.

        Implements double spending detection by tracking transactions from
        the same sender within a time window.

        Args:
            transactions: List of transactions to check

        Returns:
            bool: True if double spend detected
        """
        seen_senders = set()
        for tx in transactions:
            if tx.sender != "SYSTEM":
                # Create unique key based on sender, amount, and time window
                key = f"{tx.sender}_{tx.amount}_{int(time.time() // 60)}"  # Minute-based window
                if key in seen_senders:
                    print(f"Double spend detected: {tx.sender} spending {tx.amount}")
                    self.double_spend_transactions.append(tx.to_dict())
                    return True
                seen_senders.add(key)
        return False

    def create_private_network_fork(self, attacker_addr: str, network_size: int = 6) -> Dict[str, Any]:
        """
        Create a private network fork with specified number of nodes.

        Used for simulating double spending attacks by creating an isolated
        network where attacker can mine blocks privately.

        Args:
            attacker_addr: Attacker's wallet address
            network_size: Number of nodes in private network (minimum 6)

        Returns:
            Dict with private network details
        """
        if network_size < 6:
            network_size = 6

        # Create private network structure
        private_network = {
            "id": f"private_network_{int(time.time())}",
            "nodes": [],
            "chain_fork": self.chain.copy(),  # Fork from current chain state
            "created_at": int(time.time()),
            "attacker": attacker_addr,
            "network_size": network_size
        }

        # Create private nodes controlled by attacker
        for i in range(network_size):
            node = {
                "id": f"private_node_{i + 1}",
                "type": "attacker_controlled",
                "mining_power": 0.15,
                "region": "PrivateNetwork",
                "status": "active"
            }
            private_network["nodes"].append(node)

        # Store private network for tracking
        self.private_networks[private_network["id"]] = private_network

        print(f"Created private network with {network_size} nodes for attacker {attacker_addr}")
        return private_network

    def mine_private_blocks(self, private_network_id: str, num_blocks: int,
                            double_spend_tx: Transaction = None) -> List[Block]:
        """
        Mine blocks in private network for double spending attack.

        Simulates the mining process in a private network where attacker
        can include double spending transactions.

        Args:
            private_network_id: ID of the private network
            num_blocks: Number of blocks to mine
            double_spend_tx: Double spending transaction to include

        Returns:
            List of mined private blocks
        """
        if private_network_id not in self.private_networks:
            raise ValueError("Private network not found")

        private_network = self.private_networks[private_network_id]
        private_chain = private_network["chain_fork"]
        mined_blocks = []

        print(f"Mining {num_blocks} private blocks in network {private_network_id}")

        for i in range(num_blocks):
            last_private_block = private_chain[-1]
            new_index = last_private_block.index + 1

            # Prepare transactions for private block
            transactions = []
            if double_spend_tx and i == 0:  # Include double spend in first block
                transactions.append(double_spend_tx)
                print(f"Including double spend transaction: {double_spend_tx.sender} -> {double_spend_tx.receiver}")

            # Create and mine new block
            new_block = Block(
                index=new_index,
                transactions=transactions,
                previous_hash=last_private_block.hash,
                timestamp=int(time.time()),
                nonce=0
            )

            mined_block = self._proof_of_work(new_block)
            private_chain.append(mined_block)
            mined_blocks.append(mined_block)

            print(
                f"✅ Private block #{new_index} mined by {private_network['nodes'][i % len(private_network['nodes'])]['id']}")

        # Update private network state
        private_network["chain_fork"] = private_chain
        private_network["mined_blocks"] = mined_blocks
        private_network["last_mined"] = int(time.time())

        return mined_blocks

    def resolve_conflicts(self) -> bool:
        """
        Resolve blockchain conflicts using longest chain rule.

        Queries all peer nodes and adopts the longest valid chain to maintain
        network consensus.

        Returns:
            bool: True if chain was replaced with longer valid chain
        """
        longest_chain = None
        max_length = len(self.chain)

        # Query all peers for their chains
        for peer in list(self.peers):
            try:
                response = requests.get(f'{peer}/blocks', timeout=5)
                if response.status_code == 200:
                    data = response.json()

                    # Convert received chain data to Block objects
                    peer_chain = [Block.from_dict(b) for b in data['chain']]
                    peer_length = len(peer_chain)

                    # Adopt longer valid chain
                    if peer_length > max_length and self.validate_chain(peer_chain):
                        max_length = peer_length
                        longest_chain = peer_chain
            except Exception as e:
                print(f"Error fetching chain from {peer}: {e}")
                continue

        # Replace chain if longer valid chain found
        if longest_chain:
            self.chain = longest_chain
            self.mempool = []  # Clear mempool to avoid conflicts
            return True
        return False

    def validate_chain(self, chain_to_validate: List[Block]) -> bool:
        """
        Validate entire blockchain for integrity and consistency.

        Checks:
        - Genesis block validity
        - Hash continuity between blocks
        - Proof-of-work validity for each block

        Args:
            chain_to_validate: List of blocks to validate

        Returns:
            bool: True if chain is valid
        """
        if not chain_to_validate:
            return False

        # Validate genesis block proof-of-work
        if not chain_to_validate[0].compute_hash().startswith('0' * self.difficulty):
            return False

        # Validate each subsequent block
        for i in range(1, len(chain_to_validate)):
            curr = chain_to_validate[i]
            prev = chain_to_validate[i - 1]

            # Check hash continuity
            if curr.previous_hash != prev.hash:
                return False

            # Check block hash integrity
            if curr.hash != curr.compute_hash():
                return False

            # Check proof-of-work validity
            if not curr.hash.startswith('0' * self.difficulty):
                return False
        return True

    def new_transaction(self, sender: str, receiver: str, amount: float) -> str:
        """
        Create and add new transaction to mempool.

        Args:
            sender: Sender's wallet address
            receiver: Receiver's wallet address
            amount: Transaction amount

        Returns:
            str: Transaction ID
        """
        tx = Transaction(sender=sender, receiver=receiver, amount=amount)
        if not self.is_valid_transaction_structure(tx):
            raise ValueError("Invalid transaction structure")
        self.mempool.append(tx)
        return tx.id

    def _valid_proof(self, block: Block) -> bool:
        """Check if block meets proof-of-work difficulty requirement"""
        return block.hash.startswith('0' * self.difficulty)

    def _proof_of_work(self, block: Block) -> Block:
        """
        Perform proof-of-work mining on a block.

        Increments nonce until block hash meets difficulty requirement.

        Args:
            block: Block to mine

        Returns:
            Block: Mined block with valid nonce and hash
        """
        block.nonce = 0
        computed = block.compute_hash()

        # Keep trying different nonces until hash meets difficulty
        while not computed.startswith('0' * self.difficulty):
            block.nonce += 1
            computed = block.compute_hash()

        block.hash = computed
        return block

    def _mine_block_genesis(self, genesis_block: Block) -> Block:
        """
        Mine genesis block if not already valid.

        Args:
            genesis_block: Genesis block to mine

        Returns:
            Block: Valid genesis block
        """
        if not self._valid_proof(genesis_block):
            return self._proof_of_work(genesis_block)
        return genesis_block

    def mine_pending_transactions(self, miner_address: str, max_txs_per_block: int = 5) -> Block:
        """
        Mine pending transactions into a new block.

        Args:
            miner_address: Address to receive mining reward
            max_txs_per_block: Maximum transactions per block

        Returns:
            Block: Newly mined block
        """
        # Select transactions to include in block
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

        # Mine the block
        mined = self._proof_of_work(new_block)
        self.chain.append(mined)

        # Remove mined transactions from mempool
        included_ids = {tx.id for tx in txs_to_mine if tx.sender != "SYSTEM"}
        self.mempool = [tx for tx in self.mempool if tx.id not in included_ids]

        return mined

    def is_chain_valid(self) -> bool:
        """
        Validate the entire current blockchain.

        Returns:
            bool: True if blockchain is valid
        """
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

    def get_balances(self):
        """
        Calculate wallet balances from blockchain transactions.

        Processes all transactions in the blockchain to compute current balances
        for all wallet addresses. Includes handling for double spending attack
        scenarios.

        Returns:
            dict: Wallet addresses mapped to their current balances
        """
        balances = {}

        # Process all transactions in blockchain
        for block in self.chain:
            for tx in block.transactions:
                sender = tx.sender
                receiver = tx.receiver
                amount = tx.amount

                # Initialize balances for new addresses
                if sender not in balances:
                    balances[sender] = 0
                if receiver not in balances:
                    balances[receiver] = 0

                # Update balances (deduct from sender, add to receiver)
                if sender != "SYSTEM":
                    balances[sender] -= amount
                balances[receiver] += amount

        # Handle double spending attack scenarios
        from main import RECENT_ATTACK_RESULTS
        if 'last_attack' in RECENT_ATTACK_RESULTS:
            attack_data = RECENT_ATTACK_RESULTS['last_attack']
            attacker = attack_data.get('attacker', 'RedHawk')
            amount = attack_data.get('amount', 0)
            attack_success = attack_data.get('result', {}).get('successful', False)

            if attacker not in balances:
                balances[attacker] = 0

            # Adjust balances based on attack success
            if attack_success:
                balances[attacker] += amount
                if self.chain:
                    last_block = self.chain[-1]
                    for tx in last_block.transactions:
                        if tx.sender != "SYSTEM" and tx.amount == amount:
                            victim = tx.receiver
                            if victim in balances:
                                balances[victim] -= amount
                            break

        # Remove SYSTEM account from displayed balances
        if "SYSTEM" in balances:
            del balances["SYSTEM"]

        return balances

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert blockchain to dictionary for serialization.

        Returns:
            Dict: Blockchain data in serializable format
        """
        return {
            "chain": [blk.to_dict() for blk in self.chain],
            "mempool": [tx.to_dict() for tx in self.mempool],
            "difficulty": self.difficulty,
            "peers": list(self.peers),
            "miner_reward": self.miner_reward,
            "private_networks_count": len(self.private_networks),
            "double_spend_detected": len(self.double_spend_transactions) > 0
        }

    def __repr__(self):
        """String representation of blockchain for debugging"""
        return f"Blockchain(len={len(self.chain)} peers={len(self.peers)} mempool={len(self.mempool)})"