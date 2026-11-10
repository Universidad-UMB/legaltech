#!/usr/bin/env python3
"""LegalTech backend autonomous ticket runner.

Uses Codex CLI but never treats an LLM's success message as a passing gate.
This script is intentionally dependency-free; backend tools are installed later.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / '.autopilot'
STATE_FILE = STATE_DIR / 'state.json'
LOG_DIR = STATE_DIR / 'logs'
APPROVAL = ROOT / 'governance' / 'APROBACION-DEMO-001.json'
TICKETS = [f'INC-{i:02d}' for i in range(8)]
TOOLS = ('git', 'codex', 'uv', 'docker')


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_approval(path: Path = APPROVAL) -> tuple[bool, list[str]]:
    issues: list[str] = []
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        return False, [f'No se puede leer el gate de aprobación: {exc}']
    if value.get('aceptacion_tecnica') != 'ACEPTAR':
        issues.append('Aceptación técnica sigue pendiente')
    decisions = value.get('decisiones')
    if not isinstance(decisions, dict):
        return False, issues + ['Falta mapa de decisiones']
    for n in range(1, 7):
        key = f'DF5-{n:02d}'
        if decisions.get(key) != 'ACEPTAR':
            issues.append(f'{key} no tiene aceptación explícita')
    if not value.get('aprobador_autores', '').strip():
        issues.append('Falta identificar al menos un autor aprobador')
    if not value.get('fecha_iso', '').strip():
        issues.append('Falta fecha de aprobación')
    if not value.get('evidencia', '').strip():
        issues.append('Falta referencia de evidencia de aprobación')
    return not issues, issues


def initial_state() -> dict[str, Any]:
    return {'schema': 1, 'created_at': utc(), 'tickets': {ticket: {'status':'PENDING', 'attempts':0, 'history':[]} for ticket in TICKETS}}


def read_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return initial_state()
    value = json.loads(STATE_FILE.read_text(encoding='utf-8'))
    if value.get('schema') != 1 or set(value.get('tickets', {})) != set(TICKETS):
        raise RuntimeError('Estado incompatible: se necesita revisión del operador')
    return value


def save_state(state: dict[str, Any]) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    output = json.dumps(state, ensure_ascii=False, indent=2) + '\n'
    temp = STATE_FILE.with_suffix('.tmp')
    temp.write_text(output, encoding='utf-8')
    temp.replace(STATE_FILE)


def show_status(state: dict[str, Any]) -> None:
    for ticket in TICKETS:
        t = state['tickets'][ticket]
        print(f"{ticket}: {t['status']:<11} intentos={t['attempts']} " + (t.get('reason') or ''))
    print('Todos los incrementos DONE:', all(state['tickets'][t]['status']=='DONE' for t in TICKETS))


def doctor(verbose: bool = True) -> bool:
    ok, issues = read_approval()
    for entry in ('AGENT.md','AGENTS.md','contratos/API-001.openapi.yaml','docs/PLAN-DEV-001_v0.1.md','scripts/validate_handoff.py'):
        if not (ROOT/entry).is_file():
            issues.append(f'Archivo requerido ausente: {entry}')
    for t in TICKETS:
        if not (ROOT/'tickets'/f'{t}.md').is_file():
            issues.append(f'Ticket requerido ausente: {t}')
    if not (ROOT/'.git').exists():
        issues.append('Git no inicializado en la carpeta del proyecto')
    for tool in TOOLS:
        if not shutil.which(tool):
            issues.append(f'No se encontró ejecutable: {tool}')
    if verbose:
        print('Gate de decisiones:', 'ACEPTADO' if ok else 'PENDIENTE')
        if issues:
            for issue in issues:
                print(' -',issue)
        else:
            print('Precondiciones locales presentes; Docker/DB se verificarán al ejecutar.')
    return not issues


def run_logged(cmd: list[str], cwd: Path, destination: Path, timeout: int) -> tuple[bool, str]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    with destination.open('w', encoding='utf-8', errors='replace') as out:
        out.write(f'# cmd: {json.dumps(cmd, ensure_ascii=False)}\n# cwd: {cwd}\n# utc: {utc()}\n')
        out.flush()
        try:
            proc = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT)
        except OSError as exc:
            out.write(f'ERROR_START: {exc}\n')
            return False, f'No inicia el comando: {exc}'
        try:
            code = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            out.write(f'\nTIMEOUT después de {timeout}s\n')
            return False, 'Timeout'
        out.write(f'\n# exit_code={code} duration_s={round(time.monotonic()-start,1)}\n')
    return code == 0, f'exit_code={code}'


def run_capture(cmd: list[str], cwd: Path, destination: Path, timeout: int = 120) -> tuple[bool,str]:
    success, reason = run_logged(cmd,cwd,destination,timeout)
    return success, reason


def command_paths(ticket: str) -> list[tuple[str,list[str],Path,int]]:
    # These commands are fixed, never LLM-generated or parsed from editable manifests.
    backend = ROOT/'backend'
    result: list[tuple[str,list[str],Path,int]] = [
        ('handoff', [sys.executable,'scripts/validate_handoff.py'], ROOT, 120),
    ]
    if ticket not in TICKETS:
        raise ValueError(ticket)
    result.extend([
        ('compose-validate',['docker','compose','config','-q'],backend,120),
        ('start-demo-postgres',['docker','compose','up','-d','db'],backend,300),
        ('migrate',['uv','run','--frozen','alembic','upgrade','head'],backend,300),
        ('openapi',['uv','run','--frozen','python','../orchestration/check_runtime_openapi.py','--through',ticket],backend,240),
        ('lint',['uv','run','--frozen','ruff','check','.'],backend,240),
        ('types',['uv','run','--frozen','mypy','app'],backend,240),
        ('tests',['uv','run','--frozen','pytest','-q'],backend,600),
    ])
    if ticket == 'INC-07':
        result.append(('collect',['uv','run','--frozen','pytest','--collect-only','-q'],backend,300))
    return result


def basic_artifacts() -> list[str]:
    paths = ['backend/pyproject.toml','backend/uv.lock','backend/app/main.py',
             'backend/alembic.ini','backend/compose.yaml','backend/tests']
    return [p for p in paths if not (ROOT/p).exists()]


def expected_ids() -> dict[str, list[str]]:
    import csv
    acceptance = json.loads((ROOT/'pruebas/PROTO-AT-001.json').read_text(encoding='utf-8'))
    expected = {'AT':[x['id'] for x in acceptance]}
    for key, filename in (('API','API-NEG-001.csv'), ('DATA','DATA-TEST-001.csv')):
        with (ROOT/'pruebas'/filename).open(encoding='utf-8-sig',newline='') as stream:
            expected[key] = [row['id'] for row in csv.DictReader(stream)]
    return expected


def check_collected_tests(path: Path) -> tuple[bool,str]:
    text = path.read_text(encoding='utf-8',errors='replace') if path.exists() else ''
    expected = expected_ids()
    missing: list[str] = []
    for ids in expected.values():
        for identifier in ids:
            if identifier.lower() not in text.lower():
                missing.append(identifier)
    if missing:
        return False, f'{len(missing)} IDs sin prueba recolectada: '+', '.join(missing[:14])
    return True, f'{sum(map(len,expected.values()))} IDs recolectados (no equivale a pruebas pasadas)'


def verify(ticket: str, attempt: int, timeout: int, approval_sha: str) -> tuple[bool,str,list[dict[str,str]]]:
    if digest(APPROVAL) != approval_sha:
        return False, 'El archivo de aprobación fue modificado durante la ejecución', []
    absent = basic_artifacts()
    if absent:
        return False, 'Artefactos de backend faltantes: '+', '.join(absent), []
    results=[]
    for name,cmd,cwd,limit in command_paths(ticket):
        log = LOG_DIR/f'{ticket}-attempt-{attempt:02d}-verify-{name}.log'
        passed, reason = run_capture(cmd,cwd,log,min(limit,timeout))
        results.append({'gate':name,'status':'PASS' if passed else 'FAIL','log':str(log.relative_to(ROOT))})
        if not passed:
            return False, f'{name}: {reason}. Revisar {log.relative_to(ROOT)}', results
        if name == 'collect':
            found, message=check_collected_tests(log)
            if not found:
                return False, message, results
    if ticket == 'INC-07' and not (ROOT/'docs'/'ENTREGA-FINAL.md').is_file():
        return False, 'Falta docs/ENTREGA-FINAL.md', results
    if digest(APPROVAL) != approval_sha:
        return False,'Archivo de aprobación modificado durante verificación',results
    return True,'Todos los gates automatizados verificables superados',results


def make_prompt(ticket: str, attempt: int, reason: str) -> str:
    intro=f'''Implementa únicamente {ticket} de forma completa y profesional.
Lee primero AGENTS.md, AGENT.md, tickets/{ticket}.md, documentación de dominio y arquitectura, contrato OpenAPI y fixtures. Trabaja en backend/.
Este es el intento {attempt}. El orquestador no preguntará si debe continuar a otro incremento: verificará tus cambios y lo lanzará automáticamente si pasa.
No edites governance/APROBACION-DEMO-001.json, .autopilot/ ni las pruebas canónicas como atajo. No añadas integraciones reales.
Debes crear/actualizar tests reales, asegurar uv.lock, DB local PostgreSQL, Alembic, Ruff, mypy y pytest. No aceptes 'terminado' sin pruebas. Evita cambios no autorizados a OpenAPI, no publiques código, no hagas git push, ni toques datos reales.
Al finalizar deja un resumen de archivos y comandos ejecutados con resultados verdaderos; cualquier bloqueo nuevo debe quedar por escrito y sin falsificar el estado.
'''
    if reason:
        intro += f'\nEl intento anterior no pasó el gate. Diagnóstico resumido:\n{reason[:3000]}\nResuelve la causa antes de terminar.\n'
    return intro


def run_pipeline(args: argparse.Namespace) -> int:
    if args.dry_run:
        print('Simulación del plan INC-00..INC-07 sin ejecutar agentes ni migraciones.')
        for ticket in TICKETS:
            print(ticket, '-> codex exec -> Compose/PostgreSQL -> Alembic -> Ruff -> mypy -> Pytest')
        ok, issues=read_approval()
        print('Gate:', 'ACEPTADO' if ok else 'PENDIENTE', '; '.join(issues))
        return 0
    if not doctor():
        print('BLOCKED: autorizar una vez los documentos de prototipo y preparar el entorno antes de ejecutar.',file=sys.stderr)
        return 2
    sha = digest(APPROVAL)
    LOG_DIR.mkdir(parents=True,exist_ok=True)
    state=read_state()
    for ticket in TICKETS:
        t=state['tickets'][ticket]
        if t['status']=='DONE':
            print(ticket,'ya validado; siguiente')
            continue
        last_reason=t.get('reason','')
        for _ in range(args.max_attempts):
            if digest(APPROVAL) != sha:
                t['status']='BLOCKED'; t['reason']='Gate de aprobación cambiado durante ejecución';save_state(state);return 3
            attempt=t['attempts']+1
            t['attempts']=attempt;t['status']='RUNNING';t['started_at']=utc();save_state(state)
            print(f'[{utc()}] {ticket} intento {attempt}; iniciando Codex',flush=True)
            output_path=LOG_DIR/f'{ticket}-attempt-{attempt:02d}-final.txt'
            prompt = make_prompt(ticket,attempt,last_reason)
            cmd=['codex','exec','--sandbox','workspace-write','--ask-for-approval','never','--cd',str(ROOT),'--output-last-message',str(output_path),prompt]
            call_log=LOG_DIR/f'{ticket}-attempt-{attempt:02d}-codex.log'
            ok, msg = run_logged(cmd,ROOT,call_log,args.timeout_seconds)
            results=[]
            final_message = output_path.read_text(encoding='utf-8',errors='replace') if output_path.exists() else ''
            explicit_blocker = bool(re.search(r'^BLOCKED\s*:', final_message, re.MULTILINE | re.IGNORECASE))
            if ok and explicit_blocker:
                ok=False
                last_reason='Agente declaró bloqueo material, revisar mensaje de cierre y decisiones'
            elif ok:
                t['status']='VERIFYING';save_state(state)
                ok,last_reason,results=verify(ticket,attempt,args.timeout_seconds,sha)
            else:
                last_reason=f'Codex {msg}; revisar {call_log.relative_to(ROOT)}'
            t['history'].append({'attempt':attempt,'when':utc(),'passed':ok,'reason':last_reason,'checks':results})
            if ok:
                t['status']='DONE';t['completed_at']=utc();t['reason']='Gates ejecutados sin error';save_state(state)
                print(f'{ticket}: DONE, se continúa automáticamente.',flush=True)
                break
            t['status']='BLOCKED';t['reason']=last_reason;save_state(state)
            print(f'{ticket}: fallo de verificación; {last_reason}',file=sys.stderr,flush=True)
            if explicit_blocker:
                print('Bloqueo de negocio declarado: requiere revisión del operador, sin reintentar automáticamente.',file=sys.stderr)
                return 5
        if t['status']!='DONE':
            print(f'BLOCKED: {ticket} agotó los {args.max_attempts} intentos de esta ejecución; ver logs. Reanudar tras corregir entorno.',file=sys.stderr)
            return 4
    print('ALL_DONE: INC-00..INC-07 verificados. Revisión humana final pendiente antes de merge o despliegue.')
    return 0


def main() -> int:
    parser=argparse.ArgumentParser(description='Orquestación segura y retomable para el backend LegalTech')
    sub=parser.add_subparsers(dest='action',required=True)
    sub.add_parser('doctor'); sub.add_parser('status')
    runner=sub.add_parser('run')
    runner.add_argument('--dry-run',action='store_true')
    runner.add_argument('--max-attempts',type=int,default=3)
    runner.add_argument('--timeout-seconds',type=int,default=3600)
    args=parser.parse_args()
    if args.action=='doctor':return 0 if doctor() else 2
    if args.action=='status':show_status(read_state());return 0
    if args.max_attempts<1 or args.max_attempts>8 or args.timeout_seconds<60:
        parser.error('Reintentos deben ser 1..8 y timeout >= 60 segundos')
    return run_pipeline(args)

if __name__ == '__main__':
    raise SystemExit(main())
