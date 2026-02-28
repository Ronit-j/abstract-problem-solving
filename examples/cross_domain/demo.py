"""
Cross-Domain Demo: One Abstract Pattern, Many Concrete Solutions

This demo shows the core thesis in action:
    The "Divide and Conquer" pattern is ONE abstract solution
    that manifests across algorithms, mathematics, management, and more.

Run: python -m examples.cross_domain.demo
"""

import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.core import (
    CompositionType,
    Constraint,
    ConstraintType,
    Entity,
    Goal,
    GoalType,
    Instantiation,
    Operation,
    Pattern,
    Postcondition,
    Problem,
    Relation,
    Solution,
    Step,
    Structure,
    Transformation,
)
from src.mapping import DomainMapping, abstract, instantiate
from src.store import PatternStore


# ============================================================================
# Step 1: Define abstract patterns (domain-independent)
# ============================================================================

def build_divide_and_conquer() -> Pattern:
    """The Divide & Conquer pattern — works across any domain."""

    problem = Problem(
        id="prob-dac",
        name="Recursively Decomposable Problem",
        structure=Structure(
            entities=[
                Entity("whole", "collection", {"size": "n"}),
                Entity("part_1", "collection", {"size": "n/2"}),
                Entity("part_2", "collection", {"size": "n/2"}),
            ],
            relations=[
                Relation("whole", "part_1", "contains"),
                Relation("whole", "part_2", "contains"),
            ],
        ),
        constraints=[
            Constraint("parts are independent", ["part_1", "part_2"], ConstraintType.INVARIANT),
            Constraint("parts cover whole", ["whole", "part_1", "part_2"], ConstraintType.INVARIANT),
        ],
        goal=Goal(GoalType.TRANSFORM, "whole", "whole is in solved state"),
        tags=["recursive_decomposability", "independent_subproblems"],
    )

    solution = Solution(
        id="sol-dac",
        name="Divide and Conquer",
        preconditions=["recursive_decomposability", "independent_subproblems"],
        transformation=Transformation(
            steps=[
                Step(Operation.DECOMPOSE, {"predicate": "recursive_split"}, "parts",
                     "Break into smaller instances of the same problem type"),
                Step(Operation.TRANSFORM, {"morphism": "solve", "condition": "is_base_case"}, "base_solutions",
                     "Solve base cases directly"),
                Step(Operation.COMPOSE, {"rule": "merge"}, "full_solution",
                     "Combine sub-solutions into complete solution"),
            ],
            composition_type=CompositionType.SEQUENTIAL,
        ),
        postconditions=[
            Postcondition("whole is in solved state", "Solution covers all parts"),
        ],
    )

    return Pattern(
        id="pat-divide-conquer",
        name="Divide and Conquer",
        description=(
            "When a problem can be recursively decomposed into independent "
            "sub-problems of the same type, solve each sub-problem independently "
            "and combine the results."
        ),
        problem=problem,
        solution=solution,
        instantiations=[
            Instantiation(
                "algorithms",
                "Sort a list of n elements",
                "Merge sort: split in half, sort each, merge sorted halves",
                "decompose=split at midpoint, base_case=single element, compose=merge",
            ),
            Instantiation(
                "mathematics",
                "Compute Fourier transform of signal with n samples",
                "FFT: decompose into even/odd indices, recurse, combine with twiddle factors",
                "decompose=even/odd split, base_case=single point DFT, compose=butterfly",
            ),
            Instantiation(
                "management",
                "Execute large project with many deliverables",
                "WBS: decompose into work packages, assign teams, integrate results",
                "decompose=WBS, base_case=atomic task, compose=integration",
            ),
            Instantiation(
                "mathematics",
                "Multiply two n-digit numbers",
                "Karatsuba: split digits, 3 recursive multiplications instead of 4, combine",
                "decompose=split digits, base_case=single digit multiply, compose=shift and add",
            ),
        ],
        related_patterns=["pat-reduction", "pat-incremental"],
        tags=["structural", "recursive", "parallelizable"],
    )


def build_reduction_pattern() -> Pattern:
    """The Reduction pattern — transform hard problem into easier equivalent."""

    problem = Problem(
        id="prob-reduction",
        name="Problem Reducible to Known Form",
        structure=Structure(
            entities=[
                Entity("problem_A", "problem", {"difficulty": "hard"}),
                Entity("problem_B", "problem", {"difficulty": "easier"}),
            ],
            relations=[
                Relation("problem_A", "problem_B", "maps_to", {"preserves": "solution"}),
            ],
        ),
        goal=Goal(GoalType.TRANSFORM, "problem_A", "problem_A is solved"),
        tags=["reducible", "has_known_equivalent"],
    )

    solution = Solution(
        id="sol-reduction",
        name="Reduction to Known Problem",
        preconditions=["reducible", "has_known_equivalent"],
        transformation=Transformation(
            steps=[
                Step(Operation.TRANSFORM, {"morphism": "encode"}, "reduced_form",
                     "Transform problem into equivalent easier form"),
                Step(Operation.SEARCH, {"predicate": "is_solved"}, "reduced_solution",
                     "Solve the easier problem"),
                Step(Operation.TRANSFORM, {"morphism": "decode"}, "original_solution",
                     "Map solution back to original problem space"),
            ],
        ),
        postconditions=[
            Postcondition("problem_A is solved", "If encode/decode are correct and B is solved, A is solved"),
        ],
    )

    return Pattern(
        id="pat-reduction",
        name="Reduction to Known Problem",
        description=(
            "When a hard problem can be transformed into an equivalent problem "
            "that we already know how to solve, transform, solve, and map back."
        ),
        problem=problem,
        solution=solution,
        instantiations=[
            Instantiation(
                "algorithms",
                "Find shortest path with negative edge weights",
                "Reduce to Bellman-Ford by reweighting edges (Johnson's algorithm)",
                "encode=reweight edges, solve=Bellman-Ford, decode=adjust distances",
            ),
            Instantiation(
                "mathematics",
                "Solve differential equation",
                "Laplace transform: convert to algebraic equation, solve, inverse transform",
                "encode=Laplace transform, solve=algebra, decode=inverse Laplace",
            ),
            Instantiation(
                "software_engineering",
                "Complex data format conversion (A→C)",
                "Convert to intermediate canonical form (A→B→C) using existing A→B and B→C converters",
                "encode=convert to canonical, solve=identity, decode=convert from canonical",
            ),
            Instantiation(
                "cryptography",
                "Break cipher by finding structure",
                "Reduce to known algebraic problem (e.g., discrete log, factoring)",
                "encode=algebraic formulation, solve=known algorithm, decode=extract key",
            ),
        ],
        related_patterns=["pat-divide-conquer", "pat-dualization"],
        tags=["transformational", "equivalence", "mapping"],
    )


def build_fixed_point_pattern() -> Pattern:
    """The Fixed Point pattern — iterate until stable."""

    problem = Problem(
        id="prob-fixedpoint",
        name="Convergent Iterative Process",
        structure=Structure(
            entities=[
                Entity("state", "element", {"mutable": True}),
                Entity("transform", "operation", {"contractive": True}),
            ],
            relations=[
                Relation("transform", "state", "maps_to"),
            ],
        ),
        constraints=[
            Constraint("transform is contractive", ["transform"], ConstraintType.PRECONDITION),
        ],
        goal=Goal(GoalType.FIND, "state", "f(state) = state"),
        tags=["iterative", "convergent", "has_contractive_map"],
    )

    solution = Solution(
        id="sol-fixedpoint",
        name="Fixed Point Iteration",
        preconditions=["iterative", "has_contractive_map"],
        transformation=Transformation(
            steps=[
                Step(Operation.SEARCH, {"predicate": "initial_guess"}, "x0",
                     "Start with an initial approximation"),
                Step(Operation.FIX, {"morphism": "apply_transform_repeatedly"}, "x_star",
                     "Iterate x_{n+1} = f(x_n) until convergence"),
            ],
            composition_type=CompositionType.ITERATIVE,
        ),
        postconditions=[
            Postcondition("f(x_star) = x_star", "Converges to fixed point if f is contractive"),
        ],
    )

    return Pattern(
        id="pat-fixedpoint",
        name="Fixed Point Iteration",
        description=(
            "When you have a transformation that is contractive (brings things closer together), "
            "repeatedly applying it will converge to a unique stable point."
        ),
        problem=problem,
        solution=solution,
        instantiations=[
            Instantiation(
                "mathematics",
                "Find root of f(x) = 0",
                "Newton's method: x_{n+1} = x_n - f(x_n)/f'(x_n)",
                "transform=Newton update, convergence=quadratic near root",
            ),
            Instantiation(
                "compilers",
                "Compute reaching definitions in dataflow analysis",
                "Iterate dataflow equations over CFG until no changes",
                "transform=transfer functions, convergence=monotone on finite lattice",
            ),
            Instantiation(
                "machine_learning",
                "Train model parameters",
                "Gradient descent: θ_{n+1} = θ_n - α∇L(θ_n) until convergence",
                "transform=gradient update, convergence=with proper learning rate",
            ),
            Instantiation(
                "economics",
                "Find market equilibrium price",
                "Tatonnement: adjust price based on excess demand until supply=demand",
                "transform=price adjustment, convergence=under gross substitutability",
            ),
            Instantiation(
                "software_engineering",
                "Resolve dependency versions",
                "SAT solver / iterative constraint propagation until consistent assignment",
                "transform=propagate constraints, convergence=finite domain",
            ),
        ],
        related_patterns=["pat-reduction", "pat-invariance"],
        tags=["iterative", "convergent", "numerical"],
    )


# ============================================================================
# Step 2: Define domain mappings
# ============================================================================

def build_domain_mappings() -> dict[str, DomainMapping]:
    return {
        "algorithms": DomainMapping(
            domain="algorithms",
            type_map={
                "array": "collection",
                "element": "element",
                "comparison": "relation",
                "index": "position",
            },
            operation_map={
                "split": "decompose",
                "merge": "compose",
                "sort": "transform",
                "binary_search": "search",
                "memoize": "fix",
            },
        ),
        "linear_algebra": DomainMapping(
            domain="linear_algebra",
            type_map={
                "vector_space": "collection",
                "vector": "element",
                "matrix": "operation",
                "scalar": "element",
                "subspace": "sub_collection",
            },
            operation_map={
                "eigendecomposition": "decompose",
                "matrix_multiply": "compose",
                "linear_transform": "transform",
                "row_reduce": "reduce",
                "solve_system": "search",
                "transpose": "dualize",
            },
            axioms={
                "composable": True,
                "commutative": False,
                "invertible": "when det != 0",
            },
        ),
        "software_engineering": DomainMapping(
            domain="software_engineering",
            type_map={
                "class": "collection",
                "method": "operation",
                "field": "element",
                "interface": "contract",
                "module": "container",
                "dependency": "relation",
            },
            operation_map={
                "extract_class": "decompose",
                "compose_services": "compose",
                "refactor": "transform",
                "simplify": "reduce",
                "find_implementation": "search",
                "define_interface": "lift",
                "implement_interface": "project",
            },
        ),
    }


# ============================================================================
# Step 3: Demo — matching a new problem against the pattern store
# ============================================================================

def demo():
    print("=" * 70)
    print("ABSTRACT PROBLEM-SOLVING FRAMEWORK — Cross-Domain Demo")
    print("=" * 70)

    # Build pattern store
    store = PatternStore()
    store.add(build_divide_and_conquer())
    store.add(build_reduction_pattern())
    store.add(build_fixed_point_pattern())
    print(f"\nPattern store: {store}")

    # --- Demo 1: Match a concrete problem ---
    print("\n" + "-" * 70)
    print("DEMO 1: Matching a new problem")
    print("-" * 70)

    # A new problem: "Compute the closest pair of points in 2D"
    closest_pair = Problem(
        id="new-closest-pair",
        name="Find closest pair of points in 2D plane",
        structure=Structure(
            entities=[
                Entity("points", "collection", {"size": "n", "dimensions": 2}),
                Entity("left_half", "collection", {"size": "n/2"}),
                Entity("right_half", "collection", {"size": "n/2"}),
                Entity("distance", "element", {"type": "metric"}),
            ],
            relations=[
                Relation("points", "left_half", "contains"),
                Relation("points", "right_half", "contains"),
            ],
        ),
        goal=Goal(GoalType.FIND, "pair", "distance(pair) is minimal"),
        tags=["recursive_decomposability", "independent_subproblems"],
    )

    print(f"\nProblem: {closest_pair.name}")
    print(f"Structural features: {closest_pair.structural_features}")
    print(f"Tags: {closest_pair.tags}")

    matches = store.match(closest_pair, threshold=0.3)
    print(f"\nMatches found: {len(matches)}")
    for m in matches:
        print(f"\n  Pattern: {m.pattern.name}")
        print(f"  Score:   {m.score:.0%}")
        print(f"  Matched: {m.matched_features}")
        if m.unmatched_preconditions:
            print(f"  Missing: {m.unmatched_preconditions}")
        print(f"  Known instantiations in: {', '.join(m.pattern.domains_covered)}")

    # --- Demo 2: Instantiate solution in a specific domain ---
    print("\n" + "-" * 70)
    print("DEMO 2: Instantiating abstract solution in a concrete domain")
    print("-" * 70)

    best_match = matches[0]
    mappings = build_domain_mappings()

    for domain_name, mapping in mappings.items():
        concrete_steps = instantiate(best_match.pattern.solution, mapping)
        print(f"\n  In {domain_name}:")
        for step in concrete_steps:
            print(f"    → {step['operation']} ({step['rationale']})")

    # --- Demo 3: A problem that matches the Fixed Point pattern ---
    print("\n" + "-" * 70)
    print("DEMO 3: Different problem, different pattern")
    print("-" * 70)

    pagerank = Problem(
        id="new-pagerank",
        name="Compute PageRank of web graph",
        structure=Structure(
            entities=[
                Entity("scores", "element", {"mutable": True}),
                Entity("update_rule", "operation", {"contractive": True}),
            ],
            relations=[
                Relation("update_rule", "scores", "maps_to"),
            ],
        ),
        goal=Goal(GoalType.FIND, "scores", "scores are stable under update_rule"),
        tags=["iterative", "convergent", "has_contractive_map"],
    )

    print(f"\nProblem: {pagerank.name}")
    matches = store.match(pagerank, threshold=0.3)
    for m in matches:
        print(f"\n  Pattern: {m.pattern.name}")
        print(f"  Score:   {m.score:.0%}")
        print(f"  Matched: {m.matched_features}")
        print(f"\n  This tells us PageRank is structurally identical to:")
        for inst in m.pattern.instantiations:
            print(f"    - [{inst.domain}] {inst.concrete_problem}")

    # --- Demo 4: Save and reload ---
    print("\n" + "-" * 70)
    print("DEMO 4: Persistence")
    print("-" * 70)

    store_path = Path(__file__).parent / "pattern_store.json"
    store.save(store_path)
    print(f"\n  Saved {len(store)} patterns to {store_path.name}")

    store2 = PatternStore()
    store2.load(store_path)
    print(f"  Loaded {len(store2)} patterns back")
    print(f"  Patterns: {[p.name for p in store2.all_patterns]}")

    print("\n" + "=" * 70)
    print("KEY INSIGHT: The same abstract patterns appear across all domains.")
    print("A solution discovered in one domain transfers to any domain")
    print("with the same abstract structure.")
    print("=" * 70)


if __name__ == "__main__":
    demo()
