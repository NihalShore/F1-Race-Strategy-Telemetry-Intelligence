import json
from pathlib import Path

from backend.ingestion.validation import (
    OPTIONAL_COLUMNS,
    REQUIRED_COLUMNS,
)


SCHEMA_PATH = (
    Path(__file__).parents[1] / "data" / "schemas" / "laps.csv.schema.json"
)


def test_lap_schema_is_a_valid_json_schema_document():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == REQUIRED_COLUMNS
    assert set(schema["properties"]) == REQUIRED_COLUMNS | OPTIONAL_COLUMNS


def test_lap_schema_matches_ingestion_column_contract():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    properties = schema["properties"]

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
