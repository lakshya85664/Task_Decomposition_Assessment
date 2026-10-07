"""
Tests for Topic 8 — Tasks 1–5.
"""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIR),
    )


from task_decomposition import (
    RULES,
    Task,
    build_task_tree,
    check_quality,
    decompose,
    leaves,
)


# ---------------------------------------------------------------------------
# Task 1 — Build the task tree
# ---------------------------------------------------------------------------

def test_task_dataclass_creates_named_task():
    task = Task("launch blog")

    assert task.name == "launch blog"
    assert task.children == []
    assert task.depends_on == []


def test_rule_table_contains_launch_blog():
    assert "launch blog" in RULES


def test_launch_blog_has_two_top_level_tasks():
    tree = build_task_tree(
        "launch blog"
    )

    assert [
        child.name
        for child in tree.children
    ] == [
        "write posts",
        "build site",
    ]


def test_write_posts_contains_three_children():
    tree = build_task_tree(
        "launch blog"
    )

    write_posts = tree.children[0]

    assert [
        child.name
        for child in write_posts.children
    ] == [
        "pick topics",
        "draft",
        "proofread",
    ]


def test_build_site_contains_two_children():
    tree = build_task_tree(
        "launch blog"
    )

    build_site = tree.children[1]

    assert [
        child.name
        for child in build_site.children
    ] == [
        "choose theme",
        "configure hosting",
    ]


def test_tree_has_at_least_three_levels():
    tree = build_task_tree(
        "launch blog"
    )

    assert tree.name == "launch blog"

    assert tree.children

    assert any(
        child.children
        for child in tree.children
    )


def test_dependencies_are_recorded():
    tree = build_task_tree(
        "launch blog"
    )

    write_posts = tree.children[0]

    draft = write_posts.children[1]
    proofread = write_posts.children[2]

    assert draft.depends_on == [
        "pick topics"
    ]

    assert proofread.depends_on == [
        "draft"
    ]


def test_empty_goal_is_rejected():
    try:
        build_task_tree("")
    except ValueError as error:
        assert "must not be empty" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_non_string_goal_is_rejected():
    try:
        build_task_tree(123)
    except TypeError as error:
        assert "must be a string" in str(error)
    else:
        raise AssertionError(
            "Expected TypeError"
        )


# ---------------------------------------------------------------------------
# Task 2 — Recursive decomposition
# ---------------------------------------------------------------------------

def test_decompose_recursively_builds_children():
    tree = decompose(
        "launch blog"
    )

    assert tree.name == "launch blog"

    assert [
        child.name
        for child in tree.children
    ] == [
        "write posts",
        "build site",
    ]

    assert [
        child.name
        for child in tree.children[0].children
    ] == [
        "pick topics",
        "draft",
        "proofread",
    ]


def test_decompose_attaches_sibling_dependencies():
    tree = decompose(
        "launch blog"
    )

    write_posts = tree.children[0]
    build_site = tree.children[1]

    assert write_posts.children[0].depends_on == []

    assert write_posts.children[1].depends_on == [
        "pick topics"
    ]

    assert write_posts.children[2].depends_on == [
        "draft"
    ]

    assert build_site.children[0].depends_on == []

    assert build_site.children[1].depends_on == [
        "choose theme"
    ]


def test_decompose_supports_two_level_goal():
    tree = decompose(
        "write posts"
    )

    assert tree.name == "write posts"

    assert [
        child.name
        for child in tree.children
    ] == [
        "pick topics",
        "draft",
        "proofread",
    ]


def test_decompose_preserves_depth_argument():
    tree = decompose(
        "write posts",
        depth=2,
        max_depth=4,
    )

    assert tree.name == "write posts"

    assert len(tree.children) == 3


def test_decompose_rejects_negative_depth():
    try:
        decompose(
            "launch blog",
            depth=-1,
        )
    except ValueError as error:
        assert "must not be negative" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_decompose_rejects_invalid_max_depth():
    try:
        decompose(
            "launch blog",
            max_depth=0,
        )
    except ValueError as error:
        assert "greater than zero" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


# ---------------------------------------------------------------------------
# Task 3 — Maximum depth
# ---------------------------------------------------------------------------

def test_normal_tree_fits_within_max_depth():
    tree = decompose(
        "launch blog",
        max_depth=2,
    )

    assert tree.name == "launch blog"

    assert [
        child.name
        for child in tree.children
    ] == [
        "write posts",
        "build site",
    ]


def test_depth_limit_raises_recursion_error():
    original_rules = list(
        RULES.get(
            "loop",
            [],
        )
    )

    try:
        RULES["loop"] = [
            (
                "loop",
                [],
            )
        ]

        try:
            decompose(
                "loop",
                max_depth=3,
            )
        except RecursionError as error:
            assert "maximum decomposition depth" in str(
                error
            )
            assert "loop" in str(
                error
            )
        else:
            raise AssertionError(
                "Expected RecursionError"
            )

    finally:
        if original_rules:
            RULES["loop"] = original_rules
        else:
            RULES.pop(
                "loop",
                None,
            )


def test_depth_limit_is_deterministic():
    original_rules = list(
        RULES.get(
            "loop",
            [],
        )
    )

    try:
        RULES["loop"] = [
            (
                "loop",
                [],
            )
        ]

        messages = []

        for _ in range(2):
            try:
                decompose(
                    "loop",
                    max_depth=2,
                )
            except RecursionError as error:
                messages.append(
                    str(error)
                )

        assert len(messages) == 2
        assert messages[0] == messages[1]

    finally:
        if original_rules:
            RULES["loop"] = original_rules
        else:
            RULES.pop(
                "loop",
                None,
            )


# ---------------------------------------------------------------------------
# Task 4 — Flatten to atomic tasks
# ---------------------------------------------------------------------------

def test_leaves_returns_only_atomic_tasks():
    tree = decompose(
        "launch blog"
    )

    result = leaves(tree)

    assert [
        task.name
        for task in result
    ] == [
        "pick topics",
        "draft",
        "proofread",
        "choose theme",
        "configure hosting",
    ]


def test_leaves_returns_exactly_five_tasks():
    tree = decompose(
        "launch blog"
    )

    result = leaves(tree)

    assert len(result) == 5


def test_leaves_excludes_non_atomic_tasks():
    tree = decompose(
        "launch blog"
    )

    names = [
        task.name
        for task in leaves(tree)
    ]

    assert "launch blog" not in names
    assert "write posts" not in names
    assert "build site" not in names


def test_leaf_dependencies_are_preserved():
    tree = decompose(
        "launch blog"
    )

    result = leaves(tree)

    dependencies = {
        task.name: task.depends_on
        for task in result
    }

    assert dependencies == {
        "pick topics": [],
        "draft": ["pick topics"],
        "proofread": ["draft"],
        "choose theme": [],
        "configure hosting": ["choose theme"],
    }


def test_leaves_accepts_single_atomic_task():
    task = Task(
        "write README"
    )

    result = leaves(task)

    assert len(result) == 1
    assert result[0].name == "write README"


def test_leaves_rejects_invalid_input():
    try:
        leaves("launch blog")
    except TypeError as error:
        assert "must be a Task" in str(error)
    else:
        raise AssertionError(
            "Expected TypeError"
        )


# ---------------------------------------------------------------------------
# Task 5 — Task quality
# ---------------------------------------------------------------------------

def test_valid_decomposed_tree_passes_quality_check():
    tree = decompose(
        "launch blog"
    )

    valid, errors = check_quality(
        tree
    )

    assert valid is True
    assert errors == []


def test_quality_check_rejects_empty_task_name():
    task = Task(
        ""
    )

    valid, errors = check_quality(
        task
    )

    assert valid is False
    assert any(
        "must not be empty" in error
        for error in errors
    )


def test_quality_check_rejects_duplicate_sibling_names():
    task = Task(
        "launch blog",
        children=[
            Task("write posts"),
            Task("write posts"),
        ],
    )

    valid, errors = check_quality(
        task
    )

    assert valid is False
    assert any(
        "sibling task names must be unique" in error
        for error in errors
    )


def test_quality_check_rejects_unknown_dependency():
    task = Task(
        "launch blog",
        children=[
            Task(
                "write posts",
                depends_on=["missing task"],
            ),
        ],
    )

    valid, errors = check_quality(
        task
    )

    assert valid is False
    assert any(
        "unknown dependency" in error
        for error in errors
    )


def test_quality_check_rejects_self_dependency():
    task = Task(
        "draft",
        depends_on=["draft"],
    )

    valid, errors = check_quality(
        task
    )

    assert valid is False
    assert any(
        "cannot depend on itself" in error
        for error in errors
    )


def test_quality_check_rejects_non_task_child():
    task = Task(
        "launch blog",
        children=[
            "not a task",
        ],
    )

    valid, errors = check_quality(
        task
    )

    assert valid is False
    assert any(
        "must be a Task" in error
        for error in errors
    )


def test_quality_check_rejects_non_string_dependency():
    task = Task(
        "draft",
        depends_on=[123],
    )

    valid, errors = check_quality(
        task
    )

    assert valid is False
    assert any(
        "dependency names must be strings" in error
        for error in errors
    )