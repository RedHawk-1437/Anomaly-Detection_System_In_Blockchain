"""
__init__.py - Package Initialization Module

This module initializes the blockchain package and controls public API exposure.
It serves as the main entry point for importing blockchain components and
attack simulation functionality from external code.

The module provides organized access to:
- Core blockchain classes (Blockchain, Block, Transaction)
- Attack simulation functions and utilities
- SimBlock network integration
- Public API definition for clean imports

Usage:
    from blockchain import Blockchain, Transaction, Block
    from blockchain import run_attack, simulate_private_mining
    from blockchain import simblock_network
"""

# Import main classes from other files for easy access
# This allows clean imports like: from blockchain import Blockchain
from .blockchain import Blockchain   # Core Blockchain logic
from .transaction import Transaction # Transaction object
from .block import Block             # Block object

# Import attacker simulation functions
# These functions handle double spending attacks and network simulations
from .attacker import (
    run_attack,
    simulate_private_mining,
    broadcast_private_chain,
    simulate_network_partition,
    analyze_attack_patterns,
    run_double_spending_attack  # Double spending attack simulation
)

# Import SimBlock network integration
# Provides realistic network simulation with 120+ nodes
from .simblock_integration import simblock_network

# Define public API for 'from blockchain import *' imports
# Controls which classes/functions are exposed to external code
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
