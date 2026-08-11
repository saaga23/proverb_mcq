#!/usr/bin/env python3
"""
Run all analysis agents and produce unified report.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'agents'))

from agent_data_quality import run as run_data_quality
from agent_api_health import run as run_api_health
from agent_position_bias import run as run_position_bias
from agent_statistics import run as run_statistics
from agent_encoder_analysis import run as run_encoder
from agent_scale_readiness import run as run_scale

def main():
    print("=" * 70)
    print("  ProverbGap Multi-Agent Analysis Framework")
    print("  N=50 Kaggle Run -> Scale Readiness for N=700")
    print("=" * 70)
    
    results = {}
    results['Data Quality'] = run_data_quality()
    results['API Health'] = run_api_health()
    results['Position Bias'] = run_position_bias()
    results['Statistics'] = run_statistics()
    results['Encoder Baselines'] = run_encoder()
    results['Scale Readiness'] = run_scale()
    
    print("\n" + "=" * 70)
    print("  AGENT SUMMARY")
    print("=" * 70)
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name:25} [{status}]")
    
    all_pass = all(results.values())
    print(f"\n  Overall: {'ALL AGENTS PASSED' if all_pass else 'SOME AGENTS FAILED'}")
    
    # Write unified report
    report_lines = []
    report_lines.append("# Unified Multi-Agent Analysis Report")
    report_lines.append("")
    report_lines.append("## Agent Results")
    report_lines.append("")
    report_lines.append("| Agent | Status |")
    report_lines.append("|-------|--------|")
    for name, passed in results.items():
        report_lines.append(f"| {name} | {'PASS' if passed else 'FAIL'} |")
    report_lines.append("")
    report_lines.append(f"## Verdict: {'Ready for N=700 scaling' if all_pass else 'Blockers identified — see individual agent outputs'}")
    
    with open('reports/unified_analysis_report.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"\n  Report saved: reports/unified_analysis_report.md")

if __name__ == '__main__':
    main()
