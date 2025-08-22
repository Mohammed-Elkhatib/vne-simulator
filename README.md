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
python experiment_runner.py

# Direct commands
python experiment_runner.py "echo 2"  # Topology comparison
python experiment_runner.py "echo 4"  # Load testing (recommended)
```

### View Results

Results are saved in `experiments/results/` with:
- Performance metrics (JSON)
- Timeline visualizations
- Resource utilization plots
- Algorithm comparison charts

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

### Scalability Testing (Needs Redesign)
Current implementation has design flaws (fixed VNR load on growing networks).
See `experiments/docs/VNE_Scalability_Testing_Analysis.md` for detailed analysis and proposed fixes.

## Project Structure

```
vne-algorithm-framework/
├── experiment_runner.py           # Main entry point
├── src/                          # Source code
│   ├── algorithms/               # VNE algorithms
│   ├── networks/                 # Network generators
│   ├── simulation/               # Simulation engine
│   ├── visualization/            # Plotting functions
│   └── metrics/                  # Performance metrics
└── experiments/                  # Experimental framework
    ├── docs/                    # Analysis documentation
    └── results/                 # Generated results
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

### NetworkX Scalability Issues
RW_MaxMatch crashes on large networks (≥20 nodes) due to `shortest_simple_paths` limitations.

**Solutions**:
```bash
# GPU acceleration (10x-500x speedup)
pip install nx-cugraph-cu12
export NX_CUGRAPH_AUTOCONFIG=True
```

### Dependencies
- Python 3.8+
- NetworkX 3.0+
- Matplotlib 3.5+
- NumPy 1.20+

## Documentation

Comprehensive analysis available in `experiments/docs/`:
- **VNE_Topology_Comparison_Results.md**: 6-network topology analysis
- **VNE_Load_Testing_Results.md**: VNR demand scaling study
- **VNE_Scalability_Testing_Analysis.md**: Network size scaling analysis
- **VNE_Scalability_Load_Testing_Analysis.md**: Framework comparison

## Contributing

This framework is designed for VNE research and algorithm development. To add new algorithms:

1. Implement algorithm in `src/algorithms/`
2. Follow existing interface (substrate, vnr_queue parameters)
3. Add to algorithm list in `experiment_runner.py`
4. Run comprehensive experiments for evaluation

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