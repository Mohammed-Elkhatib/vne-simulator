#!/usr/bin/env python3
"""
Unified Load Testing Experiments Runner

Runs load testing experiments with 3 demand scenarios:
- Light demand: Lower CPU/bandwidth requirements, diverse VNR topologies
- Medium demand: Moderate CPU/bandwidth requirements, diverse VNR topologies  
- Heavy demand: Higher CPU/bandwidth requirements, diverse VNR topologies

Each scenario uses:
- Same substrate network (consistency across scenarios)
- Same 4 algorithms: Simple_Greedy, RW_BFS, RW_MaxMatch, Yu2008
- 20 diverse VNRs per scenario (not all 2-3 node chains)
- 3 output figures per scenario (timeline, utilization, metrics)

Output Structure:
experiments/load_testing_experiment/
├── substrate_network.png (shared)
├── light_demand_experiment/
├── medium_demand_experiment/
└── heavy_demand_experiment/
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
import copy

# Add src to path
sys.path.append('../src')

from src.networks.substrate_networks import create_german_network
from src.networks.vne_generators import generate_vnr
from src.algorithms.greedy import simple_greedy_algorithm
from src.algorithms.rw_bfs import rw_bfs_algorithm  
from src.algorithms.rw_maxmatch import rw_maxmatch_algorithm
from src.algorithms.yu_baseline import yu2008_algorithm, create_chunks
from src.simulation.simulation import vne_simulation
from src.metrics.metrics import calculate_acceptance_ratio
from src.visualization.simulation_plots import _extract_timeline_data, _calculate_cumulative_acceptance

class UnifiedLoadExperiments:
    """Unified experiment runner for load testing scenarios."""
    
    def __init__(self):
        self.output_base_dir = Path("experiments") / "load_testing_experiment"
        self.output_base_dir.mkdir(parents=True, exist_ok=True)
        
        # Use German network as substrate (proven good performance from topology experiments)
        self.substrate_network = None
        
        # All 4 algorithms
        self.algorithms = {
            'Simple_Greedy': simple_greedy_algorithm,
            'RW_BFS': rw_bfs_algorithm,
            'RW_MaxMatch': rw_maxmatch_algorithm,
            'Yu2008': yu2008_algorithm
        }
        
        # Load scenarios matching original VNE load testing methodology
        # CRITICAL: This follows standard VNE literature approach - increasing VNR count + demand
        self.load_scenarios = {
            'light_demand': {
                'count': 15,                   # Fewer VNRs (original methodology)
                'cpu_range': (10, 20),         # Light CPU requirements (original)
                'bandwidth_range': (5, 15),    # Light bandwidth requirements (original)
                'vnr_sizes': [2, 3, 4],        # Mix of small VNRs (diverse)
                'topologies': ['path', 'star', 'cycle'],  # Simple topologies
                'description': 'Light load: 15 diverse VNRs with low resource demands'
            },
            'medium_demand': {
                'count': 25,                   # Medium VNR count (original methodology)
                'cpu_range': (15, 30),         # Medium CPU requirements (original)  
                'bandwidth_range': (10, 25),   # Medium bandwidth requirements (original)
                'vnr_sizes': [3, 4, 5],        # Mix of medium VNRs (diverse)
                'topologies': ['path', 'star', 'cycle', 'tree'],  # More variety
                'description': 'Medium load: 25 diverse VNRs with moderate resource demands'
            },
            'heavy_demand': {
                'count': 35,                   # High VNR count (original methodology)
                'cpu_range': (20, 40),         # Heavy CPU requirements (original)
                'bandwidth_range': (15, 35),   # Heavy bandwidth requirements (original)  
                'vnr_sizes': [4, 5, 6],        # Mix of larger VNRs (diverse)
                'topologies': ['star', 'cycle', 'tree', 'random'],  # Complex topologies
                'description': 'Heavy load: 35 diverse VNRs with high resource demands'
            }
        }
        
    def generate_substrate(self):
        """Generate substrate network (German network for consistency)."""
        print("Generating substrate network (German)...")
        
        # Use seed 100 for consistency with topology experiments
        random.seed(100)
        self.substrate_network = create_german_network()
        
        nodes = len(self.substrate_network.nodes())
        edges = len(self.substrate_network.edges())
        print(f"  German substrate: {nodes} nodes, {edges} edges")
        
        # Generate and save substrate figure
        from src.visualization.network_plots import plot_substrate_network
        plt.figure(figsize=(10, 8))
        plot_substrate_network(self.substrate_network, "Load Testing Substrate Network", seed=42)
        plt.savefig(self.output_base_dir / "substrate_network.png", dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  Saved: {self.output_base_dir / 'substrate_network.png'}")
    
    def generate_diverse_vnr_queue(self, scenario_name, scenario_config):
        """Generate diverse VNR queue for a specific load scenario."""
        print(f"  Generating diverse VNRs for {scenario_name}...")
        
        vnr_queue = []
        vnr_sizes = scenario_config['vnr_sizes']
        topologies = scenario_config['topologies']
        cpu_range = scenario_config['cpu_range']
        bandwidth_range = scenario_config['bandwidth_range']
        
        vnr_count = scenario_config['count']  # Use variable VNR count per scenario
        for vnr_id in range(vnr_count):
            # Vary VNR characteristics for diversity
            vnr_size = random.choice(vnr_sizes)
            topology = random.choice(topologies)
            
            # Create VNR with specific topology
            if topology == 'path':
                vnr = nx.path_graph(vnr_size)
            elif topology == 'star':
                vnr = nx.star_graph(vnr_size - 1)  # star_graph(n) creates n+1 nodes
            elif topology == 'cycle':
                if vnr_size >= 3:
                    vnr = nx.cycle_graph(vnr_size)
                else:
                    vnr = nx.path_graph(vnr_size)  # Fallback for small sizes
            elif topology == 'tree':
                # Create a tree using random spanning tree
                if vnr_size <= 2:
                    vnr = nx.path_graph(vnr_size)
                else:
                    # Create connected graph then find spanning tree
                    temp = nx.erdos_renyi_graph(vnr_size, 0.8, seed=vnr_id)
                    if nx.is_connected(temp):
                        vnr = nx.minimum_spanning_tree(temp)
                    else:
                        vnr = nx.path_graph(vnr_size)  # Fallback
            elif topology == 'random':
                # Create small random graph
                vnr = nx.erdos_renyi_graph(vnr_size, 0.6, seed=vnr_id)
                if not nx.is_connected(vnr):
                    # Ensure connectivity
                    vnr = nx.path_graph(vnr_size)
            else:
                vnr = nx.path_graph(vnr_size)  # Default fallback
            
            # Add VNR attributes
            vnr.graph['vnr_id'] = f"{scenario_name}_vnr_{vnr_id}"
            vnr.graph['arrival_time'] = vnr_id * 2  # Spread arrivals
            vnr.graph['lifetime'] = random.randint(10, 20)
            
            # Add node CPU requirements (varied within range)
            for node in vnr.nodes():
                vnr.nodes[node]['cpu_req'] = random.randint(*cpu_range)
            
            # Add edge bandwidth requirements (varied within range)
            for edge in vnr.edges():
                vnr.edges[edge]['bandwidth_req'] = random.randint(*bandwidth_range)
            
            vnr_queue.append(vnr)
        
        print(f"    Generated {len(vnr_queue)} diverse VNRs")
        print(f"    Topologies: {set(topologies)}")
        print(f"    Sizes: {vnr_sizes}")
        print(f"    CPU range: {cpu_range}")
        print(f"    Bandwidth range: {bandwidth_range}")
        
        return vnr_queue
    
    def run_single_load_experiment(self, scenario_name, scenario_config):
        """Run experiment for one load scenario: 4 algorithms, 3 output figures."""
        print(f"\n{'='*50}")
        print(f"RUNNING {scenario_name.upper().replace('_', ' ')} EXPERIMENT")
        print(f"{'='*50}")
        
        # Create experiment directory
        exp_dir = self.output_base_dir / f"{scenario_name}_experiment"
        exp_dir.mkdir(exist_ok=True)
        
        # Generate diverse VNR queue for this scenario
        vnr_queue = self.generate_diverse_vnr_queue(scenario_name, scenario_config)
        
        # Generate VNR visualization
        from src.visualization.network_plots import plot_all_vnrs
        vnr_title = f"{scenario_name.replace('_', ' ').title()} ({len(vnr_queue)} VNRs)"
        plot_all_vnrs(vnr_queue, title_prefix=vnr_title, 
                     filename=f"{scenario_name}_vnrs.png")
        
        # Copy VNR figure to experiment directory
        import shutil
        vnr_source = f"pictures/{scenario_name}_vnrs.png"
        if os.path.exists(vnr_source):
            shutil.copy2(vnr_source, exp_dir / f"{scenario_name}_vnrs.png")
            print(f"  Generated VNR visualization: {exp_dir / f'{scenario_name}_vnrs.png'}")
        
        # Run algorithms
        all_results = {}
        
        for alg_name, algorithm in self.algorithms.items():
            print(f"\n  Running {alg_name}...")
            
            # Create fresh substrate copy for each algorithm
            substrate_copy = copy.deepcopy(self.substrate_network)
            
            try:
                if alg_name == 'Yu2008':
                    # Yu2008 uses chunked approach and needs cpu_available attribute
                    self._initialize_substrate_resources(substrate_copy)
                    vnr_chunks = create_chunks(vnr_queue)
                    results = algorithm(substrate_copy, vnr_chunks)
                    
                    # CRITICAL: Sort by arrival_time for proper timeline visualization
                    results = sorted(results, key=lambda x: x['arrival_time'])
                else:
                    # Other algorithms use standard VNE simulation
                    results = vne_simulation(substrate_copy, vnr_queue, algorithm)
                
                # Calculate metrics using topology experiment pattern
                enhanced_results = []
                from src.metrics.metrics import calculate_revenue, calculate_cost
                
                for result in results:
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
                total_revenue = sum(r['revenue'] for r in enhanced_results if r.get('success', False))
                total_cost = sum(r['cost'] for r in enhanced_results)
                
                metrics = {
                    'total_requests': total,
                    'successful_requests': successful,
                    'acceptance_ratio': successful / total if total > 0 else 0,
                    'total_revenue': total_revenue,
                    'total_cost': total_cost,
                    'revenue_cost_ratio': total_revenue / total_cost if total_cost > 0 else 0
                }
                all_results[alg_name] = {
                    'results': results,
                    'metrics': metrics,
                    'status': 'SUCCESS'
                }
                
                acceptance = metrics['acceptance_ratio']
                revenue_cost = metrics['revenue_cost_ratio']
                print(f"    Success: {acceptance:.1%} ({metrics['successful_requests']}/{metrics['total_requests']})")
                print(f"    Revenue/Cost: {revenue_cost:.3f}")
                
            except Exception as e:
                print(f"    ERROR: {e}")
                all_results[alg_name] = {'status': 'FAILED', 'error': str(e)}
        
        # Generate visualizations
        self._generate_load_visualizations(scenario_name, all_results, vnr_queue, exp_dir)
        
        # Save results
        self._save_load_results(scenario_name, scenario_config, all_results, exp_dir)
        
        return all_results
    
    def _generate_load_visualizations(self, scenario_name, all_results, vnr_queue, output_dir):
        """Generate the 3 required visualizations for load experiment."""
        
        # 1. Timeline Comparison (4×2 layout)
        self._generate_timeline_figure(scenario_name, all_results, vnr_queue, output_dir)
        
        # 2. Resource Utilization Comparison (2×2 layout)  
        self._generate_utilization_figure(scenario_name, all_results, vnr_queue, output_dir)
        
        # 3. Metrics Comparison (2×2 layout)
        self._generate_metrics_figure(scenario_name, all_results, output_dir)
    
    def _generate_timeline_figure(self, scenario_name, all_results, vnr_queue, output_dir):
        """Generate timeline comparison figure (4×2 layout) - EXACT copy from topology experiments."""
        # Convert to format expected by topology timeline function
        results = {}
        for alg_name, data in all_results.items():
            if data['status'] == 'SUCCESS':
                results[alg_name] = data['results']
        
        fig, axes = plt.subplots(4, 2, figsize=(20, 24))  # 4 rows, 2 columns for 4 algorithms
        fig.suptitle(f'{scenario_name.replace("_", " ").title()} Demand - Timeline Comparison (4 Algorithms)', 
                     fontsize=18, fontweight='bold', y=0.98)  # Add spacing from top
        
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
                
                # Add summary stats to right subplot
                ax2.text(1.05, 0.5, f'Total: {total}\nSuccess: {successful}\nRatio: {acceptance_ratio:.1%}',
                        transform=ax2.transAxes, fontsize=10, verticalalignment='center',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Hide unused subplots
        for idx in range(len(results), 4):
            axes[idx, 0].set_visible(False)
            axes[idx, 1].set_visible(False)
            
        plt.tight_layout()
        plt.subplots_adjust(left=0.05, right=0.85, top=0.95)  # Add space for statistics boxes
        
        filename = output_dir / f"{scenario_name}_timelines.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"    Saved: {filename}")
    
    def _generate_utilization_figure(self, scenario_name, all_results, vnr_queue, output_dir):
        """Generate resource utilization comparison figure (2×2 layout) - EXACT copy from topology experiments."""
        # Convert to format expected by topology utilization function
        results = {}
        for alg_name, data in all_results.items():
            if data['status'] == 'SUCCESS':
                results[alg_name] = data['results']
        
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        axes = axes.flatten()
        
        for idx, (alg_name, alg_results) in enumerate(results.items()):
            if idx >= 4:  # Only 4 algorithms max
                break
                
            ax = axes[idx]
            successful_results = [r for r in alg_results if r.get('success', False)]
            
            if successful_results:
                try:
                    # Create substrate copy with proper resource tracking
                    substrate_copy = self.substrate_network.copy()
                    
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
                        
                        ax.set_title(f'{alg_name.replace("_", " ")} Peak Resource Utilization\\n(T={peak_embeddings["peak_time"]}, {peak_embeddings["active_count"]} active VNRs)', 
                                    fontweight='bold', fontsize=10)
                        ax.axis('off')
                        
                    else:
                        ax.text(0.5, 0.5, f'{alg_name}\\nNo Valid\\nEmbeddings',
                               ha='center', va='center', transform=ax.transAxes, fontsize=12,
                               bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))
                        ax.set_title(f'{alg_name}', fontweight='bold', fontsize=12)
                        ax.axis('off')
                        
                except Exception as e:
                    print(f"      Error processing {alg_name}: {e}")
                    ax.text(0.5, 0.5, f'{alg_name}\\nVisualization\\nError',
                           ha='center', va='center', transform=ax.transAxes, fontsize=12,
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral"))
                    ax.set_title(f'{alg_name}', fontweight='bold', fontsize=12)
                    ax.axis('off')
            else:
                ax.text(0.5, 0.5, f'{alg_name}\\nNo Successful\\nEmbeddings',
                       ha='center', va='center', transform=ax.transAxes, fontsize=12,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
                ax.set_title(f'{alg_name}', fontweight='bold', fontsize=12)
                ax.axis('off')
        
        # Hide unused subplots
        for idx in range(len(results), 4):
            axes[idx].set_visible(False)
        
        plt.tight_layout()
        
        # Add colorbar and legend - EXACT copy from topology experiments
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
        
        title = f"{scenario_name.replace('_', ' ').title()} Demand - Resource Utilization Comparison"
        fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
        
        # Adjust layout to accommodate colorbar and legend
        plt.subplots_adjust(left=0.15, right=0.9, top=0.93)  # Add space between suptitle and subplots
        
        filename = output_dir / f"{scenario_name}_utilization.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"    Saved: {filename}")
    
    def _generate_metrics_figure(self, scenario_name, all_results, output_dir):
        """Generate metrics comparison figure (2×2 layout)."""
        
        # Extract metrics for comparison
        metrics_data = {}
        for alg_name, data in all_results.items():
            if data['status'] == 'SUCCESS':
                metrics_data[alg_name] = data['metrics']
        
        if not metrics_data:
            print(f"    No successful results for metrics comparison")
            return
        
        # Create metrics comparison figure (same as topology experiments)
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        
        algorithms = list(metrics_data.keys())
        
        # Acceptance ratio comparison
        ax1 = axes[0, 0]
        acceptance_ratios = [metrics_data[alg]['acceptance_ratio'] for alg in algorithms]
        bars1 = ax1.bar(algorithms, acceptance_ratios, color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])
        ax1.set_ylabel('Acceptance Ratio')
        ax1.set_title('Acceptance Ratio Comparison')
        ax1.set_ylim(0, 1.1)
        ax1.grid(True, alpha=0.3)
        
        # Add percentage labels on bars
        for bar, ratio in zip(bars1, acceptance_ratios):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{ratio:.1%}', ha='center', va='bottom', fontweight='bold')
        
        # Revenue comparison
        ax2 = axes[0, 1]
        revenues = [metrics_data[alg]['total_revenue'] for alg in algorithms]
        ax2.bar(algorithms, revenues, color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])
        ax2.set_ylabel('Total Revenue')
        ax2.set_title('Revenue Comparison')
        ax2.grid(True, alpha=0.3)
        
        # Cost comparison
        ax3 = axes[1, 0]
        costs = [metrics_data[alg]['total_cost'] for alg in algorithms]
        ax3.bar(algorithms, costs, color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])
        ax3.set_ylabel('Total Cost')
        ax3.set_title('Cost Comparison')
        ax3.grid(True, alpha=0.3)
        
        # Revenue/Cost ratio
        ax4 = axes[1, 1]
        ratios = [metrics_data[alg]['revenue_cost_ratio'] for alg in algorithms]
        ax4.bar(algorithms, ratios, color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])
        ax4.set_ylabel('Revenue/Cost Ratio')
        ax4.set_title('Efficiency Comparison')
        ax4.grid(True, alpha=0.3)
        
        title = f"{scenario_name.replace('_', ' ').title()} Demand - Algorithm Comparison"
        fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout()
        plt.subplots_adjust(top=0.93)
        
        filename = output_dir / f"{scenario_name}_metrics.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"    Saved: {filename}")
    
    def _find_peak_utilization_snapshot(self, results, vnr_queue):
        """Find time point with maximum concurrent active VNRs."""
        # Track events: arrivals and departures
        events = []
        
        for result in results:
            if result['success']:
                vnr_id = result['vnr_id']
                arrival_time = result['arrival_time']
                
                # Find VNR object for lifetime
                vnr = next(v for v in vnr_queue if v.graph['vnr_id'] == vnr_id)
                departure_time = arrival_time + vnr.graph['lifetime']
                
                events.append((arrival_time, 'arrival', result))
                events.append((departure_time, 'departure', result))
        
        # Sort events by time
        events.sort(key=lambda x: x[0])
        
        # Track active embeddings over time
        active_embeddings = {}
        max_active_count = 0
        peak_time = 0
        peak_active = {}
        
        for time, event_type, result in events:
            vnr_id = result['vnr_id']
            
            if event_type == 'arrival':
                # Find corresponding VNR
                vnr = next(v for v in vnr_queue if v.graph['vnr_id'] == vnr_id)
                active_embeddings[vnr_id] = (result['node_mapping'], result['link_mapping'], vnr)
            elif event_type == 'departure':
                if vnr_id in active_embeddings:
                    del active_embeddings[vnr_id]
            
            # Check if this is peak utilization
            if len(active_embeddings) > max_active_count:
                max_active_count = len(active_embeddings)
                peak_time = time
                peak_active = active_embeddings.copy()
        
        return {
            'peak_time': peak_time,
            'active_count': max_active_count,
            'active_embeddings': peak_active
        }
    
    def _save_load_results(self, scenario_name, scenario_config, all_results, output_dir):
        """Save experiment results and metadata."""
        
        # Save results summary
        serializable_results = {}
        for alg_name, data in all_results.items():
            if data['status'] == 'SUCCESS':
                serializable_results[alg_name] = {
                    'metrics': data['metrics'],
                    'status': data['status']
                }
            else:
                serializable_results[alg_name] = {
                    'status': data['status'],
                    'error': data.get('error', 'Unknown error')
                }
        
        with open(output_dir / 'results_summary.json', 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        # Save metadata
        metadata = {
            'scenario': scenario_name,
            'description': scenario_config['description'],
            'experiment_date': datetime.now().isoformat(),
            'substrate_network': 'German',
            'total_algorithms': len(self.algorithms),
            'vnr_queue_size': scenario_config['count'],
            'cpu_range': scenario_config['cpu_range'],
            'bandwidth_range': scenario_config['bandwidth_range'],
            'vnr_sizes': scenario_config['vnr_sizes'],
            'topologies': scenario_config['topologies']
        }
        
        with open(output_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"    Saved: {output_dir / 'results_summary.json'}")
        print(f"    Saved: {output_dir / 'metadata.json'}")
    
    def run_all_load_experiments(self):
        """Run all 3 load testing scenarios."""
        print("UNIFIED LOAD TESTING EXPERIMENTS")
        print("=" * 60)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Generate substrate network once
        self.generate_substrate()
        print()
        
        # Run all scenarios
        all_scenario_results = {}
        
        for scenario_name, scenario_config in self.load_scenarios.items():
            results = self.run_single_load_experiment(scenario_name, scenario_config)
            all_scenario_results[scenario_name] = results
            print()
        
        # Summary
        print("ALL LOAD EXPERIMENTS COMPLETED!")
        print("=" * 60)
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("Generated files:")
        print(f"  {self.output_base_dir}/")
        print("    ├── substrate_network.png - Shared substrate network")
        print("    ├── light_demand_experiment/ - 3 figures + JSON data")
        print("    ├── medium_demand_experiment/ - 3 figures + JSON data")
        print("    └── heavy_demand_experiment/ - 3 figures + JSON data")
        print()
        print("Total output: 1 substrate + 9 experiment figures + 6 data files")
        
        return all_scenario_results
    
    def _initialize_substrate_resources(self, substrate):
        """Initialize substrate resource attributes for algorithms."""
        for node in substrate.nodes():
            substrate.nodes[node]['cpu_available'] = substrate.nodes[node]['cpu']
        for edge in substrate.edges():
            substrate.edges[edge]['bandwidth_available'] = substrate.edges[edge]['bandwidth']

def main():
    """Main execution function."""
    try:
        experiment = UnifiedLoadExperiments()
        results = experiment.run_all_load_experiments()
        return 0
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)