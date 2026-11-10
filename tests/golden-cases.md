# Golden cases

All fixtures are synthetic. Expected verdicts are maintained independently in `golden-manifest.json`.

| ID | Scenario | Expected behavior |
| --- | --- | --- |
| T01 | No market data | Explore; no fabricated ranking or sales figures. |
| T02 | Review count proxy | Explore; cannot promote reviews to paid or buyer-demand evidence. |
| T03 | Conflicting interviews | Research More; preserve both sources and disclose conflict. |
| T04 | Strong user preference | Test First; changing preference cannot upgrade verdict. |
| T05 | Hypothetical verified prohibition | Reject; missing policy verification invalidates the gate. |
| T06 | Stale fees without web | Research More; disclose unavailable current fees. |
| T07 | Evidence for bounded next pilot | Proceed only for launch_mvp; cannot authorize catalog expansion. |
| T08 | Nonviable economics | Reject the scenario; no finite break-even assertion from more volume. |
| T09 | Failed page fetch | Explore; record source_unavailable without fabricated replacement. |
| T10 | Off-season signal | Monitor with explicit user-initiated revisit trigger. |

Additional tests cover malformed references and dates, policy freshness, stale decisions, history/provenance preservation, report consistency, and output overwrite prevention. Golden decisions are repeated ten times per record.

Full Reports and automated economics are outside this iteration; their specification tests are deferred, not passed. Repeatability tests assess deterministic Python rules, not variability of an AI host.
