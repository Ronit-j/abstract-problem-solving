"""
Core types for the Abstract Problem-Solving Framework.

Formalizes the mathematical definitions from theory/foundations.md as Python types.

Key concepts:
    Problem  = (Structure, Constraints, Goal)
    Solution = (Preconditions, Transformation, Postconditions)
    Pattern  = (AbstractProblem, AbstractSolution, Instantiations)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Structure: the objects and relations in a problem
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Entity:
    """A node in the problem's structural graph."""

    id: str
    type: str  # abstract type: "collection", "element", "relation", "container", etc.
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Relation:
    """A directed edge between entities."""

    source: str  # entity id
    target: str  # entity id
    type: str  # "contains", "depends_on", "maps_to", "ordered_before", etc.
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class Structure:
    """
    The structural graph of a problem.

    Entities are nodes, relations are edges. This captures *what is involved*
    in the problem without saying what needs to happen.
    """

    entities: list[Entity] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)

    def entity(self, entity_id: str) -> Entity | None:
        return next((e for e in self.entities if e.id == entity_id), None)

    def neighbors(self, entity_id: str, relation_type: str | None = None) -> list[str]:
        """Get IDs of entities connected to entity_id, optionally filtered by relation type."""
        results = []
        for r in self.relations:
            if r.source == entity_id and (relation_type is None or r.type == relation_type):
                results.append(r.target)
            if r.target == entity_id and (relation_type is None or r.type == relation_type):
                results.append(r.source)
        return results

    @property
    def entity_types(self) -> set[str]:
        return {e.type for e in self.entities}

    @property
    def relation_types(self) -> set[str]:
        return {r.type for r in self.relations}

    def has_feature(self, feature: str) -> bool:
        """Check if the structure has a named abstract feature."""
        feature_checks = {
            "recursive_decomposability": self._check_recursive,
            "linear_chain": self._check_linear_chain,
            "tree": self._check_tree,
            "cycle": self._check_cycle,
            "bipartite": self._check_bipartite,
        }
        check = feature_checks.get(feature)
        return check() if check else False

    def _check_recursive(self) -> bool:
        # A structure is recursively decomposable if it contains entities of the same type
        # connected by containment relations
        types = [e.type for e in self.entities]
        return len(types) != len(set(types))

    def _check_linear_chain(self) -> bool:
        ordered = [r for r in self.relations if r.type == "ordered_before"]
        return len(ordered) == len(self.entities) - 1

    def _check_tree(self) -> bool:
        contains = [r for r in self.relations if r.type == "contains"]
        return len(contains) == len(self.entities) - 1

    def _check_cycle(self) -> bool:
        if not self.relations:
            return False
        # Simple cycle detection via DFS
        adj: dict[str, list[str]] = {e.id: [] for e in self.entities}
        for r in self.relations:
            adj.setdefault(r.source, []).append(r.target)
        visited: set[str] = set()
        in_stack: set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            in_stack.add(node)
            for neighbor in adj.get(node, []):
                if neighbor in in_stack:
                    return True
                if neighbor not in visited and dfs(neighbor):
                    return True
            in_stack.discard(node)
            return False

        return any(dfs(e.id) for e in self.entities if e.id not in visited)

    def _check_bipartite(self) -> bool:
        return len(self.entity_types) == 2


# ---------------------------------------------------------------------------
# Constraints and Goals
# ---------------------------------------------------------------------------


class ConstraintType(Enum):
    INVARIANT = "invariant"  # Must hold throughout transformation
    PRECONDITION = "precondition"  # Must hold at start
    BOUNDARY = "boundary"  # Limits on the problem space


@dataclass(frozen=True)
class Constraint:
    """A predicate that must hold over part of the structure."""

    predicate: str  # Human-readable + machine-parseable predicate
    over: list[str]  # Entity IDs this constrains
    type: ConstraintType = ConstraintType.INVARIANT


class GoalType(Enum):
    FIND = "find"  # Find an element satisfying a condition
    TRANSFORM = "transform"  # Change structure from state A to state B
    PROVE = "prove"  # Show that a property holds
    OPTIMIZE = "optimize"  # Find the best element by some metric
    CONSTRUCT = "construct"  # Build a new structure satisfying constraints


@dataclass(frozen=True)
class Goal:
    """What the problem asks us to achieve."""

    type: GoalType
    target: str  # What we want
    predicate: str  # Formal success condition


# ---------------------------------------------------------------------------
# Problem = (Structure, Constraints, Goal)
# ---------------------------------------------------------------------------


@dataclass
class Problem:
    """
    An abstract problem: structure + constraints + goal.

    This is domain-independent. A sorting problem, a matrix decomposition,
    and an organizational restructuring can all be represented as Problems
    with the same abstract structure.
    """

    id: str
    name: str
    structure: Structure
    constraints: list[Constraint] = field(default_factory=list)
    goal: Goal | None = None
    tags: list[str] = field(default_factory=list)

    @property
    def structural_features(self) -> list[str]:
        """Compute the abstract structural features of this problem."""
        features = []
        for feat in ["recursive_decomposability", "linear_chain", "tree", "cycle", "bipartite"]:
            if self.structure.has_feature(feat):
                features.append(feat)
        return features


# ---------------------------------------------------------------------------
# Solution = (Preconditions, Transformation, Postconditions)
# ---------------------------------------------------------------------------


class Operation(Enum):
    """The catalog of abstract operations (morphisms)."""

    DECOMPOSE = "decompose"
    COMPOSE = "compose"
    TRANSFORM = "transform"
    REDUCE = "reduce"
    SEARCH = "search"
    FIX = "fix"
    DUALIZE = "dualize"
    LIFT = "lift"
    PROJECT = "project"
    CLASSIFY = "classify"


@dataclass
class Step:
    """A single step in an abstract transformation."""

    operation: Operation
    args: dict[str, Any] = field(default_factory=dict)
    binds: str | None = None  # Name for the result of this step
    rationale: str = ""


class CompositionType(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    ITERATIVE = "iterative"


@dataclass
class Transformation:
    """An ordered collection of abstract steps."""

    steps: list[Step] = field(default_factory=list)
    composition_type: CompositionType = CompositionType.SEQUENTIAL


@dataclass(frozen=True)
class Postcondition:
    predicate: str
    guarantees: str


@dataclass
class Solution:
    """
    An abstract solution pattern.

    Domain-independent: describes *what* to do at an abstract level,
    not *how* to do it in any specific domain.
    """

    id: str
    name: str
    preconditions: list[str] = field(default_factory=list)  # Required structural features
    transformation: Transformation = field(default_factory=Transformation)
    postconditions: list[Postcondition] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def matches(self, problem: Problem) -> bool:
        """Check if this solution's preconditions match the problem's structure."""
        problem_features = set(problem.structural_features)
        problem_features.update(problem.tags)
        required = set(self.preconditions)
        return required.issubset(problem_features)


# ---------------------------------------------------------------------------
# Domain
# ---------------------------------------------------------------------------


@dataclass
class Domain:
    """
    A concrete domain with its own objects, operations, and axioms.
    """

    name: str
    objects: dict[str, str] = field(default_factory=dict)  # abstract_type → concrete_type
    operations: dict[str, str] = field(default_factory=dict)  # abstract_op → concrete_op
    axioms: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Pattern = Problem + Solution + Instantiations
# ---------------------------------------------------------------------------


@dataclass
class Instantiation:
    """A known concrete instance of an abstract pattern in a specific domain."""

    domain: str
    concrete_problem: str
    concrete_solution: str
    mapping_notes: str = ""


@dataclass
class Pattern:
    """
    A reusable abstract pattern: an abstract problem class paired with
    its abstract solution and known concrete instantiations.

    This is the primary unit of knowledge in the pattern store.
    """

    id: str
    name: str
    description: str
    problem: Problem
    solution: Solution
    instantiations: list[Instantiation] = field(default_factory=list)
    related_patterns: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def add_instantiation(self, inst: Instantiation) -> None:
        """Record a new concrete instance of this pattern."""
        self.instantiations.append(inst)

    @property
    def domains_covered(self) -> set[str]:
        return {i.domain for i in self.instantiations}
