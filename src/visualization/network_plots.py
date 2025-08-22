import matplotlib.pyplot as plt
import networkx as nx
import os


def plot_substrate_network(substrate, title="Substrate Network", figsize=(10, 8), seed=42):
    plt.figure(figsize=figsize)
    pos = nx.spring_layout(substrate, seed=seed)
    node_sizes = [len(str(substrate.nodes[n]['cpu'])) * 400 + 600 for n in substrate.nodes()]

    # Draw with labels showing constraints
    nx.draw_networkx_nodes(substrate, pos, node_size=node_sizes, node_color='lightblue')
    nx.draw_networkx_edges(substrate, pos, width=2)

    # Node labels with CPU
    node_labels = {n: f"{n}\nCPU:{substrate.nodes[n]['cpu']}" for n in substrate.nodes()}
    nx.draw_networkx_labels(substrate, pos, node_labels, font_size=9)

    # Edge labels with bandwidth and cost (if available)
    edge_labels = {}
    for e in substrate.edges():
        bw = substrate.edges[e]['bandwidth']
        if 'cost' in substrate.edges[e]:
            edge_labels[e] = f"BW:{bw}\ncost:{substrate.edges[e]['cost']}"
        else:
            edge_labels[e] = f"BW:{bw}"
    nx.draw_networkx_edge_labels(substrate, pos, edge_labels, font_size=8)

    plt.title(title)
    plt.axis('off')
    filename = os.path.join("pictures", title.replace(" ", "_").lower() + ".png")
    os.makedirs("pictures", exist_ok=True)
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()


def plot_network_from_function(network_function, network_name, seed=42):
    """Generic function to plot any substrate network created by a function."""
    network = network_function()
    print(f"{network_name} network created: {len(network.nodes())} nodes, {len(network.edges())} edges")
    
    plot_substrate_network(network, f"{network_name} Substrate Network", seed=seed)


def plot_german_network():
    from ..networks.substrate_networks import create_german_network
    plot_network_from_function(create_german_network, "German", seed=42)


def plot_italian_network():
    from ..networks.substrate_networks import create_italian_network
    plot_network_from_function(create_italian_network, "Italian", seed=44)


def plot_generated_substrate(nodes=10, topology="erdos_renyi", title=None, **kwargs):
    """Plot substrate network created by generators with flexible parameters."""
    from ..networks.vne_generators import generate_substrate_network
    
    if title is None:
        title = f"Generated {topology.title().replace('_', ' ')} Substrate ({nodes} nodes)"
    
    substrate = generate_substrate_network(nodes, topology=topology, **kwargs)
    print(f"Generated substrate: {len(substrate.nodes())} nodes, {len(substrate.edges())} edges")
    
    plot_substrate_network(substrate, title, seed=kwargs.get('seed', 42))


def plot_example_substrate():
    """Plot the example substrate network from generators."""
    from ..networks.vne_generators import create_example_substrate
    
    substrate = create_example_substrate()
    print(f"Example substrate: {len(substrate.nodes())} nodes, {len(substrate.edges())} edges")
    
    plot_substrate_network(substrate, "Example Substrate Network", seed=42)


def plot_single_vnr(vnr, title=None, figsize=(6, 4), ax=None, save_file=True):
    if ax is None:
        plt.figure(figsize=figsize)
        ax = plt.gca()
    
    if title is None:
        arrival = vnr.graph['arrival_time']
        lifetime = vnr.graph['lifetime']
        title = f"{vnr.graph['vnr_id']}\nArrival: {arrival}, Life: {lifetime}"
    
    # Create layout for this VNR
    pos = nx.spring_layout(vnr, seed=42)

    # Draw nodes
    nx.draw_networkx_nodes(vnr, pos, node_size=1000, node_color='lightcoral', alpha=0.7, ax=ax)

    # Draw edges
    nx.draw_networkx_edges(vnr, pos, width=1.5, alpha=0.6, ax=ax)

    # Add node labels with CPU requirements
    node_labels = {n: f"{n}\n{vnr.nodes[n]['cpu_req']}" for n in vnr.nodes()}
    nx.draw_networkx_labels(vnr, pos, node_labels, font_size=14, ax=ax)

    # Add edge labels with bandwidth requirements
    edge_labels = {e: f"{vnr.edges[e]['bandwidth_req']}" for e in vnr.edges()}
    nx.draw_networkx_edge_labels(vnr, pos, edge_labels, font_size=12, ax=ax)

    ax.set_title(title, fontsize=16)
    ax.axis('off')
    
    if save_file and ax == plt.gca():
        filename = os.path.join("pictures", title.replace(" ", "_").replace(":", "").replace("\n", "_").replace(",", "").lower() + ".png")
        os.makedirs("pictures", exist_ok=True)
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.show()


def plot_all_vnrs(vnr_queue=None, title_prefix="All VNRs", filename="all_vnrs.png"):
    if vnr_queue is None:
        from ..networks.vnr_creation import create_vnr_queue
        vnr_queue = create_vnr_queue()
    
    num_vnrs = len(vnr_queue)
    
    # Calculate optimal grid dimensions
    import math
    cols = math.ceil(math.sqrt(num_vnrs))
    rows = math.ceil(num_vnrs / cols)
    
    # Dynamic figure size based on number of VNRs
    fig_width = cols * 5
    fig_height = rows * 4
    
    fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height))
    
    # Handle case where there's only one subplot
    if num_vnrs == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    for i, vnr in enumerate(vnr_queue):
        ax = axes[i]
        
        # Use the single VNR plotting function with custom title
        arrival = vnr.graph['arrival_time']
        lifetime = vnr.graph['lifetime']
        title = f"{vnr.graph['vnr_id']}\nArrival: {arrival}, Life: {lifetime}"
        
        plot_single_vnr(vnr, title=title, ax=ax, save_file=False)
        ax.set_title(title, fontsize=16)  # Adjusted fontsize for flexibility
    
    # Hide empty subplots if any
    for i in range(num_vnrs, len(axes)):
        axes[i].set_visible(False)

    plt.suptitle(f'{title_prefix} ({num_vnrs} VNRs) - Node Labels: CPU Requirements, Edge Labels: Bandwidth Requirements', 
                 fontsize=max(20, min(30, fig_width)), y=0.98)
    plt.tight_layout()
    os.makedirs("pictures", exist_ok=True)
    plt.savefig(os.path.join("pictures", filename), dpi=300, bbox_inches='tight')
    plt.show()


def plot_vnr_characteristics(vnr_queue=None, title_prefix="VNR", filename="vnr_characteristics.png"):
    if vnr_queue is None:
        from ..networks.vnr_creation import create_vnr_queue
        vnr_queue = create_vnr_queue()
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Plot 1: Node sizes distribution
    sizes = [len(vnr.nodes()) for vnr in vnr_queue]
    ax1.hist(sizes, bins=range(min(sizes), max(sizes)+2), alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Number of Nodes')
    ax1.set_ylabel('Frequency')
    ax1.set_title('VNR Node Size Distribution')
    
    # Plot 2: Arrival times
    arrival_times = [vnr.graph['arrival_time'] for vnr in vnr_queue]
    ax2.scatter(range(len(arrival_times)), arrival_times, alpha=0.7)
    ax2.set_xlabel('VNR Index')
    ax2.set_ylabel('Arrival Time')
    ax2.set_title('VNR Arrival Times')
    
    # Plot 3: Lifetimes
    lifetimes = [vnr.graph['lifetime'] for vnr in vnr_queue]
    ax3.hist(lifetimes, bins=10, alpha=0.7, edgecolor='black')
    ax3.set_xlabel('Lifetime')
    ax3.set_ylabel('Frequency')
    ax3.set_title('VNR Lifetime Distribution')
    
    # Plot 4: CPU vs Bandwidth requirements
    cpu_reqs = [sum(vnr.nodes[n]['cpu_req'] for n in vnr.nodes()) for vnr in vnr_queue]
    bw_reqs = [sum(vnr.edges[e]['bandwidth_req'] for e in vnr.edges()) for vnr in vnr_queue]
    
    ax4.scatter(cpu_reqs, bw_reqs, alpha=0.7)
    ax4.set_xlabel('Total CPU Requirement')
    ax4.set_ylabel('Total Bandwidth Requirement')
    ax4.set_title('CPU vs Bandwidth Requirements')
    
    plt.suptitle(f'{title_prefix} Characteristics ({len(vnr_queue)} VNRs)', fontsize=16)
    plt.tight_layout()
    os.makedirs("pictures", exist_ok=True)
    plt.savefig(os.path.join("pictures", filename), dpi=300, bbox_inches='tight')
    plt.show()


def plot_generated_vnr_batch(substrate_nodes, count=10, title_prefix="Generated VNRs", filename="generated_vnrs.png", **kwargs):
    """Plot VNRs created by generator with flexible parameters."""
    from ..networks.vne_generators import generate_vnr_batch
    
    vnr_batch = generate_vnr_batch(substrate_nodes, count, **kwargs)
    
    plot_all_vnrs(vnr_batch, title_prefix=title_prefix, filename=filename)


def plot_single_generated_vnr(substrate_nodes, topology="random", title=None, **kwargs):
    """Plot a single VNR created by generator with flexible parameters."""
    from ..networks.vne_generators import generate_vnr
    
    vnr = generate_vnr(substrate_nodes, topology=topology, **kwargs)
    
    if title is None:
        title = f"Generated {topology.title()} VNR ({len(vnr.nodes())} nodes)"
    
    plot_single_vnr(vnr, title=title)