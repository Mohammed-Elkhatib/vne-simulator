import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add root directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.networks.substrate_networks import create_german_network, create_italian_network
from src.networks.vne_generators import generate_substrate_network, generate_vnr_batch
from src.networks.vnr_creation import create_vnr_queue
from src.algorithms.greedy import simple_greedy_algorithm
from src.algorithms.rw_bfs import rw_bfs_algorithm
from src.algorithms.rw_maxmatch import rw_maxmatch_algorithm
from src.algorithms.yu_baseline import yu2008_algorithm, create_chunks
from src.simulation.simulation import vne_simulation
from src.metrics.metrics import calculate_acceptance_ratio, calculate_metrics_summary, calculate_revenue, calculate_cost
from src.visualization.simulation_plots import plot_algorithm_comparison, plot_simulation_timeline
from src.visualization.network_plots import plot_substrate_network, plot_all_vnrs
from src.visualization.resource_plots import plot_resource_utilization_snapshot


class VNEExperiment:
    """Single VNE experiment configuration and execution"""
    
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.results_dir = Path(f"experiments/results/{name}")
        self.results = {}
    
    def run_algorithms(self, substrate, vnr_queue, algorithms=None):
        """Run all specified algorithms on the same substrate/VNR setup"""
        
        if algorithms is None:
            algorithms = get_default_algorithms()
        
        print(f"\n=== Running Experiment: {self.name} ===")
        print(f"Substrate: {len(substrate.nodes())} nodes, {len(substrate.edges())} edges")
        print(f"VNR Queue: {len(vnr_queue)} requests")
        print(f"Algorithms: {list(algorithms.keys())}")
        
        for alg_name, alg_func in algorithms.items():
            print(f"\nTesting {alg_name}...")
            
            try:
                if alg_name == "Yu2008":
                    # Special handling for Yu2008 chunked algorithm
                    results = self._run_yu2008(substrate, vnr_queue, alg_func)
                else:
                    # Standard algorithm simulation
                    results = vne_simulation(substrate.copy(), vnr_queue, alg_func)
                
                # Calculate all metrics
                metrics = self._calculate_comprehensive_metrics(results, vnr_queue)
                
                self.results[alg_name] = {
                    'results': results,
                    'metrics': metrics,
                    'status': 'SUCCESS'
                }
                
                print(f"  {alg_name}: {metrics['successful_requests']}/{metrics['total_requests']} = {metrics['acceptance_ratio']:.3f}")
                
            except Exception as e:
                print(f"  {alg_name}: FAILED - {str(e)}")
                self.results[alg_name] = {'status': 'FAILED', 'error': str(e)}
        
        return self.results
    
    def run_and_save(self, substrate, vnr_queue, algorithms=None):
        """Run algorithms and save results with visualizations"""
        self.run_algorithms(substrate, vnr_queue, algorithms)
        self.save_results(substrate, vnr_queue)
        return self.results
    
    def _run_yu2008(self, substrate, vnr_queue, alg_func):
        """Special handling for Yu2008 chunked algorithm"""
        chunks = create_chunks(vnr_queue, time_window=25)
        substrate_working = substrate.copy()
        
        # Initialize available resources
        for node in substrate_working.nodes():
            substrate_working.nodes[node]['cpu_available'] = substrate_working.nodes[node]['cpu']
        for edge in substrate_working.edges():
            substrate_working.edges[edge]['bandwidth_available'] = substrate_working.edges[edge]['bandwidth']
        
        return alg_func(substrate_working, chunks, time_window=25)
    
    def _calculate_comprehensive_metrics(self, results, vnr_queue):
        """Calculate all available metrics for the results"""
        # First calculate revenue and cost for each result
        enhanced_results = []
        for result in results:
            if result['success']:
                vnr = next(v for v in vnr_queue if v.graph['vnr_id'] == result['vnr_id'])
                revenue = calculate_revenue(vnr)
                cost = calculate_cost(vnr, result['node_mapping'], result['link_mapping'])
                enhanced_result = result.copy()
                enhanced_result.update({'revenue': revenue, 'cost': cost})
            else:
                enhanced_result = result.copy()
                enhanced_result.update({'revenue': 0, 'cost': 0})
            enhanced_results.append(enhanced_result)
        
        # Calculate comprehensive metrics
        return calculate_metrics_summary(enhanced_results)
    
    def save_results(self, substrate, vnr_queue, include_visualizations=True):
        """Save experiment results and metadata"""
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Save metadata
        metadata = {
            'experiment_name': self.name,
            'description': self.description,
            'run_date': datetime.now().isoformat(),
            'algorithms_tested': list(self.results.keys()),
            'total_algorithms': len(self.results)
        }
        
        with open(self.results_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Save results (only serializable data)
        serializable_results = {}
        for alg_name, data in self.results.items():
            if data.get('status') == 'SUCCESS':
                serializable_results[alg_name] = {
                    'metrics': data['metrics'],
                    'status': data['status']
                }
            else:
                serializable_results[alg_name] = data
        
        with open(self.results_dir / 'results_summary.json', 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        # Generate visualizations
        if include_visualizations:
            try:
                self._generate_comprehensive_visualizations(substrate, vnr_queue)
            except Exception as e:
                print(f"Warning: Visualization generation failed: {e}")
        
        print(f"\nResults saved to: {self.results_dir}")
    
    def _generate_comprehensive_visualizations(self, substrate, vnr_queue):
        """Generate comprehensive visualizations including substrate, VNRs, utilization, and results"""
        import matplotlib.pyplot as plt
        
        # Change to results directory for all visualizations
        original_dir = os.getcwd()
        os.makedirs(self.results_dir, exist_ok=True)
        os.chdir(self.results_dir)
        
        try:
            # 1. Plot substrate network
            print("  Generating substrate network visualization...")
            substrate_copy = substrate.copy()
            plot_substrate_network(substrate_copy, 
                                 title=f"{self.name} - Substrate Network",
                                 figsize=(10, 8))
            
            # 2. Plot all VNRs
            print("  Generating VNR visualization...")
            plot_all_vnrs(vnr_queue, 
                         title_prefix=f"{self.name} - VNRs",
                         filename=f"{self.name}_vnr_requests.png")
            
            # 3. Generate algorithm comparison
            plot_data = {alg: data for alg, data in self.results.items() 
                        if data.get('status') == 'SUCCESS'}
            
            if len(plot_data) > 1:
                print("  Generating algorithm comparison...")
                algorithms = list(plot_data.keys())
                acceptance_ratios = [data['metrics']['acceptance_ratio'] for data in plot_data.values()]
                
                plt.figure(figsize=(15, 10))
                
                # Main comparison plot
                plt.subplot(2, 2, 1)
                bars = plt.bar(algorithms, acceptance_ratios, color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])
                plt.ylabel('Acceptance Ratio')
                plt.title(f'Algorithm Comparison - {self.name}')
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
                plt.savefig(f"{self.name}_comprehensive_comparison.png", dpi=300, bbox_inches='tight')
                plt.close()
                
            # 4. Generate individual algorithm timelines and resource utilization
            for alg_name, data in plot_data.items():
                if data.get('status') == 'SUCCESS':
                    print(f"  Generating {alg_name} detailed analysis...")
                    
                    # Timeline plot
                    results = data['results']
                    plot_simulation_timeline(results, 
                                           title=f"{alg_name} - {self.name}",
                                           filename=f"{self.name}_{alg_name}_timeline.png")
                    
                    # Resource utilization at peak load (VNE literature best practice)
                    peak_embeddings = self._find_peak_utilization_snapshot(results, vnr_queue)
                    
                    if peak_embeddings['active_embeddings']:
                        # Add cpu_available to substrate for resource visualization
                        substrate_vis = substrate.copy()
                        for node in substrate_vis.nodes():
                            substrate_vis.nodes[node]['cpu_available'] = substrate_vis.nodes[node]['cpu']
                        for edge in substrate_vis.edges():
                            substrate_vis.edges[edge]['bandwidth_available'] = substrate_vis.edges[edge]['bandwidth']
                        
                        plot_resource_utilization_snapshot(substrate_vis, peak_embeddings['active_embeddings'],
                                                         title=f"{alg_name} Peak Resource Utilization (T={peak_embeddings['time']}, {peak_embeddings['count']} active VNRs) - {self.name}",
                                                         filename=f"{self.name}_{alg_name}_peak_resource_utilization.png")
            
            print(f"  All visualizations saved to: {self.results_dir}")
            
        finally:
            os.chdir(original_dir)
    
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
        events.sort(key=lambda x: x['time'])
        
        # Find peak utilization point
        active_vnrs = {}
        max_active_count = 0
        peak_time = 0
        peak_active_embeddings = {}
        
        for event in events:
            if event['type'] == 'ARRIVAL':
                active_vnrs[event['vnr_id']] = {
                    'result': event['result'],
                    'vnr': event['vnr']
                }
            elif event['type'] == 'DEPARTURE':
                if event['vnr_id'] in active_vnrs:
                    del active_vnrs[event['vnr_id']]
            
            # Check if this is the peak
            if len(active_vnrs) > max_active_count:
                max_active_count = len(active_vnrs)
                peak_time = event['time']
                # Convert to format expected by visualization
                peak_active_embeddings = {
                    vnr_id: (data['result']['node_mapping'], data['result']['link_mapping'], data['vnr'])
                    for vnr_id, data in active_vnrs.items()
                }
        
        return {
            'time': peak_time,
            'count': max_active_count,
            'active_embeddings': peak_active_embeddings
        }


def get_default_algorithms():
    """Get the standard set of VNE algorithms"""
    return {
        'Simple_Greedy': simple_greedy_algorithm,
        'RW_BFS': rw_bfs_algorithm,
        'RW_MaxMatch': rw_maxmatch_algorithm,
        'Yu2008': yu2008_algorithm
    }


def run_substrate_topology_experiments():
    """Experiment 1: Test different substrate topologies"""
    
    substrates = {
        'German': create_german_network(),
        'Italian': create_italian_network(),
        'ER_8_sparse': generate_substrate_network(8, 'erdos_renyi', p=0.3),
        'ER_8_dense': generate_substrate_network(8, 'erdos_renyi', p=0.6),
        'BA_8': generate_substrate_network(8, 'barabasi_albert', m=2),
        'Grid_9': generate_substrate_network(9, 'grid')
    }
    
    vnr_queue = create_vnr_queue()  # Standard VNR set
    results_summary = {}
    
    for substrate_name, substrate in substrates.items():
        exp = VNEExperiment(f"topology_comparison_{substrate_name}")
        exp.run_and_save(substrate, vnr_queue)
        
        # Collect summary for comparison
        results_summary[substrate_name] = {
            alg: data.get('metrics', {}).get('acceptance_ratio', 0) 
            for alg, data in exp.results.items() 
            if data.get('status') == 'SUCCESS'
        }
    
    return results_summary


def run_network_size_experiments():
    """Experiment 2: Test scalability with network size"""
    
    sizes = [8, 12, 16, 20]
    vnr_queue = create_vnr_queue()
    results_summary = {}
    
    for size in sizes:
        substrate = generate_substrate_network(size, 'erdos_renyi', p=0.4)
        exp = VNEExperiment(f"scalability_test_{size}_nodes")
        exp.run_and_save(substrate, vnr_queue)
        
        results_summary[f"size_{size}"] = {
            alg: data.get('metrics', {}).get('acceptance_ratio', 0)
            for alg, data in exp.results.items()
            if data.get('status') == 'SUCCESS'
        }
    
    return results_summary


def run_vnr_load_experiments():
    """Experiment 3: Test different VNR loads"""
    
    substrate = create_german_network()
    load_scenarios = {
        'light': {'count': 15, 'cpu_range': (10, 20), 'bandwidth_range': (5, 15)},
        'medium': {'count': 25, 'cpu_range': (15, 30), 'bandwidth_range': (10, 25)},
        'heavy': {'count': 35, 'cpu_range': (20, 40), 'bandwidth_range': (15, 35)}
    }
    
    results_summary = {}
    
    for load_name, params in load_scenarios.items():
        # Generate VNRs with specified parameters
        substrate_nodes = list(substrate.nodes())
        vnr_queue = generate_vnr_batch(substrate_nodes, **params)
        
        exp = VNEExperiment(f"load_testing_{load_name}_demand")
        exp.run_and_save(substrate, vnr_queue)
        
        results_summary[load_name] = {
            alg: data.get('metrics', {}).get('acceptance_ratio', 0)
            for alg, data in exp.results.items()
            if data.get('status') == 'SUCCESS'
        }
    
    return results_summary


def run_single_experiment(substrate_name="german", vnr_type="standard"):
    """Run a single experiment for quick testing"""
    
    # Get substrate
    if substrate_name == "german":
        substrate = create_german_network()
        substrate_desc = f"german_{len(substrate.nodes())}nodes"
    elif substrate_name == "italian":
        substrate = create_italian_network()
        substrate_desc = f"italian_{len(substrate.nodes())}nodes"
    else:
        substrate = generate_substrate_network(10, 'erdos_renyi', p=0.4)
        substrate_desc = f"generated_{len(substrate.nodes())}nodes"
    
    # Get VNR queue  
    if vnr_type == "standard":
        vnr_queue = create_vnr_queue()
        vnr_desc = f"{len(vnr_queue)}vnrs_standard"
    else:
        substrate_nodes = list(substrate.nodes())
        vnr_queue = generate_vnr_batch(substrate_nodes, count=20)
        vnr_desc = f"{len(vnr_queue)}vnrs_generated"
    
    # Run experiment with descriptive name
    exp = VNEExperiment(f"{substrate_desc}_{vnr_desc}")
    results = exp.run_and_save(substrate, vnr_queue)
    
    return results


def main():
    """Main experiment runner"""
    import sys
    print("VNE Experimental Framework")
    print("=" * 50)
    
    # Create results directory
    os.makedirs("experiments/results", exist_ok=True)
    
    # Handle command line arguments
    if len(sys.argv) > 1 and sys.argv[1].startswith("echo"):
        choice = sys.argv[1].split()[1]
    else:
        choice = input("Choose experiment:\n1. Single test\n2. Topology comparison\n3. Size scalability\n4. Load testing\nChoice (1-4): ")
    
    if choice == "1":
        run_single_experiment()
    elif choice == "2":
        print("Running substrate topology experiments...")
        run_substrate_topology_experiments()
    elif choice == "3":
        print("Running network size experiments...")
        run_network_size_experiments()
    elif choice == "4":
        print("Running VNR load experiments...")
        run_vnr_load_experiments()
    else:
        print("Running single test...")
        run_single_experiment()
    
    print("\nAll experiments completed!")


if __name__ == "__main__":
    main()