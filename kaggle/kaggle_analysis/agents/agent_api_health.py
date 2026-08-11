#!/usr/bin/env python3
"""Agent 2: API Health Monitor"""
import pandas as pd
from pathlib import Path
from config import INPUT_DIR

def run():
    print("\n[AGENT 2] API Health Monitor")
    print("-" * 50)
    
    try:
        df = pd.read_csv(INPUT_DIR / 'evaluation_results.csv')
        
        # Overall failure rate
        errors = df[df['error'].notna() & (df['error'] != '')]
        err_rate = 100 * len(errors) / len(df)
        print(f"  Overall API failure rate: {err_rate:.1f}%")
        
        # Per-model failure rate
        print(f"\n  Per-model failure rates:")
        for model in sorted(df['model'].unique()):
            m_df = df[df['model'] == model]
            m_err = m_df[m_df['error'].notna() & (m_df['error'] != '')]
            rate = 100 * len(m_err) / len(m_df)
            status = "OK" if rate < 5 else "DEGRADED" if rate < 20 else "CRITICAL"
            print(f"    {model:45} {rate:5.1f}% [{status}]")
        
        # Top error messages
        if len(errors) > 0:
            print(f"\n  Top error messages:")
            for msg, count in errors['error'].value_counts().head(5).items():
                print(f"    ({count}x) {msg[:80]}")
        
        return err_rate < 5
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

if __name__ == '__main__':
    run()
