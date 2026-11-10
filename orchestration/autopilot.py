#!/usr/bin/env python3
"""LegalTech backend autonomous ticket runner.

Uses Codex CLI but never treats an LLM's success message as a passing gate.
This script is intentionally dependency-free; backend tools are installed later.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import posixpath
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
# Only this branch is authorized for agent-produced commits and remote pushes.
GIT_BRANCH = 'agent/legaltech-backend'
GIT_REMOTE = 'origin'
EXPECTED_REMOTE = 'https://github.com/Universidad-UMB/legaltech.git'
COMMIT_MESSAGES = {
    'INC-00': 'chore(inc-00): initialize backend infrastructure',
    'INC-01': 'feat(inc-01): implement clients and trackings',
    'INC-02': 'feat(inc-02): implement observations and baseline',
    'INC-03': 'feat(inc-03): implement deterministic comparison',
    'INC-04': 'feat(inc-04): implement novelty treatment',
    'INC-05': 'feat(inc-05): implement versioned publications',
    'INC-06': 'feat(inc-06): implement portal authorization',
    'INC-07': 'test(inc-07): complete acceptance and security tests',
}



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



class GitGateError(RuntimeError):
    """Git refused an unsafe state or GitHub publication failed."""


def git(*args: str, timeout: int = 90) -> str:
    # Disable credential prompts: a background task must fail instead of hanging.
    env = os.environ.copy()
    env['GIT_TERMINAL_PROMPT'] = '0'
    env['GCM_INTERACTIVE'] = 'never'
    result = subprocess.run(
        ['git', *args], cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        timeout=timeout, check=False,
    )
    if result.returncode != 0:
        info = (result.stderr or result.stdout).strip()
        raise GitGateError(f"git {' '.join(args)} falló (exit={result.returncode}): {info[:700]}")
    return result.stdout.strip()


def approved_branch() -> str:
    return git('branch', '--show-current')


def ensure_git_branch() -> None:
    worktree = Path(git('rev-parse', '--show-toplevel')).resolve()
    if worktree != ROOT.resolve():
        raise GitGateError(f'Repositorio inesperado: {worktree}')
    remote = git('remote', 'get-url', GIT_REMOTE).rstrip('/')
    if remote != EXPECTED_REMOTE.rstrip('/'):
        raise GitGateError(f'Remoto no autorizado: {remote}')
    current = approved_branch()
    if current == GIT_BRANCH:
        return
    if current != 'main':
        raise GitGateError(f'Rama inesperada {current!r}; se exige main o {GIT_BRANCH}')
    if git('status', '--porcelain', '--untracked-files=no'):
        raise GitGateError('Hay cambios rastreados en main; guardarlos antes de cambiar de rama')
    # The user's untracked .nodeterm/ remains untouched.
    existing = subprocess.run(
        ['git', 'show-ref', '--verify', '--quiet', f'refs/heads/{GIT_BRANCH}'],
        cwd=ROOT, stdin=subprocess.DEVNULL, capture_output=True, check=False,
    )
    if existing.returncode == 0:
        git('switch', GIT_BRANCH)
    elif existing.returncode == 1:
        git('switch', '-c', GIT_BRANCH)
    else:
        raise GitGateError('No se puede inspeccionar la rama del agente')
    if approved_branch() != GIT_BRANCH:
        raise GitGateError('No se pudo cambiar a la rama del agente')


def valid_artifact_path(path: str) -> bool:
    norm = path.replace('\\', '/')
    return norm.startswith('backend/') or norm == 'docs/ENTREGA-FINAL.md'


def forbidden_artifact_path(path: str) -> bool:
    norm = path.replace('\\', '/')
    parts = posixpath.normpath(norm).split('/')
    if any(p in {'.venv', '__pycache__', '.pytest_cache', '.mypy_cache',
                  '.ruff_cache', 'node_modules', '.tox', '.git', '.autopilot'} for p in parts):
        return True
    name = parts[-1].lower()
    if name == '.env' or (name.startswith('.env.') and name not in {'.env.example', '.env.sample', '.env.template'}):
        return True
    if name in {'id_rsa', 'id_ed25519', 'credentials.json', 'service-account.json'}:
        return True
    return name.endswith(('.pem', '.p12', '.pfx', '.key', '.keystore', '.pyc'))


def changed_paths() -> list[str]:
    tracked = git('diff', '--name-only', '-z', 'HEAD').split('\0')
    # Include untracked files so new files outside backend cannot hide.
    untracked = git('ls-files', '--others', '--exclude-standard', '-z').split('\0')
    return [x for x in (tracked + untracked) if x]


def check_git_scope() -> None:
    if approved_branch() != GIT_BRANCH:
        raise GitGateError('Prohibido trabajar sobre main u otra rama')
    unexpected = []
    for path in changed_paths():
        if path.startswith(('.nodeterm/', '.autopilot/')):
            continue
        if not valid_artifact_path(path) or forbidden_artifact_path(path):
            unexpected.append(path)
    if unexpected:
        raise GitGateError('Cambios fuera del alcance permitido: ' + ', '.join(unexpected[:12]))


def commit_verified_ticket(ticket: str) -> str:
    """Stage a strict allowlist; never stage .nodeterm, .autopilot, or secrets."""
    check_git_scope()
    git('add', '-A', '--', 'backend')
    if (ROOT / 'docs' / 'ENTREGA-FINAL.md').exists():
        git('add', '-A', '--', 'docs/ENTREGA-FINAL.md')
    staged = [x for x in git('diff', '--cached', '--name-only', '-z').split('\0') if x]
    if not staged:
        raise GitGateError(f'{ticket} pasó pruebas, pero no produjo cambios para commit')
    invalid = [p for p in staged if not valid_artifact_path(p) or forbidden_artifact_path(p)]
    if invalid:
        raise GitGateError('Se detectaron archivos no permitidos en staging: ' + ', '.join(invalid[:12]))
    git('diff', '--cached', '--check')
    git('commit', '-m', COMMIT_MESSAGES[ticket], timeout=240)
    return git('rev-parse', 'HEAD')


def push_verified_commit(sha: str) -> None:
    if approved_branch() != GIT_BRANCH:
        raise GitGateError('El push fue bloqueado: rama diferente de la autorizada')
    if git('rev-parse', 'HEAD') != sha:
        raise GitGateError('El HEAD cambió después del commit; push cancelado')
    # Explicit destination avoids inheriting Git push.default=matching / main.
    git('push', '--porcelain', '--set-upstream', GIT_REMOTE,
        f'HEAD:refs/heads/{GIT_BRANCH}', timeout=300)
    remote_ref = git('ls-remote', '--heads', GIT_REMOTE,
                     f'refs/heads/{GIT_BRANCH}', timeout=90)
    remote_sha = remote_ref.split()[0] if remote_ref else None
    if remote_sha != sha:
        raise GitGateError(f'El SHA remoto {remote_sha!r} no coincide con commit {sha}')


def finish_published_ticket(state: dict[str, Any], ticket: str) -> None:
    entry = state['tickets'][ticket]
    sha = entry.get('commit_sha')
    if not sha:
        raise GitGateError(f'{ticket} no tiene commit para publicar')
    push_verified_commit(sha)
    entry['status'] = 'DONE'
    entry['completed_at'] = utc()
    entry['reason'] = f'Pruebas y push confirmados: {sha[:12]}'
    entry['remote_branch'] = GIT_BRANCH
    save_state(state)
    print(f'{ticket}: DONE, commit {sha[:12]} confirmado en origin/{GIT_BRANCH}', flush=True)

def make_prompt(ticket: str, attempt: int, reason: str) -> str:
    intro=f'''Implementa únicamente {ticket} de forma completa y profesional.
Lee primero AGENTS.md, AGENT.md, tickets/{ticket}.md, documentación de dominio y arquitectura, contrato OpenAPI y fixtures. Trabaja en backend/.
Este es el intento {attempt}. El orquestador no preguntará si debe continuar a otro incremento: verificará tus cambios y lo lanzará automáticamente si pasa.
No edites governance/APROBACION-DEMO-001.json, .autopilot/, AGENTS.md, orquestación ni pruebas canónicas como atajo. No añadas integraciones reales. Modifica solo backend/ y, en INC-07, docs/ENTREGA-FINAL.md.
Debes crear/actualizar tests reales, asegurar uv.lock, DB local PostgreSQL, Alembic, Ruff, mypy y pytest. No aceptes 'terminado' sin pruebas. Evita cambios no autorizados a OpenAPI, no ejecutes git add/commit/push (lo hará el orquestador tras verificar), ni toques datos reales. No formules preguntas al operador; documenta bloqueos materiales.
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
    try:
        ensure_git_branch()
    except (GitGateError, subprocess.TimeoutExpired) as exc:
        print(f'BLOCKED: preparación Git: {exc}', file=sys.stderr)
        return 6
    state=read_state()
    for ticket in TICKETS:
        t=state['tickets'][ticket]
        if t['status']=='DONE':
            print(ticket,'ya validado; siguiente')
            continue
        # Crash/retry-safe: if a verified commit exists, retry only its push.
        if t.get('commit_sha'):
            try:
                finish_published_ticket(state, ticket)
            except (GitGateError, subprocess.TimeoutExpired) as exc:
                t['status']='BLOCKED';t['reason']=f'Push pendiente: {exc}';save_state(state)
                print(f'BLOCKED: {t["reason"]}', file=sys.stderr)
                return 6
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
            sandbox = 'danger-full-access' if args.full_access else 'workspace-write'
            # --ask-for-approval is a global option on Codex CLI.
            cmd=[shutil.which('codex') or 'codex', '--ask-for-approval', 'never',
                 '--model', 'gpt-6-luna','--config', 'model_reasoning_effort="max"',
                 'exec', '--sandbox', sandbox, '--cd', str(ROOT),
                 '--output-last-message', str(output_path), prompt]
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
                try:
                    sha_commit = commit_verified_ticket(ticket)
                    t['commit_sha'] = sha_commit
                    t['status'] = 'PUSHING'
                    t['reason'] = 'Pruebas superadas; commit local creado, push pendiente'
                    save_state(state)  # Persist before network operation.
                    finish_published_ticket(state, ticket)
                except (GitGateError, subprocess.TimeoutExpired) as exc:
                    t['status'] = 'BLOCKED'
                    t['reason'] = f'Git: {exc}'
                    save_state(state)
                    print(f'BLOCKED: {ticket} {t["reason"]}', file=sys.stderr)
                    return 6
                break
            t['status']='BLOCKED';t['reason']=last_reason;save_state(state)
            print(f'{ticket}: fallo de verificación; {last_reason}',file=sys.stderr,flush=True)
            if explicit_blocker:
                print('Bloqueo de negocio declarado: requiere revisión del operador, sin reintentar automáticamente.',file=sys.stderr)
                return 5
        if t['status']!='DONE':
            print(f'BLOCKED: {ticket} agotó los {args.max_attempts} intentos de esta ejecución; ver logs. Reanudar tras corregir entorno.',file=sys.stderr)
            return 4
    print('ALL_DONE: INC-00..INC-07 verificados y publicados en rama de agente. Merge/despliegue requieren revisión humana.')
    return 0


def main() -> int:
    parser=argparse.ArgumentParser(description='Orquestación segura y retomable para el backend LegalTech')
    sub=parser.add_subparsers(dest='action',required=True)
    sub.add_parser('doctor'); sub.add_parser('status')
    runner=sub.add_parser('run')
    runner.add_argument('--dry-run',action='store_true')
    runner.add_argument('--full-access',action='store_true',
                        help='Codex sin sandbox (solo en máquina/VM aislada). Sin esta opción, workspace-write.')
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
