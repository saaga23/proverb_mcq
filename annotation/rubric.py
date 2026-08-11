"""Annotation rubric and validation schema for ProverbGap MCQ human validation."""

from typing import Dict, List, Tuple, Any

# All annotation fields for the CSV output
ANNOTATION_FIELDS: List[str] = [
    "validation_id",
    "language",
    "proverb",
    "option_A",
    "option_B",
    "option_C",
    "option_D",
    "answer",
    "plausibility_A",
    "plausibility_B",
    "plausibility_C",
    "plausibility_D",
    "shortcut_flag",
    "confidence",
]

# Valid answer letters
VALID_ANSWERS: List[str] = ["A", "B", "C", "D"]

# Valid confidence values (1-3)
VALID_CONFIDENCE: List[int] = [1, 2, 3]

# Valid plausibility values (1-5)
VALID_PLAUSIBILITY: range = range(1, 6)

# Valid shortcut flags
SHORTCUT_FLAGS: List[str] = [
    "same_structure",
    "length_outlier",
    "semantic_echo",
    "generic_idiom",
    "cultural_mismatch",
    "none",
]


def validate_annotation_row(row: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a single annotation row.

    Args:
        row: Dictionary containing annotation fields.

    Returns:
        Tuple of (is_valid, list of error messages).
    """
    errors: List[str] = []

    # Required fields
    required_fields = {
        "validation_id",
        "language",
        "answer",
        "confidence",
    }
    for field in required_fields:
        if field not in row or row[field] is None or row[field] == "":
            errors.append(f"Missing required field: {field}")

    # Validate answer letter
    if "answer" in row and row["answer"]:
        if row["answer"].upper() not in VALID_ANSWERS:
            errors.append(f"Invalid answer: {row['answer']}. Must be one of {VALID_ANSWERS}")

    # Validate confidence
    if "confidence" in row and row["confidence"]:
        try:
            conf = int(row["confidence"])
            if conf not in VALID_CONFIDENCE:
                errors.append(f"Invalid confidence: {conf}. Must be one of {VALID_CONFIDENCE}")
        except (ValueError, TypeError):
            errors.append(f"Invalid confidence type: {row['confidence']}")

    # Validate plausibility ratings
    for opt in ["A", "B", "C", "D"]:
        field = f"plausibility_{opt}"
        if field in row and row[field]:
            try:
                plaus = int(row[field])
                if plaus not in VALID_PLAUSIBILITY:
                    errors.append(f"Invalid {field}: {plaus}. Must be in {list(VALID_PLAUSIBILITY)}")
            except (ValueError, TypeError):
                errors.append(f"Invalid {field} type: {row[field]}")

    # Validate shortcut flag
    if "shortcut_flag" in row and row["shortcut_flag"]:
        # Allow multiple flags separated by semicolon
        flags = str(row["shortcut_flag"]).split(";")
        flags = [f.strip() for f in flags if f.strip()]
        for flag in flags:
            if flag not in SHORTCUT_FLAGS:
                errors.append(f"Invalid shortcut flag: {flag}. Must be one of {SHORTCUT_FLAGS}")

    return len(errors) == 0, errors


def create_annotation_schema() -> Dict[str, Any]:
    """Create a schema dictionary suitable for pandas/CSV validation.

    Returns:
        Dictionary mapping field names to their expected types and constraints.
    """
    schema: Dict[str, Any] = {
        "validation_id": {"type": "string", "required": True, "unique": True},
        "language": {"type": "string", "required": True, "allowed": ["English", "Arabic", "Yoruba"]},
        "proverb": {"type": "string", "required": True},
        "option_A": {"type": "string", "required": True},
        "option_B": {"type": "string", "required": True},
        "option_C": {"type": "string", "required": True},
        "option_D": {"type": "string", "required": True},
        "answer": {"type": "string", "required": True, "allowed": VALID_ANSWERS},
        "plausibility_A": {"type": "integer", "required": True, "min": 1, "max": 5},
        "plausibility_B": {"type": "integer", "required": True, "min": 1, "max": 5},
        "plausibility_C": {"type": "integer", "required": True, "min": 1, "max": 5},
        "plausibility_D": {"type": "integer", "required": True, "min": 1, "max": 5},
        "shortcut_flag": {"type": "string", "required": False, "allowed": SHORTCUT_FLAGS},
        "confidence": {"type": "integer", "required": True, "allowed": VALID_CONFIDENCE},
    }
    return schema