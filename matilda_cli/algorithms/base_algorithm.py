"""Base algorithm interface for MATILDA."""

from abc import ABC, abstractmethod

from matilda_cli.database.alchemy_utility import AlchemyUtility
from matilda_cli.utils.rules import Rule


class BaseAlgorithm(ABC):
    """Abstract base class for rule discovery algorithms."""

    def __init__(self, database: AlchemyUtility):
        """
        Initialize the algorithm with a database.

        Args:
            database: AlchemyUtility instance for database operations
        """
        self.database = database

    @abstractmethod
    def discover_rules(self, **kwargs) -> Rule:
        """
        Discovers rules from the provided database.

        Args:
            **kwargs: Additional parameters required by specific algorithms.

        Returns:
            Generator yielding discovered rules.
        """
        pass
