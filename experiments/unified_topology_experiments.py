#!/usr/bin/env python3
"""
Unified Topology Experiments Runner

Runs all 6 topology experiments using:
- Exact same substrate networks as the working substrate figure
- Same 20 VNR queue for all experiments  
- All 4 algorithms: Simple_Greedy, RW_BFS, RW_MaxMatch, Yu2008
- Clean organized output: 3 figures per topology (timeline, utilization, metrics)

Output Structure:
topology_final/
├── substrate_networks_all.png (already done)
├── german_experiment/
├── italian_experiment/  
├── er_sparse_experiment/
├── er_dense_experiment/
├── ba_8_experiment/
└── grid_9_experiment/
"""

import sys
import random
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append('../src')

# Import required modules
from src.networks.substrate_networks import create_german_network, create_italian_network
from src.networks.vne_generators import generate_substrate_network
from src.networks.vnr_creation import create_vnr_queue
from src.algorithms.greedy import simple_greedy_algorithm
from src.algorithms.rw_bfs import rw_bfs_algorithm  
from src.algorithms.rw_maxmatch import rw_maxmatch_algorithm
from src.algorithms.yu_baseline import yu2008_algorithm, create_chunks
from src.simulation.simulation import vne_simulation
from src.metrics.metrics import calculate_acceptance_ratio, calculate_metrics_summary

class UnifiedTopologyExperiments:
    """Unified experiment runner for all 6 topologies."""
    
    def __init__(self):
        self.output_base_dir = Path("experiments/topology_experiment")
        self.output_base_dir.mkdir(exist_ok=True)
        
        # Use EXACT same parameters as working substrate figure
        self.substrate_configs = {
            'German': {'type': 'hardcoded', 'generator': create_german_network},
            'Italian': {'type': 'hardcoded', 'generator': create_italian_network},
            'ER_Sparse': {'type': 'synthetic', 'nodes': 8, 'topology': 'erdos_renyi', 'edge_prob': 0.15},
            'ER_Dense': {'type': 'synthetic', 'nodes': 8, 'topology': 'erdos_renyi', 'edge_prob': 0.5},
            'BA_8': {'type': 'synthetic', 'nodes': 8, 'topology': 'barabasi_albert', 'm': 2},
            'Grid_9': {'type': 'synthetic', 'nodes': 9, 'topology': 'grid'}
        }
        
        # All 4 algorithms
        self.algorithms = {
            'Simple_Greedy': simple_greedy_algorithm,
            'RW_BFS': rw_bfs_algorithm,
            'RW_MaxMatch': rw_maxmatch_algorithm,
            'Yu2008': yu2008_algorithm
        }
        
        self.substrates = {}
        self.vnr_queue = None
        
    def generate_substrates(self):
        """Generate exact same substrates as the working substrate figure."""
        print("Generating substrate networks (same as substrate figure)...")
        
        # CRITICAL: Use seed 100 for consistent results across all experiments
        # This matches our working substrate figure and gives consistent Yu2008 results
        random.seed(100)
        
        for name, config in self.substrate_configs.items():
            print(f"  Generating {name}...")
            
            if config['type'] == 'hardcoded':
                substrate = config['generator']()
            else:
                # Use same generation logic as substrate figure
                substrate = generate_substrate_network(
                    config['nodes'], 
                    config['topology'], 
                    **{k: v for k, v in config.items() if k not in ['type', 'nodes', 'topology']}
                )
            
            self.substrates[name] = substrate
            nodes = len(substrate.nodes())
            edges = len(substrate.edges())
            print(f"    {nodes} nodes, {edges} edges")
    
    def run_single_topology_experiment(self, topology_name, substrate):
        """Run experiment for one topology: 4 algorithms, 3 output figures."""
        print(f"\n{'='*50}")
        print(f"RUNNING {topology_name.upper()} EXPERIMENT")
        print(f"{'='*50}")
        
        # Create experiment directory
        exp_dir = self.output_base_dir / f"{topology_name.lower()}_experiment"
        exp_dir.mkdir(exist_ok=True)
        
        # Use same VNR queue for all algorithms (fair comparison)
        vnr_queue = create_vnr_queue()
        print(f"Using standard VNR queue: {len(vnr_queue)} VNRs")
        
        # Run all algorithms
        results = {}
        for alg_name, alg_func in self.algorithms.items():
            print(f"  Running {alg_name}...")
            
            try:
                if alg_name == "Yu2008":
                    # Special handling for Yu2008 chunked algorithm
                    substrate_working = substrate.copy()
                    self._initialize_substrate_resources(substrate_working)
                    chunks = create_chunks(vnr_queue, time_window=25)
                    alg_results = alg_func(substrate_working, chunks, time_window=25)
                    
                    # CRITICAL: Sort by arrival_time for proper timeline visualization
                    alg_results = sorted(alg_results, key=lambda x: x['arrival_time'])
                else:
                    # Standard simulation
                    alg_results = vne_simulation(substrate.copy(), vnr_queue, alg_func)
                
                results[alg_name] = alg_results
                
                # Calculate basic metrics
                successes = len([r for r in alg_results if r.get('success', False)])
                acceptance_ratio = successes / len(alg_results)
                print(f"    Results: {successes}/{len(alg_results)} success ({acceptance_ratio:.1%})")
                
            except Exception as e:
                print(f"    ERROR: {e}")
                results[alg_name] = []
        
        # Generate 3 figures for this topology
        self._generate_timeline_comparison(topology_name, results, exp_dir)
        self._generate_utilization_comparison(topology_name, substrate, results, exp_dir)
        self._generate_metrics_comparison(topology_name, results, exp_dir)
        
        # Save JSON results using working pattern from experiment_runner.py
        self._save_results_json(topology_name, results, exp_dir)
        
        print(f"[OK] Completed {topology_name} experiment")
        return results
    
    def _initialize_substrate_resources(self, substrate):
        """Initialize substrate available resources for Yu2008."""
        for node in substrate.nodes():
            substrate.nodes[node]['cpu_available'] = substrate.nodes[node]['cpu']
        for edge in substrate.edges():
            substrate.edges[edge]['bandwidth_available'] = substrate.edges[edge]['bandwidth']
    
    def _generate_timeline_comparison(self, topology_name, results, output_dir):
        """Generate timeline comparison using the ACTUAL working plot_simulation_timeline function."""
        print(f"    Generating timeline comparison...")
        
        from src.visualization.simulation_plots import plot_simulation_timeline
        from src.visualization.simulation_plots import _extract_timeline_data, _calculate_cumulative_acceptance
        import os
        
        # Use the working timeline function structure but for 4 algorithms
        fig, axes = plt.subplots(4, 2, figsize=(20, 24))  # 4 rows, 2 columns for 4 algorithms
        fig.suptitle(f'{topology_name} Network - Timeline Comparison (4 Algorithms)', 
                     fontsize=18, fontweight='bold', y=0.98)  # Add spacing from top
        
        alg_names = list(results.keys())
        
        for idx, (alg_name, alg_results) in enumerate(results.items()):
            if idx >= 4:  # Safety check
                break
                
            if alg_results:
                # Use the working _extract_timeline_data function
                arrival_times, successes = _extract_timeline_data(alg_results)
                cumulative_success = _calculate_cumulative_acceptance(successes)
                
                # Subplot 1: Success/failure scatter (left column)
                ax1 = axes[idx, 0]
                colors = ['green' if s else 'red' for s in successes]
                ax1.scatter(arrival_times, successes, c=colors, alpha=0.7, s=100)
                ax1.set_ylabel('Success (1) / Failure (0)')
                ax1.set_title(f'{alg_name} - Success/Failure Pattern', fontweight='bold', fontsize=12)
                ax1.set_ylim(-0.1, 1.1)
                ax1.set_yticks([0, 1])
                ax1.grid(True, alpha=0.3)
                if idx == 3:  # Last row
                    ax1.set_xlabel('Arrival Time')
                
                # Subplot 2: Cumulative acceptance ratio (right column)
                ax2 = axes[idx, 1]
                ax2.plot(arrival_times, cumulative_success, 'b-', linewidth=2, marker='o')
                ax2.set_ylabel('Cumulative Acceptance Ratio')
                ax2.set_title(f'{alg_name} - Cumulative Performance Over Time', fontweight='bold', fontsize=12)
                ax2.grid(True, alpha=0.3)
                ax2.set_ylim(0, 1.05)
                if idx == 3:  # Last row
                    ax2.set_xlabel('Arrival Time')
                    
                # Add summary stats
                total = len(alg_results)
                successful = sum(successes)
                acceptance_ratio = successful / total if total > 0 else 0
                ax1.text(0.02, 0.98, f'Total: {total}\\nSuccess: {successful}\\nRatio: {acceptance_ratio:.1%}',
                        transform=ax1.transAxes, fontsize=10, verticalalignment='top',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.95)  # Add space between suptitle and subplots
        output_path = output_dir / f"{topology_name.lower()}_timelines.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"      Saved: {output_path}")
    
    def _generate_utilization_comparison(self, topology_name, substrate, results, output_dir):
        """Generate actual resource utilization visualizations using working functions."""
        print(f"    Generating utilization comparison...")
        
        from src.visualization.resource_plots import plot_resource_utilization_snapshot
        from src.networks.vnr_creation import create_vnr_queue
        import networkx as nx
        import os
        
        # Create a 2x2 subplot for the 4 algorithms
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        fig.suptitle(f'{topology_name} Network - Resource Utilization Comparison', 
                     fontsize=16, fontweight='bold', y=0.98)  # Add spacing from top
        
        positions = [(0,0), (0,1), (1,0), (1,1)]
        vnr_queue = create_vnr_queue()
        
        for idx, (alg_name, alg_results) in enumerate(results.items()):
            if idx >= 4:  # Safety check
                break
                
            row, col = positions[idx]
            ax = axes[row, col]
            plt.sca(ax)  # Set current axes for the resource plot function
            
            if alg_results:
                # Find successful embeddings
                successful_results = [r for r in alg_results if r.get('success', False)]
                
                if successful_results:
                    try:
                        # Create substrate copy with proper resource tracking
                        substrate_copy = substrate.copy()
                        
                        # Initialize available resources properly
                        for node in substrate_copy.nodes():
                            substrate_copy.nodes[node]['cpu_available'] = substrate_copy.nodes[node]['cpu']
                        for edge in substrate_copy.edges():
                            substrate_copy.edges[edge]['bandwidth_available'] = substrate_copy.edges[edge]['bandwidth']
                        
                        # Find peak utilization snapshot (working approach from experiment_runner.py)
                        peak_embeddings = self._find_peak_utilization_snapshot(successful_results, vnr_queue)
                        active_embeddings = peak_embeddings['active_embeddings']
                        
                        if active_embeddings:
                            # Use the working components directly without file saving
                            plt.sca(ax)
                            pos = nx.spring_layout(substrate_copy, seed=42)
                            
                            from src.visualization.resource_plots import _calculate_utilization_from_embeddings, _draw_resource_network
                            
                            # Calculate utilization using the working function
                            node_utilization, edge_utilization = _calculate_utilization_from_embeddings(substrate_copy, active_embeddings)
                            
                            # Draw the network using the working function  
                            _draw_resource_network(substrate_copy, pos, node_utilization, edge_utilization, edge_labels=True)
                            
                            ax.set_title(f'{alg_name.replace("_", " ")} Peak Resource Utilization\\n(T={peak_embeddings["time"]}, {peak_embeddings["count"]} active VNRs)', 
                                        fontweight='bold', fontsize=10)
                            ax.axis('off')
                            
                        else:
                            ax.text(0.5, 0.5, f'{alg_name}\\nNo Valid\\nEmbeddings',
                                   ha='center', va='center', transform=ax.transAxes, fontsize=12,
                                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))
                            ax.set_title(f'{alg_name}', fontweight='bold', fontsize=12)
                            ax.axis('off')
                            
                    except Exception as e:
                        print(f"        Warning: Could not generate utilization for {alg_name}: {e}")
                        ax.text(0.5, 0.5, f'{alg_name}\\nVisualization\\nError',
                               ha='center', va='center', transform=ax.transAxes, fontsize=12,
                               bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral"))
                        ax.set_title(f'{alg_name}', fontweight='bold', fontsize=12)
                        ax.axis('off')
                else:
                    ax.text(0.5, 0.5, f'{alg_name}\\nNo Successful\\nEmbeddings',
                           ha='center', va='center', transform=ax.transAxes, fontsize=12,
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))
                    ax.set_title(f'{alg_name}', fontweight='bold', fontsize=12)
                    ax.axis('off')
            else:
                ax.text(0.5, 0.5, f'{alg_name}\\nNo Data',
                       ha='center', va='center', transform=ax.transAxes, fontsize=12,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral"))
                ax.set_title(f'{alg_name}', fontweight='bold', fontsize=12)
                ax.axis('off')
        
        plt.tight_layout()
        
        # Add a single colorbar for the entire figure
        from src.visualization.resource_plots import _add_visualization_elements
        
        # Add colorbar on the right side of the entire figure
        sm_nodes = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(vmin=0, vmax=1))
        sm_nodes.set_array([])
        
        # Position colorbar on the right side
        cbar_ax = fig.add_axes([0.92, 0.3, 0.02, 0.4])  # [left, bottom, width, height]
        cbar = plt.colorbar(sm_nodes, cax=cbar_ax)
        cbar.set_label('CPU Utilization', rotation=270, labelpad=15)
        
        # Add edge utilization legend
        legend_elements = [
            plt.Line2D([0], [0], color='lightgray', linewidth=1, linestyle='--', label='Unused (0%)'),
            plt.Line2D([0], [0], color='lightblue', linewidth=2, label='Light (1-33%)'),
            plt.Line2D([0], [0], color='blue', linewidth=3, label='Medium (34-66%)'),
            plt.Line2D([0], [0], color='darkblue', linewidth=4, label='Heavy (67-100%)')
        ]
        
        # Position legend on the left side
        fig.legend(handles=legend_elements, title='Edge Bandwidth Utilization', 
                  loc='center left', bbox_to_anchor=(0.02, 0.5))
        
        # Adjust layout to accommodate colorbar and legend
        plt.subplots_adjust(left=0.15, right=0.9, top=0.93)  # Add space between suptitle and subplots
        
        output_path = output_dir / f"{topology_name.lower()}_utilization.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"      Saved: {output_path}")
    
    def _generate_metrics_comparison(self, topology_name, results, output_dir):
        """Generate metrics comparison using EXACT working code from experiment_runner.py."""
        print(f"    Generating metrics comparison...")
        
        # Calculate enhanced metrics like the working code does
        from src.metrics.metrics import calculate_revenue, calculate_cost
        vnr_queue = create_vnr_queue()
        
        plot_data = {}
        for alg_name, alg_results in results.items():
            if alg_results:
                # Calculate comprehensive metrics like the working experiment
                enhanced_results = []
                for result in alg_results:
                    if result.get('success', False):
                        vnr = next(v for v in vnr_queue if v.graph['vnr_id'] == result['vnr_id'])
                        revenue = calculate_revenue(vnr)
                        cost = calculate_cost(vnr, result['node_mapping'], result['link_mapping'])
                        enhanced_results.append({**result, 'revenue': revenue, 'cost': cost})
                    else:
                        enhanced_results.append({**result, 'revenue': 0, 'cost': 0})
                
                # Calculate summary metrics
                total = len(enhanced_results)
                successful = len([r for r in enhanced_results if r.get('success', False)])
                total_revenue = sum(r['revenue'] for r in enhanced_results)
                total_cost = sum(r['cost'] for r in enhanced_results)
                acceptance_ratio = successful / total if total > 0 else 0
                revenue_cost_ratio = total_revenue / total_cost if total_cost > 0 else 0
                
                plot_data[alg_name] = {
                    'metrics': {
                        'total_requests': total,
                        'successful_requests': successful,
                        'acceptance_ratio': acceptance_ratio,
                        'total_revenue': total_revenue,
                        'total_cost': total_cost,
                        'revenue_cost_ratio': revenue_cost_ratio
                    }
                }
        
        # EXACT code from experiment_runner.py comprehensive comparison
        if len(plot_data) > 1:
            algorithms = list(plot_data.keys())
            acceptance_ratios = [data['metrics']['acceptance_ratio'] for data in plot_data.values()]
            
            plt.figure(figsize=(15, 10))
            
            # Main comparison plot
            plt.subplot(2, 2, 1)
            bars = plt.bar(algorithms, acceptance_ratios, color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])
            plt.ylabel('Acceptance Ratio')
            plt.title(f'Algorithm Comparison - {topology_name}')
            plt.ylim(0, 1.05)
            for bar, ratio in zip(bars, acceptance_ratios):
                plt.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                        f'{ratio:.3f}', ha='center', va='bottom')
            plt.grid(True, alpha=0.3)
            
            # Revenue comparison
            plt.subplot(2, 2, 2)
            revenues = [data['metrics']['total_revenue'] for data in plot_data.values()]
            plt.bar(algorithms, revenues, color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])
            plt.ylabel('Total Revenue')
            plt.title('Revenue Comparison')
            plt.grid(True, alpha=0.3)
            
            # Cost comparison
            plt.subplot(2, 2, 3)
            costs = [data['metrics']['total_cost'] for data in plot_data.values()]
            plt.bar(algorithms, costs, color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])
            plt.ylabel('Total Cost')
            plt.title('Cost Comparison')
            plt.grid(True, alpha=0.3)
            
            # Revenue/Cost ratio
            plt.subplot(2, 2, 4)
            ratios = [data['metrics']['revenue_cost_ratio'] for data in plot_data.values()]
            plt.bar(algorithms, ratios, color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])
            plt.ylabel('Revenue/Cost Ratio')
            plt.title('Efficiency Comparison')
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            output_path = output_dir / f"{topology_name.lower()}_metrics.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"      Saved: {output_path}")
    
    def _save_results_json(self, topology_name, results, output_dir):
        """Save results as JSON using working pattern from experiment_runner.py."""
        print(f"    Saving JSON results...")
        
        # Calculate enhanced metrics for summary
        from src.metrics.metrics import calculate_revenue, calculate_cost
        vnr_queue = create_vnr_queue()
        
        # Create metadata
        metadata = {
            'topology': topology_name,
            'experiment_date': datetime.now().isoformat(),
            'total_algorithms': len(results),
            'vnr_queue_size': len(vnr_queue)
        }
        
        with open(output_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Save results summary (only serializable data)
        serializable_results = {}
        for alg_name, alg_results in results.items():
            if alg_results:
                # Calculate summary metrics like experiment_runner.py
                enhanced_results = []
                for result in alg_results:
                    if result.get('success', False):
                        try:
                            vnr = next(v for v in vnr_queue if v.graph['vnr_id'] == result['vnr_id'])
                            revenue = calculate_revenue(vnr)
                            cost = calculate_cost(vnr, result['node_mapping'], result['link_mapping'])
                            enhanced_results.append({**result, 'revenue': revenue, 'cost': cost})
                        except:
                            enhanced_results.append({**result, 'revenue': 0, 'cost': 0})
                    else:
                        enhanced_results.append({**result, 'revenue': 0, 'cost': 0})
                
                # Calculate summary metrics
                total = len(enhanced_results)
                successful = len([r for r in enhanced_results if r.get('success', False)])
                total_revenue = sum(r['revenue'] for r in enhanced_results)
                total_cost = sum(r['cost'] for r in enhanced_results)
                acceptance_ratio = successful / total if total > 0 else 0
                revenue_cost_ratio = total_revenue / total_cost if total_cost > 0 else 0
                
                serializable_results[alg_name] = {
                    'metrics': {
                        'total_requests': total,
                        'successful_requests': successful,
                        'acceptance_ratio': acceptance_ratio,
                        'total_revenue': total_revenue,
                        'total_cost': total_cost,
                        'revenue_cost_ratio': revenue_cost_ratio
                    },
                    'status': 'SUCCESS'
                }
            else:
                serializable_results[alg_name] = {
                    'status': 'ERROR',
                    'metrics': {}
                }
        
        with open(output_dir / 'results_summary.json', 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"      Saved: {output_dir / 'results_summary.json'}")
    
    def _find_peak_utilization_snapshot(self, results, vnr_queue):
        """Find the time point with maximum active VNRs for realistic utilization visualization"""
        # Create timeline of all arrival and departure events
        events = []
        
        for result in results:
            if result['success']:
                vnr = next(v for v in vnr_queue if v.graph['vnr_id'] == result['vnr_id'])
                arrival_time = vnr.graph['arrival_time']
                departure_time = arrival_time + vnr.graph['lifetime']
                
                events.append({
                    'time': arrival_time,
                    'type': 'ARRIVAL',
                    'vnr_id': result['vnr_id'],
                    'result': result,
                    'vnr': vnr
                })
                events.append({
                    'time': departure_time,
                    'type': 'DEPARTURE',
                    'vnr_id': result['vnr_id']
                })
        
        # Sort events by time
        events.sort(key=lambda x: (x['time'], x['type'] == 'DEPARTURE'))  # Departures before arrivals at same time
        
        # Track active VNRs and find peak
        active_vnrs = {}
        max_active = 0
        peak_time = 0
        peak_active = {}
        
        for event in events:
            if event['type'] == 'ARRIVAL':
                active_vnrs[event['vnr_id']] = {
                    'result': event['result'],
                    'vnr': event['vnr']
                }
            else:  # DEPARTURE
                if event['vnr_id'] in active_vnrs:
                    del active_vnrs[event['vnr_id']]
            
            # Check if this is a new peak
            if len(active_vnrs) > max_active:
                max_active = len(active_vnrs)
                peak_time = event['time']
                peak_active = active_vnrs.copy()
        
        # Convert to format expected by resource visualization
        active_embeddings = {}
        for vnr_id, data in peak_active.items():
            result = data['result']
            vnr = data['vnr']
            if 'node_mapping' in result and 'link_mapping' in result:
                active_embeddings[vnr_id] = (
                    result['node_mapping'],
                    result['link_mapping'],
                    vnr
                )
        
        return {
            'time': peak_time,
            'count': len(active_embeddings),
            'active_embeddings': active_embeddings
        }
    
    def run_all_experiments(self):
        """Run experiments for all 6 topologies."""
        print("UNIFIED TOPOLOGY EXPERIMENTS")
        print("=" * 60)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Generate substrates (same as substrate figure)
        self.generate_substrates()
        
        # Run experiment for each topology
        all_results = {}
        for topology_name, substrate in self.substrates.items():
            topology_results = self.run_single_topology_experiment(topology_name, substrate)
            all_results[topology_name] = topology_results
        
        print(f"\n{'='*60}")
        print("ALL EXPERIMENTS COMPLETED!")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nOutput directory: {self.output_base_dir}")
        print("Generated:")
        print("  - 1 substrate networks figure (already exists)")
        print("  - 6 topology experiments × 3 figures each = 18 figures")
        print("  - Total: 19 figures")
        
        return all_results

if __name__ == "__main__":
    experiment = UnifiedTopologyExperiments()
    results = experiment.run_all_experiments()