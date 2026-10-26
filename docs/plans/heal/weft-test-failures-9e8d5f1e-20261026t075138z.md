---
project: weft
slug: heal-weft-test-failures-9e8d5f1e-20261026t075138z
title: Heal test-failures in weft: 1 red test(s) on review/buildability-2026-10-08
heal_signature: 9e8d5f1e8f7953a3
heal_kind: test-failures
seat_pin: quill
merge_target: review/buildability-2026-10-08
abstract: rev heal report test-failures in weft (sig 9e8d5f1e8f7953a3): 1 red test(s) on review/buildability-2026-10-08
tags: heal, test-failures, weft
---

# Plan -- heal test-failures in weft (sig 9e8d5f1e8f7953a3)

Written by `rev heal report` (zero-LLM, self-heal doctrine A6/A9). The defect was recorded as kb:Failure https://loom.ghostsystems.ai/shade_weft/Failure/heal-test-failures-9e8d5f1e; budget $15.00.

## §1 Investigate, root-cause, fix the mechanism on the real artifact, test, commit, prove
<!-- kb:order 1 kb:kind code kb:executor claude kb:model opus kb:touches tests/test_package.py kb:checkKind fable-judgment -->

Reproduce the defect below on the real artifact (not a fixture), find the mechanism that produced it and fix THAT, not the symptom. Add a regression test that fails before the fix and passes after, bump the project version per its rule, commit, push, and prove the fix by re-running the reproduction. Evidence (verbatim):

> python3 -m pytest tests -q -rfE --tb=short -p no:cacheprovider
> ERROR tests/test_package.py -- (no reason line)

- Rule: fix the mechanism on the real artifact; no test is deleted, skipped, xfail'd or loosened to make the defect disappear.
- Rule: provisiond's own files (/var/spool/weaverd-provision*, /etc/provisiond*), installed units + drop-ins under /etc/systemd/system, sudo/sudoers, weaver-server unit files, destructive project ops (drop/deinit/force-reinit, history rewrite), pushes off the forge mesh and billing/subscription surfaces are ASK-FIRST: a worker that reaches one writes a kb:Question naming it and says so in `summary` -- never in blockers[]. Stored data only an operator may drop/move (I-41 strays): tag that Question `heal-operator-disposal` (`rev log question ... --tags heal-operator-disposal --summary '... <iri> <iri>'`) and write each graph IRI in full as `<iri>`, never brace-abbreviated -- the heal sweep stops re-filing only the IRIs it names that way.
- Rule: any further failure seen while working is logged (`rev log failure`) and named in `summary` for the foreground to enqueue -- never "pre-existing, skipped".
