"""Blinded export functions for ProverbGap MCQ human annotation."""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any
import pandas as pd


def _hash_validation_id(lang: str, proverb: str, seed: int = 20260615) -> str:
    """Create deterministic hash for validation ID.

    Args:
        lang: Language code/name.
        proverb: The proverb text.
        seed: Random seed for reproducibility.

    Returns:
        SHA256 hash string (first 12 characters).
    """
    combined = f"{seed}:{lang}:{proverb}"
    return hashlib.sha256(combined.encode()).hexdigest()[:12]


def load_production_sample(csv_path: str) -> pd.DataFrame:
    """Load the production MCQ sample from CSV.

    Args:
        csv_path: Path to the generated MCQ CSV file.

    Returns:
        DataFrame with production MCQs.
    """
    return pd.read_csv(csv_path)


def create_blinded_annotation_pack(
    df: pd.DataFrame,
    output_dir: str,
    seed: int = 20260615,
) -> Dict[str, str]:
    """Create blinded annotation package for human annotators.

    Args:
        df: DataFrame with production MCQs (must contain original language columns).
        output_dir: Directory to write output files.
        seed: Random seed for reproducibility.

    Returns:
        Dictionary mapping file names to their paths.

    Note:
        Explicitly excludes: correct_label, consensus_label, all vote columns,
        correct_meaning, and any other answer-revealing columns.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create validation IDs if not present
    if "validation_id" not in df.columns:
        df = df.copy()
        df["validation_id"] = df.apply(
            lambda r: _hash_validation_id(r["language"], r["proverb"], seed), axis=1
        )

    # Input columns that exist in production data (to keep)
    input_columns = [
        "validation_id",
        "language",
        "proverb",
        "option_A",
        "option_B",
        "option_C",
        "option_D",
        "generation_status",
    ]

    # Select only columns that exist
    existing_cols = [c for c in input_columns if c in df.columns]
    blinded_df = df[existing_cols].copy()

    # Initialize empty annotation columns
    blinded_df["answer"] = ""
    blinded_df["plausibility_A"] = ""
    blinded_df["plausibility_B"] = ""
    blinded_df["plausibility_C"] = ""
    blinded_df["plausibility_D"] = ""
    blinded_df["shortcut_flag"] = ""
    blinded_df["confidence"] = ""

    # Write blinded CSV
    blinded_csv_path = output_path / "blinded_items.csv"
    blinded_df.to_csv(blinded_csv_path, index=False)

    # Create annotator assignments (placeholder - to be populated by actual assignment)
    assignments_path = output_path / "annotator_assignments.json"
    assignments = {
        "seed": seed,
        "annotators": {
            "English": ["annotator_en_1", "annotator_en_2", "annotator_en_3"],
            "Arabic": ["annotator_ar_1", "annotator_ar_2", "annotator_ar_3"],
            "Yoruba": ["annotator_yo_1", "annotator_yo_2", "annotator_yo_3"],
        },
        "items_per_annotator": {},
    }
    # Assign items to annotators by language
    for lang in ["English", "Arabic", "Yoruba"]:
        lang_items = df[df["language"] == lang]["validation_id"].tolist()
        for ann in assignments["annotators"][lang]:
            assignments["items_per_annotator"][ann] = lang_items

    with open(assignments_path, "w") as f:
        json.dump(assignments, f, indent=2)

    # Create randomization manifest
    manifest_path = output_path / "randomization_manifest.json"
    manifest = {
        "seed": seed,
        "total_items": len(df),
        "languages": {
            "English": len(df[df["language"] == "English"]),
            "Arabic": len(df[df["language"] == "Arabic"]),
            "Yoruba": len(df[df["language"] == "Yoruba"]),
        },
    }
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    return {
        "blinded_csv": str(blinded_csv_path),
        "assignments_json": str(assignments_path),
        "manifest_json": str(manifest_path),
    }


def unblind_results(blinded_csv: str, master_csv: str) -> pd.DataFrame:
    """Join human answers back to master data for analysis.

    Args:
        blinded_csv: Path to completed blinded annotation CSV.
        master_csv: Path to original production MCQ CSV with correct answers.

    Returns:
        DataFrame with both annotation and original data columns.
    """
    blinded_df = pd.read_csv(blinded_csv)
    master_df = pd.read_csv(master_csv)

    # Merge on validation_id
    result = master_df.merge(
        blinded_df,
        on="validation_id",
        how="inner",
        suffixes=("", "_annotation"),
    )

    return result