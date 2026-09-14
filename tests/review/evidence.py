"""Coldline.

===================

File:              tests/review/evidence.py
Component:         Sprint review — Evidence index
Purpose:           Locate each Sprint 2 decision in this repository and derive the settled ones.
Interacts With:    The delivered source tree, the retrieval workflow, and the two config files
Sprint/Task:       Sprint 2 — Project 2 / Task 2.9
Concepts:          Evidence reuse, decisions embodied in code
Tools:             Python 3.12

Supplied and protected. Task 2.9 asks you to defend decisions rather than make
new ones. This module locates the supplied checkpoint and derives its two
configuration facts. Prior student implementations and run results remain in
their original Task pull requests.

Two notes on what "derives" means here.

The Task 2.2 boundary is read from the *composition*, not from a comment: the
workflow exposes both injected halves, so constructing it the way
`api/bootstrap.py` does and asking which half is delegated answers the question
from behavior.

The Task 2.7 decision is read from the two configuration files. A kept
experiment leaves the tuned value live and the two files differing; a reverted
one leaves them identical. That is a fact a `diff` settles.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from api.extensions import wiring
from api.retrieval_workflow import CITATION_LIMIT, RetrievalWorkflow
from tests.benchmark.config import baseline_config, experiment_config
from tests.doubles import StubRetriever

TASK_ROOT = Path(__file__).resolve().parents[2]

RETRIEVAL_ORCHESTRATION = "retrieval_orchestration"
CONTEXT_ASSEMBLY = "context_assembly"
BOUNDARIES = (RETRIEVAL_ORCHESTRATION, CONTEXT_ASSEMBLY)

KEEP = "keep"
REVERT = "revert"
DECISIONS = (KEEP, REVERT)

# Retrieval parameters for the composition probe below. They decide nothing:
# the probe asks which half is delegated, and never runs a query.
PROBE_TOP_K = 3
PROBE_DENSE_WEIGHT = 0.5
PROBE_TOKEN_BUDGET = 320


class EvidenceError(ValueError):
    """Report a decision this repository does not settle unambiguously."""


@dataclass(frozen=True)
class EvidenceItem:
    """One decision, where its evidence lives, and what to show for it."""

    task: str
    decision: str
    paths: tuple[str, ...]
    show: str


# The three defence segments the lesson asks for, and the evidence each rests
# on. Every path is checked to exist, so this index cannot quietly rot as the
# supplied tree changes.
SEGMENTS: dict[str, tuple[EvidenceItem, ...]] = {
    "Part 1 — Service boundary decoupling (about 3 minutes)": (
        EvidenceItem(
            task="2.1",
            decision="Hybrid retrieval baseline, and object custody read through the port",
            paths=(
                "src/adapters/retriever/postgres_hybrid.py",
                "src/adapters/object_store/s3.py",
                "docs/retrieval/pipeline.md",
                "infra/corpus/README.md",
            ),
            show="`poe baseline`: every published query, its outcome, and the chunks returned",
        ),
        EvidenceItem(
            task="2.2",
            decision="One responsibility extracted from the coupled workflow",
            paths=(
                "src/domain/services.py",
                "src/api/retrieval_orchestration.py",
                "src/api/retrieval_workflow.py",
                "src/api/extensions/wiring.py",
            ),
            show=(
                "the workflow's two injectable halves, and which one the composition "
                "delegates; then the dependency direction the authoring check enforces"
            ),
        ),
    ),
    "Part 2 — Persistence, isolation, compatibility, migrations (about 3.5 minutes)": (
        EvidenceItem(
            task="2.3",
            decision="Atomic document and chunk writes behind a repository",
            paths=(
                "src/domain/repositories.py",
                "src/adapters/persistence/document_repository.py",
                "src/api/document_service.py",
            ),
            show=(
                "the supplied transaction implementation here; open your Task 2.3 pull request "
                "for your implementation and recorded failed-write rollback test"
            ),
        ),
        EvidenceItem(
            task="2.4",
            decision="Tenant and classification authorization applied at query time",
            paths=(
                "src/domain/access.py",
                "src/domain/tenant_authorization.py",
                "src/api/access_policy.py",
                "src/api/extensions/wiring.py",
                "tests/contract/test_authorization_checkpoint.py",
                "src/adapters/retriever/postgres_hybrid.py",
                "docs/fidelity/Retriever.md",
            ),
            show=(
                "the constraint clause inside both query arms, and the authorization stage's "
                "readable pool in `poe diagnose` output"
            ),
        ),
        EvidenceItem(
            task="2.5",
            decision="A version 2 write path protected by idempotency",
            paths=(
                "src/api/v2_contracts.py",
                "src/api/idempotency.py",
                "src/domain/idempotency.py",
                "src/adapters/persistence/idempotency.py",
                "src/api/extensions/api_v2.py",
                "infra/postgres/003_idempotency.sql",
            ),
            show="claim before write, complete after success, and the replayed response",
        ),
        EvidenceItem(
            task="2.6",
            decision="One reversible migration, applied on every start",
            paths=(
                "alembic.ini",
                "migrations/env.py",
                "migrations/versions",
                "infra/postgres/004_migration_baseline.sql",
                "src/api/initialize.py",
            ),
            show="`poe migrate-current`, then the migration's own `upgrade` and `downgrade`",
        ),
    ),
    "Part 3 — Empirical optimization and failure attribution (about 3.5 minutes)": (
        EvidenceItem(
            task="2.7",
            decision="One controlled parameter change, kept or reverted on the evidence",
            paths=(
                "config/retrieval-baseline.yaml",
                "config/student/retrieval.yaml",
                "tests/benchmark/metrics.py",
                "tests/benchmark/policy.py",
                "infra/judge/README.md",
            ),
            show="`poe compare`: the two signals, the classification, and the policy verdict",
        ),
        EvidenceItem(
            task="2.8",
            decision="One miss attributed to one stage, with another stage ruled out",
            paths=(
                "infra/corpus/investigation.jsonl",
                "tests/diagnostics/attribution.py",
                "tests/diagnostics/inspect.py",
                "infra/profiles/vector-engines.yaml",
                "infra/profiles/object-store-fidelity.yaml",
            ),
            show="`poe diagnose`: the per-stage lines, and the ordered rule they feed",
        ),
    ),
}


def missing_paths() -> list[str]:
    """Return every path this index names that is not in the repository."""
    return sorted(
        item_path
        for items in SEGMENTS.values()
        for item in items
        for item_path in item.paths
        if not (TASK_ROOT / item_path).exists()
    )


def extracted_boundary() -> str:
    """Return which Task 2.2 responsibility the delivered composition delegates.

    Built the way `api/bootstrap.py` builds it, with a test double in place of
    the retrieval port. No query runs: the question is which half the
    composition hands to a service and which half the workflow still performs
    itself, and the workflow exposes both.
    """
    workflow = RetrievalWorkflow(
        StubRetriever(()),
        top_k=PROBE_TOP_K,
        dense_weight=PROBE_DENSE_WEIGHT,
        token_budget=PROBE_TOKEN_BUDGET,
        retrieval_orchestrator=wiring.build_retrieval_orchestrator(
            StubRetriever(()),
            top_k=PROBE_TOP_K,
            dense_weight=PROBE_DENSE_WEIGHT,
            citation_limit=CITATION_LIMIT,
        ),
    )
    delegated = {
        RETRIEVAL_ORCHESTRATION: workflow.retrieval_orchestrator is not None,
        CONTEXT_ASSEMBLY: workflow.context_assembler is not None,
    }
    extracted = sorted(name for name, injected in delegated.items() if injected)
    if len(extracted) != 1:
        raise EvidenceError(
            "the composition delegates "
            f"{extracted or 'neither responsibility'}, so this repository does not settle one "
            "extracted boundary. Task 2.2 extracts exactly one."
        )
    return extracted[0]


def adopted_decision() -> str:
    """Return whether the Task 2.7 experiment's configuration was kept or reverted.

    A kept experiment leaves its tuned value live, so the adopted configuration
    and the original baseline differ. A reverted one restores the baseline, so
    they are identical.
    """
    return REVERT if experiment_config() == baseline_config() else KEEP


def summary() -> dict[str, str]:
    """Return the two decisions this repository embodies."""
    return {
        "defended_boundary": extracted_boundary(),
        "defended_decision": adopted_decision(),
    }
