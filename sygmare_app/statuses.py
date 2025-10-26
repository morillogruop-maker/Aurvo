from enum import Enum


class BuildStatus(str, Enum):
    BUILT = "built"
    SKIPPED = "skipped"
    MISSING = "missing"
    FAILED = "failed"
    QUALITY_FAILED = "quality_failed"


__all__ = ["BuildStatus"]
