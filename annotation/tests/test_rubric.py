"""Tests for annotation rubric validation."""

import pytest
from annotation.rubric import (
    validate_annotation_row,
    create_annotation_schema,
    VALID_ANSWERS,
    VALID_CONFIDENCE,
    VALID_PLAUSIBILITY,
    SHORTCUT_FLAGS,
)


class TestRubricValidation:
    """Tests for validate_annotation_row function."""

    def test_valid_annotation_row_passes(self):
        """A complete valid annotation row should pass validation."""
        row = {
            "validation_id": "abc123",
            "language": "English",
            "proverb": "Actions speak louder",
            "option_A": "Actions speak louder than words",
            "option_B": "Talk is cheap",
            "option_C": "Actions speak softly",
            "option_D": "Words are meaningless",
            "answer": "A",
            "plausibility_A": 1,
            "plausibility_B": 3,
            "plausibility_C": 2,
            "plausibility_D": 2,
            "shortcut_flag": "none",
            "confidence": 3,
        }
        is_valid, errors = validate_annotation_row(row)
        assert is_valid is True
        assert len(errors) == 0

    def test_invalid_answer_letter_fails(self):
        """An invalid answer letter should fail validation."""
        row = {
            "validation_id": "abc123",
            "language": "English",
            "answer": "E",
            "confidence": 2,
            "plausibility_A": 1,
            "plausibility_B": 1,
            "plausibility_C": 1,
            "plausibility_D": 1,
        }
        is_valid, errors = validate_annotation_row(row)
        assert is_valid is False
        assert any("Invalid answer" in e for e in errors)

    def test_out_of_range_confidence_fails(self):
        """Confidence outside 1-3 should fail validation."""
        row = {
            "validation_id": "abc123",
            "language": "English",
            "answer": "A",
            "confidence": 4,
            "plausibility_A": 1,
            "plausibility_B": 1,
            "plausibility_C": 1,
            "plausibility_D": 1,
        }
        is_valid, errors = validate_annotation_row(row)
        assert is_valid is False
        assert any("Invalid confidence" in e for e in errors)

    def test_invalid_plausibility_fails(self):
        """Plausibility outside 1-5 should fail validation."""
        row = {
            "validation_id": "abc123",
            "language": "English",
            "answer": "A",
            "confidence": 2,
            "plausibility_A": 6,
            "plausibility_B": 1,
            "plausibility_C": 1,
            "plausibility_D": 1,
        }
        is_valid, errors = validate_annotation_row(row)
        assert is_valid is False
        assert any("Invalid plausibility_A" in e for e in errors)

    def test_missing_required_fields_fails(self):
        """Missing required fields should fail validation."""
        row = {
            "validation_id": "abc123",
        }
        is_valid, errors = validate_annotation_row(row)
        assert is_valid is False
        assert any("Missing required field" in e for e in errors)


class TestAnnotationSchema:
    """Tests for create_annotation_schema function."""

    def test_schema_has_required_fields(self):
        """Schema should include all required fields."""
        schema = create_annotation_schema()
        required_fields = ["validation_id", "language", "proverb", "answer", "confidence"]
        for field in required_fields:
            assert field in schema
            assert schema[field]["required"] is True


class TestConstants:
    """Tests for constant definitions."""

    def test_valid_answers(self):
        assert set(VALID_ANSWERS) == {"A", "B", "C", "D"}

    def test_valid_confidence(self):
        assert VALID_CONFIDENCE == [1, 2, 3]

    def test_valid_plausibility_range(self):
        assert list(VALID_PLAUSIBILITY) == [1, 2, 3, 4, 5]

    def test_shortcut_flags_include_none(self):
        assert "none" in SHORTCUT_FLAGS