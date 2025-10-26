from __future__ import annotations

import json
from pathlib import Path

from dataclasses import dataclass
from typing import Iterable, List

from .models import BuildKind, Component, Manifest, QualitySpec


@dataclass(frozen=True)
class DiscoveredComponent:
    name: str
    path: Path
    kind: BuildKind
    quality: QualitySpec | None = None
    commands: tuple[tuple[str, ...], ...] = ()
    dependencies: tuple[str, ...] = ()


class ManifestLoader:
    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root

    def load(self, manifest_path: Path | None) -> Manifest:
        if manifest_path and manifest_path.exists():
            data = json.loads(manifest_path.read_text())
            components = [self._from_dict(item, manifest_path.parent) for item in data]
            return Manifest(components)
        return self.default_manifest()

    def default_manifest(self) -> Manifest:
        discovered = list(self._discover_components())
        components = [
            Component(
                name=item.name,
                path=item.path,
                kind=item.kind,
                build_commands=item.commands,
                dependencies=item.dependencies,
                quality=item.quality,
            )
            for item in discovered
        ]
        return Manifest(components)

    def _discover_components(self) -> Iterable[DiscoveredComponent]:
        yield from self._discover_python_packages()
        yield from self._discover_python_modules()
        yield from self._discover_node_projects()
        yield from self._discover_shell_scripts()

    def _discover_python_packages(self) -> Iterable[DiscoveredComponent]:
        for path in sorted(self._repo_root.iterdir()):
            if not path.is_dir() or path.name.startswith('.'):
                continue
            init_file = path / "__init__.py"
            if not init_file.exists():
                continue
            yield DiscoveredComponent(
                name=f"Paquete Python::{path.name}",
                path=path,
                kind=BuildKind.PYTHON,
                quality=QualitySpec(
                    required_paths=("__init__.py",),
                    description="Paquete Python autodetectado",
                ),
            )

    def _discover_python_modules(self) -> Iterable[DiscoveredComponent]:
        for path in sorted(self._repo_root.glob("*.py")):
            if path.name.startswith("_"):
                continue
            if path.name == "__init__.py":
                continue
            yield DiscoveredComponent(
                name=f"Módulo Python::{path.stem}",
                path=path,
                kind=BuildKind.PYTHON,
                quality=QualitySpec(
                    forbid_empty=True,
                    description="Módulo Python autodetectado",
                ),
            )

    def _discover_node_projects(self) -> Iterable[DiscoveredComponent]:
        for package_json in sorted(self._repo_root.glob("**/package.json")):
            project_dir = package_json.parent
            if project_dir == self._repo_root or project_dir.name.startswith('.'):
                continue
            yield DiscoveredComponent(
                name=f"Proyecto Node::{project_dir.name}",
                path=project_dir,
                kind=BuildKind.NODE,
                quality=QualitySpec(
                    forbid_empty=True,
                    description="Proyecto Node autodetectado",
                ),
            )

    def _discover_shell_scripts(self) -> Iterable[DiscoveredComponent]:
        candidates: List[Path] = []
        candidates.extend(sorted(self._repo_root.glob("*.sh")))
        candidates.extend(sorted(self._repo_root.glob("scripts/*.sh")))
        for path in sorted(set(candidates)):
            yield DiscoveredComponent(
                name=f"Script Shell::{path.stem}",
                path=path,
                kind=BuildKind.SHELL,
                quality=QualitySpec(
                    forbid_empty=True,
                    description="Script shell autodetectado",
                ),
            )

    def _from_dict(self, item: dict, base: Path) -> Component:
        path = item.get("path")
        if not path:
            raise ValueError("Cada componente necesita un campo 'path'.")

        commands = item.get("commands") or []
        dependencies = item.get("dependencies") or []
        kind = BuildKind(item.get("kind", "python"))

        quality_spec = None
        quality_data = item.get("quality")
        if quality_data is not None:
            quality_spec = QualitySpec(
                required_paths=tuple(quality_data.get("required_paths", ())),
                forbid_empty=quality_data.get("forbid_empty", True),
                description=quality_data.get("description"),
            )

        return Component(
            name=item["name"],
            path=(base / path) if not Path(path).is_absolute() else Path(path),
            kind=kind,
            build_commands=tuple(tuple(cmd) for cmd in commands),
            dependencies=tuple(dependencies),
            quality=quality_spec,
        )


__all__ = ["ManifestLoader"]
