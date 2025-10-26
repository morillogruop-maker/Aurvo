from enum import Enum


class BuildStatus(str, Enum):
    BUILT = "built"
    SKIPPED = "skipped"
    MISSING = "missing"
    FAILED = "failed"
    QUALITY_FAILED = "quality_failed"

    def icon(self) -> str:
        return {
            BuildStatus.BUILT: "✔",
            BuildStatus.SKIPPED: "➖",
            BuildStatus.MISSING: "✖",
            BuildStatus.FAILED: "✖",
            BuildStatus.QUALITY_FAILED: "✖",
        }[self]

    def label(self) -> str:
        return {
            BuildStatus.BUILT: "Construido",
            BuildStatus.SKIPPED: "Omitido",
            BuildStatus.MISSING: "No encontrado",
            BuildStatus.FAILED: "Falló",
            BuildStatus.QUALITY_FAILED: "Calidad fallida",
        }[self]


__all__ = ["BuildStatus"]
