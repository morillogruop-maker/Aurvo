from __future__ import annotations

import json
from pathlib import Path

from .models import BuildKind, Component, Manifest, QualitySpec


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
        root = self._repo_root
        components = [
            Component(
                name="AURVO Core",
                path=root / "AURVO_OS" / "core",
                kind=BuildKind.PYTHON,
                quality=QualitySpec(required_paths=("__init__.py",)),
            ),
            Component(
                name="Hiperorquestación Cognitiva",
                path=root / "AURVO_OS" / "hoc",
                kind=BuildKind.PYTHON,
                quality=QualitySpec(required_paths=("__init__.py",)),
            ),
            Component(
                name="SantoSecure",
                path=root / "AURVO_OS" / "security",
                kind=BuildKind.PYTHON,
                quality=QualitySpec(required_paths=("__init__.py",)),
            ),
            Component(
                name="Aurvo AI",
                path=root / "AURVO_OS" / "ai",
                kind=BuildKind.PYTHON,
                quality=QualitySpec(required_paths=("__init__.py",)),
            ),
            Component(
                name="Aurvo Dashboard",
                path=root / "AURVO_OS" / "ui",
                kind=BuildKind.NODE,
                quality=QualitySpec(forbid_empty=True),
            ),
            Component(
                name="Maestro bootstrap",
                path=root / "aurvo OS código ",
                kind=BuildKind.SHELL,
                quality=QualitySpec(forbid_empty=True),
            ),
        ]
        return Manifest(components)

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
