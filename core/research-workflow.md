# Research workflow

Follow INTAKE → PLAN → COLLECT → VALIDATE → ANALYZE → CHALLENGE → DECIDE → REPORT. A quick check gets one bounded collection pass and one counter-case review; standard work needs an explicit research budget.

1. Define hypotheses with claims, supporting and disconfirming references, decision impact, and status.
2. Collect supplied evidence with provenance. Record failed sources in `source_unavailable` without substituting memory as live information.
3. Separate observations from findings and assumptions. Show conflicting sources, methods, and dates explicitly.
4. Complete evidence-backed gates and the analyst assessment. See decision rules for conservative defaults.
5. Validate and evaluate; render views from that evaluated record. The CLI rejects missing or stale decisions.
6. Stop desktop research when a cheap behavioral test has greater value, the budget is exhausted, or missing data cannot reasonably be obtained. Research More must name a bounded question.
7. Append user results to a new version. Preserve prior evidence and decisions; reset gates for reassessment. The CLI refuses to overwrite existing output files.

No state implies a background job. Monitor means a user-initiated future review when a named trigger occurs.
