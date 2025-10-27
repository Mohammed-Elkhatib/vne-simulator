#!/usr/bin/env python3
"""
Complete Load Testing Experiments Runner

This script generates ALL required figures for load testing analysis:
1. Substrate network figure (1 shared substrate) 
2. 3 load scenarios × 4 figures each = 12 experiment figures
3. JSON results for all scenarios

Total: 13 figures + 6 JSON files for complete load testing analysis

IMPORTANT: Run this script from the project root directory.

Usage:
    python run_complete_load_experiments.py

Output Structure:
    experiments/load_testing_experiment/
    ├── substrate_network.png           # Shared substrate network
    ├── light_demand_experiment/
    │   ├── light_demand_vnrs.png       # VNR queue visualization
    │   ├── light_demand_timelines.png  # Timeline comparison
    │   ├── light_demand_utilization.png # Resource utilization  
    │   ├── light_demand_metrics.png    # Performance metrics
    │   ├── results_summary.json        # Algorithm results
    │   └── metadata.json               # Experiment metadata
    ├── medium_demand_experiment/
    └── heavy_demand_experiment/

Estimated Runtime: 3-5 minutes for all load experiments
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path - works from both project root and experiments/ directory
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
src_path = project_root / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import unified load experiment runner (now in same directory)
from unified_load_experiments import UnifiedLoadExperiments

def main():
    """Main execution function."""
    print("COMPLETE LOAD TESTING EXPERIMENTS RUNNER")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Create and run unified load experiments
        experiment = UnifiedLoadExperiments()
        all_results = experiment.run_all_load_experiments()
        
        # Summary
        print("ALL LOAD EXPERIMENTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("Generated files:")
        print("  experiments/load_testing_experiment/")
        print("    ├── substrate_network.png - Shared German substrate network")
        print("    ├── light_demand_experiment/")
        print("    │   ├── light_demand_vnrs.png - Diverse light VNRs visualization")
        print("    │   ├── light_demand_timelines.png - Timeline comparison (4 algorithms)")
        print("    │   ├── light_demand_utilization.png - Peak resource utilization")
        print("    │   ├── light_demand_metrics.png - Performance metrics comparison")
        print("    │   ├── results_summary.json - Algorithm performance data")
        print("    │   └── metadata.json - Experiment metadata")
        print("    ├── medium_demand_experiment/ - Same structure")
        print("    └── heavy_demand_experiment/ - Same structure")
        print()
        print("Total output for load testing analysis:")
        print("  • 1 substrate network figure (shared German network)")
        print("  • 3 VNR queue figures (15, 25, 35 diverse VNRs)")
        print("  • 9 experiment figures (3 scenarios × 3 figures)")
        print("  • 6 data files (3 scenarios × 2 JSON files)")
        print("  • Grand total: 19 files ready for load testing analysis")
        print()
        print("Load Testing Methodology (VNE Literature Standard):")
        print("  • Light: 15 VNRs, CPU(10-20), BW(5-15)")
        print("  • Medium: 25 VNRs, CPU(15-30), BW(10-25)")
        print("  • Heavy: 35 VNRs, CPU(20-40), BW(15-35)")
        print()
        
        # Performance summary
        print("Load Testing Performance Summary:")
        print("-" * 40)
        
        for scenario_name, scenario_results in all_results.items():
            print(f"\n{scenario_name.replace('_', ' ').title()}:")
            
            for alg_name, alg_data in scenario_results.items():
                if alg_data['status'] == 'SUCCESS':
                    metrics = alg_data['metrics']
                    acceptance = metrics['acceptance_ratio'] 
                    revenue_cost = metrics['revenue_cost_ratio']
                    print(f"  {alg_name}: {acceptance:.1%} acceptance ({revenue_cost:.3f} revenue/cost)")
                else:
                    print(f"  {alg_name}: FAILED")
        
    except Exception as e:
        print(f"ERROR: {e}")
        print("Check the error message above and ensure:")
        print("  - You're running from the project root directory")
        print("  - All src/ modules are available")
        print("  - No file permission issues")
        return 1
        
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)