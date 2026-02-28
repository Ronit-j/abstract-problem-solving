"""
Abstract Problem-Solving Framework

A formal system for representing problems and solutions as domain-independent
abstract structures, enabling solution reuse across mathematics, software
engineering, and any other domain.
"""

from .core import (
    Entity,
    Relation,
    Structure,
    Constraint,
    Goal,
    Problem,
    Step,
    Transformation,
    Solution,
    Domain,
    Pattern,
    Instantiation,
)
from .mapping import DomainMapping, abstract, instantiate
from .store import PatternStore

__all__ = [
    "Entity",
    "Relation",
    "Structure",
    "Constraint",
    "Goal",
    "Problem",
    "Step",
    "Transformation",
    "Solution",
    "Domain",
    "Pattern",
    "Instantiation",
    "DomainMapping",
    "abstract",
    "instantiate",
    "PatternStore",
]
