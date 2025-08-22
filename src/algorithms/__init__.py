"""
VNE Algorithms Package

Provides access to all 4 embedding algorithms:
- Simple Greedy Algorithm
- Yu 2008 Baseline Algorithm  
- RW-MaxMatch Algorithm
- RW-BFS Algorithm
"""

from .greedy import simple_greedy_algorithm
from .yu_baseline import yu2008_algorithm, calculate_revenue, create_chunks
from .rw_maxmatch import rw_maxmatch_algorithm 
from .noderank import compute_noderank
from .rw_bfs import rw_bfs_algorithm

# Make all algorithms available at package level
__all__ = [
    'simple_greedy_algorithm',
    'yu2008_algorithm', 
    'calculate_revenue',
    'create_chunks',
    'rw_maxmatch_algorithm',
    'compute_noderank', 
    'rw_bfs_algorithm'
]
