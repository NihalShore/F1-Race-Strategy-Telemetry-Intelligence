import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from backend.ingestion.validation import (
    OPTIONAL_COLUMNS,
    REQUIRED_COLUMNS,
)


SCHEMA_PATH = (
    Path(__file__).parents[1] / "data" / "schemas" / "laps.csv.schema.json"
)


def load_lap_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_lap_schema_is_a_valid_json_schema_document():
    schema = load_lap_schema()

    Draft202012Validator.check_schema(schema)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == REQUIRED_COLUMNS
    assert set(schema["properties"]) == REQUIRED_COLUMNS | OPTIONAL_COLUMNS


def test_lap_schema_matches_ingestion_column_contract():
    properties = load_lap_schema()["properties"]

    assert properties["session_id"]["type"] == "string"
    assert properties["driver"]["type"] == "string"
    assert properties["lap_number"]["type"] == "integer"
    assert properties["lap_number"]["minimum"] == 1
    assert properties["lap_time_s"]["type"] == "number"
    assert properties["lap_time_s"]["exclusiveMinimum"] == 0

    for field in ("sector1_s", "sector2_s", "sector3_s"):
        assert properties[field]["type"] == ["number", "null"]
        assert properties[field]["exclusiveMinimum"] == 0

    assert properties["compound"]["type"] == ["string", "null"]
    assert properties["tyre_age_laps"]["type"] == ["integer", "null"]
    assert properties["tyre_age_laps"]["minimum"] == 0


def test_normalized_lap_record_validates_against_schema():
    validator = Draft202012Validator(load_lap_schema())
    record = {
        "session_id": "race-1",
        "driver": "VER",
        "lap_number": 1,
        "lap_time_s": 84.2,
        "sector1_s": None,
        "sector2_s": 31.1,
        "sector3_s": 26.0,
        "compound": "MEDIUM",
        "tyre_age_laps": 1,
    }

    validator.validate(record)


@pytest.mark.parametrize(
    "field,value",
    [
        ("session_id", ""),
        ("session_id", "   "),
        ("driver", ""),
        ("driver", "\t "),
        ("compound", ""),
        ("compound", "   "),
    ],
)
def test_schema_rejects_blank_string_values(field, value):
    validator = Draft202012Validator(load_lap_schema())
    record = {
        "session_id": "race-1",
        "driver": "VER",
        "lap_number": 1,
        "lap_time_s": 84.2,
        "compound": "MEDIUM",
    }
    record[field] = value

    with pytest.raises(ValidationError):
        validator.validate(record)
