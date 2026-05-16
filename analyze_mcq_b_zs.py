import pandas as pd
import numpy as np
import sys

files = [
    '_unzipped/mcq_b_zs_yoruba.csv',
    '_unzipped/mcq_b_zs_arabic.csv',
    '_unzipped/mcq_b_zs_english.csv',
    '_unzipped/mcq_b_zs_french.csv',
    '_unzipped/mcq_b_zs_spanish.csv',
    '_unzipped/mcq_b_zs_german.csv',
]

out_path = 'analyze_mcq_b_zs_output.txt'
with open(out_path, 'w', encoding='utf-8') as out:
    def w(s=''):
        out.write(s + '\n')

    for f in files:
        w('='*80)
        w(f'FILE: {f}')
        w('='*80)
        try:
            df = pd.read_csv(f)
        except Exception as e:
            w(f'ERROR reading {f}: {e}')
            continue

        # Basic info
        w(f'Total rows: {len(df)}')
        w(f'Total columns: {len(df.columns)}')
        w(f'Column names: {list(df.columns)}')
        w()

        # First 3 rows verbatim
        w('--- FIRST 3 ROWS ---')
        for idx, row in df.head(3).iterrows():
            w(f'Row {idx}:')
            for col in df.columns:
                val = row[col]
                if pd.isna(val):
                    val_repr = 'NaN'
                else:
                    val_repr = repr(val)
                w(f'  {col}: {val_repr}')
            w()

        # Last 3 rows verbatim
        w('--- LAST 3 ROWS ---')
        for idx, row in df.tail(3).iterrows():
            w(f'Row {idx}:')
            for col in df.columns:
                val = row[col]
                if pd.isna(val):
                    val_repr = 'NaN'
                else:
                    val_repr = repr(val)
                w(f'  {col}: {val_repr}')
            w()

        # Summary stats for specific columns
        stats_cols = ['parse', 'complete', 'distinct', 'quality', 'len_r']
        w('--- SUMMARY STATS ---')
        for col in stats_cols:
            if col in df.columns:
                w(f'Column: {col}')
                w(df[col].describe().to_string())
                w()
            else:
                w(f'Column: {col} -- NOT FOUND')
                w()

        # Empty/blank counts
        w('--- EMPTY/BLANK COUNTS ---')
        blank_cols = ['distractor_1', 'distractor_2', 'distractor_3', 'Choice_A', 'Choice_B', 'Choice_C', 'Choice_D']
        for col in blank_cols:
            if col in df.columns:
                blank_count = df[col].isna().sum() + ((~df[col].isna()) & (df[col].astype(str).str.strip() == '')).sum()
                w(f'{col}: {blank_count}')
            else:
                w(f'{col}: COLUMN NOT FOUND')

        # Answer blank
        if 'Answer' in df.columns:
            ans_blank = df['Answer'].isna().sum() + ((~df['Answer'].isna()) & (df['Answer'].astype(str).str.strip() == '')).sum()
            w(f'Answer blank: {ans_blank}')
        else:
            w('Answer blank: COLUMN NOT FOUND')
        w()

        # Anomalies
        w('--- ANOMALIES ---')
        # Check for duplicate rows
        dups = df.duplicated().sum()
        w(f'Duplicate rows: {dups}')
        # Check data types
        w('Dtypes:')
        for col in df.columns:
            w(f'  {col}: {df[col].dtype}')
        # Check unique counts for categorical-like columns
        if 'proverb_id' in df.columns:
            w(f'Unique proverb_id: {df["proverb_id"].nunique()}')
        if 'sample_id' in df.columns:
            w(f'Unique sample_id: {df["sample_id"].nunique()}')
        if 'lang' in df.columns:
            w(f'Unique lang values: {df["lang"].unique()}')
        if 'language' in df.columns:
            w(f'Unique language values: {df["language"].unique()}')
        if 'model' in df.columns:
            w(f'Unique model values: {df["model"].unique()}')
        if 'Answer' in df.columns:
            w(f'Unique Answer values: {df["Answer"].unique()}')
        # Check len_r range
        if 'len_r' in df.columns:
            w(f'len_r min: {df["len_r"].min()}, max: {df["len_r"].max()}')
        # Check for unexpected values in binary columns
        for col in ['parse', 'complete', 'distinct', 'quality']:
            if col in df.columns:
                uniques = sorted(df[col].dropna().unique())
                w(f'{col} unique values: {uniques}')
        # Check distractor duplicates within row (first 1000 rows)
        dup_distractor_count = 0
        for i, row in df.iterrows():
            d1 = str(row.get('distractor_1', '')).strip()
            d2 = str(row.get('distractor_2', '')).strip()
            d3 = str(row.get('distractor_3', '')).strip()
            if d1 and d2 and d1 == d2:
                w(f'Row {i}: distractor_1 == distractor_2 ({d1})')
                dup_distractor_count += 1
            if d1 and d3 and d1 == d3:
                w(f'Row {i}: distractor_1 == distractor_3 ({d1})')
                dup_distractor_count += 1
            if d2 and d3 and d2 == d3:
                w(f'Row {i}: distractor_2 == distractor_3 ({d2})')
                dup_distractor_count += 1
            if i >= 1000:
                break
        if dup_distractor_count == 0:
            w('No duplicate distractors found in first 1000 rows')
        w()
        w()

print(f'Output written to {out_path}')
