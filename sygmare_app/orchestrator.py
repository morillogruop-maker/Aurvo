from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .executors import CommandResult, builder_registry
from .models import BuildError, BuildRecord, Component
from .quality import StrictQualityInspector
from .statuses import BuildStatus


@dataclass
class OrchestratorConfig:
    dry_run: bool = False
    stop_on_failure: bool = False


class Orchestrator:
    def __init__(self, config: OrchestratorConfig | None = None) -> None:
        self.config = config or OrchestratorConfig()
        self._quality = StrictQualityInspector()
        self._builders = builder_registry()

    def build(self, components: Iterable[Component]) -> List[BuildRecord]:
        records: List[BuildRecord] = []
        for component in components:
            print(f"▶ {component.name}")
            report = self._quality.evaluate(component)
            if not report.passed:
                details = report.formatted()
                print("  ✖ Calidad no superada:")
                for line in details.splitlines():
                    print(f"    {line}")
                records.append(BuildRecord(component, BuildStatus.QUALITY_FAILED.value, details))
                if self.config.stop_on_failure:
                    raise BuildError(f"Calidad fallida para {component.name}")
                print()
                continue

            builder = self._builders.get(component.kind)
            if builder is None:
                message = f"Tipo de componente no soportado: {component.kind}"
                print(f"  ⚠️  {message}")
                records.append(BuildRecord(component, BuildStatus.SKIPPED.value, message))
                print()
                continue

            result: CommandResult = builder.build(component, dry_run=self.config.dry_run)
            records.append(BuildRecord(component, result.status.value, result.details))
            print(f"  → Resultado: {result.status.value}\n")

            if result.status == BuildStatus.FAILED and self.config.stop_on_failure:
                raise BuildError(f"Fallo de compilación en {component.name}")

        return records


__all__ = ["Orchestrator", "OrchestratorConfig"]
