#!/usr/bin/env python3
"""Agent 5: Encoder Baseline Analyst"""
import pandas as pd
from pathlib import Path
from config import INPUT_DIR

def run():
    print("\n[AGENT 5] Encoder Baseline Analyst")
    print("-" * 50)
    
    try:
        encoder = pd.read_csv(INPUT_DIR / 'encoder_results.csv')
        
        print(f"  Total encoder evaluations: {len(encoder)}")
        print(f"\n  Per-encoder accuracy:")
        for enc in sorted(encoder['model'].unique()):
            for strategy in ['S1', 'S2']:
                sub = encoder[(encoder['model'] == enc) & (encoder['strategy'] == strategy)]
                if len(sub) > 0:
                    acc = 100 * sub['hit'].mean()
                    print(f"    {enc:12} {strategy}: {acc:5.1f}% (n={len(sub)})")
        
        print(f"\n  Per-language encoder accuracy:")
        for lang in ['English', 'Arabic', 'Yoruba']:
            sub = encoder[encoder['language'] == lang]
            if len(sub) > 0:
                acc = 100 * sub['hit'].mean()
                print(f"    {lang:8}: {acc:5.1f}% (n={len(sub)})")
        
        return len(encoder) > 0
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

if __name__ == '__main__':
    run()
