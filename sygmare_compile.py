#!/usr/bin/env python3
"""Aplicación de hiperorquestación sintética Sygmare para AURVO.

Este módulo actúa como *entrypoint* de la aplicación estricta diseñada para
coordinar compilaciones, verificaciones de calidad y dependencias entre todos
los componentes del ecosistema.  Internamente delega en ``sygmare_app`` que
implementa algoritmos rigurosos de planificación topológica, controles de
calidad y ejecución resiliente de comandos.
"""

from __future__ import annotations

from sygmare_app.cli import run_cli


def main() -> int:
    return run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
