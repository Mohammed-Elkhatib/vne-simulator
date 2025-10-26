# VNE Algorithm Comparison Framework

A comprehensive experimental framework for evaluating Virtual Network Embedding (VNE) algorithms with publication-quality visualizations and systematic performance analysis.

## Features

- **4 VNE Algorithms**: Simple_Greedy, RW_BFS, RW_MaxMatch, Yu2008
- **Multiple Network Topologies**: German, Italian, Erdős-Rényi, Barabási-Albert, Grid
- **Comprehensive Experiments**: Topology comparison, load testing, scalability analysis
- **Publication-Quality Visualizations**: Timeline plots, resource utilization, algorithm comparisons
- **Systematic Metrics**: Acceptance ratio, blocking probability, revenue/cost ratio

## Quick Start

### Installation

```bash
git clone <repository-url>
cd vne-algorithm-framework
pip install networkx matplotlib numpy
```

### Run Experiments

```bash
# Interactive mode
python main.py

# Direct commands
python main.py topology      # Topology comparison experiments
python main.py load          # Load testing experiments (recommended)
python main.py scalability   # Scalability testing experiments
python main.py all          # Run all experiments
```

### View Results

Results are organized by experiment type:
- **Topology**: `experiments/topology_final/` (32 files)
- **Load Testing**: `experiments/load_experiment/` (18 files)
- **Scalability**: `experiments/scalability_experiment/` (25 files)

Each includes: Performance metrics (JSON), timeline visualizations, resource utilization plots, algorithm comparison charts

## Algorithms Implemented

### 1. Simple_Greedy
- **Type**: Baseline greedy algorithm
- **Performance**: 50-90% acceptance ratio
- **Characteristics**: Fast, predictable, degrades on complex topologies

### 2. RW_BFS (Random Walk with BFS)
- **Type**: Random walk with breadth-first search
- **Performance**: 80-100% acceptance ratio
- **Characteristics**: Best overall performance, excellent cost efficiency

### 3. RW_MaxMatch (Random Walk with Max Matching)
- **Type**: Random walk with maximum matching
- **Performance**: 75-100% acceptance ratio
- **Characteristics**: Good performance, NetworkX scalability limitations

### 4. Yu2008 (Revenue-Based Chunked)
- **Type**: Batch optimization algorithm
- **Performance**: 73-100% acceptance ratio
- **Characteristics**: Excellent under resource pressure, higher costs

## Experiment Types

### Topology Comparison (Recommended)
Tests algorithm performance across 6 different network topologies:
- **Real Networks**: German (7 nodes), Italian (10 nodes)
- **Random Networks**: Erdős-Rényi sparse/dense (8 nodes)
- **Structured Networks**: Barabási-Albert (8 nodes), Grid (9 nodes)

**Key Findings**:
- RW_BFS achieves 100% acceptance on real networks
- Random networks provide challenging test cases (60-85% acceptance)
- Algorithm ranking varies by topology characteristics

### Load Testing (Primary Method)
Tests algorithm performance under increasing VNR demand:
- **Light Load**: 15 VNRs (67-73% acceptance)
- **Medium Load**: 25 VNRs (36-40% acceptance)  
- **Heavy Load**: 35 VNRs (31-37% acceptance)

**Key Findings**:
- Yu2008 maintains best acceptance under extreme load
- RW_BFS provides superior cost efficiency
- Clear performance differentiation across load levels

### Scalability Testing (Complete)
Tests algorithm performance across 4 network sizes (8, 12, 16, 20 nodes):
- **8-Node Networks**: Yu2008 best (90%), others 75-85%
- **12-Node Networks**: Perfect performance for all except Simple_Greedy (90%)
- **16-Node Networks**: RW algorithms achieve 100%, Yu2008 95%, Simple_Greedy 75%
- **20-Node Networks**: Advanced algorithms maintain 100%, Simple_Greedy drops to 70%

**Key Findings**:
- RW-BFS achieves 100% acceptance on networks ≥12 nodes
- Simple_Greedy performance degrades with network sparsity
- Critical performance bugs fixed for larger networks

## Project Structure

```
vne-algorithm-framework/
├── main.py                       # 🎯 MAIN CLI INTERFACE
├── run_complete_topology_experiments.py     # Topology experiments
├── run_complete_load_experiments.py         # Load testing experiments  
├── unified_scalability_experiments.py       # Scalability experiments
├── src/                          # Source code
│   ├── algorithms/               # VNE algorithms (4 implementations)
│   ├── networks/                 # Network generators
│   ├── simulation/               # Simulation engine
│   ├── visualization/            # Publication-quality plotting
│   └── metrics/                  # Performance metrics
└── experiments/                  # Generated results
    ├── topology_final/          # Topology experiment results
    ├── load_experiment/         # Load testing results
    └── scalability_experiment/  # Scalability testing results
```

## Key Research Findings

### Algorithm Performance Ranking
1. **RW_BFS**: Best overall performance and cost efficiency
2. **Yu2008**: Best under resource pressure, higher costs
3. **RW_MaxMatch**: Good performance, scalability issues
4. **Simple_Greedy**: Reliable baseline, topology-sensitive

### Network Difficulty Classification
- **Easy Networks** (90-100%): German, Italian (real topologies)
- **Moderate Networks** (80-90%): Barabási-Albert (scale-free)
- **Challenging Networks** (60-85%): Erdős-Rényi, Grid (sparse connectivity)

### Performance Targets for New Algorithms
- **Easy Networks**: 95-100% acceptance to be competitive
- **Challenging Networks**: 85-90% acceptance to match state-of-the-art
- **Cost Efficiency**: Revenue/cost ratio >0.90 for practical deployment

## Technical Notes

### Critical Scalability Fixes Applied
**Problem**: RW_MaxMatch and Yu2008 hung for 30+ minutes on larger networks
**Solution**: Fixed unlimited path enumeration bug:
```python
# Before (computed ALL paths - extremely slow)
list(nx.shortest_simple_paths(...))

# After (only compute k paths - fast)
list(itertools.islice(nx.shortest_simple_paths(...), k))
```
**Result**: All algorithms now complete in reasonable time

### Dependencies
- Python 3.8+
- NetworkX 3.0+
- Matplotlib 3.5+
- NumPy 1.20+

## Documentation

Comprehensive analysis and results documented in:
- **CLAUDE.md**: Complete experiment results, technical findings, and implementation details
- **experiments/docs/**: Detailed analysis documents
  - `VNE_Topology_Comparison_Results.md` - 6-network topology analysis
  - `VNE_Load_Testing_Results.md` - VNR demand scaling study  
  - `VNE_Scalability_Experiments_Results.md` - Network size scaling analysis
- **JSON Results**: Detailed performance metrics for each experiment
- **Generated Visualizations**: Publication-quality figures for thesis/papers

## Contributing

This framework is designed for VNE research and algorithm development. To add new algorithms:

1. Implement algorithm in `src/algorithms/`
2. Follow existing interface (substrate, vnr_queue parameters)
3. Add to algorithm list in experiment scripts
4. Run comprehensive experiments: `python main.py all`

## Citation

If you use this framework in your research, please cite:

```bibtex
@misc{vne-algorithm-framework,
  title={VNE Algorithm Simulator},
  author={[Mohammed-Elkhatib]},
  year={2025},
  url={[https://github.com/Mohammed-Elkhatib/vne-simulator.git]}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Experimental framework for systematic VNE algorithm evaluation and comparison*