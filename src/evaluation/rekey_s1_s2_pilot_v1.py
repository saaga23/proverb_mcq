"""Re-key existing Pilot 2 v1 S1/S2 CSVs so correct answers are balanced A-D.

Input : S1_S2_pilot_v1/extracted/mcqs_s1.csv, mcqs_s2.csv
Output: S1_S2_pilot_v1/extracted/mcqs_s1_rekeyed.csv, mcqs_s2_rekeyed.csv
"""

import os
import pandas as pd

INPUT_DIR = "S1_S2_pilot_v1/extracted"
OUTPUT_DIR = "S1_S2_pilot_v1/extracted"


def rekey(df, strategy):
    """Re-distribute correct answers round-robin across A-D.

    For S1 the gold option is the value in the `gold` column.
    For S2 the gold option is the value in the `source_proverb` column.
    """
    labels = ["A", "B", "C", "D"]
    out_rows = []
    gold_col = "gold" if strategy == "S1" else "source_proverb"

    for i, (_, row) in enumerate(df.iterrows()):
        options = {k: row[f"Choice_{k}"] for k in labels}
        gold_value = row[gold_col]

        current_label = None
        for k, v in options.items():
            if str(v).strip() == str(gold_value).strip():
                current_label = k
                break
        if current_label is None:
            raise ValueError(f"Row {i}: could not locate gold option for {strategy}")

        new_label = labels[i % 4]
        distractors = [v for k, v in options.items() if k != current_label]
        new_pos = labels.index(new_label)
        ordered = (
            distractors[:new_pos]
            + [options[current_label]]
            + distractors[new_pos:]
        )

        new_row = row.to_dict()
        for k, opt in zip(labels, ordered):
            new_row[f"Choice_{k}"] = opt
        new_row["Answer"] = new_label
        out_rows.append(new_row)

    return pd.DataFrame(out_rows)


def main():
    for strategy in ["S1", "S2"]:
        in_path = os.path.join(INPUT_DIR, f"mcqs_{strategy.lower()}.csv")
        out_path = os.path.join(OUTPUT_DIR, f"mcqs_{strategy.lower()}_rekeyed.csv")

        df = pd.read_csv(in_path, encoding="utf-8-sig")
        rekeyed = rekey(df, strategy)
        rekeyed.to_csv(out_path, index=False, encoding="utf-8-sig")

        dist = rekeyed["Answer"].value_counts().reindex(["A", "B", "C", "D"]).fillna(0)
        print(f"{strategy}: wrote {out_path}")
        print(f"  New Answer distribution: {dist.to_dict()}")


if __name__ == "__main__":
    main()
