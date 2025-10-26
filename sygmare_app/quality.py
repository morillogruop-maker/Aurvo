from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .models import BuildKind, Component


@dataclass
class QualityFinding:
    level: str
    message: str


@dataclass
class QualityReport:
    component: Component
    findings: List[QualityFinding] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.findings.append(QualityFinding("error", message))

    def add_warning(self, message: str) -> None:
        self.findings.append(QualityFinding("warning", message))

    @property
    def passed(self) -> bool:
        return all(f.level != "error" for f in self.findings)

    def formatted(self) -> str:
        if not self.findings:
            return "OK"
        return "\n".join(f"[{f.level.upper()}] {f.message}" for f in self.findings)


class StrictQualityInspector:
    """Strict validation stage prior to orchestration."""

    def evaluate(self, component: Component) -> QualityReport:
        report = QualityReport(component)
        path = component.path

        if not path.exists():
            report.add_error(f"La ruta {path} no existe.")
            return report

        target_for_spec = path if path.is_dir() else path.parent

        if component.kind == BuildKind.PYTHON:
            if path.is_file():
                python_files = [path] if path.suffix == ".py" else []
            else:
                python_files = list(path.rglob("*.py"))
            if not python_files:
                report.add_error("No se detectaron archivos Python.")
        elif component.kind == BuildKind.NODE:
            package_json = path / "package.json"
            if not package_json.exists():
                report.add_error("Falta package.json para construir el proyecto Node.")
        elif component.kind == BuildKind.SHELL:
            if not path.is_file():
                report.add_error("El componente shell debe apuntar a un archivo ejecutable.")
            elif path.stat().st_size == 0:
                report.add_error("El script shell está vacío.")

        spec = component.quality
        if spec:
            for required in spec.materialized_paths(target_for_spec):
                if not required.exists():
                    report.add_error(f"Falta recurso requerido: {required}.")
            if spec.forbid_empty and component.kind != BuildKind.SHELL:
                if path.is_dir() and not any(path.iterdir()):
                    report.add_error("El directorio del componente está vacío.")
                if path.is_file() and path.stat().st_size == 0:
                    report.add_error("El archivo del componente está vacío.")

        return report


__all__ = [
    "QualityFinding",
    "QualityReport",
    "StrictQualityInspector",
]
