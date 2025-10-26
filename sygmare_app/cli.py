from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Iterable, Optional

from .manifest import ManifestLoader
from .models import BuildError
from .orchestrator import Orchestrator, OrchestratorConfig
from .planner import StrictPlanner
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

    orchestrator = Orchestrator(
        OrchestratorConfig(dry_run=args.dry_run, stop_on_failure=args.stop_on_failure)
    )

    try:
        records = orchestrator.build(plan)
    except BuildError as exc:
        print(f"✖ {exc}")
        return 1

    counts = Counter(record.status for record in records)

    print("Resumen:")
    for record in records:
        print(f"  - {record.component.name}: {record.status}")
        if record.details:
            print(f"      {record.details}")

    print("\nTotales:")
    for status in BuildStatus:
        print(f"  {status.value:>14}: {counts.get(status.value, 0)}")

    failures = counts.get(BuildStatus.FAILED.value, 0)
    quality_failures = counts.get(BuildStatus.QUALITY_FAILED.value, 0)
    return 0 if failures == 0 and quality_failures == 0 else 1


__all__ = ["build_argument_parser", "run_cli"]
