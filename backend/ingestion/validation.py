from __future__ import annotations

import math
from collections.abc import Iterable, Mapping

from backend.schemas import LapRecord


REQUIRED_COLUMNS = {"session_id", "driver", "lap_number", "lap_time_s"}


class CsvValidationError(ValueError):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("CSV validation failed:\n" + "\n".join(errors))


def _clean_value(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _parse_float(
    value: object,
    field: str,
    row_number: int,
    errors: list[str],
    *,
    optional: bool = False,
) -> float | None:
    if isinstance(value, bool):
        errors.append(f"row {row_number}: {field} must be a number")
        return None

    cleaned = _clean_value(value)
    if not cleaned and optional:
        return None
    if not cleaned:
        errors.append(f"row {row_number}: {field} is required")
        return None

    try:
        number = float(cleaned)
    except ValueError:
        errors.append(f"row {row_number}: {field} must be a number")
        return None

    if not math.isfinite(number) or number <= 0:
        errors.append(f"row {row_number}: {field} must be greater than zero")
        return None
    return number


def _parse_integer(
    value: object,
    field: str,
    row_number: int,
    errors: list[str],
    *,
    minimum: int,
) -> int | None:
    if isinstance(value, bool):
        errors.append(f"row {row_number}: {field} must be an integer of at least {minimum}")
        return None

    cleaned = _clean_value(value)
    try:
        number = int(cleaned)
    except (TypeError, ValueError):
        errors.append(f"row {row_number}: {field} must be an integer of at least {minimum}")
        return None

    if number < minimum:
        errors.append(f"row {row_number}: {field} must be an integer of at least {minimum}")
        return None
    return number


def validate_lap_rows(rows: Iterable[Mapping[str, object]]) -> list[LapRecord]:
    records: list[LapRecord] = []
    errors: list[str] = []
    seen: set[tuple[str, str, int]] = set()

    for row_number, row in enumerate(rows, start=2):
        if row is None or not any(_clean_value(value) for value in row.values()):
            continue

        if None in row:
            errors.append(f"row {row_number}: too many fields")
            continue

        session_id = _clean_value(row.get("session_id"))
        driver = _clean_value(row.get("driver")).upper()
        if not session_id:
            errors.append(f"row {row_number}: session_id is required")
        if not driver:
            errors.append(f"row {row_number}: driver is required")

        lap_number = _parse_integer(
            row.get("lap_number"), "lap_number", row_number, errors, minimum=1
        )
        lap_time_s = _parse_float(
            row.get("lap_time_s"), "lap_time_s", row_number, errors
        )
        sectors = [
            _parse_float(
                row.get(f"sector{i}_s"),
                f"sector{i}_s",
                row_number,
                errors,
                optional=True,
            )
            for i in range(1, 4)
        ]
        tyre_age = _parse_integer(
            row.get("tyre_age_laps"),
            "tyre_age_laps",
            row_number,
            errors,
            minimum=0,
        ) if _clean_value(row.get("tyre_age_laps")) else None

        if session_id and driver and lap_number is not None:
            key = (session_id, driver, lap_number)
            if key in seen:
                errors.append(
                    f"row {row_number}: duplicate lap for {session_id}/{driver}/lap {lap_number}"
                )
            seen.add(key)

        if (
            session_id
            and driver
            and lap_number is not None
            and lap_time_s is not None
        ):
            records.append(
                LapRecord(
                    session_id=session_id,
                    driver=driver,
                    lap_number=lap_number,
                    lap_time_s=lap_time_s,
                    sector1_s=sectors[0],
                    sector2_s=sectors[1],
                    sector3_s=sectors[2],
                    compound=_clean_value(row.get("compound")).upper() or None,
                    tyre_age_laps=tyre_age,
                )
            )

    if errors:
        raise CsvValidationError(errors)
    return records
