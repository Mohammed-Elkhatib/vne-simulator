#!/usr/bin/env python3
"""
Unified Scalability Experiments - EXACT COPY of working topology/load patterns

Tests 4 VNE algorithms across 4 substrate network sizes (8, 12, 16, 20 nodes)
using the same standard VNR queue for fair comparison.

COPIED EXACTLY from working unified_topology_experiments.py patterns.
"""

import sys
import os
import random
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
from pathlib import Path
from datetime import datetime
import networkx as nx

# Add src to path - works from both project root and experiments/ directory
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
src_path = project_root / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import required modules - EXACT COPY from working topology experiments
from src.networks.substrate_networks import create_german_network, create_italian_network
from src.networks.vne_generators import generate_substrate_network
from src.networks.vnr_creation import create_vnr_queue
from src.algorithms.greedy import simple_greedy_algorithm
from src.algorithms.rw_bfs import rw_bfs_algorithm  
from src.algorithms.rw_maxmatch import rw_maxmatch_algorithm
from src.algorithms.yu_baseline import yu2008_algorithm, create_chunks
from src.simulation.simulation import vne_simulation
from src.metrics.metrics import calculate_acceptance_ratio, calculate_metrics_summary


class UnifiedScalabilityExperiments:
    """Unified scalability experiment runner - exact copy of working topology patterns."""
    
    def __init__(self):
        self.output_base_dir = Path("scalability_experiment")
        self.output_base_dir.mkdir(parents=True, exist_ok=True)
        
        # Global seed for reproducible substrate generation
        random.seed(100)
        
        # Network size configurations
        self.network_configs = {
            '8_nodes': {
                'size': 8,
                'connection_prob': 0.4,
                'description': '8-node Erdős-Rényi network',
                'viz_seed': 42,
                'timeout_minutes': 10
            },
            '12_nodes': {
                'size': 12, 
                'connection_prob': 0.4,
                'description': '12-node Erdős-Rényi network',
                'viz_seed': 42,
                'timeout_minutes': 15
            },
            '16_nodes': {
                'size': 16,
                'connection_prob': 0.1,
                'description': '16-node Erdős-Rényi network', 
                'viz_seed': 42,
                'timeout_minutes': 25
            },
            '20_nodes': {
                'size': 20,
                'connection_prob': 0.06,
                'description': '20-node Erdős-Rényi network',
                'viz_seed': 42,
                'timeout_minutes': 35
            }
        }
        
        # Algorithm configurations - EXACT COPY from topology experiments
        self.algorithms = {
            'Simple_Greedy': simple_greedy_algorithm,
            'RW_BFS': rw_bfs_algorithm,
            'RW_MaxMatch': rw_maxmatch_algorithm,
            'Yu2008': yu2008_algorithm
        }
    
    def _create_substrate_network(self, config):
        """Create substrate network with specified configuration."""
        substrate = generate_substrate_network(
            nodes=config['size'],
            topology='erdos_renyi',
            edge_prob=config['connection_prob'],
            seed=config['viz_seed']
        )
        
        # Ensure connectivity for VNE compliance
        if not nx.is_connected(substrate):
            print(f"Warning: Generated {config['size']}-node network not connected, regenerating...")
            for attempt in range(3):
                substrate = generate_substrate_network(
                    nodes=config['size'],
                    topology='erdos_renyi', 
                    edge_prob=config['connection_prob'] + 0.1 * (attempt + 1),
                    seed=config['viz_seed']
                )
                if nx.is_connected(substrate):
                    break
        
        return substrate
    
    def run_single_network_experiment(self, network_name, config, vnr_queue):
        """Run complete experiment for single network size - EXACT COPY of topology pattern."""
        print(f"\n=== Running {network_name} Experiment ===")
        
        # Create substrate network
        substrate = self._create_substrate_network(config)
        print(f"Substrate: {len(substrate.nodes())} nodes, {len(substrate.edges())} edges")
        
        # Create experiment directory
        exp_dir = self.output_base_dir / f"{network_name}_experiment"
        exp_dir.mkdir(exist_ok=True)
        
        # Run all algorithms - EXACT COPY from topology experiments
        results = {}
        for alg_name, alg_func in self.algorithms.items():
            print(f"  Running {alg_name}...")
            
            try:
                if alg_name == "Yu2008":
                    # Special handling for Yu2008 chunked algorithm - EXACT COPY
                    substrate_working = substrate.copy()
                    self._initialize_substrate_resources(substrate_working)
                    chunks = create_chunks(vnr_queue, time_window=25)
                    alg_results = alg_func(substrate_working, chunks, time_window=25)
                    
                    # CRITICAL: Sort by arrival_time for proper timeline visualization
                    alg_results = sorted(alg_results, key=lambda x: x['arrival_time'])
                else:
                    # Standard simulation - EXACT COPY
                    alg_results = vne_simulation(substrate.copy(), vnr_queue, alg_func)
                
                results[alg_name] = alg_results
                
                # Calculate basic metrics - EXACT COPY
                successes = len([r for r in alg_results if r.get('success', False)])
                acceptance_ratio = successes / len(alg_results)
                print(f"    Results: {successes}/{len(alg_results)} success ({acceptance_ratio:.1%})")
                
            except Exception as e:
                print(f"    ERROR: {e}")
                results[alg_name] = []
        
        # Generate substrate network visualization
        self._generate_substrate_visualization(network_name, config, substrate, exp_dir)
        
        # Generate 3 figures for this network size - EXACT COPY from topology
        self._generate_timeline_comparison(network_name, results, exp_dir)
        utilization_data = self._generate_utilization_comparison(network_name, config, substrate, results, exp_dir)
        self._generate_metrics_comparison(network_name, results, exp_dir)

        # Save JSON results - EXACT COPY from topology
        self._save_results_json(network_name, results, exp_dir, utilization_data)
        
        print(f"[OK] Completed {network_name} experiment")
        return results
    
    def _initialize_substrate_resources(self, substrate):
        """Initialize substrate available resources for Yu2008 - EXACT COPY."""
        for node in substrate.nodes():
            substrate.nodes[node]['cpu_available'] = substrate.nodes[node]['cpu']
        for edge in substrate.edges():
            substrate.edges[edge]['bandwidth_available'] = substrate.edges[edge]['bandwidth']
    
    def _find_peak_utilization_snapshot(self, results, vnr_queue):
        """Find the time point with maximum active VNRs for realistic utilization visualization - EXACT COPY"""
        # Create timeline of all arrival and departure events
        events = []
        
        for result in results:
            if result['success']:
                vnr = next(v for v in vnr_queue if v.graph['vnr_id'] == result['vnr_id'])

                # CRITICAL FIX: Use embedding_time for Yu2008 (accounts for retries)
                embedding_time = result.get('embedding_time', vnr.graph['arrival_time'])
                departure_time = embedding_time + vnr.graph['lifetime']

                events.append({
                    'time': embedding_time,
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
        
        # Sort events by time - CRITICAL: Departures before arrivals at same time
        events.sort(key=lambda x: (x['time'], x['type'] != 'DEPARTURE'))  # False < True, so DEPARTURE comes first
        
        # Track active VNRs at each time point
        active_vnrs = {}
        max_active_count = 0
        peak_time = 0
        peak_embeddings = []
        
        for event in events:
            if event['type'] == 'ARRIVAL':
                active_vnrs[event['vnr_id']] = event
            else:  # DEPARTURE
                if event['vnr_id'] in active_vnrs:
                    del active_vnrs[event['vnr_id']]
            
            # Check if this is the new peak
            if len(active_vnrs) > max_active_count:
                max_active_count = len(active_vnrs)
                peak_time = event['time']
                peak_embeddings = [info['result'] for info in active_vnrs.values()]
        
        # Convert peak_embeddings list to dictionary format expected by _calculate_utilization_from_embeddings
        active_embeddings_dict = {}
        for result in peak_embeddings:
            vnr = next(v for v in vnr_queue if v.graph['vnr_id'] == result['vnr_id'])
            active_embeddings_dict[result['vnr_id']] = (
                result['node_mapping'], 
                result['link_mapping'], 
                vnr
            )
        
        return {
            'time': peak_time,
            'count': max_active_count,
            'active_embeddings': active_embeddings_dict
        }
    
    def _generate_substrate_visualization(self, network_name, config, substrate, output_dir):
        """Generate substrate network visualization with custom seed for clarity."""
        print(f"    Generating substrate visualization...")
        
        from src.visualization.network_plots import plot_substrate_network
        
        # Generate plot
        plot_substrate_network(
            substrate, 
            title=f"{config['description']} - Substrate Network",
            seed=config['viz_seed']
        )
        
        # Save the plot
        substrate_file = output_dir / f"{network_name}_substrate.png"
        plt.savefig(substrate_file, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _generate_timeline_comparison(self, network_name, results, output_dir):
        """Generate timeline comparison using the ACTUAL working plot_simulation_timeline function - EXACT COPY."""
        print(f"    Generating timeline comparison...")
        
        from src.visualization.simulation_plots import plot_simulation_timeline
        from src.visualization.simulation_plots import _extract_timeline_data, _calculate_cumulative_acceptance
        import os
        
        # Use the working timeline function structure but for 4 algorithms - EXACT COPY
        fig, axes = plt.subplots(4, 2, figsize=(20, 24))  # 4 rows, 2 columns for 4 algorithms
        fig.suptitle(f'{network_name} Network - Timeline Comparison (4 Algorithms)', 
                     fontsize=18, fontweight='bold', y=0.98)  # Add spacing from top
        
        alg_names = list(results.keys())
        
        for idx, (alg_name, alg_results) in enumerate(results.items()):
            if idx >= 4:  # Safety check
                break
                
            if alg_results:
                # Use the working _extract_timeline_data function - EXACT COPY
                arrival_times, successes = _extract_timeline_data(alg_results)
                cumulative_success = _calculate_cumulative_acceptance(successes)
                
                # Subplot 1: Success/failure scatter (left column) - EXACT COPY
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
                
                # Subplot 2: Cumulative acceptance ratio (right column) - EXACT COPY
                ax2 = axes[idx, 1]
                ax2.plot(arrival_times, cumulative_success, 'b-', linewidth=2, marker='o')
                ax2.set_ylabel('Cumulative Acceptance Ratio')
                ax2.set_title(f'{alg_name} - Cumulative Performance Over Time', fontweight='bold', fontsize=12)
                ax2.grid(True, alpha=0.3)
                ax2.set_ylim(0, 1.05)
                if idx == 3:  # Last row
                    ax2.set_xlabel('Arrival Time')
                    
                # Add summary stats - EXACT COPY
                total = len(alg_results)
                successful = sum(successes)
                acceptance_ratio = successful / total if total > 0 else 0
                ax1.text(0.02, 0.98, f'Total: {total}\\nSuccess: {successful}\\nRatio: {acceptance_ratio:.1%}',
                        transform=ax1.transAxes, fontsize=10, verticalalignment='top',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.95)  # Add space between suptitle and subplots
        output_path = output_dir / f"{network_name.lower()}_timelines.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"      Saved: {output_path}")
    
    def _generate_utilization_comparison(self, network_name, config, substrate, results, output_dir):
        """Generate actual resource utilization visualizations using working functions - EXACT COPY."""
        print(f"    Generating utilization comparison...")
        
        from src.visualization.resource_plots import plot_resource_utilization_snapshot
        from src.networks.vnr_creation import create_vnr_queue
        import networkx as nx
        import numpy as np  # ADDED for utilization metrics calculation
        import os
        
        # Create a 2x2 subplot for the 4 algorithms - EXACT COPY
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        fig.suptitle(f'{network_name} Network - Resource Utilization Comparison', 
                     fontsize=16, fontweight='bold', y=0.98)  # Add spacing from top
        
        positions = [(0,0), (0,1), (1,0), (1,1)]
        vnr_queue = create_vnr_queue()

        # ADDED: Dictionary to store utilization metrics for each algorithm
        utilization_metrics = {}
        
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
                            pos = nx.spring_layout(substrate_copy, seed=config['viz_seed'])
                            
                            from src.visualization.resource_plots import _calculate_utilization_from_embeddings, _draw_resource_network
                            
                            # Calculate utilization using the working function
                            node_utilization, edge_utilization = _calculate_utilization_from_embeddings(substrate_copy, active_embeddings)

                            # ADDED: Extract and save DETAILED utilization metrics
                            node_values = list(node_utilization.values())
                            edge_values = [v for v in edge_utilization.values() if v > 0]

                            utilization_metrics[alg_name] = {
                                'peak_time': peak_embeddings['time'],
                                'peak_active_vnrs': peak_embeddings['count'],
                                'node_utilization': {str(node): float(util) for node, util in node_utilization.items()},
                                'edge_utilization': {f"{e[0]}-{e[1]}": float(util) for e, util in edge_utilization.items() if util > 0},
                                'summary': {
                                    'avg_node_utilization': float(np.mean(node_values)) if node_values else 0.0,
                                    'max_node_utilization': float(np.max(node_values)) if node_values else 0.0,
                                    'min_node_utilization': float(np.min(node_values)) if node_values else 0.0,
                                    'std_node_utilization': float(np.std(node_values)) if node_values else 0.0,
                                    'avg_edge_utilization': float(np.mean(edge_values)) if edge_values else 0.0,
                                    'max_edge_utilization': float(np.max(edge_values)) if edge_values else 0.0,
                                    'num_nodes_over_80pct': int(sum(1 for v in node_values if v > 0.8)),
                                    'num_nodes_over_50pct': int(sum(1 for v in node_values if v > 0.5)),
                                    'num_nodes_unused': int(sum(1 for v in node_values if v == 0)),
                                    'num_edges_utilized': len(edge_values)
                                }
                            }

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
        
        output_path = output_dir / f"{network_name.lower()}_utilization.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"      Saved: {output_path}")

        # ADDED: Return utilization metrics for JSON saving
        return utilization_metrics
    
    def _generate_metrics_comparison(self, network_name, results, output_dir):
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
            plt.title(f'Algorithm Comparison - {network_name}')
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
            output_path = output_dir / f"{network_name.lower()}_metrics.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"      Saved: {output_path}")
    
    def _save_results_json(self, network_name, results, output_dir, utilization_data=None):
        """Save JSON results - EXACT COPY from topology experiments."""

        # Calculate comprehensive metrics for each algorithm
        from src.metrics.metrics import calculate_revenue, calculate_cost
        vnr_queue = create_vnr_queue()

        summary_data = {}
        for alg_name, alg_results in results.items():
            if alg_results:  # Only process if we have results
                # Enhance results with revenue/cost like the metrics comparison function does
                enhanced_results = []
                for result in alg_results:
                    if result.get('success', False):
                        vnr = next(v for v in vnr_queue if v.graph['vnr_id'] == result['vnr_id'])
                        revenue = calculate_revenue(vnr)
                        cost = calculate_cost(vnr, result['node_mapping'], result['link_mapping'])
                        enhanced_results.append({**result, 'revenue': revenue, 'cost': cost})
                    else:
                        enhanced_results.append({**result, 'revenue': 0, 'cost': 0})

                metrics = calculate_metrics_summary(enhanced_results)
                result_entry = {
                    'metrics': metrics,
                    'status': 'SUCCESS'
                }

                # ADDED: Include utilization data if available
                if utilization_data and alg_name in utilization_data:
                    result_entry['utilization'] = utilization_data[alg_name]

                summary_data[alg_name] = result_entry
            else:
                summary_data[alg_name] = {
                    'status': 'FAILED',
                    'error': 'No results generated'
                }
        
        # Save results summary
        results_file = output_dir / 'results_summary.json'
        with open(results_file, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        # Save metadata
        metadata = {
            'experiment_type': 'scalability_testing',
            'network_name': network_name,
            'experiment_date': datetime.now().isoformat(),
            'algorithms_tested': list(self.algorithms.keys())
        }
        
        metadata_file = output_dir / 'metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def run_all_experiments(self):
        """Run complete scalability experiment suite."""
        print("STARTING UNIFIED SCALABILITY EXPERIMENTS")
        print("=" * 70)
        
        # Create standard VNR queue (same for all experiments)
        vnr_queue = create_vnr_queue()
        print(f"Created standard VNR queue: {len(vnr_queue)} requests")
        
        # Generate shared VNR queue visualization - EXACT COPY from topology experiments
        print("Generating shared VNR queue visualization...")
        from src.visualization.network_plots import plot_all_vnrs
        plot_all_vnrs(vnr_queue, title_prefix="Scalability Testing", filename="vnr_queue.png")
        
        # Copy to main experiment directory - EXACT COPY from topology experiments  
        import shutil
        vnr_source = "pictures/vnr_queue.png"
        vnr_dest = self.output_base_dir / "vnr_queue.png"
        if os.path.exists(vnr_source):
            shutil.copy2(vnr_source, vnr_dest)
            print(f"  Saved: {vnr_dest}")
        else:
            print(f"  Warning: {vnr_source} not found")
        
        # Run experiments for all network sizes
        all_results = {}
        test_configs = {
            '8_nodes': self.network_configs['8_nodes'],
            '12_nodes': self.network_configs['12_nodes'],
            '16_nodes': self.network_configs['16_nodes'],
            '20_nodes': self.network_configs['20_nodes']
        }
        for network_name, config in test_configs.items():
            try:
                results = self.run_single_network_experiment(network_name, config, vnr_queue)
                all_results[network_name] = results
            except Exception as e:
                print(f"Failed {network_name} experiment: {str(e)}")
                all_results[network_name] = {'status': 'EXPERIMENT_FAILED', 'error': str(e)}
        
        print("\nSCALABILITY EXPERIMENTS COMPLETED!")
        print(f"Results saved to: {self.output_base_dir}")
        
        return all_results


def main():
    """Main entry point."""
    scalability_exp = UnifiedScalabilityExperiments()
    return scalability_exp.run_all_experiments()


if __name__ == "__main__":
    main()