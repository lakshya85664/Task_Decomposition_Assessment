"""
Topic 8: Implement Task Decomposition in Code.

Tasks implemented:

Task 1:
    Build a deterministic task tree.

Task 2:
    Recursively decompose a goal into subtasks and attach
    dependencies between sibling subtasks.

Task 3:
    Enforce a maximum recursion depth.

Task 4:
    Flatten a task tree into atomic leaf tasks.

Task 5:
    Validate task-tree quality.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """
    Represents one node in a task decomposition tree.
    """

    name: str
    children: list["Task"] = field(
        default_factory=list
    )
    depends_on: list[str] = field(
        default_factory=list
    )


RULES: dict[str, list[tuple[str, list[str]]]] = {
    "launch blog": [
        (
            "write posts",
            [],
        ),
        (
            "build site",
            [],
        ),
    ],
    "write posts": [
        (
            "pick topics",
            [],
        ),
        (
            "draft",
            ["pick topics"],
        ),
        (
            "proofread",
            ["draft"],
        ),
    ],
    "build site": [
        (
            "choose theme",
            [],
        ),
        (
            "configure hosting",
            ["choose theme"],
        ),
    ],
}


def decompose(
    name: str,
    depth: int = 0,
    max_depth: int = 4,
) -> Task:
    """
    Recursively decompose a goal into a Task tree.

    Recursion is stopped when depth exceeds max_depth.
    """

    if not isinstance(
        name,
        str,
    ):
        raise TypeError(
            "name must be a string"
        )

    name = name.strip()

    if not name:
        raise ValueError(
            "name must not be empty"
        )

    if not isinstance(
        depth,
        int,
    ) or isinstance(
        depth,
        bool,
    ):
        raise TypeError(
            "depth must be an integer"
        )

    if not isinstance(
        max_depth,
        int,
    ) or isinstance(
        max_depth,
        bool,
    ):
        raise TypeError(
            "max_depth must be an integer"
        )

    if depth < 0:
        raise ValueError(
            "depth must not be negative"
        )

    if max_depth <= 0:
        raise ValueError(
            "max_depth must be greater than zero"
        )

    if depth > max_depth:
        raise RecursionError(
            f"maximum decomposition depth "
            f"{max_depth} exceeded for '{name}'"
        )

    task = Task(
        name=name
    )

    for child_name, dependencies in RULES.get(
        name,
        [],
    ):
        child = decompose(
            child_name,
            depth=depth + 1,
            max_depth=max_depth,
        )

        child.depends_on = list(
            dependencies
        )

        task.children.append(
            child
        )

    return task


def build_task_tree(
    name: str,
) -> Task:
    """
    Backward-compatible wrapper for the assessment API.
    """

    return decompose(
        name,
        depth=0,
        max_depth=4,
    )


def leaves(
    task: Task,
) -> list[Task]:
    """
    Return all atomic leaf tasks in depth-first order.

    Leaf tasks are nodes that do not contain any children.
    """

    if not isinstance(
        task,
        Task,
    ):
        raise TypeError(
            "task must be a Task"
        )

    if not task.children:
        return [task]

    result: list[Task] = []

    for child in task.children:
        result.extend(
            leaves(child)
        )

    return result


def check_quality(
    task: Task,
) -> tuple[bool, list[str]]:
    """
    Validate the structure and dependencies of a task tree.

    Returns:
        (True, []) when the tree is valid.

        (False, errors) when one or more quality issues
        are detected.
    """

    errors: list[str] = []

    # Track visited object IDs so malformed cyclic task structures
    # cannot cause infinite recursion during validation.
    visited: set[int] = set()

    def visit(
        current: Task,
        path: str,
    ) -> None:

        if not isinstance(
            current,
            Task,
        ):
            errors.append(
                f"{path}: task must be a Task"
            )
            return

        current_id = id(current)

        if current_id in visited:
            errors.append(
                f"{path}: task tree contains a cycle"
            )
            return

        visited.add(
            current_id
        )

        if not isinstance(
            current.name,
            str,
        ):
            errors.append(
                f"{path}: task name must be a string"
            )
            return

        if not current.name.strip():
            errors.append(
                f"{path}: task name must not be empty"
            )

        if not isinstance(
            current.children,
            list,
        ):
            errors.append(
                f"{path}: children must be a list"
            )
            return

        if not isinstance(
            current.depends_on,
            list,
        ):
            errors.append(
                f"{path}: depends_on must be a list"
            )
            return

        # Validate the current task's own dependencies.
        for dependency in current.depends_on:

            if not isinstance(
                dependency,
                str,
            ):
                errors.append(
                    f"{path}: dependency names must be strings"
                )
                continue

            if dependency == current.name:
                errors.append(
                    f"{path}: task cannot depend on itself"
                )

        # Collect valid sibling names.
        #
        # Invalid children are reported separately and are deliberately
        # excluded here so malformed objects cannot cause AttributeError.
        sibling_names: list[str] = []

        for index, child in enumerate(
            current.children
        ):
            if not isinstance(
                child,
                Task,
            ):
                errors.append(
                    f"{path}: child {index} must be a Task"
                )
                continue

            if not isinstance(
                child.name,
                str,
            ):
                errors.append(
                    f"{path}: child {index} task name must be a string"
                )
                continue

            sibling_names.append(
                child.name
            )

        # Check duplicate sibling names only after ensuring names
        # are valid strings.
        if len(sibling_names) != len(
            set(sibling_names)
        ):
            errors.append(
                f"{path}: sibling task names must be unique"
            )

        sibling_name_set = set(
            sibling_names
        )

        # Validate dependencies for every valid child.
        #
        # IMPORTANT:
        # Invalid children are skipped here. This prevents errors such
        # as:
        #     AttributeError: 'str' object has no attribute 'depends_on'
        #
        # while still retaining the earlier validation error saying
        # that the child must be a Task.
        for child in current.children:

            if not isinstance(
                child,
                Task,
            ):
                continue

            # If the child's name itself is invalid, it has already
            # been reported above. We can still safely validate its
            # dependency list only when that list is actually a list.
            if not isinstance(
                child.depends_on,
                list,
            ):
                errors.append(
                    f"{path}/{child.name}: "
                    f"depends_on must be a list"
                )
                continue

            for dependency in child.depends_on:

                if not isinstance(
                    dependency,
                    str,
                ):
                    errors.append(
                        f"{path}/{child.name}: "
                        f"dependency names must be strings"
                    )
                    continue

                if dependency == child.name:
                    errors.append(
                        f"{path}/{child.name}: "
                        f"task cannot depend on itself"
                    )
                    continue

                if dependency not in sibling_name_set:
                    errors.append(
                        f"{path}/{child.name}: "
                        f"unknown dependency '{dependency}'"
                    )

        # Recursively validate valid child tasks.
        for child in current.children:

            if not isinstance(
                child,
                Task,
            ):
                continue

            child_path = (
                f"{path}/{child.name}"
                if isinstance(
                    child.name,
                    str,
                )
                else f"{path}/<invalid-name>"
            )

            visit(
                child,
                child_path,
            )

    visit(
        task,
        task.name
        if isinstance(
            task,
            Task,
        )
        else "<invalid>",
    )

    return (
        len(errors) == 0,
        errors,
    )


def show(
    task: Task,
    indent: int = 0,
) -> None:
    """
    Print a readable representation of the task tree.
    """

    if not isinstance(
        task,
        Task,
    ):
        raise TypeError(
            "task must be a Task"
        )

    dependency_text = ""

    if task.depends_on:
        dependency_text = (
            " (after: "
            + ", ".join(task.depends_on)
            + ")"
        )

    print(
        "  " * indent
        + "- "
        + task.name
        + dependency_text
    )

    for child in task.children:
        show(
            child,
            indent + 1,
        )


def main() -> None:
    """
    Run the complete Topic 8 demonstration.
    """

    tree = decompose(
        "launch blog"
    )

    print(
        "Topic 8 — Task Decomposition"
    )
    print("=" * 60)
    print()

    print(
        "Recursively decomposed task tree:"
    )

    show(
        tree
    )

    print()
    print(
        "Atomic leaf tasks:"
    )

    for task in leaves(
        tree
    ):

        dependency_text = ""

        if task.depends_on:
            dependency_text = (
                f" (after: "
                f"{', '.join(task.depends_on)})"
            )

        print(
            f"- {task.name}"
            f"{dependency_text}"
        )

    print()
    print(
        "Quality check:"
    )

    valid, errors = check_quality(
        tree
    )

    print(
        f"valid={valid}"
    )

    if errors:
        for error in errors:
            print(
                f"- {error}"
            )


if __name__ == "__main__":
    main()