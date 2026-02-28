# Abstract Problem-Solving Framework

A formal system for representing problems and solutions as **domain-independent abstract structures**, enabling solution reuse across mathematics, software engineering, and any other domain.

## Core Thesis

Any problem, regardless of domain, can be decomposed into abstract structural components. Solutions to these abstract structures are domain-independent and can be instantiated in any concrete domain that shares the same structure.

This is not merely an analogy — it is a formal claim rooted in category theory: if two problems share the same abstract structure (are isomorphic in the appropriate category), then a solution to one is a solution to the other, modulo a structure-preserving mapping.

## How It Works

```
┌──────────────┐     F (abstract)     ┌──────────────────┐
│   Concrete   │ ──────────────────►  │    Abstract      │
│   Problem    │                      │    Problem       │
└──────────────┘                      └──────────────────┘
                                              │
                                              │ Pattern Match
                                              ▼
                                      ┌──────────────────┐
                                      │   Abstract       │
                                      │   Solution       │
                                      └──────────────────┘
                                              │
┌──────────────┐     G (instantiate)          │
│   Concrete   │ ◄────────────────────────────┘
│   Solution   │
└──────────────┘
```

1. **Abstract** — Given a concrete problem, map it to an abstract representation using an abstraction functor F
2. **Match** — Search the pattern store for a known abstract solution
3. **Instantiate** — Map the abstract solution back to concrete steps using an instantiation functor G
4. **Verify** — Confirm the concrete solution satisfies the original problem

## Formal Types

| Concept | Definition |
|---------|-----------|
| **Problem** | `(Structure, Constraints, Goal)` — a graph of entities/relations, what must hold, what we want |
| **Solution** | `(Preconditions, Transformation, Postconditions)` — when to apply, what steps, what's guaranteed |
| **Pattern** | Problem + Solution + known concrete instantiations across domains |
| **Abstraction Functor (F)** | Maps concrete domain objects/operations → abstract types |
| **Instantiation Functor (G)** | Maps abstract solution → concrete steps in any target domain |
| **PatternStore** | Knowledge base that matches new problems to known abstract patterns |

## Example: One Pattern, Many Domains

The **Fixed Point Iteration** pattern — "repeatedly apply a contractive transformation until stable" — appears identically in:

| Domain | Concrete Problem | Concrete Solution |
|--------|-----------------|-------------------|
| Mathematics | Find root of f(x) = 0 | Newton's method |
| Machine Learning | Train model parameters | Gradient descent |
| Compilers | Compute reaching definitions | Dataflow analysis |
| Economics | Find market equilibrium | Tatonnement process |
| Software Engineering | Resolve dependency versions | Constraint propagation |

These are all **the same abstract solution**. Discovering the pattern in one domain gives you the solution in all of them.

## Quick Start

```python
from src import PatternStore, Problem, Structure, Entity, Relation, Goal, GoalType

# Create a pattern store and load patterns
store = PatternStore()
store.load("examples/cross_domain/pattern_store.json")

# Define a new problem
problem = Problem(
    id="my-problem",
    name="Compute PageRank",
    structure=Structure(
        entities=[
            Entity("scores", "element", {"mutable": True}),
            Entity("update", "operation", {"contractive": True}),
        ],
        relations=[Relation("update", "scores", "maps_to")],
    ),
    goal=Goal(GoalType.FIND, "scores", "scores are stable"),
    tags=["iterative", "has_contractive_map"],
)

# Find matching abstract patterns
matches = store.match(problem)
for m in matches:
    print(f"{m.pattern.name}: {m.score:.0%} match")
    for inst in m.pattern.instantiations:
        print(f"  [{inst.domain}] {inst.concrete_problem}")
```

Run the full demo:

```bash
python examples/cross_domain/demo.py
```

## Project Structure

```
├── theory/
│   ├── foundations.md      # Core theory, definitions, taxonomy, formal properties
│   └── schema.md           # YAML/JSON schema specification for patterns
├── src/
│   ├── core.py             # Formal types: Problem, Solution, Pattern, Domain
│   ├── mapping.py          # Abstraction & instantiation functors
│   └── store.py            # Pattern storage, matching, persistence
├── examples/
│   └── cross_domain/
│       └── demo.py         # Working demo across 6+ domains
└── patterns/               # Pattern library (YAML/JSON)
```

## Abstract Operations Catalog

The framework defines 10 domain-independent operations that all solution patterns are composed from:

| Operation | Description | Math | Software |
|-----------|-------------|------|----------|
| `decompose` | Split into parts | Factor polynomial | Extract module |
| `compose` | Combine under rule | Function composition | Compose services |
| `transform` | Structure-preserving map | Linear transform | Refactor |
| `reduce` | Simplify preserving essence | Reduce fraction | Normalize data |
| `search` | Find element by predicate | Find root | Query/lookup |
| `fix` | Find stable point | Fixed-point iteration | Recursive definition |
| `dualize` | Switch perspective | Fourier transform | Interface inversion |
| `lift` | Move to higher abstraction | Generalize theorem | Extract interface |
| `project` | Move to lower/specific level | Restrict to subspace | Implement interface |
| `classify` | Group by equivalence | Quotient group | Type classification |

## Influences

Built on ideas from category theory, TRIZ, design patterns (GoF), Polya's heuristics, abstract interpretation, structure mapping theory, and the Curry-Howard correspondence. See [theory/foundations.md](theory/foundations.md) for the full theoretical grounding.
