# Schema Specification

## Overview

This document defines the formal YAML/JSON schemas used to represent abstract problems, solutions, and patterns in a machine-readable format. These schemas are the bridge between the mathematical theory (foundations.md) and the Python implementation.

---

## Problem Schema

```yaml
problem:
  id: string                    # Unique identifier
  name: string                  # Human-readable name

  structure:
    entities:                   # Nodes in the structural graph
      - id: string
        type: string            # Abstract type (e.g., "collection", "element", "relation")
        properties: {}          # Key-value pairs

    relations:                  # Edges in the structural graph
      - source: entity_id
        target: entity_id
        type: string            # e.g., "contains", "depends_on", "maps_to", "ordered_before"
        properties: {}

  constraints:                  # Predicates that must hold
    - predicate: string         # e.g., "forall x in A: P(x)"
      over: [entity_id]        # Which entities this constrains
      type: string              # "invariant" | "precondition" | "boundary"

  goal:
    type: string                # "find" | "transform" | "prove" | "optimize" | "construct"
    target: string              # What we want to achieve
    predicate: string           # Formal condition for success
```

## Solution Schema

```yaml
solution:
  id: string
  name: string

  preconditions:                # When does this solution apply?
    structural:                 # Required structural features
      - pattern: string         # e.g., "has_decomposable_structure"
        params: {}
    constraints:                # Required constraint types
      - type: string
        condition: string

  transformation:               # The abstract solution steps
    steps:
      - operation: string       # One of the abstract operations (decompose, compose, etc.)
        args: {}                # Operation-specific arguments
        binds: string           # Name to bind the result to
        rationale: string       # Why this step

    composition_type: string    # "sequential" | "parallel" | "conditional" | "iterative"

  postconditions:
    - predicate: string
      guarantees: string        # What this ensures about the goal

  metadata:
    discovered_in: [string]     # Domains where this pattern was first observed
    complexity: string          # Abstract complexity class
    composable_with: [string]   # Other pattern IDs this composes with
```

## Pattern Schema (Problem + Solution pair)

```yaml
pattern:
  id: string
  name: string
  description: string

  abstract_problem:             # The class of problems this solves
    structure_type: string      # From taxonomy: "decomposition", "search", etc.
    key_features: [string]      # Distinguishing structural features

  abstract_solution:            # Reference to solution
    solution_id: string

  instantiations:               # Known concrete instances
    - domain: string            # e.g., "software_engineering"
      concrete_problem: string  # e.g., "God class with too many responsibilities"
      concrete_solution: string # e.g., "Extract class refactoring"
      mapping_notes: string     # How abstract maps to concrete

    - domain: string
      concrete_problem: string
      concrete_solution: string
      mapping_notes: string

  related_patterns: [string]    # IDs of related patterns

  tags: [string]                # For search/retrieval
```

## Domain Mapping Schema

```yaml
domain_mapping:
  id: string
  domain: string                # e.g., "linear_algebra"

  type_map:                     # Abstract type → concrete type
    collection: "vector_space"
    element: "vector"
    operation: "linear_map"

  operation_map:                # Abstract operation → concrete operation
    decompose: "eigendecomposition"
    compose: "matrix_multiplication"
    transform: "linear_transformation"
    reduce: "row_reduction"
    search: "solve_system"

  axiom_map:                    # Which abstract axioms hold in this domain
    composable: true
    commutative: false          # Matrix multiplication is not commutative
    invertible: "when det != 0"

  constraints:                  # Domain-specific constraints
    - "dimensions must be compatible"
    - "field must be specified"
```

---

## Example: Fully Specified Pattern

```yaml
pattern:
  id: "divide-and-conquer"
  name: "Divide and Conquer"
  description: >
    When a problem's structure can be recursively decomposed into
    independent sub-problems of the same type, solve each sub-problem
    independently and combine the results.

  abstract_problem:
    structure_type: "transformational"
    key_features:
      - "recursive_decomposability"
      - "independent_subproblems"
      - "combinable_subsolutions"

  abstract_solution:
    solution_id: "sol-divide-conquer"
    steps:
      - operation: "decompose"
        args: { predicate: "recursive_split" }
        rationale: "Break into smaller instances of the same problem"
      - operation: "transform"
        args: { morphism: "solve_base_case", condition: "is_base_case" }
        rationale: "Solve trivially small instances directly"
      - operation: "compose"
        args: { rule: "merge_subsolutions" }
        rationale: "Combine sub-results into full result"

  instantiations:
    - domain: "algorithms"
      concrete_problem: "Sort a list of n elements"
      concrete_solution: "Merge sort: split list in half, sort each, merge"
      mapping_notes: "decompose=split, base_case=single element, compose=merge"

    - domain: "mathematics"
      concrete_problem: "Compute the Fourier transform of a signal"
      concrete_solution: "FFT: decompose into even/odd frequencies, combine with twiddle factors"
      mapping_notes: "decompose=even/odd split, base_case=single point DFT, compose=butterfly operation"

    - domain: "management"
      concrete_problem: "Large project with many independent deliverables"
      concrete_solution: "Work breakdown structure: decompose into work packages, assign teams, integrate"
      mapping_notes: "decompose=WBS, base_case=atomic task, compose=integration plan"

    - domain: "mathematics"
      concrete_problem: "Prove a theorem about all natural numbers"
      concrete_solution: "Strong induction: prove base case, assume for all k<n, prove for n"
      mapping_notes: "decompose=inductive structure, base_case=n=0, compose=inductive step"

  related_patterns: ["recursion", "reduction", "incremental-build"]
  tags: ["structural", "recursive", "parallelizable"]
```
