import pandas as pd
import numpy as np
import os
import sys

files = [
    '_unzipped_results/mcq_a_cot_en_yoruba.csv',
    '_unzipped_results/mcq_a_cot_en_arabic.csv',
    '_unzipped_results/mcq_a_cot_en_english.csv',
    '_unzipped_results/mcq_a_cot_en_french.csv',
    '_unzipped_results/mcq_a_cot_en_spanish.csv',
    '_unzipped_results/mcq_a_cot_en_german.csv'
]

# Redirect stdout to file with utf-8 encoding
sys.stdout = open('mcq_cot_en_report.txt', 'w', encoding='utf-8')

for f in files:
    print('=' * 80)
    print('FILE:', os.path.basename(f))
    print('=' * 80)
    
    try:
        df = pd.read_csv(f)
    except Exception as e:
        print(f'ERROR reading {f}: {e}')
        continue
    
    # Total rows and columns
    print('\n--- Total rows and columns ---')
    print(f'Rows: {df.shape[0]}, Columns: {df.shape[1]}')
    
    # Column names
    print('\n--- Column names ---')
    print(list(df.columns))
    
    # First 3 rows
    print('\n--- First 3 rows ---')
    for i in range(min(3, len(df))):
        print(f'Row {i}:')
        for col in df.columns:
            val = df.iloc[i][col]
            print(f'  {col}: {repr(val)}')
        print()
    
    # Last 3 rows
    print('\n--- Last 3 rows ---')
    for i in range(max(0, len(df)-3), len(df)):
        print(f'Row {i}:')
        for col in df.columns:
            val = df.iloc[i][col]
            print(f'  {col}: {repr(val)}')
        print()
    
    # Summary stats for: parse, complete, distinct, quality, len_r
    print('\n--- Summary stats for parse, complete, distinct, quality, len_r ---')
    for col in ['parse', 'complete', 'distinct', 'quality', 'len_r']:
        if col in df.columns:
            print(f'\n{col}:')
            print(df[col].describe().to_string())
        else:
            print(f'\n{col}: COLUMN NOT FOUND')
    
    # Number of rows with empty/blank distractor_1, distractor_2, distractor_3, Choice_A, Choice_B, Choice_C, Choice_D
    print('\n--- Empty/blank counts ---')
    for col in ['distractor_1', 'distractor_2', 'distractor_3', 'Choice_A', 'Choice_B', 'Choice_C', 'Choice_D']:
        if col in df.columns:
            mask = df[col].isna() | (df[col].astype(str).str.strip() == '') | (df[col].astype(str) == 'nan')
            blank = int(mask.sum())
            print(f'{col}: {blank}')
        else:
            print(f'{col}: COLUMN NOT FOUND')
    
    # Number of rows where Answer is blank
    print('\n--- Answer blank count ---')
    if 'Answer' in df.columns:
        mask = df['Answer'].isna() | (df['Answer'].astype(str).str.strip() == '') | (df['Answer'].astype(str) == 'nan')
        blank_answer = int(mask.sum())
        print(f'Answer blank: {blank_answer}')
    else:
        print('Answer: COLUMN NOT FOUND')
    
    # Anomalies
    print('\n--- Other anomalies ---')
    print(f'Duplicate rows: {df.duplicated().sum()}')
    
    # Constant columns
    for col in df.columns:
        nunique = df[col].nunique(dropna=False)
        if nunique == 1:
            print(f'Constant column: {col} = {df[col].iloc[0]}')
    
    # Unique Answer values
    if 'Answer' in df.columns:
        uniq_ans = sorted(df['Answer'].dropna().unique())
        print(f'Unique Answer values: {uniq_ans}')
    
    # Quality outliers
    if 'quality' in df.columns:
        q_low = (df['quality'] < 0).sum()
        q_high = (df['quality'] > 100).sum()
        if q_low or q_high:
            print(f'Quality out of [0,100]: {q_low} below 0, {q_high} above 100')
    
    # Completely null rows
    null_rows = df.isnull().all(axis=1).sum()
    print(f'Completely null rows: {null_rows}')
    
    print('\n' + '=' * 80 + '\n')

sys.stdout.close()
