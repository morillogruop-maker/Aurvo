"""Permite ejecutar la aplicación Sygmare como módulo."""
from __future__ import annotations

from .cli import run_cli


def main() -> int:
    return run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
