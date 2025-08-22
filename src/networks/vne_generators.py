"""
VNE Network Generators
Literature-compliant network generation for Virtual Network Embedding
"""

import networkx as nx
import random
import math

_vnr_counter = 0

def _get_unique_vnr_id():
    global _vnr_counter
    _vnr_counter += 1
    return f"VNR_{_vnr_counter}"

def generate_substrate_network(nodes, topology="erdos_renyi", edge_prob=0.15, **kwargs):
    """Generate substrate network using standard VNE topologies. Guarantees connectivity."""
    
    # Start with spanning tree to guarantee connectivity
    if nodes <= 1:
        G = nx.Graph()
        G.add_nodes_from(range(nodes))
    else:
        # Create initial connected backbone
        G = nx.path_graph(nodes)  # Linear spanning tree
    
    # Add topology-specific edges while maintaining connectivity
    if topology == "erdos_renyi":
        # Add random edges based on probability
        for i in range(nodes):
            for j in range(i + 1, nodes):
                if not G.has_edge(i, j) and random.random() < edge_prob:
                    G.add_edge(i, j)
                    
    elif topology == "barabasi_albert":
        # Start fresh with BA model (already connected)
        m = kwargs.get('m', max(1, int(nodes * edge_prob / 2)))
        G = nx.barabasi_albert_graph(nodes, m)
        
    elif topology == "grid":
        # Grid is naturally connected for rectangular grids
        side = int(math.sqrt(nodes))
        G = nx.grid_2d_graph(side, side)
        G = nx.convert_node_labels_to_integers(G)
        
    else:
        raise ValueError(f"Unsupported topology: {topology}")
    
    # Verify connectivity
    if not nx.is_connected(G) and len(G.nodes()) > 1:
        raise RuntimeError(f"Failed to create connected {topology} substrate - VNE requirement violated")
    
    # Add resource attributes (uniform 50-100)
    for node in G.nodes():
        G.nodes[node]['cpu'] = random.randint(50, 100)
    
    for edge in G.edges():
        G.edges[edge]['bandwidth'] = random.randint(50, 100)
    
    return G


def generate_vnr(substrate_nodes, nodes=None, topology="random", **kwargs):
    """Generate VNR with literature-compliant characteristics."""
    # VNR size: 2-20 nodes as per literature
    if nodes is None:
        nodes = random.randint(2, min(6, len(substrate_nodes) // 2))
    
    # Create VNR topology
    if topology == "random":
        edge_prob = kwargs.get('edge_prob', 0.5)
        vnr = nx.erdos_renyi_graph(nodes, edge_prob)
    elif topology == "star":
        vnr = nx.star_graph(nodes - 1)
    elif topology == "linear":
        vnr = nx.path_graph(nodes)
    elif topology == "tree":
        # Create a random tree using a different approach since random_tree may not exist
        vnr = nx.Graph()
        vnr.add_nodes_from(range(nodes))
        if nodes > 1:
            # Create a tree by connecting random nodes
            for i in range(1, nodes):
                parent = random.randint(0, i-1)
                vnr.add_edge(parent, i)
    else:
        raise ValueError(f"Unsupported VNR topology: {topology}")
    
    # Ensure connectivity
    if not nx.is_connected(vnr) and len(vnr.nodes()) > 1:
        components = list(nx.connected_components(vnr))
        for i in range(len(components) - 1):
            u = random.choice(list(components[i]))
            v = random.choice(list(components[i + 1]))
            vnr.add_edge(u, v)
    
    # Add resource requirements (0-50 as typical in literature)
    for node in vnr.nodes():
        vnr.nodes[node]['cpu_req'] = random.randint(10, 50)
    
    for edge in vnr.edges():
        vnr.edges[edge]['bandwidth_req'] = random.randint(5, 30)
    
    # Add VNR metadata
    arrival_time = kwargs.get('arrival_time', random.randint(0, 100))
    lifetime = kwargs.get('lifetime', random.randint(20, 60))
    vnr_id = kwargs.get('vnr_id', _get_unique_vnr_id())
    
    vnr.graph.update({
        'vnr_id': vnr_id,
        'arrival_time': arrival_time,
        'lifetime': lifetime
    })
    
    return vnr


def generate_vnr_batch(substrate_nodes, count, **kwargs):
    """Generate batch of VNRs with temporal distribution."""
    vnrs = []
    for i in range(count):
        arrival_time = int(kwargs.get('arrival_rate', 1.0) * i + random.randint(0, 5))
        vnr_id = f"VNR_{i+1}"
        
        vnr = generate_vnr(
            substrate_nodes, 
            arrival_time=arrival_time,
            vnr_id=vnr_id,
            **kwargs
        )
        vnrs.append(vnr)
    
    return vnrs


def create_example_substrate():
    """Create example substrate for testing."""
    G = nx.Graph()
    
    # Add nodes with CPU capacity
    G.add_node(1, cpu=100)
    G.add_node(2, cpu=150)
    G.add_node(3, cpu=80)
    G.add_node(4, cpu=120)
    G.add_node(5, cpu=90)
    G.add_node(6, cpu=110)
    G.add_node(7, cpu=140)
    
    # Add edges with bandwidth capacity
    edges = [
        (1, 2, 100), (1, 3, 80), (2, 4, 120), (2, 5, 90),
        (2, 6, 135), (3, 4, 100), (4, 5, 110), (6, 1, 95),
        (7, 5, 105), (7, 4, 125), (2, 3, 85)
    ]
    
    for u, v, bw in edges:
        G.add_edge(u, v, bandwidth=bw)
    
    return G
