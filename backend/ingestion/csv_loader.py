import csv
from pathlib import Path

from backend.schemas import LapRecord
from .validation import REQUIRED_COLUMNS, CsvValidationError, validate_lap_rows


def load_laps_csv(path: str | Path) -> list[LapRecord]:
    csv_path = Path(path)
    with csv_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise CsvValidationError(["CSV file is empty or has no header"])

        missing = sorted(REQUIRED_COLUMNS - set(reader.fieldnames))
        if missing:
            raise CsvValidationError([f"missing required columns: {', '.join(missing)}"])

        return validate_lap_rows(reader)
