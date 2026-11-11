"""Comprobaciones ESTATICAS, sin conexión PostgreSQL; no prueban sintaxis/semántica SQL."""
from pathlib import Path
import re
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sql = (ROOT/'ddl/DATA-DDL-001_CANDIDATO.sql').read_text()
# Recorta cada definición de tabla sin intentar interpretar el parser SQL.
starts = list(re.finditer(r'^CREATE TABLE\s+(\w+)\s*\(', sql, flags=re.M))
tables = {}
for i, match in enumerate(starts):
    end = starts[i + 1].start() if i + 1 < len(starts) else len(sql)
    body = sql[match.end():end]
    body = body[:body.find('\n);')]
    cols = set(re.findall(r'^\s{4}(\w+)\s+(?:uuid|varchar|text|bytea|timestamp|timestamptz|integer|date)\b', body, flags=re.M))
    candidate_keys=set()
    for key_m in re.finditer(r'\b(?:UNIQUE|PRIMARY KEY)\s*\(([^)]*)\)',body,flags=re.I|re.S):
        candidate_keys.add(tuple(x.strip() for x in key_m.group(1).split(',')))
    for key_col in re.findall(r'^\s{4}(\w+)\s+\w+\s+PRIMARY KEY\b', body, flags=re.M):
        candidate_keys.add((key_col,))
    for key_col in re.findall(r'^\s{4}(\w+)\s+\w+\s+[^\n]*?\bUNIQUE\b', body, flags=re.M):
        candidate_keys.add((key_col,))
    tables[match.group(1)] = {'cols':cols, 'body':body, 'keys':candidate_keys}

assert len(tables) == 24, f'Esperadas 24 tablas, encontradas {len(tables)}'
errors=[]
for t, v in tables.items():
    # FK, single and multi-column; excludes raw ALTER TABLE (se valida aparte).
    for m in re.finditer(r'FOREIGN KEY\s*\(([^)]*)\)\s*REFERENCES\s+(\w+)\s*\(([^)]*)\)', v['body'],flags=re.I|re.S):
        source_cols=[x.strip() for x in m.group(1).split(',')]
        target_table=m.group(2)
        target_cols=[x.strip() for x in m.group(3).split(',')]
        if target_table not in tables: errors.append(f'{t}: tabla destino inexistente {target_table}');continue
        if len(source_cols)!=len(target_cols):errors.append(f'{t}: FK con número distinto de columnas {m.group(0)[:80]}')
        if tuple(target_cols) not in tables[target_table]['keys']:
            errors.append(f"{t}: FK refiere a columnas no únicas {target_table}({','.join(target_cols)})")
        for col in source_cols:
            if col not in v['cols']:errors.append(f'{t}: columna FK inexistente {col}')
        for col in target_cols:
            if col not in tables[target_table]['cols']:errors.append(f'{t}: destino {target_table}.{col} inexistente')
    for m in re.finditer(r'\bREFERENCES\s+(\w+)\s*\((\w+)\)',v['body'],flags=re.I):
        name, col=m.group(1),m.group(2)
        if name not in tables or col not in tables[name]['cols']:errors.append(f'{t}: referencia {name}.{col} inválida')

for required in ['tr_acquisition_run_finalize','tr_observation_accept','tr_observations_seal','tr_observed_action_insert',
 'tr_comparison_guard','tr_technical_change_guard','tr_tracking_baseline_guard','tr_publication_version_guard','tr_preparers_guard',
 'tr_version_novelties_guard','tr_approval_guard','tr_current_publication_guard']:
    if f'CREATE TRIGGER {required} ' not in sql: errors.append(f'Trigger faltante: {required}')

for fragment in ['UNIQUE (tracking_id,change_id)', 'UNIQUE (old_observation_id,new_observation_id,rule_version)',
    'FOREIGN KEY (current_version_id,id)', "WHERE status IN ('PENDING','ACTIVE')", 
    "CHECK (evaluation_decision='ELIGIBLE')", 'CHECK (radicado ~']:
    if fragment not in sql: errors.append(f'Constraint clave faltante: {fragment}')

for p in (ROOT/'diagramas').glob('*.mmd'):
    body=p.read_text()
    if not body.startswith('erDiagram\n'): errors.append(f'Diagrama no ER: {p.name}')
assert len(list((ROOT/'diagramas').glob('*.mmd')))==3
if errors:
    raise AssertionError('\n'.join(errors))
print('ESTÁTICA OK: 24 tablas, referencias de FK a tablas/columnas declaradas, 12 triggers críticos,')
print('3 diagramas ER y restricciones críticas presentes. SQL NO ejecutado ni parseado por PostgreSQL.')
