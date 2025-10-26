#!/usr/bin/env python3
"""
Topology Experiments Runner 

This script generates ALL required figures for topology experiment results:
1. Substrate networks figure (6 topologies)
2. VNR characteristics figure (20 VNRs)  
3. 6 topology experiments × 3 figures each = 18 experiment figures
4. JSON results for all experiments

Total: 20 figures + 6 JSON files for complete topology experiment

IMPORTANT: Run this script from the project root directory.

Usage:
    python run_complete_topology_experiments.py

Output Structure:
    experiments/topology_experiment/
    ├── substrate_networks_all.png      # 6 substrate topologies
    ├── vnr_queue.png                   # 20 VNR queue visualization
    ├── german_experiment/
    │   ├── german_timelines.png        # Timeline comparison
    │   ├── german_utilization.png      # Resource utilization  
    │   ├── german_metrics.png          # Performance metrics
    │   ├── results_summary.json        # Algorithm results
    │   └── metadata.json               # Experiment metadata
    ├── italian_experiment/
    ├── er_sparse_experiment/
    ├── er_dense_experiment/
    ├── ba_8_experiment/
    └── grid_9_experiment/

Estimated Runtime: 5-10 minutes for all experiments
"""

import sys
import os
import random
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
from datetime import datetime

# Add src to path (now we're in experiments/ so go up one level)
sys.path.append('../src')

# Import unified experiment runner (now in same directory)
from unified_topology_experiments import UnifiedTopologyExperiments

# Import working visualization functions
from src.visualization.network_plots import plot_substrate_network, plot_all_vnrs
from src.networks.substrate_networks import create_german_network, create_italian_network
from src.networks.vne_generators import generate_substrate_network
from src.networks.vnr_creation import create_vnr_queue

def generate_substrate_networks_figure():
    """Generate the 6 substrate networks figure using working implementation."""
    print("Generating substrate networks figure...")
    
    # Use EXACT same seed and parameters as unified experiments for consistency
    random.seed(100)
    
    # Generate all 6 substrate networks (same as unified experiments)
    substrate_configs = {
        'German': {'type': 'hardcoded', 'generator': create_german_network},
        'Italian': {'type': 'hardcoded', 'generator': create_italian_network},
        'ER_Sparse': {'type': 'synthetic', 'nodes': 8, 'topology': 'erdos_renyi', 'edge_prob': 0.15},
        'ER_Dense': {'type': 'synthetic', 'nodes': 8, 'topology': 'erdos_renyi', 'edge_prob': 0.5},
        'BA_8': {'type': 'synthetic', 'nodes': 8, 'topology': 'barabasi_albert', 'm': 2},
        'Grid_9': {'type': 'synthetic', 'nodes': 9, 'topology': 'grid'}
    }
    
    substrates = {}
    for name, config in substrate_configs.items():
        if config['type'] == 'hardcoded':
            substrate = config['generator']()
        else:
            substrate = generate_substrate_network(
                config['nodes'], 
                config['topology'], 
                **{k: v for k, v in config.items() if k not in ['type', 'nodes', 'topology']}
            )
        substrates[name] = substrate
        print(f"  Generated {name}: {len(substrate.nodes())} nodes, {len(substrate.edges())} edges")
    
    # Create the combined substrate figure
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Substrate Network Topologies for VNE Experiments', fontsize=16, fontweight='bold', y=0.98)
    
    positions = [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)]
    
    for idx, (name, substrate) in enumerate(substrates.items()):
        row, col = positions[idx]
        ax = axes[row, col]
        
        # Draw substrate network directly on subplot (avoid plot_substrate_network creating new figure)
        pos = nx.spring_layout(substrate, seed=42)
        node_sizes = [len(str(substrate.nodes[n]['cpu'])) * 400 + 600 for n in substrate.nodes()]

        # Draw with labels showing constraints
        nx.draw_networkx_nodes(substrate, pos, node_size=node_sizes, node_color='lightblue', ax=ax)
        nx.draw_networkx_edges(substrate, pos, width=2, ax=ax)

        # Node labels with CPU
        node_labels = {n: f"{n}\\nCPU:{substrate.nodes[n]['cpu']}" for n in substrate.nodes()}
        nx.draw_networkx_labels(substrate, pos, node_labels, font_size=9, ax=ax)

        # Edge labels with bandwidth 
        edge_labels = {}
        for e in substrate.edges():
            bw = substrate.edges[e]['bandwidth']
            edge_labels[e] = f"BW:{bw}"
        nx.draw_networkx_edge_labels(substrate, pos, edge_labels, font_size=8, ax=ax)

        ax.set_title(f"{name} Network\\n{len(substrate.nodes())} nodes, {len(substrate.edges())} edges", 
                    fontweight='bold', fontsize=12)
        ax.axis('off')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)  # Space for main title
    plt.savefig('substrate_networks_all.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: substrate_networks_all.png")

def generate_vnr_queue_figure(output_dir):
    """Generate VNR queue visualization showing all 20 VNRs used in experiments."""
    print("Generating VNR queue figure...")
    
    # Use the standard VNR queue (same as all experiments)
    vnr_queue = create_vnr_queue()
    
    # Use the working plot_all_vnrs function (saves to pictures/ folder)
    plot_all_vnrs(vnr_queue, title_prefix="VNR Queue", filename="vnr_queue.png")
    
    # Copy the file to topology experiment directory
    import shutil
    source = "pictures/vnr_queue.png"
    destination = output_dir / "vnr_queue.png"
    if os.path.exists(source):
        shutil.copy2(source, destination)
        print(f"  Saved: {destination}")
    else:
        print(f"  Warning: Could not find {source}")

def run_all_topology_experiments():
    """Run all 6 topology experiments with fixed visualizations."""
    print("Running all topology experiments...")
    
    # Create and run unified experiments
    experiment = UnifiedTopologyExperiments()
    
    # Change output directory to experiments/topology_experiment/
    experiments_dir = Path("experiments")
    experiments_dir.mkdir(exist_ok=True)
    experiment.output_base_dir = experiments_dir / "topology_experiment"
    experiment.output_base_dir.mkdir(exist_ok=True)
    
    # Generate substrate networks (with consistent seed)
    experiment.generate_substrates()
    
    # Run all 6 experiments
    results = experiment.run_all_experiments()
    
    return results

def main():
    """Main execution function."""
    print("COMPLETE TOPOLOGY EXPERIMENTS RUNNER")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Create main topology experiment directory
        experiments_dir = Path("experiments")
        experiments_dir.mkdir(exist_ok=True)
        topology_experiment_dir = experiments_dir / "topology_experiment"
        topology_experiment_dir.mkdir(exist_ok=True)
        
        # Step 1: Generate substrate networks figure in topology_experiment directory
        print("Generating substrate networks figure...")
        generate_substrate_networks_figure()
        # Move substrate figure to topology experiment directory
        import shutil
        if os.path.exists("substrate_networks_all.png"):
            shutil.move("substrate_networks_all.png", topology_experiment_dir / "substrate_networks_all.png")
            print(f"  Moved to: {topology_experiment_dir / 'substrate_networks_all.png'}")
        print()
        
        # Step 2: Generate VNR queue figure in topology_experiment directory
        generate_vnr_queue_figure(topology_experiment_dir)
        print()
        
        # Step 3: Run all topology experiments (also in topology_experiment directory)
        all_results = run_all_topology_experiments()
        print()
        
        # Summary
        print("ALL EXPERIMENTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("Generated files:")
        print("  experiments/topology_experiment/")
        print("    ├── substrate_networks_all.png - 6 substrate topologies")
        print("    ├── vnr_queue.png - 20 VNR queue visualization")
        print("    ├── german_experiment/ - 3 figures + JSON data")
        print("    ├── italian_experiment/ - 3 figures + JSON data")
        print("    ├── er_sparse_experiment/ - 3 figures + JSON data")
        print("    ├── er_dense_experiment/ - 3 figures + JSON data")
        print("    ├── ba_8_experiment/ - 3 figures + JSON data")
        print("    └── grid_9_experiment/ - 3 figures + JSON data")
        print()
        print("Total output for TOPOLOGY EXPERIMENT:")
        print("  - 2 analysis figures")
        print("  - 18 experiment figures (6 topologies × 3 figures)")
        print("  - 12 data files (6 experiments × 2 JSON files)")
        print("  - Grand total: 32 files")
        
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