# Topic 8: Implement Task Decomposition in Code

## Objective
The objective of this activity is to implement task decomposition in Python by representing a complex goal as a hierarchical task tree. The implementation recursively decomposes a goal into smaller subtasks, preserves dependencies between sibling tasks, enforces a maximum decomposition depth, extracts atomic leaf tasks, and validates the quality of the resulting task tree.

## Assessment Tasks

### Task 1 — Build the task tree
A deterministic task tree was created for the goal **launch blog**:

- launch blog
  - write posts
    - pick topics
    - draft
    - proofread
  - build site
    - choose theme
    - configure hosting

Dependencies are represented explicitly between related subtasks.

### Task 2 — Implement `decompose()`
The `decompose()` function recursively builds the task tree from predefined decomposition rules. It validates inputs, creates `Task` objects, recursively expands known tasks, attaches dependency information, and returns a deterministic tree.

### Task 3 — Enforce depth
A `max_depth` parameter prevents uncontrolled recursive decomposition. When decomposition exceeds the permitted depth, the implementation raises `RecursionError` with a descriptive message, providing a safe stopping mechanism.

### Task 4 — Flatten to atomic tasks
The `leaves()` function traverses the tree depth-first and returns only tasks with no children.

Final atomic tasks:
1. pick topics
2. draft
3. proofread
4. choose theme
5. configure hosting

Dependency information is preserved.

### Task 5 — Check task quality
The `check_quality()` function validates:
- valid `Task` objects
- non-empty task names
- valid child and dependency collections
- duplicate sibling task names
- unknown dependencies
- self-dependencies
- non-string dependencies
- malformed non-Task children
- cyclic task structures

The generated tree returns `valid=True` with no validation errors.

## Testing
Final regression command:

```text
python -m pytest -q
```

Final result:

```text
31 passed in 0.07s
```

The complete test suite covers all five required assessment tasks.

## Evidence
The `evidence` directory contains:
- `task_tree.json` — task-tree structure
- `decomposition_trace.json` — recursive decomposition and rules
- `depth_guard.json` — maximum-depth safety check
- `atomic_tasks.json` — flattened leaf tasks
- `quality_checks.json` — quality-validation cases
- `test_summary.json` — final regression result
- `run_output.txt` — application execution output
- `pytest_output.txt` — test execution evidence
- `generate_evidence.py` — deterministic evidence generator

## Example Output
```text
Topic 8 — Task Decomposition
============================================================

Recursively decomposed task tree:
- launch blog
  - write posts
    - pick topics
    - draft (after: pick topics)
    - proofread (after: draft)
  - build site
    - choose theme
    - configure hosting (after: choose theme)

Atomic leaf tasks:
- pick topics
- draft (after: pick topics)
- proofread (after: draft)
- choose theme
- configure hosting (after: choose theme)

Quality check:
valid=True
```

## Project Structure
```text
Task_Decomposition_Assessment/
├── src/
│   └── task_decomposition.py
├── tests/
│   └── test_task1.py
├── evidence/
│   ├── atomic_tasks.json
│   ├── decomposition_trace.json
│   ├── depth_guard.json
│   ├── generate_evidence.py
│   ├── pytest_output.txt
│   ├── quality_checks.json
│   ├── run_output.txt
│   ├── task_tree.json
│   └── test_summary.json
├── outputs/
├── requirements.txt
├── .gitignore
└── README.md
```

## Requirements
- Python 3.13.9
- pytest 8.4.2

## Running the Project
```text
python -m pytest -q
python src\task_decomposition.py
python evidence\generate_evidence.py
```

## Reflection
This activity helped me understand task decomposition as a practical engineering pattern rather than only a conceptual planning technique. The most useful part was converting a high-level goal into a deterministic hierarchy of smaller tasks and representing dependencies explicitly. This made the relationship between planning and executable code much clearer.

Implementing `decompose()` showed how recursion can naturally represent hierarchical planning. At the same time, the depth limit demonstrated why recursive systems need safety boundaries. Without a stopping condition, a faulty decomposition rule could continue indefinitely. Handling this with a controlled `RecursionError` made the implementation safer and easier to test.

The `leaves()` function reinforced the difference between intermediate planning steps and atomic executable tasks. Flattening the tree provides a practical representation of the actions that ultimately need to be completed while retaining their dependency information.

The quality-checking task was particularly valuable because a structurally valid-looking tree can still contain problems such as duplicate sibling names, missing dependencies, self-dependencies, malformed children, or invalid dependency values. Building validation around these cases made the implementation more robust.

Overall, this activity improved my understanding of hierarchical planning, recursive algorithms, dependency validation, defensive programming, and test-driven development. The final implementation is deterministic, locally executable, does not require external APIs or credentials, and includes reproducible evidence for each assessment task. The final regression suite contains 31 passing tests, providing confidence that the required functionality and hardening changes work together correctly.
