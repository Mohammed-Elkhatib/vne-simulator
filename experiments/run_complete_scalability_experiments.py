#!/usr/bin/env python3
"""
Complete Scalability Experiments Runner

Production script to run comprehensive VNE scalability testing experiments.
Tests 4 algorithms across 4 substrate network sizes (8, 12, 16, 20 nodes).

Output Structure:
experiments/scalability_experiment/
├── vnr_characteristics.png              # VNR queue analysis (shared)
├── 8_nodes_experiment/
│   ├── 8_nodes_substrate.png           # Substrate network
│   ├── 8_nodes_timelines.png           # Timeline comparison (4 algorithms)  
│   ├── 8_nodes_utilization.png         # Peak resource utilization
│   ├── 8_nodes_metrics.png             # Performance metrics
│   ├── results_summary.json            # Algorithm performance data
│   └── metadata.json                   # Experiment metadata
├── 12_nodes_experiment/                 # Same structure
├── 16_nodes_experiment/                 # Same structure  
└── 20_nodes_experiment/                 # Same structure

Features:
- Timeout handling for larger networks
- Graceful error handling for algorithm failures
- Comprehensive visualization generation
- Same VNR queue across all experiments for fair comparison
- Production-ready output structure
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.append('.')

try:
    from unified_scalability_experiments import UnifiedScalabilityExperiments
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


def main():
    """Main runner for complete scalability experiments."""
    
    print("VNE SCALABILITY EXPERIMENTS")
    print("=" * 50)
    print("Testing algorithm performance across network sizes")
    print("Network sizes: 8, 12, 16, 20 nodes")  
    print("Algorithms: Simple_Greedy, RW_BFS, RW_MaxMatch, Yu2008")
    print("Same VNR queue (20 requests) for fair comparison")
    print("=" * 50)
    
    print("\nStarting scalability experiments...")
    
    # Create experiment system
    scalability_exp = UnifiedScalabilityExperiments()
    
    try:
        # Run all experiments
        results = scalability_exp.run_all_experiments()
        
        if results:
            print("\nEXPERIMENTS COMPLETED SUCCESSFULLY!")
            print(f"Results saved to: experiments/scalability_experiment/")
            print(f"Generated files:")
            print(f"   - 1 VNR characteristics figure")
            print(f"   - 4 substrate network figures (one per size)")
            print(f"   - 16 experiment figures (4 sizes × 4 figures)")
            print(f"   - 8 JSON data files (4 sizes × 2 files)")
            print(f"   - Total: 29 files")
            
            # Print quick summary
            print(f"\nQuick Results Summary:")
            successful_count = sum(
                1 for exp_results in results.values() 
                if isinstance(exp_results, dict) and 'status' not in exp_results
            )
            print(f"   - Successful experiments: {successful_count}/4")
            print(f"   - Output directory: experiments/scalability_experiment/")
            
        else:
            print("No experiments completed successfully")
            
    except KeyboardInterrupt:
        print("\n\nExperiments interrupted by user")
        print("Partial results may be available in experiments/scalability_experiment/")
        
    except Exception as e:
        print(f"\nExperiments failed with error: {str(e)}")
        print("Check the error details above for troubleshooting")


if __name__ == "__main__":
    main()