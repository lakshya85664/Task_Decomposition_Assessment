"""
Evidence generator for Topic 8:
Implement Task Decomposition in Code.

Generates structured JSON evidence for:
1. Task-tree construction
2. Recursive decomposition
3. Maximum-depth enforcement
4. Atomic-task flattening
5. Task-quality validation
6. Final pytest summary
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
EVIDENCE_DIR = PROJECT_ROOT / "evidence"

sys.path.insert(
    0,
    str(SRC_DIR),
)

from task_decomposition import (  # noqa: E402
    RULES,
    Task,
    check_quality,
    decompose,
    leaves,
)


def save_json(
    filename: str,
    data: object,
) -> None:
    """
    Save JSON evidence using readable formatting.
    """

    path = EVIDENCE_DIR / filename

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
        )

    print(
        f"Created: evidence/{filename}"
    )


def task_to_dict(
    task: Task,
) -> dict:
    """
    Convert a Task tree into a JSON-safe dictionary.
    """

    return {
        "name": task.name,
        "depends_on": list(
            task.depends_on
        ),
        "children": [
            task_to_dict(child)
            for child in task.children
        ],
    }


def generate_task_tree_evidence() -> None:
    """
    Evidence for Task 1:
    deterministic hierarchical task tree.
    """

    tree = decompose(
        "launch blog"
    )

    data = {
        "assessment_task": 1,
        "title": "Build the task tree",
        "root_goal": "launch blog",
        "tree": task_to_dict(
            tree
        ),
    }

    save_json(
        "task_tree.json",
        data,
    )


def generate_decomposition_evidence() -> None:
    """
    Evidence for Task 2:
    recursive decomposition and dependencies.
    """

    tree = decompose(
        "launch blog"
    )

    data = {
        "assessment_task": 2,
        "title": "Implement decompose()",
        "root_goal": tree.name,
        "rules_used": {
            name: [
                {
                    "task": child_name,
                    "depends_on": dependencies,
                }
                for child_name, dependencies in children
            ]
            for name, children in RULES.items()
        },
        "result": task_to_dict(
            tree
        ),
    }

    save_json(
        "decomposition_trace.json",
        data,
    )


def generate_depth_evidence() -> None:
    """
    Evidence for Task 3:
    maximum recursion-depth enforcement.
    """

    original_loop = RULES.get(
        "loop"
    )

    RULES["loop"] = [
        (
            "loop",
            [],
        )
    ]

    caught = False
    error_message = ""

    try:
        decompose(
            "loop",
            max_depth=2,
        )

    except RecursionError as error:
        caught = True
        error_message = str(
            error
        )

    finally:
        if original_loop is None:
            RULES.pop(
                "loop",
                None,
            )
        else:
            RULES["loop"] = original_loop

    data = {
        "assessment_task": 3,
        "title": "Enforce depth",
        "test_goal": "loop",
        "max_depth": 2,
        "recursion_error_caught": caught,
        "error_message": error_message,
        "safe_stop_verified": caught,
    }

    save_json(
        "depth_guard.json",
        data,
    )


def generate_atomic_task_evidence() -> None:
    """
    Evidence for Task 4:
    flattening the tree into atomic leaf tasks.
    """

    tree = decompose(
        "launch blog"
    )

    atomic_tasks = leaves(
        tree
    )

    data = {
        "assessment_task": 4,
        "title": "Flatten to atomic tasks",
        "count": len(
            atomic_tasks
        ),
        "atomic_tasks": [
            {
                "name": task.name,
                "depends_on": list(
                    task.depends_on
                ),
            }
            for task in atomic_tasks
        ],
    }

    save_json(
        "atomic_tasks.json",
        data,
    )


def generate_quality_evidence() -> None:
    """
    Evidence for Task 5:
    task-tree quality checks.
    """

    valid_tree = decompose(
        "launch blog"
    )

    valid_result, valid_errors = check_quality(
        valid_tree
    )

    duplicate_tree = Task(
        "root",
        children=[
            Task(
                "same"
            ),
            Task(
                "same"
            ),
        ],
    )

    duplicate_result, duplicate_errors = check_quality(
        duplicate_tree
    )

    unknown_dependency_tree = Task(
        "root",
        children=[
            Task(
                "task-a",
                depends_on=[
                    "missing-task",
                ],
            ),
        ],
    )

    unknown_result, unknown_errors = check_quality(
        unknown_dependency_tree
    )

    self_dependency_tree = Task(
        "root",
        children=[
            Task(
                "task-a",
                depends_on=[
                    "task-a",
                ],
            ),
        ],
    )

    self_result, self_errors = check_quality(
        self_dependency_tree
    )

    malformed_child_tree = Task(
        "root",
        children=[
            "not a task",
        ],
    )

    malformed_result, malformed_errors = check_quality(
        malformed_child_tree
    )

    data = {
        "assessment_task": 5,
        "title": "Check task quality",
        "cases": {
            "valid_tree": {
                "valid": valid_result,
                "errors": valid_errors,
            },
            "duplicate_sibling": {
                "valid": duplicate_result,
                "errors": duplicate_errors,
            },
            "unknown_dependency": {
                "valid": unknown_result,
                "errors": unknown_errors,
            },
            "self_dependency": {
                "valid": self_result,
                "errors": self_errors,
            },
            "malformed_child": {
                "valid": malformed_result,
                "errors": malformed_errors,
            },
        },
    }

    save_json(
        "quality_checks.json",
        data,
    )


def generate_test_summary() -> None:
    """
    Run pytest and save the final regression result.
    """

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    output = (
        result.stdout
        + result.stderr
    ).strip()

    data = {
        "command": "python -m pytest -q",
        "return_code": result.returncode,
        "passed": result.returncode == 0,
        "output": output,
    }

    save_json(
        "test_summary.json",
        data,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Final pytest regression failed."
        )


def main() -> None:
    """
    Generate all Topic 8 assessment evidence.
    """

    print(
        "Topic 8 — Evidence Generation"
    )
    print("=" * 60)

    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    generate_task_tree_evidence()
    generate_decomposition_evidence()
    generate_depth_evidence()
    generate_atomic_task_evidence()
    generate_quality_evidence()
    generate_test_summary()

    print()
    print(
        "All Topic 8 evidence generated successfully."
    )


if __name__ == "__main__":
    main()