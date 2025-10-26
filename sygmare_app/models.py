from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Sequence

from .statuses import BuildStatus


class BuildKind(str, Enum):
    """Canonical build kinds supported by the orchestration engine."""

    PYTHON = "python"
    NODE = "node"
    SHELL = "shell"


@dataclass(frozen=True)
class QualitySpec:
    """Declarative description of quality gates for a component."""

    required_paths: Sequence[str] = ()
    forbid_empty: bool = True
    description: Optional[str] = None

    def materialized_paths(self, base_path: Path) -> List[Path]:
        return [base_path / rel for rel in self.required_paths]


@dataclass(frozen=True)
class Component:
    """Represents a buildable unit in the ecosystem."""

    name: str
    path: Path
    kind: BuildKind
    build_commands: Sequence[Sequence[str]] = ()
    dependencies: Sequence[str] = ()
    quality: Optional[QualitySpec] = None

    def normalized_commands(self) -> List[List[str]]:
        return [list(cmd) for cmd in self.build_commands]


@dataclass(frozen=True)
class Manifest:
    components: Sequence[Component] = field(default_factory=list)

    def by_name(self) -> dict[str, Component]:
        return {component.name: component for component in self.components}


@dataclass(frozen=True)
class BuildRecord:
    component: Component
    status: BuildStatus
    details: Optional[str] = None
    duration: float | None = None


class BuildError(RuntimeError):
    pass
