#!/usr/bin/env python3
"""
VNE Algorithm Comparison Framework - Main CLI Interface

Complete thesis experiment system with three major experimental methodologies:
1. Topology Experiments - Algorithm performance across different network topologies  
2. Load Testing Experiments - Algorithm behavior under increasing VNR demand
3. Scalability Experiments - Algorithm scalability across different network sizes

Usage:
    python main.py                    # Interactive menu
    python main.py topology           # Run topology experiments
    python main.py load              # Run load testing experiments  
    python main.py scalability      # Run scalability experiments
    python main.py all              # Run all experiments (LONG!)
"""

import sys
import subprocess
import time
from pathlib import Path

class VNEExperimentCLI:
    """Main CLI interface for VNE algorithm comparison experiments."""
    
    def __init__(self):
        self.experiments = {
            'topology': {
                'script': 'experiments/run_complete_topology_experiments.py',
                'description': 'Topology Experiments - Test algorithms across 6 different network topologies',
                'output': 'experiments/topology_experiment/',
                'files': '32 files (2 analysis + 18 experiment figures + 12 JSON data files)'
            },
            'load': {
                'script': 'experiments/run_complete_load_experiments.py', 
                'description': 'Load Testing Experiments - Test algorithms under increasing VNR demand',
                'output': 'experiments/load_testing_experiment/',
                'files': '18 files (12 experiment figures + 6 JSON data files)'
            },
            'scalability': {
                'script': 'experiments/unified_scalability_experiments.py',
                'description': 'Scalability Experiments - Test algorithms across different network sizes',
                'output': 'experiments/scalability_experiment/',
                'files': '25 files (1 VNR analysis + 16 experiment figures + 8 JSON data files)'
            }
        }
    
    def show_menu(self):
        """Display interactive menu."""
        print("=" * 80)
        print("VNE ALGORITHM COMPARISON FRAMEWORK")
        print("=" * 80)
        print()
        print("Available Experiments:")
        print()
        
        for i, (key, info) in enumerate(self.experiments.items(), 1):
            print(f"{i}. {key.upper()}")
            print(f"   {info['description']}")
            print(f"   Output: {info['files']}")
            print(f"   Location: {info['output']}")
            print()
        
        print(f"{len(self.experiments) + 1}. ALL")
        print("   Run all experiments sequentially")
        print()
        print("0. Exit")
        print()
    
    def run_experiment(self, experiment_type):
        """Run a specific experiment."""
        if experiment_type not in self.experiments:
            print(f"Error: Unknown experiment type '{experiment_type}'")
            return False
        
        script = self.experiments[experiment_type]['script']
        description = self.experiments[experiment_type]['description']
        
        print(f"Starting {description}...")
        print(f"Script: {script}")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            # Run the experiment script
            result = subprocess.run([sys.executable, script], 
                                  capture_output=False, 
                                  text=True,
                                  cwd=Path.cwd())
            
            if result.returncode == 0:
                elapsed = time.time() - start_time
                print("-" * 60)
                print(f"✅ {description} completed successfully!")
                print(f"Runtime: {elapsed/60:.1f} minutes")
                print(f"Results saved to: {self.experiments[experiment_type]['output']}")
                return True
            else:
                print(f"{description} failed with return code {result.returncode}")
                return False
                
        except Exception as e:
            print(f"Error running {description}: {e}")
            return False
    
    def run_all_experiments(self):
        """Run all experiments in sequence."""
        print("RUNNING ALL EXPERIMENTS")
        print("=" * 60)
        
        total_start = time.time()
        results = {}
        
        for exp_type in ['topology', 'load', 'scalability']:
            print(f"\nStarting {exp_type.upper()} experiments...")
            results[exp_type] = self.run_experiment(exp_type)
            
            if not results[exp_type]:
                print(f"Stopping due to failure in {exp_type} experiments")
                return False
        
        total_elapsed = time.time() - total_start
        
        print("\n" + "=" * 60)
        print("ALL EXPERIMENTS COMPLETED!")
        print(f"Total runtime: {total_elapsed/60:.1f} minutes")
        print()
        print("Results Summary:")
        for exp_type, success in results.items():
            status = "SUCCESS" if success else "FAILED"
            print(f"  {exp_type.upper()}: {status}")
        
        return all(results.values())
    
    def interactive_mode(self):
        """Run interactive menu mode."""
        while True:
            self.show_menu()
            try:
                choice = input("Enter your choice (0-4): ").strip()
                
                if choice == '0':
                    print("Goodbye!")
                    break
                elif choice == '1':
                    self.run_experiment('topology')
                elif choice == '2':
                    self.run_experiment('load')  
                elif choice == '3':
                    self.run_experiment('scalability')
                elif choice == '4':
                    self.run_all_experiments()
                else:
                    print("Invalid choice. Please enter 0-4.")
                    
            except KeyboardInterrupt:
                print("\\n\\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def run_cli(self, args):
        """Run CLI mode with arguments."""
        if len(args) == 0:
            self.interactive_mode()
            return
        
        command = args[0].lower()
        
        if command in self.experiments:
            self.run_experiment(command)
        elif command == 'all':
            self.run_all_experiments()
        elif command in ['help', '-h', '--help']:
            self.show_help()
        else:
            print(f"Error: Unknown command '{command}'")
            print("Available commands: topology, load, scalability, all, help")
            print("Run 'python main.py help' for more information")
    
    def show_help(self):
        """Show help information."""
        print(__doc__)


def main():
    """Main entry point."""
    cli = VNEExperimentCLI()
    cli.run_cli(sys.argv[1:])


if __name__ == "__main__":
    main()