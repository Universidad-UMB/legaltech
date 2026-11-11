#!/usr/bin/env python3
"""Compare method + path + operationId of runtime FastAPI against handoff OpenAPI.
This is a structural check, not a substitute for request/response contract tests.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def expected_routes(source: Path) -> Counter:
    items = []
    path = method = None
    for line in source.read_text(encoding='utf-8').splitlines():
        path_match = re.fullmatch(r'  (/[^:]+):', line)
        if path_match:
            path, method = path_match.group(1), None
            continue
        method_match = re.fullmatch(r'    (get|post|put|patch|delete|options|head):', line)
        if method_match:
            method = method_match.group(1)
            continue
        operation_match = re.fullmatch(r'      operationId: ([\w.-]+)', line)
        if operation_match and path and method:
            items.append((method.upper(), path, operation_match.group(1)))
    return Counter(items)


def runtime_routes(app: object) -> Counter:
    result = app.openapi()
    return Counter((method.upper(), path, config['operationId'])
                   for path, methods in result['paths'].items()
                   for method, config in methods.items()
                   if method.lower() in ('get','post','put','patch','delete','options','head'))


def compare(expected: Counter, actual: Counter) -> tuple[bool,str]:
    if not expected:
        return False, 'No hay operaciones esperadas'
    if expected != actual:
        missing = list((expected - actual).elements())
        extra = list((actual - expected).elements())
        return False, f'OpenAPI divergente: faltan={missing[:8]} sobran={extra[:8]}'
    return True, f'OpenAPI runtime coincide en {sum(expected.values())} operaciones HTTP del incremento'


def expected_until(increment: str, canonical: Counter) -> Counter:
    if increment not in [f'INC-{i:02d}' for i in range(8)]:
        raise ValueError(f'Incremento no reconocido: {increment}')
    mapping = ROOT / 'docs' / 'development' / 'traceability' / 'OPERACIONES-INC-001.csv'
    result = Counter()
    with mapping.open(encoding='utf-8-sig', newline='') as handle:
        for item in csv.DictReader(handle):
            if item['incremento'] <= increment:
                result[(item['method'].upper(), item['path'], item['operation_id'])] += 1
    if not (result - canonical) == Counter():
        raise ValueError('Mapa de operaciones por incremento contradice el contrato canónico')
    if increment == 'INC-07' and result != canonical:
        raise ValueError('El incremento final debe cubrir exactamente las 35 operaciones')
    return result

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument('--through',default='INC-07')
    args=parser.parse_args()
    try:
        from app.main import app
    except Exception as exc:
        print(f'No se pudo importar app.main.app: {exc}')
        return 2
    canonical=expected_routes(ROOT/'contratos'/'API-001.openapi.yaml')
    try:
        desired=expected_until(args.through,canonical)
    except ValueError as exc:
        print(exc); return 3
    ok,message=compare(desired,runtime_routes(app))
    print(message)
    return 0 if ok else 1

if __name__ == '__main__':
    raise SystemExit(main())
