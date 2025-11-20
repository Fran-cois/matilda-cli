"""MATILDA algorithm implementation."""

from matilda_cli.algorithms.MATILDA.candidate_rule_chains import CandidateRuleChains
from matilda_cli.algorithms.MATILDA.constraint_graph import (
    Attribute,
    AttributeMapper,
    ConstraintGraph,
    IndexedAttribute,
    JoinableIndexedAttributes,
)
from matilda_cli.algorithms.MATILDA.tgd_discovery import (
    dfs,
    init,
    instantiate_tgd,
    path_pruning,
    split_candidate_rule,
    split_pruning,
)

__all__ = [
    "Attribute",
    "AttributeMapper",
    "ConstraintGraph",
    "IndexedAttribute",
    "JoinableIndexedAttributes",
    "CandidateRuleChains",
    "init",
    "dfs",
    "path_pruning",
    "split_candidate_rule",
    "split_pruning",
    "instantiate_tgd",
]
