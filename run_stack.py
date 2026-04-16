#!/usr/bin/env python3
"""
Ponto de entrada na raiz do repositório: delega para backend/run_stack.py
(com cwd em backend/, onde estão app.py e faculdade_app.py).

Uso (na raiz):  python run_stack.py
Equivalente:     cd backend && python run_stack.py
"""
import os
import subprocess
import sys

_REPO = os.path.dirname(os.path.abspath(__file__))
_SEM = os.path.join(_REPO, "backend")
_SCRIPT = os.path.join(_SEM, "run_stack.py")

if not os.path.isfile(_SCRIPT):
    print("Erro: não encontrado backend/run_stack.py", file=sys.stderr)
    sys.exit(1)

sys.exit(
    subprocess.call([sys.executable, _SCRIPT], cwd=_SEM, env=os.environ.copy())
)
