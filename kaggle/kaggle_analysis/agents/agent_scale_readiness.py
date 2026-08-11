#!/usr/bin/env python3
"""Agent 6: Scale Readiness Assessor"""
import pandas as pd
from pathlib import Path
from config import INPUT_DIR

def run():
    print("\n[AGENT 6] Scale Readiness Assessor")
    print("-" * 50)
    
    try:
        results = pd.read_csv(INPUT_DIR / 'evaluation_results.csv')
        mcqs_s2 = pd.read_csv(INPUT_DIR / 'mcqs_strategy2.csv')
        encoder = pd.read_csv(INPUT_DIR / 'encoder_results.csv')
        
        checks = {}
        
        # Check 1: Fallback rate
        fb_rate = 100 * mcqs_s2['fallback'].sum() / len(mcqs_s2) if len(mcqs_s2) > 0 else 100
        checks['Fallback rate < 20%'] = fb_rate < 20
        print(f"  1. S2 Fallback rate: {fb_rate:.1f}% [{'PASS' if checks['Fallback rate < 20%'] else 'FAIL'}]")
        
        # Check 2: API failure rate
        errors = results[results['error'].notna() & (results['error'] != '')]
        err_rate = 100 * len(errors) / len(results) if len(results) > 0 else 100
        checks['API failure rate < 5%'] = err_rate < 5
        print(f"  2. API failure rate: {err_rate:.1f}% [{'PASS' if checks['API failure rate < 5%'] else 'FAIL'}]")
        
        # Check 3: Encoder baselines work
        checks['Encoder baselines work'] = len(encoder) > 0
        print(f"  3. Encoder baselines: {len(encoder)} rows [{'PASS' if checks['Encoder baselines work'] else 'FAIL'}]")
        
        # Check 4: Data completeness
        checks['Data complete'] = len(results) > 0
        print(f"  4. Data completeness: {len(results)} evaluations [{'PASS' if checks['Data complete'] else 'FAIL'}]")
        
        # Estimate N=700 runtime
        n_total_700 = 700 * 3 * 3 * 3 * 2  # N * langs * models * styles * 2 strategies
        print(f"\n  N=700 scale estimate:")
        print(f"    Total evaluations: {n_total_700:,}")
        print(f"    If current failure rate persists: {int(n_total_700 * err_rate / 100):,} would fail")
        
        all_pass = all(checks.values())
        print(f"\n  {'='*40}")
        print(f"  VERDICT: {'READY FOR N=700' if all_pass else 'BLOCKERS — FIX BEFORE SCALING'}")
        print(f"  {'='*40}")
        
        return all_pass
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

if __name__ == '__main__':
    run()
