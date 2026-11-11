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
