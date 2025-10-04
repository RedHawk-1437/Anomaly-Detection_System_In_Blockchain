# __init__.py - UPDATED VERSION
# This file makes the folder a Python package (so it can be imported).
# It also controls what parts of the package are directly available.

# Import main classes from other files so they can be accessed easily
from .blockchain import Blockchain   # Core Blockchain logic
from .transaction import Transaction # Transaction object
from .block import Block             # Block object

# Import attacker functions
from .attacker import (
    run_attack,
    simulate_private_mining,
    broadcast_private_chain,
    simulate_network_partition,
    analyze_attack_patterns,
    run_double_spending_attack  # NEW: Added this function
)

# Import SimBlock integration
from .simblock_integration import simblock_network

# __all__ tells Python which names should be exposed if someone writes:
#   from blockchain import *
__all__ = [
    "Blockchain",
    "Transaction",
    "Block",
    "run_attack",
    "simulate_private_mining",
    "broadcast_private_chain",
    "simulate_network_partition",
    "analyze_attack_patterns",
    "run_double_spending_attack",
    "simblock_network"
]
