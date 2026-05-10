"""Study Registry client — register, search, and manage reproducible studies."""
from .registry import register, search, validate

__version__ = "0.1.0"
__all__ = ["register", "search", "validate"]
