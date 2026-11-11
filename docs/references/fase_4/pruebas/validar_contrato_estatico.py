#!/usr/bin/env python3
"""Inspección estática offline de FASE4. No implica servidor ni DB ejecutados."""
from pathlib import Path
import csv
import sys
import yaml
from jsonschema import Draft202012Validator
P=Path(__file__).resolve().parents[1]
d=yaml.safe_load((P/'contratos'/'API-001.openapi.yaml').read_text(encoding='utf8'))
assert d.get('openapi')=='3.1.1'
all_ops=[]
allowed={'get','post','delete','put','patch'}
for path, methods in d['paths'].items():
 for method, op in methods.items():
  if method not in allowed:continue
  oid=op['operationId']; all_ops.append(oid)
  assert op['responses'], oid
  assert all(str(k) in op['responses'] for k in ['401'] if oid not in ('healthz','login')),f'{oid} missing 401'
  if oid not in ('healthz','login'):
   assert op.get('security')==[{'OpaqueBearer':[]}],f'{oid} bearer missing'
  else:
   assert op.get('security')==[],f'{oid} public auth declaration wrong'
  vars=set(__import__('re').findall(r'\{([^}]+)\}',path))
  pars={v['name'] for v in op.get('parameters',[]) if v['in']=='path' and v['required']}
  assert vars==pars,(oid,vars,pars)
  for status,resp in op['responses'].items():
   assert resp.get('description'),(oid,status)
   if status in ('401','403','404','409','422'):
    c=resp.get('content',{})
    assert c.get('application/problem+json'),(oid,status)
  if op.get('requestBody'):
   assert op['requestBody']['content'].get('application/json'),oid
assert len(all_ops)==35,(len(all_ops),all_ops)
assert len(all_ops)==len(set(all_ops))
assert len(d['paths'])==35
S=d['components']['schemas']
for name,s in S.items():
 Draft202012Validator.check_schema(s)
 if s.get('type')=='object':
  assert s.get('additionalProperties') is False,name
  assert all(key in s['properties'] for key in s.get('required',[])),name

def check_refs(node):
 if isinstance(node,dict):
  if '$ref' in node:
   ref=node['$ref']; assert ref.startswith('#/components/schemas/'),ref
   assert ref.rsplit('/',1)[-1] in S,ref
  for v in node.values():check_refs(v)
 elif isinstance(node,list):
  for v in node:check_refs(v)
check_refs(d)
with (P/'pruebas'/'API-TRZ-AT-001.csv').open(encoding='utf-8-sig',newline='') as f:
 rows=list(csv.DictReader(f))
assert len(rows)==18, len(rows)
assert {r['criterio_aceptacion'] for r in rows}=={f'PROTO-AT-{i:02d}' for i in range(1,19)}
for row in rows:
 for op in row['operationsIds'].split(';'):assert op in all_ops,(row['criterio_aceptacion'],op)
with (P/'contratos'/'API-INVENTARIO-001.csv').open(encoding='utf-8-sig',newline='') as f:
 ops=list(csv.DictReader(f))
assert len(ops)==35
assert {r['operationId'] for r in ops}==set(all_ops)
print(f'OK: openapi={d["openapi"]}, rutas={len(d["paths"])}, operaciones={len(all_ops)}, DTO={len(S)}, AT=18, refs resueltas, protecciones verificadas estáticamente')
print('NO EJECUTADO: FastAPI, PostgreSQL, migraciones, pruebas de seguridad o HTTP.')
