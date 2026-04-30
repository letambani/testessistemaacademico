"""
Sobe o microserviço da faculdade e o SPA principal.

Portas (padrão 5001 e 5050) — sobrescreva se estiverem ocupadas:
  FACULDADE_PORT=5002 SPA_PORT=5000 python run_stack.py

O SPA recebe FACULDADE_API_BASE_URL apontando para a faculdade (mesmo host, porta FACULDADE_PORT).

Uso: python run_stack.py
Encerre com Ctrl+C.
"""
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROCS = []


def _terminate_all():
    for p in PROCS:
        if p.poll() is None:
            p.terminate()
    for p in PROCS:
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()


def main():
    env = os.environ.copy()
    if "FMP_ENABLE_CORS" not in env:
        env["FMP_ENABLE_CORS"] = "1"
    fac_port = env.get("FACULDADE_PORT", "5001")
    spa_port = env.get("SPA_PORT", "5050")
    env["FACULDADE_PORT"] = str(fac_port)
    env["SPA_PORT"] = str(spa_port)
    base = env.get("FACULDADE_API_BASE_URL", f"http://127.0.0.1:{fac_port}")
    env["FACULDADE_API_BASE_URL"] = base.rstrip("/")

    fac = subprocess.Popen(
        [sys.executable, str(ROOT / "faculdade_app.py")], cwd=ROOT, env=env
    )
    PROCS.append(fac)
    time.sleep(1.5)
    spa = subprocess.Popen([sys.executable, str(ROOT / "app.py")], cwd=ROOT, env=env)
    PROCS.append(spa)
    time.sleep(1.0)
    for label, proc in (
        ("faculdade_app.py", fac),
        ("app.py", spa),
    ):
        code = proc.poll()
        if code is not None:
            print(
                f"\n[run_stack] O processo {label} encerrou ao iniciar (código {code}). "
                "Veja o traceback acima.",
                file=sys.stderr,
            )
            print(
                "[run_stack] Confira se o ambiente virtual está ativo: "
                "cd backend && source .venv/bin/activate && python run_stack.py\n",
                file=sys.stderr,
            )
            _terminate_all()
            sys.exit(1)

    print(f"Faculdade API: http://127.0.0.1:{fac_port}  |  SPA: http://127.0.0.1:{spa_port}")
    print("Ctrl+C encerra os dois processos.")

    def _handler(_sig, _frame):
        _terminate_all()
        sys.exit(0)

    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)

    for p in PROCS:
        p.wait()


if __name__ == "__main__":
    main()
