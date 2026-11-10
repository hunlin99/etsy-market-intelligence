# Phase 1 development prototype

Status: **in development**, version `0.1.0-dev`. The local Python prototype runs; the skill has not been loaded and tested in a selected AI host. No Phase 1 release is declared.

## Run locally

Requires Python 3.10+ and the dependency in `requirements.txt`. From the repository root:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m etsy_intelligence validate fixtures/strong-user-bias.json
mkdir -p work
python -m etsy_intelligence evaluate fixtures/strong-user-bias.json --output work/pet-care.json
python -m etsy_intelligence quick-check work/pet-care.json --output work/pet-care.md
python -m etsy_intelligence evaluate fixtures/bounded-proceed.json --output work/pilot.json
python -m etsy_intelligence compare work/pet-care.json work/pilot.json --output work/comparison.md
```

Output paths must be new: the CLI refuses to overwrite existing versions. Use a new filename on each run. Example reports are English; the host assistant can use the manual templates for Traditional Chinese prose.

## Updating with new results

Create a JSON array of evidence items using the schema. Preserve actual provenance, observation dates, and limitations. Do not publish private seller data.

```sh
python -m etsy_intelligence update work/pet-care.json new-evidence.json --as-of 2026-11-11 --output work/pet-care-v2.json
```

The update appends evidence, archives the previous decision with its prior research date, clears the decision, resets gates to unknown, and adds a reassessment requirement. Edit the new version's hypotheses, findings, gates, and assessment after reviewing the results. Then evaluate into another new file. New orders alone must not silently authorize more spending.

## Meaning of validation

Schema/reference checks and deterministic decisions establish structural consistency only. Analysts supply gate judgments, source quality, buyer-signal classifications, counter-cases, and next actions. Human review must verify source truth, claim support, sample representativeness, current policy applicability, and affordable action limits.

Paid validation and economics must support the specific target before Proceed. These conservative rules have not been commercially calibrated. The prototype does not parse raw competitor notes, calculate full unit economics, perform live web research, implement Full Reports, or install itself into an AI host.

## Initial test evidence

See `tests/test-results.md` for local run results and `tests/acceptance-checklist.md` for remaining release gates. The GitHub workflow runs the same automated suite on pushes and pull requests; local success does not establish a remote CI result.
