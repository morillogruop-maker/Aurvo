from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Sequence

from .models import BuildRecord
from .statuses import BuildStatus


@dataclass(frozen=True)
class Totals:
    counts: dict[BuildStatus, int]

    @classmethod
    def from_records(cls, records: Iterable[BuildRecord]) -> "Totals":
        counter = Counter(record.status for record in records)
        counts = {status: counter.get(status, 0) for status in BuildStatus}
        return cls(counts)

    def to_dict(self) -> dict[str, int]:
        return {status.value: count for status, count in self.counts.items()}


def render_table(records: Sequence[BuildRecord]) -> str:
    totals = Totals.from_records(records)
    lines: list[str] = []
    lines.append("Resumen detallado:")
    lines.append(f"{'Estado':<18}{'Duración':>10}  Nombre")
    lines.append(f"{'-' * 18}{'-' * 10}  {'-' * 40}")

    for record in records:
        duration = f"{record.duration:.2f}s" if record.duration else "-"
        lines.append(
            f"{record.status.icon()} {record.status.label():<16}{duration:>10}  {record.component.name}"
        )
        if record.details:
            for detail_line in record.details.splitlines():
                lines.append(f"    ↳ {detail_line}")

    lines.append("")
    lines.append("Totales:")
    for status in BuildStatus:
        lines.append(
            f"  {status.icon()} {status.label():<16}: {totals.counts[status]}"
        )
    return "\n".join(lines)


def render_json(records: Sequence[BuildRecord]) -> str:
    payload = {
        "records": [
            {
                "name": record.component.name,
                "path": str(record.component.path),
                "kind": record.component.kind.value,
                "status": record.status.value,
                "status_label": record.status.label(),
                "duration": record.duration,
                "details": record.details,
            }
            for record in records
        ],
        "totals": Totals.from_records(records).to_dict(),
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


__all__ = ["Totals", "render_table", "render_json"]
