from __future__ import annotations

from graphlib import CycleError, TopologicalSorter

from .models import BuildError, Component, Manifest


class StrictPlanner:
    """Determines the build order using strict dependency validation."""

    def __init__(self, manifest: Manifest) -> None:
        self._manifest = manifest

    def plan(self) -> list[Component]:
        name_map = self._manifest.by_name()
        sorter = TopologicalSorter()

        for component in self._manifest.components:
            missing = [dep for dep in component.dependencies if dep not in name_map]
            if missing:
                raise BuildError(
                    f"Dependencias desconocidas para {component.name}: {', '.join(missing)}"
                )
            sorter.add(component.name, *component.dependencies)

        try:
            ordered_names = list(sorter.static_order())
        except CycleError as exc:
            raise BuildError(f"Dependencias circulares detectadas: {exc}") from exc

        return [name_map[name] for name in ordered_names if name in name_map]


__all__ = ["StrictPlanner"]
