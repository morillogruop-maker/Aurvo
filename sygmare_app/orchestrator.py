from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
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
            component_started = perf_counter()
            print(f"▶ {component.name}")
            report = self._quality.evaluate(component)
            if not report.passed:
                details = report.formatted()
                print("  ✖ Calidad no superada:")
                for line in details.splitlines():
                    print(f"    {line}")
                duration = perf_counter() - component_started
                records.append(
                    BuildRecord(
                        component,
                        BuildStatus.QUALITY_FAILED,
                        details,
                        duration,
                    )
                )
                if self.config.stop_on_failure:
                    raise BuildError(f"Calidad fallida para {component.name}")
                print()
                continue

            builder = self._builders.get(component.kind)
            if builder is None:
                message = f"Tipo de componente no soportado: {component.kind}"
                print(f"  ⚠️  {message}")
                duration = perf_counter() - component_started
                records.append(
                    BuildRecord(component, BuildStatus.SKIPPED, message, duration)
                )
                print()
                continue

            build_started = perf_counter()
            result: CommandResult = builder.build(component, dry_run=self.config.dry_run)
            build_duration = perf_counter() - build_started
            total_duration = perf_counter() - component_started
            result_duration = result.duration if result.duration is not None else build_duration
            print(f"  → Resultado: {result.status.value} ({result_duration:.2f}s)\n")
            records.append(
                BuildRecord(
                    component,
                    result.status,
                    result.details,
                    total_duration,
                )
            )

            if result.status == BuildStatus.FAILED and self.config.stop_on_failure:
                raise BuildError(f"Fallo de compilación en {component.name}")

        return records


__all__ = ["Orchestrator", "OrchestratorConfig"]
