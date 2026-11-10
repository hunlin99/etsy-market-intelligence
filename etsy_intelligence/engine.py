"""Validate analyst-supplied judgments and apply conservative, provisional gates.

This module does not infer evidence quality or factual truth from source text.
"""
from copy import deepcopy
from datetime import date
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA = json.loads((Path(__file__).resolve().parents[1] / 'schemas/research-record.schema.json').read_text())
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def validate(record):
    errors = sorted(VALIDATOR.iter_errors(record), key=lambda e: str(list(e.path)))
    if errors:
        raise ValueError('; '.join(f'{list(e.path)}: {e.message}' for e in errors))
    evidence = record['evidence']
    ids = [e['id'] for e in evidence]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate evidence IDs')
    by_id = {e['id']: e for e in evidence}
    for key in ('hypotheses', 'findings'):
        values = [item['id'] for item in record[key]]
        if len(values) != len(set(values)):
            raise ValueError(f'Duplicate {key} IDs')

    def check_refs(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key.endswith('_ids') and isinstance(child, list):
                    missing = set(child) - set(ids)
                    if missing:
                        raise ValueError(f'Dangling evidence references: {sorted(missing)}')
                check_refs(child)
        elif isinstance(value, list):
            for child in value:
                check_refs(child)
    check_refs(record)
    for e in evidence:
        if e['collected_at'] > record['as_of'] or (e['verified_at'] and e['verified_at'] > record['as_of']):
            raise ValueError('Evidence dates cannot be after research as_of')
        if e['evidence_type'] == 'derived' and (not e['input_evidence_ids'] or not e['derivation']):
            raise ValueError('Derived evidence needs inputs and a derivation')
        if e['id'] in e['input_evidence_ids']:
            raise ValueError('Evidence cannot derive from itself')
    def visit(eid, ancestors):
        if eid in ancestors:
            raise ValueError('Cyclic evidence derivation')
        for source in by_id[eid]['input_evidence_ids']:
            visit(source, ancestors | {eid})
    for eid in ids:
        visit(eid, set())
    for f in record['findings']:
        if f['claim_type'] in ('observation', 'interpretation') and not f['evidence_ids']:
            raise ValueError('Factual/interpretive findings need evidence references')
    for name, gate in record['gates'].items():
        if gate['status'] not in ('unknown', 'not_applicable') and not gate['evidence_ids']:
            raise ValueError(f'Gate {name} requires evidence')
        if gate['status'] not in ('unknown', 'not_applicable'):
            if any(by_id[i]['evidence_type'] in ('hypothesis', 'unavailable') for i in gate['evidence_ids']):
                raise ValueError('A gate cannot be established by hypothetical/unavailable evidence')
        if name == 'platform_compliance' and gate['status'] in ('pass', 'fail'):
            if not any(by_id[i]['signal'] == 'policy' and by_id[i]['verified_at'] == record['as_of']
                       and by_id[i]['quality']['reliability'] == 'high' for i in gate['evidence_ids']):
                raise ValueError('Compliance pass/fail requires a policy source verified as_of with high reliability')
    a = record['assessment']
    for key, signals in [('demand_signal_ids', ('buyer_problem', 'paid_test')),
                         ('paid_validation_ids', ('paid_test',)),
                         ('economics_evidence_ids', ('economics',))]:
        for eid in a[key]:
            e = by_id[eid]
            if e['signal'] not in signals or e['evidence_type'] not in ('observation', 'derived'):
                raise ValueError(f'{key} cannot use proxy, hypothetical, or unavailable evidence')
    if record['decision'] and record['decision']['target'] != record['brief']['decision_target']:
        raise ValueError('Decision target must match brief')
    for h in record['decision_history']:
        date.fromisoformat(h['as_of'])
        if h['as_of'] > record['as_of']:
            raise ValueError('History cannot be dated after research')
    return record


def _decision(record):
    a, gates = record['assessment'], record['gates']
    target = record['brief']['decision_target']
    unknowns = list(a['critical_unknowns'])
    unknowns += [f'{k}: unknown' for k, g in gates.items() if g['status'] == 'unknown']
    unknowns += [f"source_unavailable: {s['source_locator']} ({s['reason']})" for s in record['source_unavailable']]
    unknowns += [f"Conflicting evidence: {c['description']}" for c in a['conflicts']]
    all_refs = set(a['demand_signal_ids'] + a['paid_validation_ids'] + a['economics_evidence_ids'])
    counter_refs = set()
    for g in gates.values():
        all_refs.update(g['evidence_ids'])
    for f in record['findings']:
        all_refs.update(f['evidence_ids'])
        counter_refs.update(f['counter_evidence_ids'])
    for conflict in a['conflicts']:
        counter_refs.update(conflict['evidence_ids'])
    hard_failure = any(g['status'] in ('fail', 'unacceptable', 'nonviable') for g in gates.values())
    complete = all(g['status'] in ('pass', 'not_applicable', 'supported', 'acceptable', 'viable_in_scenario')
                   for g in gates.values())
    by_id = {e['id']: e for e in record['evidence']}
    decisive = set(a['paid_validation_ids'] + a['economics_evidence_ids'])
    for g in gates.values():
        decisive.update(g['evidence_ids'])
    adequate = bool(decisive) and all(
        by_id[eid]['quality'][dimension] in ('medium', 'high')
        for eid in decisive for dimension in ('directness', 'reliability', 'freshness'))
    if hard_failure:
        status, reason = 'reject', 'A documented prerequisite fails; redesign or stop this proposal.'
    elif (complete and not unknowns and a['paid_validation_ids'] and a['economics_evidence_ids']
          and a['validated_target'] == target and adequate):
        status, reason = 'proceed', 'Paid-test and economics evidence supports only the specified next investment.'
    elif a['targeted_research']:
        status, reason = 'research_more', 'Resolve the bounded research question: ' + a['targeted_research']
    elif a['monitor_trigger']:
        status, reason = 'monitor', 'Revisit only when this trigger occurs: ' + a['monitor_trigger']
    elif a['demand_signal_ids']:
        status, reason = 'test_first', 'There is a buyer signal, but evidence is insufficient to approve the requested investment.'
    else:
        status, reason = 'explore', 'No qualifying buyer signal supports an investment decision yet.'
    # No automatic high confidence: the engine cannot judge source truth or representativeness.
    conf = 'medium' if status == 'proceed' else 'low' if all_refs else 'unknown'
    return {'target': target, 'status': status, 'confidence': conf, 'rationale': reason,
            'evidence_ids': sorted(all_refs), 'counter_evidence_ids': sorted(counter_refs),
            'counterarguments': [a['counter_case']], 'unknowns': unknowns,
            'what_would_change_it': a['what_would_change_it'], 'next_action': deepcopy(a['next_action'])}


def evaluate(record):
    validate(record)
    result = deepcopy(record)
    decision = _decision(result)
    if result['decision'] and result['decision'] != decision:
        result['decision_history'].append({'as_of': result['as_of'], 'decision': result['decision']})
    result['decision'] = decision
    validate(result)
    return result


def update_record(record, additions, as_of):
    """Append evidence and archive the previous decision; judgments must be reassessed."""
    validate(record)
    date.fromisoformat(as_of)
    if as_of < record['as_of']:
        raise ValueError('Updates cannot move research backwards in time')
    result = deepcopy(record)
    if result['decision']:
        result['decision_history'].append({'as_of': record['as_of'], 'decision': result['decision']})
    result['decision'] = None
    result['as_of'] = as_of
    result['evidence'].extend(deepcopy(additions))
    # Old paid/economics judgments must not silently authorize a new decision.
    result['assessment']['validated_target'] = None
    result['assessment']['critical_unknowns'].append('New evidence requires analyst reassessment')
    for g in result['gates'].values():
        g.update(status='unknown', evidence_ids=[], reason='Reassess after new evidence')
    validate(result)
    return result


def _safe(value):
    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '\\|').replace('\n', ' ')


def quick_check(record):
    validate(record)
    d = record['decision']
    if d is None or d != _decision(record):
        raise ValueError('Evaluate the current record before rendering; decision is missing or stale')
    lines = [f"# Quick Check: {_safe(record['brief']['product'])}",
             f"Research as of: {record['as_of']} · Scope: {_safe(record['brief']['scope'])} · Geography: {_safe(record['brief']['geography'])}",
             f"Decision target: {d['target']} · Verdict: {d['status']} · Confidence: {d['confidence']}",
             '\n## Evidence access',
             ', '.join(k for k, v in record['capabilities'].items() if v) or 'No tools available',
             '\n## Why', _safe(d['rationale']), '\n## Evidence log']
    for e in record['evidence']:
        lines.append(f"- [{e['id']}] ({e['evidence_type']}; {e['source_type']}) {_safe(e['original_observation'])} — {_safe(e['source_locator'])}; collected {e['collected_at']}. Limitations: {_safe('; '.join(e['limitations']))}")
        lines.append(f"  Method: {_safe(e['method'])}. Quality (analyst-assessed): {_safe(', '.join(k + '=' + v for k, v in e['quality'].items()))}.")
    if not record['evidence']:
        lines.append('Unknown — no evidence supplied.')
    lines.append('\n## Findings')
    for f in record['findings']:
        lines.append(f"- [{f['claim_type']}; {f['confidence']}] {_safe(f['claim'])} ({', '.join(f['evidence_ids']) or 'No supporting evidence'}). Counter-evidence: {', '.join(f['counter_evidence_ids']) or 'None supplied'}. Alternatives: {_safe('; '.join(f['alternative_explanations'])) or 'Not assessed'}. Limitations: {_safe('; '.join(f['limitations']))}")
    if not record['findings']:
        lines.append('Not assessed (reason: no findings supplied).')
    for title, values in [('Counter-case', d['counterarguments']), ('Unknowns and conflicts', d['unknowns']),
                          ('Assumptions', record['brief']['assumptions']), ('What would change it', d['what_would_change_it'])]:
        lines.append('\n## ' + title)
        lines.extend('- ' + _safe(v) for v in values)
        if not values:
            lines.append('None recorded; this does not establish completeness.')
    action = d['next_action']
    lines += ['\n## Next best action', _safe(action['action']),
              'Observable criterion: ' + _safe(action['success_criterion']),
              'Effort/cost bound: ' + _safe(action['effort_limit']),
              '\nPrototype limitation: analyst judgments and source truth require human review. No live Etsy research was performed.']
    return '\n'.join(lines).rstrip() + '\n'


def compare(records):
    if len(records) < 2:
        raise ValueError('Comparison needs at least two records')
    for record in records:
        quick_check(record)  # Validate stored decision and traceability.
    keys = [(r['brief']['scope'], r['brief']['geography'], r['brief']['decision_target'], r['depth'], r['as_of']) for r in records]
    if len(set(keys)) != 1:
        raise ValueError('Comparison requires matching scope, geography, target, depth, and as_of')
    if len({r['record_id'] for r in records}) != len(records):
        raise ValueError('Comparison requires distinct record IDs')
    lines = ['# Opportunity Comparison', 'No numerical ranking; compare evidence and tradeoffs for the same decision.',
             '| Candidate | Verdict | Confidence | Evidence | Unknowns | Next action |',
             '| --- | --- | --- | --- | --- | --- |']
    for r in records:
        d = r['decision']
        vals = [r['brief']['product'], d['status'], d['confidence'], ', '.join(d['evidence_ids']) or 'None',
                '; '.join(d['unknowns']) or 'None recorded', d['next_action']['action']]
        lines.append('| ' + ' | '.join(_safe(v) for v in vals) + ' |')
    lines += ['\nEvidence IDs are local to each candidate record. Detailed evidence and counter-cases follow.']
    lines.extend('\n' + quick_check(r) for r in records)
    return '\n'.join(lines).rstrip() + '\n'
