from __future__ import annotations

from typing import Iterable

from backend.schemas import LapRecord


REQUIRED_COLUMNS = {"session_id", "driver", "lap_number", "lap_time_s"}
OPTIONAL_COLUMNS = {
    "sector1_s", "sector2_s", "sector3_s", "compound", "tyre_age_laps"
}


class CsvValidationError(ValueError):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("CSV validation failed:\n" + "\n".join(errors))


def _optional_float(value: str, field: str, row_number: int, errors: list[str]):
    if value.strip() == "":
        return None
    try:
        number = float(value)
    except ValueError:
        errors.append(f"row {row_number}: {field} must be a number")
        return None
    if number <= 0:
        errors.append(f"row {row_number}: {field} must be greater than zero")
        return None
    return number


def validate_lap_rows(rows: Iterable[dict[str, str]]) -> list[LapRecord]:
    records: list[LapRecord] = []
    errors: list[str] = []
    seen: set[tuple[str, str, int]] = set()

    for row_number, row in enumerate(rows, start=2):
        session_id = row.get("session_id", "").strip()
        driver = row.get("driver", "").strip().upper()
        if not session_id:
            errors.append(f"row {row_number}: session_id is required")
        if not driver:
            errors.append(f"row {row_number}: driver is required")

        try:
            lap_number = int(row.get("lap_number", ""))
            if lap_number < 1:
                raise ValueError
        except (TypeError, ValueError):
            errors.append(f"row {row_number}: lap_number must be a positive integer")
            lap_number = 0

        try:
            lap_time_s = float(row.get("lap_time_s", ""))
            if lap_time_s <= 0:
                raise ValueError
        except (TypeError, ValueError):
            errors.append(f"row {row_number}: lap_time_s must be greater than zero")
            lap_time_s = 0.0

        sectors = [
            _optional_float(row.get(f"sector{i}_s", ""), f"sector{i}_s", row_number, errors)
            for i in range(1, 4)
        ]

        raw_age = row.get("tyre_age_laps", "").strip()
        tyre_age = None
        if raw_age:
            try:
                tyre_age = int(raw_age)
                if tyre_age < 0:
                    raise ValueError
            except ValueError:
                errors.append(f"row {row_number}: tyre_age_laps must be a non-negative integer")
                tyre_age = None

        key = (session_id, driver, lap_number)
        if key in seen:
            errors.append(
                f"row {row_number}: duplicate lap for {session_id}/{driver}/lap {lap_number}"
            )
        seen.add(key)

        if session_id and driver and lap_number > 0 and lap_time_s > 0:
            records.append(
                LapRecord(
                    session_id=session_id,
                    driver=driver,
                    lap_number=lap_number,
                    lap_time_s=lap_time_s,
                    sector1_s=sectors[0],
                    sector2_s=sectors[1],
                    sector3_s=sectors[2],
                    compound=(row.get("compound") or "").strip().upper() or None,
                    tyre_age_laps=tyre_age,
                )
            )

    if errors:
        raise CsvValidationError(errors)
    return records
