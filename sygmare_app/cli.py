from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Iterable, Optional

from .manifest import ManifestLoader
from .models import BuildError
from .orchestrator import Orchestrator, OrchestratorConfig
from .planner import StrictPlanner
from .reporting import Totals, render_json, render_table
from .statuses import BuildStatus


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Aplicación Sygmare para hiperorquestación sintética del ecosistema AURVO."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("sygmare_manifest.json"),
        help="Ruta al manifiesto JSON que describe los componentes a compilar.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra las acciones sin ejecutarlas.",
    )
    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
        help="Detiene la orquestación en el primer fallo de compilación o de calidad.",
    )
    parser.add_argument(
        "--format",
        choices=("table", "json"),
        default="table",
        help="Formato de salida para el resumen final.",
    )
    parser.add_argument(
        "--only",
        action="append",
        metavar="FILTRO",
        help=(
            "Compila solo componentes cuyo nombre contenga el filtro proporcionado. "
            "Puede especificarse varias veces."
        ),
    )
    return parser


def run_cli(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parent.parent
    loader = ManifestLoader(repo_root)

    try:
        manifest = loader.load(args.manifest)
    except Exception as exc:  # noqa: BLE001
        parser.error(str(exc))

    planner = StrictPlanner(manifest)
    try:
        plan = planner.plan()
    except BuildError as exc:
        parser.error(str(exc))

    if args.only:
        lowered_filters = [token.lower() for token in args.only]
        plan = [
            component
            for component in plan
            if any(token in component.name.lower() for token in lowered_filters)
        ]
        if not plan:
            print("No se encontraron componentes que coincidan con los filtros proporcionados.")
            return 0

    orchestrator = Orchestrator(
        OrchestratorConfig(dry_run=args.dry_run, stop_on_failure=args.stop_on_failure)
    )

    try:
        records = orchestrator.build(plan)
    except BuildError as exc:
        print(f"✖ {exc}")
        return 1

    if args.format == "json":
        print(render_json(records))
    else:
        print(render_table(records))

    totals = Totals.from_records(records)
    failures = totals.counts[BuildStatus.FAILED]
    quality_failures = totals.counts[BuildStatus.QUALITY_FAILED]
    return 0 if failures == 0 and quality_failures == 0 else 1


__all__ = ["build_argument_parser", "run_cli"]
