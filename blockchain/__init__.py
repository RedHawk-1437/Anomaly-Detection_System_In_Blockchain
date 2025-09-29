# __init__.py
# This file makes the folder a Python package (so it can be imported).
# It also controls what parts of the package are directly available.

# Import main classes from other files so they can be accessed easily
from .blockchain import Blockchain   # Core Blockchain logic
from .transaction import Transaction # Transaction object
from .block import Block             # Block object

# __all__ tells Python which names should be exposed if someone writes:
#   from blockchain import *
__all__ = ["Blockchain", "Transaction", "Block"]