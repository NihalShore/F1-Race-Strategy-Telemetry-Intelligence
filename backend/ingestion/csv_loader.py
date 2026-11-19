import csv
from pathlib import Path

from backend.schemas import LapRecord
from .validation import (
    ALLOWED_COLUMNS,
    REQUIRED_COLUMNS,
    CsvValidationError,
    validate_lap_rows,
)


def load_laps_csv(path: str | Path) -> list[LapRecord]:
    csv_path = Path(path)
    with csv_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, strict=True)

        try:
            if reader.fieldnames is None:
                raise CsvValidationError(["CSV file is empty or has no header"])

            fieldnames = [
                field.strip() if field is not None else ""
                for field in reader.fieldnames
            ]
            if any(not field for field in fieldnames):
                raise CsvValidationError(["CSV header contains an empty column name"])
            if len(fieldnames) != len(set(fieldnames)):
                raise CsvValidationError(["CSV header contains duplicate column names"])

            reader.fieldnames = fieldnames
            missing = sorted(REQUIRED_COLUMNS - set(fieldnames))
            unexpected = sorted(set(fieldnames) - ALLOWED_COLUMNS)
            header_errors = []
            if missing:
                header_errors.append(
                    f"missing required columns: {', '.join(missing)}"
                )
            if unexpected:
                header_errors.append(
                    f"unexpected columns: {', '.join(unexpected)}"
                )
            if header_errors:
                raise CsvValidationError(header_errors)

            return validate_lap_rows(reader)
        except csv.Error as exc:
            raise CsvValidationError([f"could not parse CSV: {exc}"]) from exc
        except UnicodeDecodeError as exc:
            raise CsvValidationError(["CSV file must use UTF-8 encoding"]) from exc
