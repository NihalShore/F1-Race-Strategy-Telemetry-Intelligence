from pathlib import Path

import pytest

from backend.ingestion.csv_loader import load_laps_csv
from backend.ingestion.validation import CsvValidationError


ROOT = Path(__file__).resolve().parents[1]


def test_load_sample_race():
    laps = load_laps_csv(ROOT / "data/samples/sample_race.csv")

    assert len(laps) == 4
    assert laps[0].driver == "VER"
    assert laps[0].lap_time_s == 84.231


def test_missing_required_column_is_rejected(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("session_id,driver,lap_number\nr1,VER,1\n", encoding="utf-8")

    with pytest.raises(CsvValidationError, match="missing required columns"):
        load_laps_csv(path)


def test_header_only_file_returns_no_laps(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text(
        "session_id,driver,lap_number,lap_time_s\n", encoding="utf-8"
    )

    assert load_laps_csv(path) == []


def test_whitespace_in_headers_is_ignored(tmp_path):
    path = tmp_path / "spaced.csv"
    path.write_text(
        " session_id , driver , lap_number , lap_time_s \nr1,ver,1,84.2\n",
        encoding="utf-8",
    )

    laps = load_laps_csv(path)

    assert len(laps) == 1
    assert laps[0].driver == "VER"


@pytest.mark.parametrize(
    "header",
    [
        "session_id,driver,lap_number,lap_time_s,lap_time_s",
        "session_id,driver,lap_number,lap_time_s, ",
    ],
)
def test_invalid_headers_are_rejected(tmp_path, header):
    path = tmp_path / "bad_header.csv"
    path.write_text(header + "\nr1,VER,1,84.2,84.2\n", encoding="utf-8")

    with pytest.raises(CsvValidationError):
        load_laps_csv(path)


def test_extra_csv_fields_are_rejected(tmp_path):
    path = tmp_path / "extra.csv"
    path.write_text(
        "session_id,driver,lap_number,lap_time_s\nr1,VER,1,84.2,unexpected\n",
        encoding="utf-8",
    )

    with pytest.raises(CsvValidationError, match="too many fields"):
        load_laps_csv(path)


def test_empty_extra_csv_field_is_rejected(tmp_path):
    path = tmp_path / "extra_empty.csv"
    path.write_text(
        "session_id,driver,lap_number,lap_time_s\\nr1,VER,1,84.2,\\n",
        encoding="utf-8",
    )

    with pytest.raises(CsvValidationError, match="too many fields"):
        load_laps_csv(path)


def test_blank_rows_are_ignored(tmp_path):
    path = tmp_path / "blank.csv"
    path.write_text(
        "session_id,driver,lap_number,lap_time_s\n\nr1,VER,1,84.2\n\n",
        encoding="utf-8",
    )

    assert len(load_laps_csv(path)) == 1

def test_malformed_quoted_csv_is_rejected(tmp_path):
    path = tmp_path / "malformed.csv"
    path.write_text(
        'session_id,driver,lap_number,lap_time_s\n"r1,VER,1,84.2\n',
        encoding="utf-8",
    )

    with pytest.raises(CsvValidationError, match="could not parse CSV"):
        load_laps_csv(path)

def test_malformed_quoted_header_is_rejected(tmp_path):
    path = tmp_path / "malformed_header.csv"
    path.write_text(
        '"session_id,driver,lap_number,lap_time_s\nr1,VER,1,84.2\n',
        encoding="utf-8",
    )

    with pytest.raises(CsvValidationError, match="could not parse CSV"):
        load_laps_csv(path)
