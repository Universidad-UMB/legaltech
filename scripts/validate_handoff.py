#!/usr/bin/env python3
"""Validación documental y de fixtures Fase 5; NO prueba backend ni PostgreSQL."""
import csv, json, re, sys
from pathlib import Path
from collections import Counter

root = Path(__file__).resolve().parent.parent
problems=[]
def check(condition, message):
    if not condition: problems.append(message)
def readjson(p): return json.loads((root/p).read_text(encoding='utf-8'))
def rows(p):
    with (root/p).open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))

fx=readjson('fixtures/PROTO-DAT-001.json')
expected=readjson('fixtures/PROTO-EXPECTED-001.json')
at=readjson('pruebas/PROTO-AT-001.json')
neg=rows('pruebas/API-NEG-001.csv'); db=rows('pruebas/DATA-TEST-001.csv')
ops=rows('trazabilidad/OPERACIONES-INC-001.csv')
tr=rows('trazabilidad/AT-RF-TEST-001.csv')
rnf=rows('trazabilidad/RNF-TEST-001.csv')
check(len(at)==18 and {r['id'] for r in at}=={f'PROTO-AT-{i:02}' for i in range(1,19)},'AT 18 IDs no coinciden')
check(len(neg)==36 and {r['id'] for r in neg}=={f'API-N{i:02}' for i in range(1,37)},'36 API-N no coinciden')
check(len(db)==39 and {r['id'] for r in db}=={f'DT-{i:02}' for i in range(1,40)},'39 DT no coinciden')
check(len(rnf)==14 and {r['rnf_id'] for r in rnf}=={f'RNF-{i:02}' for i in range(1,15)},'14 RNF no coinciden')
check(len(ops)==35 and len(set(r['operation_id'] for r in ops))==35,'35 operaciones por incremento no coinciden')
check(len(tr)==18 and {r['at_id'] for r in tr}=={r['id'] for r in at},'18 relaciones AT-RF no coinciden')
check(all(r['status']=='NOT_EXECUTED' for r in at) and all(r['status']=='NOT_EXECUTED' for r in neg+db+rnf),'Nunca registrar pruebas como ejecutadas en F5')
check(fx['synthetic_only'] is True,'Fixture no identificado como sintético')
check(all(re.fullmatch(r'[0-9]{23}',p['radicado']) for p in fx['processes']),'Radicados inválidos')
check(len(set(p['radicado'] for p in fx['processes']))==2,'Radicados duplicados')
track={t['alias']:t for t in fx['trackings']}
check(track['SEG-A-002']['process']=='PROC-002' and track['SEG-A-002']['client']=='alfa','A2 debe pertenecer a PROC-002 y Alfa')
check(track['SEG-A-001']['process']==track['SEG-B-001']['process']=='PROC-001','A/B deben compartir PROC-001')
check('SEG-A-002' not in next(s['trackings'] for s in fx['external_tracking_scopes'] if s['username']=='reader.alfa.demo'),'Alfa no debe tener scope A2')
for user in fx['accounts']:
    check(not any(k in user for k in ['password','password_hash','token','secret']),'Cuenta fixture contiene secreto')
    if user['kind']=='EXTERNAL':
        for s in fx['external_tracking_scopes']:
            if s['username']==user['username']:
                check(all(track[t]['client']==user['client_ref'] for t in s['trackings']),'Ámbito externo a otro cliente')
p1=readjson('fixtures/adquisiciones/OBS_001.json');p2=readjson('fixtures/adquisiciones/OBS_002.json')
a1={a['action_key'] for a in p1['actions']};a2={a['action_key'] for a in p2['actions']}
check(len(a1)==5 and len(a2)==6 and a2-a1=={'ACT-06'} and a1-a2==set(),'Diferencias ACT inválidas')
check(expected['acceptance_expectations']['comparison']==['ACT-06'],'Oráculo de comparación erróneo')
check(readjson('fixtures/adquisiciones/FAILED.json')['observation'] is None,'Fallido no debe crear snapshot válido')

try:
    import yaml
except ImportError:
    problems.append('Requiere PyYAML para validar contrato OpenAPI; instalar en entorno de revisión')
else:
    y=yaml.safe_load((root/'contratos/API-001.openapi.yaml').read_text())
    names=[]
    for p,items in y['paths'].items():
        for verb,detail in items.items():
            if verb in ('get','post','delete','patch','put'):
                names.append(detail['operationId'])
                check({'GET':'get','POST':'post','DELETE':'delete','PUT':'put','PATCH':'patch'}[next(r['method'] for r in ops if r['operation_id']==detail['operationId'])]==verb,'Método no coincide')
    check(y.get('openapi')=='3.1.1','Versión OpenAPI distinta de 3.1.1')
    check(len(names)==35 and set(names)=={r['operation_id'] for r in ops},'Operaciones YAML no coinciden con trazabilidad')
    check(all(set(row['operation_ids']).issubset(set(names)) for row in at),'AT usa operación inexistente')  # operation_ids es lista

check(all((root/'tickets'/f'INC-{i:02}.md').exists() for i in range(8)),'Tickets incompletos')
check((root/'AGENT.md').exists() and (root/'docs/DEC-F5-001_v0.1.md').exists(),'AGENT/decisiones ausentes')
if problems:
    print('FALLA:')
    for msg in problems: print(' -',msg)
    sys.exit(1)
print('OK — validación documental Fase 5: 35 operationIds, 18 AT, 36 negativos API, 39 DB, 14 RNF, 8 tickets, 5/6 ACT y fixtures consistentes.')
print('Advertencia: no se ejecutaron backend, migraciones, pruebas Pytest ni PostgreSQL.')
