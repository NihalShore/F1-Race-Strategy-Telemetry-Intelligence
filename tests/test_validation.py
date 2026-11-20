import pytest

from backend.ingestion.validation import CsvValidationError, validate_lap_rows


def valid_row():
    return {
        "session_id": "race-1",
        "driver": "VER",
        "lap_number": "1",
        "lap_time_s": "84.2",
        "sector1_s": "",
        "sector2_s": "31.1",
        "sector3_s": "26.0",
        "compound": "medium",
        "tyre_age_laps": "1",
    }


def test_valid_rows_normalize_driver_and_compound():
    records = validate_lap_rows([valid_row()])

    assert records[0].driver == "VER"
    assert records[0].compound == "MEDIUM"
    assert records[0].sector1_s is None
    assert records[0].tyre_age_laps == 1


@pytest.mark.parametrize(
    "field,value",
    [
        ("session_id", ""),
        ("driver", " "),
        ("lap_number", "0"),
        ("lap_number", "one"),
        ("lap_number", "1.5"),
        ("lap_time_s", ""),
        ("lap_time_s", "0"),
        ("lap_time_s", "fast"),
        ("lap_time_s", "nan"),
        ("lap_time_s", "inf"),
        ("sector2_s", "-1"),
        ("sector2_s", "nan"),
        ("tyre_age_laps", "-2"),
        ("tyre_age_laps", "1.5"),
    ],
)
def test_invalid_values_are_rejected(field, value):
    row = valid_row()
    row[field] = value

    with pytest.raises(CsvValidationError):
        validate_lap_rows([row])


def test_unknown_columns_are_rejected():
    row = valid_row()
    row["fuel_load_kg"] = "50"

    with pytest.raises(CsvValidationError, match="unexpected columns: fuel_load_kg"):
        validate_lap_rows([row])


def test_duplicate_laps_are_rejected():
    row = valid_row()

    with pytest.raises(CsvValidationError, match="duplicate lap"):
        validate_lap_rows([row, row])


def test_blank_rows_are_ignored():
    assert validate_lap_rows([{}, {"session_id": "", "driver": ""}, valid_row()]) == [
        validate_lap_rows([valid_row()])[0]
    ]


def test_boolean_numeric_values_are_rejected():
    row = valid_row()
    row["lap_time_s"] = True

    with pytest.raises(CsvValidationError, match="lap_time_s must be a number"):
        validate_lap_rows([row])


def test_zero_tyre_age_is_valid():
    row = valid_row()
    row["tyre_age_laps"] = "0"

    assert validate_lap_rows([row])[0].tyre_age_laps == 0


def test_sector_times_must_match_lap_time():
    row = valid_row()
    row.update(
        {
            "lap_time_s": "84.2",
            "sector1_s": "27.0",
            "sector2_s": "31.1",
            "sector3_s": "26.5",
        }
    )

    with pytest.raises(CsvValidationError, match="does not match lap_time_s"):
        validate_lap_rows([row])


def test_sector_time_rounding_difference_is_allowed():
    row = valid_row()
    row.update(
        {
            "lap_time_s": "84.2",
            "sector1_s": "27.1",
            "sector2_s": "31.1",
            "sector3_s": "26.05",
        }
    )

    records = validate_lap_rows([row])

    assert records[0].lap_time_s == 84.2


def test_sector_consistency_is_not_checked_when_a_sector_is_missing():
    row = valid_row()
    row.update(
        {
            "lap_time_s": "84.2",
            "sector1_s": "",
            "sector2_s": "31.1",
            "sector3_s": "26.5",
        }
    )

    assert len(validate_lap_rows([row])) == 1
