"""
Pattern Store: storage, retrieval, and matching of abstract patterns.

The PatternStore is the knowledge base of the framework — it holds
abstract patterns and can match them against new problems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import json

from .core import Pattern, Problem


@dataclass
class MatchResult:
    """A pattern match result with a relevance score."""

    pattern: Pattern
    score: float  # 0.0 to 1.0
    matched_features: list[str]
    unmatched_preconditions: list[str]

    @property
    def is_exact(self) -> bool:
        return self.score == 1.0


class PatternStore:
    """
    Stores abstract patterns and retrieves them by structural matching.

    The matching algorithm:
    1. Compute the problem's structural features
    2. For each pattern, check what fraction of its preconditions
       are satisfied by the problem's features
    3. Rank by match score (fraction of preconditions met)
    """

    def __init__(self) -> None:
        self._patterns: dict[str, Pattern] = {}

    def add(self, pattern: Pattern) -> None:
        """Add a pattern to the store."""
        self._patterns[pattern.id] = pattern

    def get(self, pattern_id: str) -> Pattern | None:
        return self._patterns.get(pattern_id)

    def remove(self, pattern_id: str) -> bool:
        return self._patterns.pop(pattern_id, None) is not None

    @property
    def all_patterns(self) -> list[Pattern]:
        return list(self._patterns.values())

    def match(self, problem: Problem, threshold: float = 0.5) -> list[MatchResult]:
        """
        Find patterns whose preconditions match the problem's structure.

        Args:
            problem: The abstract problem to match against
            threshold: Minimum score (0-1) to include in results

        Returns:
            List of MatchResults sorted by score (descending)
        """
        problem_features = set(problem.structural_features)
        problem_features.update(problem.tags)

        results = []
        for pattern in self._patterns.values():
            required = set(pattern.solution.preconditions)

            if not required:
                # Pattern with no preconditions matches everything weakly
                results.append(MatchResult(
                    pattern=pattern,
                    score=0.1,
                    matched_features=[],
                    unmatched_preconditions=[],
                ))
                continue

            matched = required & problem_features
            unmatched = required - problem_features
            score = len(matched) / len(required)

            if score >= threshold:
                results.append(MatchResult(
                    pattern=pattern,
                    score=score,
                    matched_features=sorted(matched),
                    unmatched_preconditions=sorted(unmatched),
                ))

        results.sort(key=lambda r: r.score, reverse=True)
        return results

    def search_by_tag(self, *tags: str) -> list[Pattern]:
        """Find patterns that have all the given tags."""
        tag_set = set(tags)
        return [p for p in self._patterns.values() if tag_set.issubset(set(p.tags))]

    def search_by_domain(self, domain: str) -> list[Pattern]:
        """Find patterns that have been instantiated in a given domain."""
        return [p for p in self._patterns.values() if domain in p.domains_covered]

    def save(self, path: str | Path) -> None:
        """Serialize the store to a JSON file."""
        path = Path(path)
        data = []
        for p in self._patterns.values():
            data.append(_pattern_to_dict(p))
        path.write_text(json.dumps(data, indent=2))

    def load(self, path: str | Path) -> None:
        """Load patterns from a JSON file."""
        path = Path(path)
        data = json.loads(path.read_text())
        for item in data:
            pattern = _dict_to_pattern(item)
            self._patterns[pattern.id] = pattern

    def __len__(self) -> int:
        return len(self._patterns)

    def __repr__(self) -> str:
        return f"PatternStore({len(self)} patterns)"


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------

def _pattern_to_dict(pattern: Pattern) -> dict:
    """Convert a Pattern to a JSON-serializable dict."""
    from .core import Postcondition

    return {
        "id": pattern.id,
        "name": pattern.name,
        "description": pattern.description,
        "problem": {
            "id": pattern.problem.id,
            "name": pattern.problem.name,
            "structure": {
                "entities": [
                    {"id": e.id, "type": e.type, "properties": e.properties}
                    for e in pattern.problem.structure.entities
                ],
                "relations": [
                    {"source": r.source, "target": r.target, "type": r.type, "properties": r.properties}
                    for r in pattern.problem.structure.relations
                ],
            },
            "constraints": [
                {"predicate": c.predicate, "over": c.over, "type": c.type.value}
                for c in pattern.problem.constraints
            ],
            "goal": {
                "type": pattern.problem.goal.type.value,
                "target": pattern.problem.goal.target,
                "predicate": pattern.problem.goal.predicate,
            } if pattern.problem.goal else None,
            "tags": pattern.problem.tags,
        },
        "solution": {
            "id": pattern.solution.id,
            "name": pattern.solution.name,
            "preconditions": pattern.solution.preconditions,
            "transformation": {
                "steps": [
                    {
                        "operation": s.operation.value,
                        "args": s.args,
                        "binds": s.binds,
                        "rationale": s.rationale,
                    }
                    for s in pattern.solution.transformation.steps
                ],
                "composition_type": pattern.solution.transformation.composition_type.value,
            },
            "postconditions": [
                {"predicate": pc.predicate, "guarantees": pc.guarantees}
                for pc in pattern.solution.postconditions
            ],
        },
        "instantiations": [
            {
                "domain": i.domain,
                "concrete_problem": i.concrete_problem,
                "concrete_solution": i.concrete_solution,
                "mapping_notes": i.mapping_notes,
            }
            for i in pattern.instantiations
        ],
        "related_patterns": pattern.related_patterns,
        "tags": pattern.tags,
    }


def _dict_to_pattern(d: dict) -> Pattern:
    """Reconstruct a Pattern from a dict."""
    from .core import (
        CompositionType,
        Constraint,
        ConstraintType,
        Entity,
        Goal,
        GoalType,
        Instantiation,
        Operation,
        Postcondition,
        Relation,
        Solution,
        Step,
        Structure,
        Transformation,
    )

    prob_d = d["problem"]
    struct = Structure(
        entities=[Entity(**e) for e in prob_d["structure"]["entities"]],
        relations=[Relation(**r) for r in prob_d["structure"]["relations"]],
    )
    constraints = [
        Constraint(predicate=c["predicate"], over=c["over"], type=ConstraintType(c["type"]))
        for c in prob_d.get("constraints", [])
    ]
    goal = None
    if prob_d.get("goal"):
        g = prob_d["goal"]
        goal = Goal(type=GoalType(g["type"]), target=g["target"], predicate=g["predicate"])

    problem = Problem(
        id=prob_d["id"],
        name=prob_d["name"],
        structure=struct,
        constraints=constraints,
        goal=goal,
        tags=prob_d.get("tags", []),
    )

    sol_d = d["solution"]
    steps = [
        Step(
            operation=Operation(s["operation"]),
            args=s.get("args", {}),
            binds=s.get("binds"),
            rationale=s.get("rationale", ""),
        )
        for s in sol_d["transformation"]["steps"]
    ]
    transformation = Transformation(
        steps=steps,
        composition_type=CompositionType(sol_d["transformation"].get("composition_type", "sequential")),
    )
    postconditions = [
        Postcondition(predicate=pc["predicate"], guarantees=pc["guarantees"])
        for pc in sol_d.get("postconditions", [])
    ]

    solution = Solution(
        id=sol_d["id"],
        name=sol_d["name"],
        preconditions=sol_d.get("preconditions", []),
        transformation=transformation,
        postconditions=postconditions,
    )

    instantiations = [Instantiation(**i) for i in d.get("instantiations", [])]

    return Pattern(
        id=d["id"],
        name=d["name"],
        description=d["description"],
        problem=problem,
        solution=solution,
        instantiations=instantiations,
        related_patterns=d.get("related_patterns", []),
        tags=d.get("tags", []),
    )
