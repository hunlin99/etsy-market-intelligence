# Local Phase 1 test results

Run date: 2026-11-10. Skill version: `0.1.0-dev`.
Runner: Python 3.12, jsonschema 4.26.0. No LLM or AI host was used for these tests.

Command: `python -m unittest discover -s tests -v`

Result: **14 test methods passed, 0 failed, 0 skipped**. The golden test method checks all ten manifest scenarios and evaluates each input ten times; expected verdicts matched and repeated decisions were identical for each record.

Verified behaviors include evidence/reference integrity, refusal to treat review proxies as paid demand, visible conflicts, preference-independent verdicts, bounded Proceed, blocked stale policy claims, preserved update history/provenance, consistent Quick Check/comparison decisions, and refusal to overwrite outputs. CLI evaluation and rendering were exercised using temporary files.

Generated demonstrations: `docs/examples/quick-check.md` and `docs/examples/comparison.md`. All observations in those reports are explicitly synthetic.

`git diff --check` passed for the implementation changes.

## Limits

These results verify deterministic local behavior, not LLM repeatability or source truth. No live Etsy claims, commercial predictions, selected-host loading, semantic traceability percentage, or Traditional Chinese host output was validated. A limited empty-input regression checks that known unsupported numerical claims do not appear; this is not a general proof against fabricated claims. See the acceptance checklist for outstanding release gates. Remote CI is separate from this local test record.
