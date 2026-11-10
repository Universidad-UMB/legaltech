import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from orchestration.autopilot import (TICKETS,check_collected_tests,expected_ids,initial_state,make_prompt,read_approval)

class RunnerTests(unittest.TestCase):
    def test_pending_gate_blocks_implementation(self):
        accepted,issues=read_approval()
        self.assertFalse(accepted)
        self.assertTrue(any('DF5-01' in x for x in issues))

    def test_signed_gate_is_recognized(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'gate.json'
            path.write_text(json.dumps({
                'aceptacion_tecnica':'ACEPTAR',
                'decisiones':{f'DF5-{i:02d}':'ACEPTAR' for i in range(1,7)},
                'aprobador_autores':'Autores',
                'fecha_iso':'2026-11-10',
                'evidencia':'acta referenciada'
            }))
            accepted,issues=read_approval(path)
            self.assertTrue(accepted,issues)

    def test_state_has_eight_tickets(self):
        state=initial_state()
        self.assertEqual(list(state['tickets'].keys()),TICKETS)
        self.assertTrue(all(x['status']=='PENDING' for x in state['tickets'].values()))

    def test_tests_manifest_counts(self):
        self.assertEqual({k:len(v) for k,v in expected_ids().items()}, {'AT':18,'API':36,'DATA':39})

    def test_collected_test_validator(self):
        with tempfile.TemporaryDirectory() as temp:
            report=Path(temp)/'collect.log'
            report.write_text('tests/test.py::test_smoke\n')
            ok,msg=check_collected_tests(report)
            self.assertFalse(ok)
            self.assertIn('IDs sin prueba',msg)
            data=expected_ids()
            report.write_text('\n'.join(f'tests/test.py::test_{name}' for ids in data.values() for name in ids))
            ok,msg=check_collected_tests(report)
            self.assertTrue(ok,msg)

    def test_prompt_restricts_scope(self):
        prompt=make_prompt('INC-03',2,'mypy falló')
        self.assertIn('INC-03',prompt)
        self.assertIn('mypy falló',prompt)
        self.assertIn('No edites governance/',prompt)

if __name__ == '__main__': unittest.main()

from orchestration.check_runtime_openapi import expected_routes, compare

class OpenApiGateTests(unittest.TestCase):
    def test_canonical_openapi_is_35_operations(self):
        source=Path(__file__).resolve().parents[2]/'contratos'/'API-001.openapi.yaml'
        observed=expected_routes(source)
        self.assertEqual(sum(observed.values()),35)
        ok,msg=compare(observed,observed.copy())
        self.assertTrue(ok,msg)

    def test_missing_operation_is_rejected(self):
        source=Path(__file__).resolve().parents[2]/'contratos'/'API-001.openapi.yaml'
        expected=expected_routes(source)
        fewer=expected.copy()
        fewer.pop(next(iter(fewer)))
        self.assertFalse(compare(expected,fewer)[0])

from orchestration.check_runtime_openapi import expected_until
class ProgressiveApiTests(unittest.TestCase):
    def test_inc00_has_four_operations(self):
        source=Path(__file__).resolve().parents[2]/'contratos'/'API-001.openapi.yaml'
        canonical=expected_routes(source)
        expected=expected_until('INC-00',canonical)
        self.assertEqual(sum(expected.values()),4)

    def test_inc07_has_all_operations(self):
        source=Path(__file__).resolve().parents[2]/'contratos'/'API-001.openapi.yaml'
        canonical=expected_routes(source)
        expected=expected_until('INC-07',canonical)
        self.assertEqual(sum(expected.values()),35)
        self.assertTrue(compare(expected,canonical)[0])
