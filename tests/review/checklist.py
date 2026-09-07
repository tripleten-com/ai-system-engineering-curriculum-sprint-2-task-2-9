"""Coldline.

===================

File:              tests/review/checklist.py
Component:         Sprint review — Evidence checklist
Purpose:           Print where each Sprint 2 decision's evidence lives in this repository.
Interacts With:    tests/review/evidence.py
Sprint/Task:       Sprint 2 — Project 2 / Task 2.9
Concepts:          Evidence reuse, time-boxed defense
Tools:             Python 3.12

Supplied and protected. `poe review-evidence` prints this. It is a navigation
aid for a ten-minute defense, not a script to read out: what you say about each
piece of evidence is the Task.
"""

from __future__ import annotations

import sys

from tests.review.evidence import SEGMENTS, TASK_ROOT, EvidenceError, missing_paths, summary

TIME_BOX_MINUTES = 10


def main() -> int:
    """Print the evidence index and the two decisions this repository embodies."""
    absent = missing_paths()
    if absent:
        print(
            "This evidence index names paths that are not in the repository, so it is out of "
            f"date rather than usable: {absent}",
            file=sys.stderr,
        )
        return 1

    print(f"Sprint 2 defense evidence — at most {TIME_BOX_MINUTES} minutes, plus questions")
    print("Show running code and verified output. Do not build slides.")
    print()
    for segment, items in SEGMENTS.items():
        print(segment)
        for item in items:
            print(f"  Task {item.task}  {item.decision}")
            print(f"    show:  {item.show}")
            for path in item.paths:
                print(f"    file:  {path}")
        print()

    print("The two answers to record, and how to read each one")
    print("  answers.defended_boundary")
    print("    Which of the workflow's two injectable halves does the composition delegate?")
    print("    src/api/retrieval_workflow.py exposes both; exactly one is injected, and the")
    print("    other stays inline. Read src/api/extensions/wiring.py and src/api/bootstrap.py.")
    print("  answers.defended_decision")
    print("    Is the Task 2.7 experiment's tuned value still live, or was the baseline")
    print("    restored? One command settles it:")
    print("      diff config/retrieval-baseline.yaml config/student/retrieval.yaml")
    print()
    # The derivation is deliberately not printed. Both answers are short reads
    # in the files named above, and handing them over would turn an evidence
    # exercise into a copied line. This does check that the repository settles
    # them unambiguously, because a Task that could not would be broken.
    try:
        summary()
    except EvidenceError as exc:
        print(f"this repository does not settle both decisions: {exc}", file=sys.stderr)
        return 1
    print()
    print("Your own Task 2.2 and Task 2.7 choices stay in those Tasks' pull requests. This")
    print("sheet records what the delivered system does; the oral defense is where you")
    print("explain the choices you made and the trade-offs you accepted.")
    print()
    print(f"Repository under review: {TASK_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
