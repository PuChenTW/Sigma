from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, TypeAlias

from pydantic import BaseModel

from studio_schemas import (
    ActivityEvent,
    DecisionProposal,
    Evidence,
    EvidenceCitation,
    InvestmentDecision,
    ResearchArtifact,
    ResearchProject,
    ResearchTask,
    Thesis,
)

TableName: TypeAlias = Literal[
    "activity_events",
    "artifacts",
    "citations",
    "decisions",
    "evidence",
    "projects",
    "proposals",
    "tasks",
    "theses",
]

TABLE_MODELS: dict[TableName, type[BaseModel]] = {
    "activity_events": ActivityEvent,
    "artifacts": ResearchArtifact,
    "citations": EvidenceCitation,
    "decisions": InvestmentDecision,
    "evidence": Evidence,
    "projects": ResearchProject,
    "proposals": DecisionProposal,
    "tasks": ResearchTask,
    "theses": Thesis,
}


def empty_database() -> dict[str, list[dict]]:
    return {table: [] for table in TABLE_MODELS}


class JsonStore:
    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write(empty_database())

    def create[T: BaseModel](self, table: TableName, record: T) -> T:
        data = self._read()
        records = data[table]
        record_id = getattr(record, "id")
        if any(item["id"] == record_id for item in records):
            raise ValueError(f"{table} record already exists: {record_id}")
        records.append(record.model_dump(mode="json"))
        self._write(data)
        return record

    def get[T: BaseModel](self, table: TableName, record_id: str) -> T | None:
        model = TABLE_MODELS[table]
        data = self._read()
        for item in data[table]:
            if item["id"] == record_id:
                return model.model_validate(item)
        return None

    def list[T: BaseModel](self, table: TableName) -> list[T]:
        model = TABLE_MODELS[table]
        data = self._read()
        return [model.model_validate(item) for item in data[table]]

    def update[T: BaseModel](self, table: TableName, record_id: str, changes: dict) -> T:
        model = TABLE_MODELS[table]
        data = self._read()
        for index, item in enumerate(data[table]):
            if item["id"] != record_id:
                continue
            updated = model.model_validate({**item, **changes})
            data[table][index] = updated.model_dump(mode="json")
            self._write(data)
            return updated
        raise KeyError(f"{table} record not found: {record_id}")

    def _read(self) -> dict[str, list[dict]]:
        with self.path.open("r", encoding="utf-8") as f:
            raw = json.load(f)

        data = empty_database()
        for table in TABLE_MODELS:
            data[table] = list(raw.get(table, []))
        return data

    def _write(self, data: dict[str, list[dict]]) -> None:
        temp_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        with temp_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        temp_path.replace(self.path)
