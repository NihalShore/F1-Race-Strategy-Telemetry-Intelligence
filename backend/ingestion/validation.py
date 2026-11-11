from __future__ import annotations

import math
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


def _clean_value(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _optional_float(value: object, field: str, row_number: int, errors: list[str]):
    if isinstance(value, bool):
        errors.append(f"row {row_number}: {field} must be a number")
        return None

    cleaned = _clean_value(value)
    if cleaned == "":
        return None
    try:
        number = float(cleaned)
    except (TypeError, ValueError):
        errors.append(f"row {row_number}: {field} must be a number")
        return None
    if not math.isfinite(number) or number <= 0:
        errors.append(f"row {row_number}: {field} must be greater than zero")
        return None
    return number


def validate_lap_rows(rows: Iterable[dict[str, str]]) -> list[LapRecord]:
    records: list[LapRecord] = []
    errors: list[str] = []
    seen: set[tuple[str, str, int]] = set()

    for row_number, row in enumerate(rows, start=2):
        if row is None:
            continue

        if not any(_clean_value(value) for value in row.values()):
            continue

        session_id = _clean_value(row.get("session_id", ""))
        driver = _clean_value(row.get("driver", "")).upper()
        if not session_id:
            errors.append(f"row {row_number}: session_id is required")
        if not driver:
            errors.append(f"row {row_number}: driver is required")

        raw_lap_number = row.get("lap_number", "")
        if isinstance(raw_lap_number, bool):
            errors.append(f"row {row_number}: lap_number must be a positive integer")
            lap_number = 0
        else:
            raw_lap_number = _clean_value(raw_lap_number)
            if raw_lap_number == "":
                errors.append(f"row {row_number}: lap_number must be a positive integer")
                lap_number = 0
            else:
                try:
                    lap_number = int(raw_lap_number)
                    if lap_number < 1:
                        raise ValueError
                except (TypeError, ValueError):
                    errors.append(f"row {row_number}: lap_number must be a positive integer")
                    lap_number = 0

        raw_lap_time = row.get("lap_time_s", "")
        if isinstance(raw_lap_time, bool):
            errors.append(f"row {row_number}: lap_time_s must be greater than zero")
            lap_time_s = 0.0
        else:
            raw_lap_time = _clean_value(raw_lap_time)
            if raw_lap_time == "":
                errors.append(f"row {row_number}: lap_time_s must be greater than zero")
                lap_time_s = 0.0
            else:
                try:
                    lap_time_s = float(raw_lap_time)
                    if not math.isfinite(lap_time_s) or lap_time_s <= 0:
                        raise ValueError
                except (TypeError, ValueError):
                    errors.append(f"row {row_number}: lap_time_s must be greater than zero")
                    lap_time_s = 0.0

        sectors = [
            _optional_float(row.get(f"sector{i}_s", ""), f"sector{i}_s", row_number, errors)
            for i in range(1, 4)
        ]

        raw_age = row.get("tyre_age_laps", "")
        tyre_age = None
        if isinstance(raw_age, bool):
            errors.append(f"row {row_number}: tyre_age_laps must be a non-negative integer")
        else:
            raw_age = _clean_value(raw_age)
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

        compound = _clean_value(row.get("compound", "")).upper() or None

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
                    compound=compound,
                    tyre_age_laps=tyre_age,
                )
            )

    if errors:
        raise CsvValidationError(errors)
    return records
