import pandas as pd
import numpy as np
import os
import sys

files = [
    '_unzipped_results/mcq_a_cot_xl_yoruba.csv',
    '_unzipped_results/mcq_a_cot_xl_arabic.csv',
    '_unzipped_results/mcq_a_cot_xl_english.csv',
    '_unzipped_results/mcq_a_cot_xl_french.csv',
    '_unzipped_results/mcq_a_cot_xl_spanish.csv',
    '_unzipped_results/mcq_a_cot_xl_german.csv',
]

with open('csv_analysis_report.txt', 'w', encoding='utf-8') as out:
    def p(text=''):
        out.write(str(text) + '\n')
    
    for f in files:
        p('=' * 80)
        p(f'FILE: {os.path.basename(f)}')
        p('=' * 80)
        
        try:
            df = pd.read_csv(f)
        except Exception as e:
            p(f'ERROR reading {f}: {e}')
            continue
        
        # Basic info
        p(f'Total rows: {len(df)}')
        p(f'Total columns: {len(df.columns)}')
        p(f'Column names: {list(df.columns)}')
        p()
        
        # First 3 rows
        p('--- FIRST 3 ROWS ---')
        for i in range(min(3, len(df))):
            p(f'Row {i}:')
            for col in df.columns:
                val = df.iloc[i][col]
                p(f'  {col}: {repr(val)}')
            p()
        
        # Last 3 rows
        p('--- LAST 3 ROWS ---')
        for i in range(max(0, len(df)-3), len(df)):
            p(f'Row {i}:')
            for col in df.columns:
                val = df.iloc[i][col]
                p(f'  {col}: {repr(val)}')
            p()
        
        # Summary stats for specific columns
        stat_cols = ['parse', 'complete', 'distinct', 'quality', 'len_r']
        p('--- SUMMARY STATS ---')
        for col in stat_cols:
            if col in df.columns:
                p(f'{col}:')
                p(df[col].describe().to_string())
                p()
            else:
                p(f'Column {col} NOT FOUND')
                p()
        
        # Empty/blank counts for distractors and choices
        p('--- EMPTY/BLANK COUNTS ---')
        check_cols = ['distractor_1', 'distractor_2', 'distractor_3', 
                      'Choice_A', 'Choice_B', 'Choice_C', 'Choice_D', 'Answer']
        for col in check_cols:
            if col in df.columns:
                if df[col].dtype == object:
                    mask = df[col].isna() | (df[col] == '') | (df[col].astype(str).str.strip() == '')
                    empty_count = int(mask.sum())
                else:
                    empty_count = int(df[col].isna().sum())
                p(f'{col}: {empty_count} empty/blank rows')
            else:
                p(f'{col}: COLUMN NOT FOUND')
        p()
        
        # Other anomalies
        p('--- ANOMALIES ---')
        if 'Answer' in df.columns and df['Answer'].dtype == object:
            unique_answers = df['Answer'].dropna().unique()
            p(f'Unique non-null Answer values: {unique_answers}')
            vc = df['Answer'].value_counts(dropna=False)
            p('Answer value counts:')
            p(vc.to_string())
            p()
        
        # Check for duplicate rows
        dupes = df.duplicated().sum()
        p(f'Duplicate rows: {dupes}')
        
        # Check data types
        p('Dtypes:')
        p(df.dtypes.to_string())
        p()
        
        # Check for any completely empty rows
        empty_rows = df.isna().all(axis=1).sum()
        p(f'Completely empty rows: {empty_rows}')
        p()
        
        # Check for rows where all distractors are empty
        if all(c in df.columns for c in ['distractor_1', 'distractor_2', 'distractor_3']):
            d_mask = df['distractor_1'].isna() & df['distractor_2'].isna() & df['distractor_3'].isna()
            p(f'Rows where all 3 distractors are NaN: {d_mask.sum()}')
        
        # Check for rows where all choices are empty
        choice_cols = ['Choice_A', 'Choice_B', 'Choice_C', 'Choice_D']
        if all(c in df.columns for c in choice_cols):
            c_mask = df['Choice_A'].isna() & df['Choice_B'].isna() & df['Choice_C'].isna() & df['Choice_D'].isna()
            p(f'Rows where all 4 choices are NaN: {c_mask.sum()}')
        
        # Check for negative values in numeric columns
        for col in stat_cols:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                neg = (df[col] < 0).sum()
                if neg > 0:
                    p(f'Negative values in {col}: {neg}')
        
        p()

print('Report written to csv_analysis_report.txt')
