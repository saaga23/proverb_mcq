#!/usr/bin/env python3
"""Agent 4: Statistical Significance Tester"""
import pandas as pd
from pathlib import Path
from config import INPUT_DIR
from scipy import stats



def mcnemar(y1, y2):
    a = sum(1 for x, y in zip(y1, y2) if x == 1 and y == 1)
    b = sum(1 for x, y in zip(y1, y2) if x == 1 and y == 0)
    c = sum(1 for x, y in zip(y1, y2) if x == 0 and y == 1)
    d = sum(1 for x, y in zip(y1, y2) if x == 0 and y == 0)
    if b + c == 0:
        return 0.0, 1.0
    stat = (abs(b - c) - 1) ** 2 / (b + c)
    p = 1 - stats.chi2.cdf(stat, 1)
    return stat, p

def run():
    print("\n[AGENT 4] Statistical Significance Tester")
    print("-" * 50)
    
    try:
        results = pd.read_csv(INPUT_DIR / 'evaluation_results.csv')
        s1 = results[results['strategy'] == 'S1']
        s2 = results[results['strategy'] == 'S2']
        s2_nf = s2[s2['fallback'] == False]
        
        # McNemar: S1 vs S2 (all)
        merged = s1.merge(s2[['model', 'style', 'sample_id', 'hit']],
                          on=['model', 'style', 'sample_id'], suffixes=('_s1', '_s2'))
        if len(merged) > 10:
            stat, p = mcnemar(merged['hit_s1'].tolist(), merged['hit_s2'].tolist())
            sig = "SIGNIFICANT" if p < 0.05 else "not significant"
            print(f"  McNemar (S1 vs S2, all): chi^2={stat:.3f}, p={p:.4f} ({sig})")
        
        # McNemar: S1 vs S2 (strict)
        merged_nf = s1.merge(s2_nf[['model', 'style', 'sample_id', 'hit']],
                             on=['model', 'style', 'sample_id'], suffixes=('_s1', '_s2'), how='inner')
        if len(merged_nf) > 10:
            stat, p = mcnemar(merged_nf['hit_s1'].tolist(), merged_nf['hit_s2'].tolist())
            sig = "SIGNIFICANT" if p < 0.05 else "not significant"
            print(f"  McNemar (S1 vs S2, strict): chi^2={stat:.3f}, p={p:.4f} ({sig})")
        
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

if __name__ == '__main__':
    run()
