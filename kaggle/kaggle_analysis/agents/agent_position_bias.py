#!/usr/bin/env python3
"""Agent 3: Position Bias Detector"""
import pandas as pd
import numpy as np
from pathlib import Path
from config import INPUT_DIR
from scipy import stats



def run():
    print("\n[AGENT 3] Position Bias Detector")
    print("-" * 50)
    
    try:
        results = pd.read_csv(INPUT_DIR / 'evaluation_results.csv')
        mcqs_s1 = pd.read_csv(INPUT_DIR / 'mcqs_strategy1.csv')
        mcqs_s2 = pd.read_csv(INPUT_DIR / 'mcqs_strategy2.csv')
        
        pos_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
        
        for strategy, df_strat, mcqs in [('S1', results[results['strategy'] == 'S1'], mcqs_s1),
                                          ('S2', results[results['strategy'] == 'S2'], mcqs_s2)]:
            mcq_map = {str(r['sample_id']): r for _, r in mcqs.iterrows()}
            hits_by_pos = {0: [], 1: [], 2: [], 3: []}
            
            for _, row in df_strat.iterrows():
                sid = str(row['sample_id'])
                if sid in mcq_map:
                    pos = pos_map.get(str(mcq_map[sid]['Answer']), None)
                    if pos is not None:
                        hits_by_pos[pos].append(row['hit'])
            
            total_correct = sum(sum(h) for h in hits_by_pos.values())
            expected = total_correct / 4.0 if total_correct > 0 else 0
            
            print(f"\n  Strategy {strategy}:")
            for p in [0, 1, 2, 3]:
                hits = hits_by_pos.get(p, [])
                acc = 100 * np.mean(hits) if hits else 0
                label = ['A', 'B', 'C', 'D'][p]
                print(f"    Position {label}: {acc:5.1f}% (n={len(hits)})")
            
            if expected > 0:
                obs_counts = [sum(hits_by_pos.get(p, [])) for p in [0, 1, 2, 3]]
                chi2 = sum((obs - expected) ** 2 / expected for obs in obs_counts)
                p_val = 1 - stats.chi2.cdf(chi2, 3)
                sig = "SIGNIFICANT" if p_val < 0.05 else "not significant"
                print(f"    Chi² = {chi2:.2f}, p = {p_val:.4f} ({sig})")
                
                return p_val >= 0.05
            else:
                print("    No data for chi-square test")
                return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

if __name__ == '__main__':
    run()
