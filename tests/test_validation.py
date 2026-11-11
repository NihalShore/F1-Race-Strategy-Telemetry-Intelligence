import pytest

from backend.ingestion.validation import CsvValidationError, validate_lap_rows


def test_valid_rows_normalize_driver_and_compound():
    records = validate_lap_rows([{
        "session_id": "race-1",
        "driver": "ver",
        "lap_number": "1",
        "lap_time_s": "84.2",
        "sector1_s": "",
        "sector2_s": "31.1",
        "sector3_s": "26.0",
        "compound": "medium",
        "tyre_age_laps": "1",
    }])

    assert records[0].driver == "VER"
    assert records[0].compound == "MEDIUM"
    assert records[0].sector1_s is None
    assert records[0].tyre_age_laps == 1


@pytest.mark.parametrize("field,value", [
    ("lap_number", "0"),
    ("lap_number", "one"),
    ("lap_time_s", "0"),
    ("lap_time_s", "fast"),
    ("sector2_s", "-1"),
    ("tyre_age_laps", "-2"),
])
def test_invalid_values_are_rejected(field, value):
    row = {
        "session_id": "race-1",
        "driver": "VER",
        "lap_number": "1",
        "lap_time_s": "84.2",
        "sector1_s": "",
        "sector2_s": "",
        "sector3_s": "",
        "compound": "",
        "tyre_age_laps": "",
    }
    row[field] = value

    with pytest.raises(CsvValidationError):
        validate_lap_rows([row])


def test_duplicate_laps_are_rejected():
    row = {
        "session_id": "race-1", "driver": "VER",
        "lap_number": "1", "lap_time_s": "84.2",
    }
    with pytest.raises(CsvValidationError, match="duplicate lap"):
        validate_lap_rows([row, row])
