"""
Domain Mapping: Abstraction and Instantiation Functors.

Provides the bidirectional mapping between concrete domain problems
and abstract problem representations.

    F: Concrete → Abstract   (abstraction)
    G: Abstract → Concrete   (instantiation)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .core import (
    Constraint,
    ConstraintType,
    Entity,
    Goal,
    GoalType,
    Operation,
    Problem,
    Relation,
    Solution,
    Step,
    Structure,
    Transformation,
)


@dataclass
class DomainMapping:
    """
    A bidirectional mapping between a concrete domain and abstract types.

    Acts as both the abstraction functor F and instantiation functor G.
    """

    domain: str

    # Concrete type → abstract type
    type_map: dict[str, str] = field(default_factory=dict)

    # Concrete operation → abstract operation
    operation_map: dict[str, str] = field(default_factory=dict)

    # Domain-specific axioms and constraints
    axioms: dict[str, Any] = field(default_factory=dict)

    @property
    def inverse_type_map(self) -> dict[str, str]:
        """Abstract type → concrete type (for instantiation)."""
        return {v: k for k, v in self.type_map.items()}

    @property
    def inverse_operation_map(self) -> dict[str, str]:
        """Abstract operation → concrete operation (for instantiation)."""
        return {v: k for k, v in self.operation_map.items()}


def abstract(problem_desc: dict[str, Any], mapping: DomainMapping) -> Problem:
    """
    Abstraction functor F: Concrete → Abstract.

    Takes a concrete problem description and a domain mapping,
    returns an abstract Problem.

    Args:
        problem_desc: Dict with keys:
            - id, name: identifiers
            - entities: list of {id, type, properties}
            - relations: list of {source, target, type, properties}
            - constraints: list of {predicate, over, type}
            - goal: {type, target, predicate}
        mapping: DomainMapping for the concrete domain

    Returns:
        An abstract Problem with concrete types mapped to abstract types.
    """
    # Map concrete entity types to abstract types
    entities = []
    for e in problem_desc.get("entities", []):
        abstract_type = mapping.type_map.get(e["type"], e["type"])
        entities.append(Entity(
            id=e["id"],
            type=abstract_type,
            properties=e.get("properties", {}),
        ))

    # Map concrete relation types to abstract types
    relations = []
    for r in problem_desc.get("relations", []):
        abstract_type = mapping.type_map.get(r["type"], r["type"])
        relations.append(Relation(
            source=r["source"],
            target=r["target"],
            type=abstract_type,
            properties=r.get("properties", {}),
        ))

    # Map constraints
    constraints = []
    for c in problem_desc.get("constraints", []):
        constraints.append(Constraint(
            predicate=c["predicate"],
            over=c.get("over", []),
            type=ConstraintType(c.get("type", "invariant")),
        ))

    # Map goal
    goal = None
    if "goal" in problem_desc:
        g = problem_desc["goal"]
        goal = Goal(
            type=GoalType(g["type"]),
            target=g["target"],
            predicate=g["predicate"],
        )

    return Problem(
        id=problem_desc.get("id", ""),
        name=problem_desc.get("name", ""),
        structure=Structure(entities=entities, relations=relations),
        constraints=constraints,
        goal=goal,
        tags=problem_desc.get("tags", []),
    )


def instantiate(
    solution: Solution,
    mapping: DomainMapping,
) -> list[dict[str, Any]]:
    """
    Instantiation functor G: Abstract → Concrete.

    Takes an abstract Solution and a domain mapping,
    returns concrete steps in the target domain.

    Args:
        solution: An abstract Solution
        mapping: DomainMapping for the target domain

    Returns:
        A list of concrete step descriptions.
    """
    inv_ops = mapping.inverse_operation_map
    concrete_steps = []

    for step in solution.transformation.steps:
        concrete_op = inv_ops.get(step.operation.value, step.operation.value)
        concrete_steps.append({
            "operation": concrete_op,
            "abstract_operation": step.operation.value,
            "args": step.args,
            "binds": step.binds,
            "rationale": step.rationale,
            "domain": mapping.domain,
        })

    return concrete_steps
