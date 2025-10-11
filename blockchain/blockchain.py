import time
import requests
import json
from typing import List, Dict, Any
from urllib.parse import urlparse
from .block import Block
from .transaction import Transaction


class Blockchain:
    def __init__(self, difficulty: int = 4, reward: float = 1.0):
        self.chain: List[Block] = []
        self.mempool: List[Transaction] = []
        self.difficulty = int(difficulty)
        self.miner_reward = float(reward)
        self.peers = set()

        # Private network tracking
        self.private_networks = {}
        self.double_spend_transactions = []

        genesis = Block(index=0, transactions=[], previous_hash="0", timestamp=int(time.time()), nonce=0)
        genesis = self._mine_block_genesis(genesis)
        self.chain.append(genesis)

    def last_block(self) -> Block:
        return self.chain[-1]

    @staticmethod
    def is_valid_transaction_structure(tx: Transaction) -> bool:
        if not isinstance(tx.amount, (int, float)):
            return False
        if tx.amount <= 0:
            return False
        if not tx.sender or not tx.receiver:
            return False
        if tx.sender == tx.receiver:
            return False
        return True

    def new_transaction_from_dict(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            new_tx = Transaction.from_dict(tx_data)
            if not self.is_valid_transaction_structure(new_tx):
                return {"error": "Invalid transaction data"}
            self.mempool.append(new_tx)
            return {"status": "ok", "message": "Transaction received"}
        except Exception as e:
            return {"error": f"Failed to add transaction: {e}"}

    def add_new_block(self, new_block: Block) -> bool:
        if not isinstance(new_block, Block):
            print("Block rejected: Invalid block type")
            return False

        last_block = self.last_block()

        if new_block.previous_hash == last_block.hash:
            print(f"Block #{new_block.index} continues from our last block #{last_block.index}")

            if not self._valid_proof(new_block):
                print(f"Block rejected: Invalid proof-of-work")
                return False

            if new_block.hash != new_block.compute_hash():
                print(f"Block rejected: Hash mismatch")
                return False

            # Check for double spending in transactions
            if self._has_double_spend(new_block.transactions):
                print(f"Block rejected: Contains double spend transactions")
                return False

            included_ids = {tx.id for tx in new_block.transactions if tx.sender != "SYSTEM"}
            self.mempool = [tx for tx in self.mempool if tx.id not in included_ids]

            self.chain.append(new_block)
            print(f"✅ Block #{new_block.index} added successfully")
            return True

        else:
            print(f"Block #{new_block.index} has different previous hash")
            print(f"Expected (block #{last_block.index}): {last_block.hash[:10]}...")
            print(f"Got: {new_block.previous_hash[:10]}...")

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

        Args:
            transactions: List of transactions to check

        Returns:
            bool: True if double spend detected
        """
        seen_senders = set()
        for tx in transactions:
            if tx.sender != "SYSTEM":
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

        Args:
            attacker_addr: Attacker's wallet address
            network_size: Number of nodes in private network (minimum 6)

        Returns:
            Dict with private network details
        """
        if network_size < 6:
            network_size = 6

        private_network = {
            "id": f"private_network_{int(time.time())}",
            "nodes": [],
            "chain_fork": self.chain.copy(),
            "created_at": int(time.time()),
            "attacker": attacker_addr,
            "network_size": network_size
        }

        # Create private nodes
        for i in range(network_size):
            node = {
                "id": f"private_node_{i + 1}",
                "type": "attacker_controlled",
                "mining_power": 0.15,
                "region": "PrivateNetwork",
                "status": "active"
            }
            private_network["nodes"].append(node)

        self.private_networks[private_network["id"]] = private_network

        print(f"Created private network with {network_size} nodes for attacker {attacker_addr}")
        return private_network

    def mine_private_blocks(self, private_network_id: str, num_blocks: int,
                            double_spend_tx: Transaction = None) -> List[Block]:
        """
        Mine blocks in private network for double spending attack.

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

        private_network["chain_fork"] = private_chain
        private_network["mined_blocks"] = mined_blocks
        private_network["last_mined"] = int(time.time())

        return mined_blocks

    def resolve_conflicts(self) -> bool:
        longest_chain = None
        max_length = len(self.chain)

        for peer in list(self.peers):
            try:
                response = requests.get(f'{peer}/blocks', timeout=5)
                if response.status_code == 200:
                    data = response.json()

                    peer_chain = [Block.from_dict(b) for b in data['chain']]
                    peer_length = len(peer_chain)

                    if peer_length > max_length and self.validate_chain(peer_chain):
                        max_length = peer_length
                        longest_chain = peer_chain
            except Exception as e:
                print(f"Error fetching chain from {peer}: {e}")
                continue

        if longest_chain:
            self.chain = longest_chain
            self.mempool = []
            return True
        return False

    def validate_chain(self, chain_to_validate: List[Block]) -> bool:
        if not chain_to_validate:
            return False

        if not chain_to_validate[0].compute_hash().startswith('0' * self.difficulty):
            return False

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

    def new_transaction(self, sender: str, receiver: str, amount: float) -> str:
        tx = Transaction(sender=sender, receiver=receiver, amount=amount)
        if not self.is_valid_transaction_structure(tx):
            raise ValueError("Invalid transaction structure")
        self.mempool.append(tx)
        return tx.id

    def _valid_proof(self, block: Block) -> bool:
        return block.hash.startswith('0' * self.difficulty)

    def _proof_of_work(self, block: Block) -> Block:
        block.nonce = 0
        computed = block.compute_hash()

        while not computed.startswith('0' * self.difficulty):
            block.nonce += 1
            computed = block.compute_hash()

        block.hash = computed
        return block

    def _mine_block_genesis(self, genesis_block: Block) -> Block:
        if not self._valid_proof(genesis_block):
            return self._proof_of_work(genesis_block)
        return genesis_block

    def mine_pending_transactions(self, miner_address: str, max_txs_per_block: int = 5) -> Block:
        if not self.mempool:
            txs_to_mine = []
        else:
            txs_to_mine = self.mempool[:max_txs_per_block]

        reward_tx = Transaction(sender="SYSTEM", receiver=miner_address, amount=self.miner_reward)
        txs_to_mine.append(reward_tx)

        new_index = self.last_block().index + 1
        new_block = Block(index=new_index, transactions=txs_to_mine, previous_hash=self.last_block().hash, nonce=0)

        mined = self._proof_of_work(new_block)
        self.chain.append(mined)

        included_ids = {tx.id for tx in txs_to_mine if tx.sender != "SYSTEM"}
        self.mempool = [tx for tx in self.mempool if tx.id not in included_ids]

        return mined

    def is_chain_valid(self) -> bool:
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
        balances = {}

        for block in self.chain:
            for tx in block.transactions:
                sender = tx.sender
                receiver = tx.receiver
                amount = tx.amount

                if sender not in balances:
                    balances[sender] = 0
                if receiver not in balances:
                    balances[receiver] = 0

                if sender != "SYSTEM":
                    balances[sender] -= amount
                balances[receiver] += amount

        from main import RECENT_ATTACK_RESULTS
        if 'last_attack' in RECENT_ATTACK_RESULTS:
            attack_data = RECENT_ATTACK_RESULTS['last_attack']
            attacker = attack_data.get('attacker', 'RedHawk')
            amount = attack_data.get('amount', 0)
            attack_success = attack_data.get('result', {}).get('successful', False)

            if attacker not in balances:
                balances[attacker] = 0

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

        if "SYSTEM" in balances:
            del balances["SYSTEM"]

        return balances

    def to_dict(self) -> Dict[str, Any]:
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
        return f"Blockchain(len={len(self.chain)} peers={len(self.peers)} mempool={len(self.mempool)})"