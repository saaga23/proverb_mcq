#!/usr/bin/env python3
"""Agent 1: Data Quality Auditor"""
import pandas as pd
from pathlib import Path
from config import INPUT_DIR
from config import OUTPUT_DIR

def run():
    print("\n[AGENT 1] Data Quality Auditor")
    print("-" * 50)
    
    issues = []
    
    # Check evaluation_results.csv
    try:
        df = pd.read_csv(INPUT_DIR / 'evaluation_results.csv')
        print(f"  evaluation_results.csv: {len(df)} rows")
        
        if df.isnull().any().any():
            issues.append(f"Null values found in columns: {df.columns[df.isnull().any()].tolist()}")
        
        if len(df) != len(df.drop_duplicates()):
            issues.append(f"{len(df) - len(df.drop_duplicates())} duplicate rows found")
        
        required = ['strategy', 'model', 'style', 'sample_id', 'language', 'hit']
        missing = [c for c in required if c not in df.columns]
        if missing:
            issues.append(f"Missing required columns: {missing}")
        
        if not issues:
            print("  Status: PASS")
        else:
            for issue in issues:
                print(f"  WARNING: {issue}")
    except Exception as e:
        print(f"  ERROR: {e}")
        return False
    
    return len(issues) == 0

if __name__ == '__main__':
    run()
