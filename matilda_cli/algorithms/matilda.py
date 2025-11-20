"""MATILDA algorithm for discovering tuple-generating dependencies."""

from typing import Generator, Optional

from matilda_cli.algorithms.base_algorithm import BaseAlgorithm
from matilda_cli.algorithms.MATILDA.tgd_discovery import (
    dfs,
    init,
    instantiate_tgd,
    path_pruning,
    split_candidate_rule,
    split_pruning,
)
from matilda_cli.utils.rules import Rule, TGDRuleFactory


class MATILDA(BaseAlgorithm):
    """MATILDA algorithm for discovering tuple-generating dependencies (TGDs).

    MATILDA (Mining Approximate Tuple-Generating Dependencies in Large Databases)
    discovers logical rules (TGDs) from relational databases by analyzing table
    relationships, foreign keys, and data patterns.

    The algorithm uses constraint graphs and depth-first search to efficiently
    explore the space of possible rules while pruning unpromising candidates.

    Attributes:
        db_inspector (object): Database inspector for schema and data access.
        settings (dict): Configuration parameters for the discovery process.

    Examples:
        >>> from matilda_cli.database.alchemy_utility import AlchemyUtility
        >>> db = AlchemyUtility("path/to/database.db")
        >>> matilda = MATILDA(db, {"nb_occurrence": 3, "max_table": 3})
        >>> for rule in matilda.discover_rules():
        ...     print(rule)

    References:
        - Famat, F. (2025). MATILDA: TGD Discovery in Relational Databases.
        - Zenodo Database Schemas: https://zenodo.org/records/17644035
    """

    def __init__(self, database: object, settings: Optional[dict] = None):
        """Initialize MATILDA algorithm.

        Args:
            database: Database inspector object (typically AlchemyUtility) that
                provides access to schema metadata and query capabilities.
            settings: Optional configuration dictionary with the following keys:
                - nb_occurrence (int): Minimum rule support threshold. Default: 3
                - max_table (int): Maximum tables in a rule. Default: 3
                - max_vars (int): Maximum variables in a rule. Default: 6
                - results_dir (str): Directory for intermediate results.

        Raises:
            ValueError: If database is None or invalid.
        """
        self.db_inspector = database
        self.settings = settings or {}

    def discover_rules(self, **kwargs) -> Generator[Rule, None, None]:
        """Discover tuple-generating dependencies from the database.

        This method implements the core MATILDA algorithm:
        1. Initialize constraint graph from database schema
        2. Generate joinable indexed attributes (JIA list)
        3. Perform depth-first search with pruning
        4. Split candidate rules into body and head
        5. Validate rules with support and confidence metrics
        6. Instantiate and yield valid TGD rules

        Args:
            **kwargs: Optional parameters that override instance settings:
                nb_occurrence (int): Minimum support threshold (default: 3).
                    Rules must appear at least this many times in the data.
                max_table (int): Maximum tables per rule (default: 3).
                    Controls rule complexity.
                max_vars (int): Maximum variables per rule (default: 6).
                    Limits the number of attributes involved.
                results_dir (str): Path for saving intermediate results.
                    Useful for debugging and analysis.

        Yields:
            Rule: TGDRule objects representing discovered dependencies.
                Each rule has body (premises), head (conclusion),
                support (frequency), and confidence (accuracy).

        Examples:
            >>> for rule in matilda.discover_rules(nb_occurrence=5):
            ...     print(f"Rule: {rule}, Support: {rule.support}")

        Notes:
            - Higher nb_occurrence values find more general rules
            - Lower max_table/max_vars reduce search space but may miss complex rules
            - The generator pattern allows processing large result sets efficiently
        """
        nb_occurrence = kwargs.get("nb_occurrence", self.settings.get("nb_occurrence", 3))
        max_table = kwargs.get("max_table", self.settings.get("max_table", 3))
        max_vars = kwargs.get("max_vars", self.settings.get("max_vars", 6))
        results_path = kwargs.get("results_dir", self.settings.get("results_dir", None))

        # create a results folder if it does not exist
        if results_path:
            import os

            os.makedirs(results_path, exist_ok=True)

        cg, mapper, jia_list = init(
            self.db_inspector, max_nb_occurrence=nb_occurrence, results_path=results_path
        )

        if not jia_list:
            return

        for candidate_rule in dfs(
            cg,
            None,
            path_pruning,
            self.db_inspector,
            mapper,
            max_table=max_table,
            max_vars=max_vars,
        ):
            if not candidate_rule:
                continue

            splits = split_candidate_rule(candidate_rule)
            for body, head in splits:
                if not body or not head or len(head) != 1:
                    continue

                res, support, confidence = split_pruning(
                    candidate_rule, body, head, self.db_inspector, mapper
                )

                if not res:
                    debug = False
                    if debug:
                        print("removed")
                        a = instantiate_tgd(candidate_rule, (body, head), mapper)
                    continue

                tgd = instantiate_tgd(candidate_rule, (body, head), mapper)
                yield TGDRuleFactory.str_to_tgd(tgd, support, confidence)
