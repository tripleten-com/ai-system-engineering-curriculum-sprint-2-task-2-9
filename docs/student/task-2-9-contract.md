# Task 2.9 — Instructor presentation and review contract

Assemble the pull request record you built across Sprint 2, record two reused decision
selections, and deliver a technical defense of at most 10 minutes. You write no new application
code and no essay.

## What is assessed, and by whom

| Assessed | By |
|---|---|
| The pull request changes only `submission.yaml` and passes CI | Automated, in this repository |
| The two recorded decisions match the delivered system | Automated, in this repository |
| Your defense of the boundary, the data layer, and the experiments | Your instructor, live |
| All nine Sprint 2 pull requests are CI-green | Your instructor, before sign-off |

Administrative completion is the instructor's record. There is no self-approval field, no pass
boolean, and no recording URL in `submission.yaml` — an answer sheet that could carry those would
be inviting you to grade yourself.

## The two answers, and where they come from

Run this first:

```shell
poe review-evidence
```

It prints, for each of Tasks 2.1 to 2.8, which files in *this* repository hold that Task's
evidence and what to show for it, then the two questions your answers settle and the exact reads
that answer them. It deliberately does not print the answers: both are short reads in the files it
names, and handing them over would turn an evidence exercise into a copied line.

| Field | Read it from |
|---|---|
| `defended_boundary` | The composition. `src/api/retrieval_workflow.py` exposes two injectable halves; exactly one is delegated to a service and the other stays inline. Which one is delegated is the answer. |
| `defended_decision` | The two configuration files. If `config/student/retrieval.yaml` still matches `config/retrieval-baseline.yaml`, the Task 2.7 experiment was reverted; if it differs, the tuned value is live and it was kept. |

### Why these are facts about *this* repository

Student source code does not transfer between Task repositories, and this repository cannot read
another one. So the checkable fact here is what the delivered system does, and that is what the
checks compare your answers against.

Your own Task 2.2 and Task 2.7 choices stay in those Tasks' pull requests, where they were
verified. The oral defense is where you explain the choices *you* made, why, and what you traded
away — and that is the part a check cannot do.

> This is a deviation from the answer specification in the Task 2.9 lesson, which names the
> Task 2.2 and Task 2.7 pull request records as the evidence source. Those records are not
> reachable from this repository, so the automated check would have nothing to compare against.
> The deviation is recorded as a proposed lesson correction.

## The 10-minute structure

Three segments. `poe review-evidence` prints the file list for each.

| Segment | Tasks | About |
|---|---:|---|
| Part 1 (~3 min) | 2.1, 2.2 | Why the baseline workflow was coupled, which responsibility you extracted, how you proved the dependency direction and substitutability without changing the caller |
| Part 2 (~3.5 min) | 2.3, 2.4, 2.5, 2.6 | Atomic document and chunk writes and the aborted-write test; query-time authorization and why it is not a post-filter; the versioned write path and the replay guarantee; the reversible migration and its rollback |
| Part 3 (~3.5 min) | 2.7, 2.8 | The controlled experiment's quality and latency deltas, why the deterministic metric and the cached judge diverged, and the intermediate telemetry that attributed one miss to one stage while ruling another out |

Show running code and verified output. Do not build slides, and do not walk the code line by line:
say why the decision was made and point at the assertion that proves it holds.

Two commands are kept here specifically as live evidence:

```shell
poe compare     # Part 3: the two evaluation signals, the classification, the policy verdict
poe diagnose    # Part 3: the per-stage evidence behind the miss attribution
```

Both need the stack running (`poe start`, then `poe ingest`).

## What the checks verify

| Check | What it looks at |
|---|---|
| `test_recorded_boundary_matches_the_extracted_service` | Constructs the workflow the way the composition root does, and asks which half is delegated |
| `test_recorded_decision_matches_the_adopted_configuration` | Whether the two configuration files still match |
| `test_the_evidence_index_names_paths_that_exist` | The supplied checklist, so it cannot name a file that has moved |

```shell
poe review-checks   # these three, without the stack
poe verify          # the full public path
```

## Student-editable paths

- `submission.yaml`

That is the whole list. There is no code to write in this Task, and the defense is delivered live
rather than committed.
