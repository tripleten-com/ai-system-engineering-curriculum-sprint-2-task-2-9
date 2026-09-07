"""Coldline.

===================

File:              tests/contract/test_sprint_review.py
Component:         Contract tests — Sprint review
Purpose:           Verify the recorded decisions against the ones this repository embodies.
Interacts With:    tests/review/evidence.py, the composition, and the two configuration files
Sprint/Task:       Sprint 2 — Project 2 / Task 2.9
Concepts:          Evidence reuse, decisions embodied in code
Tools:             Python 3.12, pytest
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.review.evidence import (
    BOUNDARIES,
    DECISIONS,
    SEGMENTS,
    adopted_decision,
    extracted_boundary,
    missing_paths,
)

TASK_ROOT = Path(__file__).resolve().parents[2]
# `assessed`: a fresh starter records nothing, so both answer checks fail.
# No container is needed: every fact these checks read is in the source tree.
pytestmark = pytest.mark.assessed


def answers() -> dict[str, Any]:
    """Return the recorded answer mapping, or fail with what is missing."""
    document = yaml.safe_load((TASK_ROOT / "submission.yaml").read_text(encoding="utf-8"))
    mapping = document.get("answers") if isinstance(document, dict) else None
    if not isinstance(mapping, dict):
        pytest.fail("submission.yaml must define an answers mapping")
    return mapping


def recorded(field: str, permitted: tuple[str, ...]) -> str:
    """Return one recorded enumerated answer."""
    value = answers().get(field)
    if not isinstance(value, str) or value not in permitted:
        pytest.fail(f"answers.{field} must be one of {list(permitted)}; found {value!r}")
    return value


def test_recorded_boundary_matches_the_extracted_service() -> None:
    """The recorded boundary must be the one the delivered composition delegates.

    This repository carries the settled Sprint 2 system, not a student's own
    Task 2.2 branch, so the checkable fact is which responsibility *this*
    composition hands to a service. A student's own Task 2.2 choice stays in
    that Task's pull request, and the oral defense is where it is explained.
    """
    answer = recorded("defended_boundary", BOUNDARIES)
    extracted = extracted_boundary()
    assert answer == extracted, (
        f"answers.defended_boundary records {answer!r}, and this repository delegates "
        f"{extracted!r}: the workflow in src/api/retrieval_workflow.py exposes both halves, "
        "and the composition injects exactly one. Run `poe review-evidence`."
    )


def test_recorded_decision_matches_the_adopted_configuration() -> None:
    """The recorded decision must be the one the two configuration files show."""
    answer = recorded("defended_decision", DECISIONS)
    adopted = adopted_decision()
    assert answer == adopted, (
        f"answers.defended_decision records {answer!r}, and this repository shows "
        f"{adopted!r}: config/student/retrieval.yaml "
        + (
            "still matches config/retrieval-baseline.yaml, which is what reverting leaves behind."
            if adopted == "revert"
            else "differs from config/retrieval-baseline.yaml, so the tuned value is live."
        )
    )


def test_the_evidence_index_names_paths_that_exist() -> None:
    """Every predecessor decision must be traceable in this repository.

    The checklist is the Task's navigation aid, so a path it names that no
    longer exists is a defect in the Task rather than in a submission. This
    check is about the supplied tree and does not read the answer sheet.
    """
    assert missing_paths() == [], (
        "the evidence index in tests/review/evidence.py names paths that are not in this "
        f"repository: {missing_paths()}"
    )

    covered = {item.task for items in SEGMENTS.values() for item in items}
    assert covered == {"2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8"}, (
        f"the evidence index covers {sorted(covered)}; the defense spans Tasks 2.1 to 2.8"
    )
    for items in SEGMENTS.values():
        for item in items:
            assert item.paths, f"Task {item.task} has no evidence path"
            assert item.show, f"Task {item.task} says nothing to show"
