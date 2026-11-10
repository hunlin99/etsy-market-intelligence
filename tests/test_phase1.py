from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from etsy_intelligence.engine import validate, evaluate, quick_check, compare, update_record

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / 'tests/golden-manifest.json').read_text())

def fixture(name):
    return json.loads((ROOT / 'fixtures' / (name + '.json')).read_text())


class Phase1Tests(unittest.TestCase):
    def test_golden_scenarios_and_repeatability(self):
        for case in MANIFEST:
            with self.subTest(case=case['id']):
                r = json.loads((ROOT / 'fixtures' / case['fixture']).read_text())
                before = deepcopy(r)
                decisions = [evaluate(r)['decision'] for _ in range(10)]
                self.assertTrue(all(d == decisions[0] for d in decisions))
                self.assertEqual(decisions[0]['status'], case['expected_status'])
                self.assertEqual(r, before)
                report = quick_check(evaluate(r))
                for field in ('Counter-case', 'Unknowns', 'What would change it', 'Next best action', 'Effort/cost bound'):
                    self.assertIn(field, report)
                for e in r['evidence']:
                    self.assertIn(e['id'], report)
                    self.assertIn(e['original_observation'], report)

    def test_user_preference_cannot_upgrade_decision(self):
        r = fixture('strong-user-bias')
        baseline = evaluate(r)['decision']
        r['brief']['user_preference'] = 'I hate this product.'
        self.assertEqual(evaluate(r)['decision'], baseline)

    def test_review_proxy_cannot_be_paid_or_demand_evidence(self):
        for key in ('paid_validation_ids', 'demand_signal_ids'):
            r = fixture('review-proxy')
            r['assessment'][key] = ['E001']
            with self.assertRaisesRegex(ValueError, 'proxy'):
                evaluate(r)

    def test_reference_and_identity_integrity(self):
        for mutation in ('duplicate', 'dangling', 'cycle', 'missing_source', 'invalid_date'):
            r = fixture('review-proxy')
            if mutation == 'duplicate': r['evidence'].append(deepcopy(r['evidence'][0]))
            if mutation == 'dangling': r['findings'][0]['evidence_ids'] = ['E999']
            if mutation == 'cycle': r['evidence'][0]['input_evidence_ids'] = ['E001']
            if mutation == 'missing_source': del r['evidence'][0]['source_locator']
            if mutation == 'invalid_date': r['as_of'] = '2026-99-99'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): validate(r)

    def test_unknown_never_automatically_rejects(self):
        self.assertEqual(evaluate(fixture('insufficient-data'))['decision']['status'], 'explore')

    def test_proceed_cannot_authorize_a_larger_target(self):
        r = fixture('bounded-proceed')
        r['brief']['decision_target'] = 'expand_catalog'
        self.assertEqual(evaluate(r)['decision']['status'], 'test_first')

    def test_proceed_blocked_by_conflicts_unknowns_or_stale_economics(self):
        for mutation in ('conflict', 'unknown', 'stale', 'unavailable'):
            r = fixture('bounded-proceed')
            if mutation == 'conflict': r['assessment']['conflicts'] = [{'description':'Contradictory pilot interpretations','evidence_ids':['E001','E002']}]
            if mutation == 'unknown': r['gates']['economics']['status'] = 'unknown'
            if mutation == 'stale': r['evidence'][1]['quality']['freshness'] = 'low'
            if mutation == 'unavailable': r['source_unavailable'] = [{'source_locator':'fixture://missing','reason':'unreachable','alternative':'Ask owner'}]
            with self.subTest(mutation=mutation): self.assertNotEqual(evaluate(r)['decision']['status'], 'proceed')

    def test_unverified_policy_cannot_fail_gate(self):
        r = fixture('verified-hard-failure')
        r['evidence'][0]['verified_at'] = None
        with self.assertRaisesRegex(ValueError, 'policy source'): evaluate(r)

    def test_conflict_visible_in_report(self):
        report = quick_check(evaluate(fixture('conflicting-evidence')))
        self.assertIn('Conflicting evidence:', report)
        self.assertIn('E001', report)
        self.assertIn('E002', report)

    def test_same_record_comparison_and_quick_check_agree(self):
        a = evaluate(fixture('strong-user-bias'))
        b = evaluate(fixture('bounded-proceed'))
        output = compare([a, b])
        self.assertIn(quick_check(a), output)
        self.assertIn(quick_check(b), output)
        b['brief']['scope'] = 'Different marketplace'
        with self.assertRaisesRegex(ValueError, 'matching scope'): compare([a, b])

    def test_reject_stale_or_missing_decision_when_rendering(self):
        r = fixture('strong-user-bias')
        with self.assertRaises(ValueError): quick_check(r)
        r = evaluate(r)
        r['assessment']['targeted_research'] = 'Resolve new buyer uncertainty'
        with self.assertRaisesRegex(ValueError, 'stale'): quick_check(r)

    def test_update_preserves_provenance_history_and_input(self):
        r = evaluate(fixture('strong-user-bias'))
        previous = deepcopy(r)
        e = deepcopy(fixture('bounded-proceed')['evidence'][0])
        e.update(id='E002', source_type='user_reported', source_locator='user-supplied pilot results')
        updated = update_record(r, [e], '2026-11-11')
        self.assertEqual(r, previous)
        self.assertEqual(updated['decision_history'][0]['decision'], r['decision'])
        self.assertEqual(updated['evidence'][0], r['evidence'][0])
        self.assertEqual(updated['evidence'][1]['source_type'], 'user_reported')
        self.assertIsNone(updated['decision'])
        self.assertNotEqual(evaluate(updated)['decision']['status'], 'proceed')
        with self.assertRaises(ValueError): update_record(r, [r['evidence'][0]], '2026-11-11')

    def test_reports_do_not_invent_numbers_on_empty_input(self):
        report = quick_check(evaluate(fixture('insufficient-data')))
        for forbidden in ('monthly sales: 100', 'revenue: $', 'conversion: 5%'):
            self.assertNotIn(forbidden, report)
        self.assertIn('no evidence supplied', report)

    def test_cli_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = str(Path(tmp) / 'evaluated.json')
            command = [sys.executable, '-m', 'etsy_intelligence', 'evaluate', str(ROOT / 'fixtures/strong-user-bias.json'), '--output', out]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            before = Path(out).read_bytes()
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(Path(out).read_bytes(), before)
            report = str(Path(tmp) / 'quick.md')
            self.assertEqual(subprocess.run([sys.executable, '-m', 'etsy_intelligence', 'quick-check', out, '--output', report], capture_output=True).returncode, 0)
            self.assertIn('test_first', Path(report).read_text())


if __name__ == '__main__':
    unittest.main()
