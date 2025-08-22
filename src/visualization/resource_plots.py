import matplotlib.pyplot as plt
import networkx as nx
import os


def _categorize_edges_by_utilization(substrate, edge_utilization):
    """Categorize edges by utilization level for visual styling."""
    edge_categories = {'unused': [], 'light': [], 'medium': [], 'heavy': []}
    
    for edge in substrate.edges():
        util = edge_utilization.get(edge, 0.0) + edge_utilization.get((edge[1], edge[0]), 0.0)
        if util == 0:
            edge_categories['unused'].append(edge)
        elif util <= 0.33:
            edge_categories['light'].append(edge)
        elif util <= 0.66:
            edge_categories['medium'].append(edge)
        else:
            edge_categories['heavy'].append(edge)
    
    return edge_categories


def _draw_edges_by_category(substrate, pos, edge_categories):
    """Draw edges with different styles based on utilization category."""
    edge_styles = {
        'unused': {'edge_color': 'lightgray', 'width': 1, 'alpha': 0.4, 'style': 'dashed'},
        'light': {'edge_color': 'lightblue', 'width': 2, 'alpha': 0.7},
        'medium': {'edge_color': 'blue', 'width': 3, 'alpha': 0.8},
        'heavy': {'edge_color': 'darkblue', 'width': 4, 'alpha': 0.9}
    }
    
    for category, edges in edge_categories.items():
        if edges:
            style = edge_styles[category]
            nx.draw_networkx_edges(substrate, pos, edgelist=edges, **style)


def _create_edge_labels(substrate, edge_utilization):
    """Create edge labels showing used/total bandwidth."""
    edge_label_dict = {}
    for edge in substrate.edges():
        util = edge_utilization.get(edge, 0.0) + edge_utilization.get((edge[1], edge[0]), 0.0)
        if util > 0:
            total_bw = substrate.edges[edge]['bandwidth']
            used_bw = int(util * total_bw)
            edge_label_dict[edge] = f"{used_bw}/{total_bw}"
    return edge_label_dict


def _draw_resource_network(substrate, pos, node_utilization, edge_utilization=None, node_labels=True, edge_labels=False):
    """Helper function to draw substrate network with meaningful resource visualization."""
    # Draw nodes with CPU utilization colors
    node_colors = [plt.cm.Reds(node_utilization[node]) for node in substrate.nodes()]
    nx.draw_networkx_nodes(substrate, pos, node_color=node_colors, node_size=800, alpha=0.8)
    
    # Draw edges with bandwidth utilization visualization
    if edge_utilization is not None:
        edge_categories = _categorize_edges_by_utilization(substrate, edge_utilization)
        _draw_edges_by_category(substrate, pos, edge_categories)
        
        # Add edge labels if requested
        if edge_labels:
            edge_label_dict = _create_edge_labels(substrate, edge_utilization)
            if edge_label_dict:
                nx.draw_networkx_edge_labels(substrate, pos, edge_label_dict, font_size=8)
    else:
        # No edge utilization data - draw simple gray edges
        nx.draw_networkx_edges(substrate, pos, edge_color='gray', width=2, alpha=0.6)
    
    # Draw node labels
    if node_labels:
        labels = {n: f"{n}\n{node_utilization[n]:.2f}" for n in substrate.nodes()}
        nx.draw_networkx_labels(substrate, pos, labels, font_size=10)


def _calculate_utilization_from_embeddings(substrate, active_embeddings):
    """Calculate resource utilization from active VNR embeddings."""
    node_utilization = {node: 0.0 for node in substrate.nodes()}
    edge_utilization = {}
    
    # Initialize edge utilization for both directions (undirected graphs)
    for edge in substrate.edges():
        edge_utilization[edge] = 0.0
        edge_utilization[(edge[1], edge[0])] = 0.0
    
    # Calculate utilization from active embeddings
    for vnr_id, (node_mapping, link_mapping, vnr) in active_embeddings.items():
        # Node utilization
        for v_node, s_node in node_mapping.items():
            cpu_req = vnr.nodes[v_node]['cpu_req']
            total_cpu = substrate.nodes[s_node]['cpu']
            node_utilization[s_node] += cpu_req / total_cpu if total_cpu > 0 else 0
        
        # Edge utilization
        for v_edge, s_path in link_mapping.items():
            bw_req = vnr.edges[v_edge]['bandwidth_req']
            for i in range(len(s_path) - 1):
                edge1 = (s_path[i], s_path[i + 1])
                edge2 = (s_path[i + 1], s_path[i])
                
                actual_edge = edge1 if edge1 in substrate.edges() else (edge2 if edge2 in substrate.edges() else None)
                if actual_edge:
                    total_bw = substrate.edges[actual_edge]['bandwidth']
                    edge_utilization[actual_edge] += bw_req / total_bw if total_bw > 0 else 0
    
    return node_utilization, edge_utilization


def _add_visualization_elements(title, has_available=True):
    """Add colorbar and legend to resource visualization."""
    plt.title(title)
    plt.axis('off')
    
    # CPU utilization colorbar
    sm_nodes = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(vmin=0, vmax=1))
    sm_nodes.set_array([])
    cbar = plt.colorbar(sm_nodes, ax=plt.gca(), shrink=0.8, pad=0.02)
    cbar.set_label('CPU Utilization' if has_available else 'Relative CPU Capacity')
    
    # Edge utilization legend
    labels = ['Unused (0%)', 'Light use (1-33%)', 'Medium use (34-66%)', 'Heavy use (67-100%)'] if has_available else ['Low capacity', 'Med-low capacity', 'Med-high capacity', 'High capacity']
    legend_elements = [
        plt.Line2D([0], [0], color='lightgray', linestyle='--', linewidth=1, label=labels[0]),
        plt.Line2D([0], [0], color='lightblue', linewidth=2, label=labels[1]),
        plt.Line2D([0], [0], color='blue', linewidth=3, label=labels[2]),
        plt.Line2D([0], [0], color='darkblue', linewidth=4, label=labels[3])
    ]
    plt.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1.15, 0.5))


def plot_resource_utilization_snapshot(substrate, active_embeddings, title="Resource Utilization Snapshot", figsize=(12, 8), seed=42, filename=None, edge_labels=True):
    """Plot actual resource utilization from active VNR embeddings."""
    plt.figure(figsize=figsize)
    pos = nx.spring_layout(substrate, seed=seed)
    
    node_utilization, edge_utilization = _calculate_utilization_from_embeddings(substrate, active_embeddings)
    _draw_resource_network(substrate, pos, node_utilization, edge_utilization, edge_labels=edge_labels)
    _add_visualization_elements(title)
    
    if filename is None:
        filename = title.replace(" ", "_").lower() + ".png"
    
    filepath = os.path.join("pictures", filename)
    os.makedirs("pictures", exist_ok=True)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.show()


def _calculate_capacity_utilization(substrate):
    """Calculate utilization based on available resources or relative capacity."""
    node_utilization = {}
    edge_utilization = {}
    
    # Check if we have availability tracking
    has_available = any(substrate.nodes[n].get('cpu_available') is not None for n in substrate.nodes())
    
    # Calculate node utilization
    if has_available:
        for node in substrate.nodes():
            total_cpu = substrate.nodes[node]['cpu']
            available_cpu = substrate.nodes[node].get('cpu_available', total_cpu)
            node_utilization[node] = 1 - (available_cpu / total_cpu) if total_cpu > 0 else 0
    else:
        max_cpu = max(substrate.nodes[n]['cpu'] for n in substrate.nodes())
        for node in substrate.nodes():
            total_cpu = substrate.nodes[node]['cpu']
            node_utilization[node] = total_cpu / max_cpu if max_cpu > 0 else 0
    
    # Calculate edge utilization  
    if has_available:
        for edge in substrate.edges():
            total_bw = substrate.edges[edge]['bandwidth']
            available_bw = substrate.edges[edge].get('bandwidth_available', total_bw)
            edge_utilization[edge] = 1 - (available_bw / total_bw) if total_bw > 0 else 0
    else:
        max_bw = max(substrate.edges[e]['bandwidth'] for e in substrate.edges())
        for edge in substrate.edges():
            total_bw = substrate.edges[edge]['bandwidth']
            edge_utilization[edge] = total_bw / max_bw if max_bw > 0 else 0
    
    return node_utilization, edge_utilization, has_available


def plot_resource_utilization(substrate, title="Substrate Resource Utilization", figsize=(12, 8), seed=42, filename=None, edge_labels=False):
    """Plot substrate resource capacity or remaining available resources."""
    plt.figure(figsize=figsize)
    pos = nx.spring_layout(substrate, seed=seed)
    
    node_utilization, edge_utilization, has_available = _calculate_capacity_utilization(substrate)
    _draw_resource_network(substrate, pos, node_utilization, edge_utilization, edge_labels=edge_labels)
    
    final_title = title if has_available else f"{title} (Showing Relative Capacity)"
    _add_visualization_elements(final_title, has_available)
    
    if filename is None:
        filename = title.replace(" ", "_").lower() + ".png"
    
    filepath = os.path.join("pictures", filename)
    os.makedirs("pictures", exist_ok=True)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.show()


def plot_embedding_visualization(substrate, node_mapping, link_mapping, vnr, title="VNR Embedding", figsize=(14, 10), seed=42, filename=None):
    plt.figure(figsize=figsize)
    pos = nx.spring_layout(substrate, seed=seed)
    
    # Draw substrate network in light colors
    nx.draw_networkx_nodes(substrate, pos, node_size=800, node_color='lightgray', alpha=0.5)
    nx.draw_networkx_edges(substrate, pos, width=1, edge_color='lightgray', alpha=0.3)
    
    # Highlight embedded nodes
    embedded_nodes = list(node_mapping.values())
    nx.draw_networkx_nodes(substrate, pos, nodelist=embedded_nodes, 
                          node_size=1000, node_color='red', alpha=0.8)
    
    # Highlight embedded paths
    for v_edge, s_path in link_mapping.items():
        for i in range(len(s_path) - 1):
            edge = (s_path[i], s_path[i + 1])
            if edge in substrate.edges():
                nx.draw_networkx_edges(substrate, pos, edgelist=[edge], 
                                     width=3, edge_color='blue', alpha=0.8)
            else:
                edge = (s_path[i + 1], s_path[i])
                if edge in substrate.edges():
                    nx.draw_networkx_edges(substrate, pos, edgelist=[edge], 
                                         width=3, edge_color='blue', alpha=0.8)
    
    # Add labels for substrate nodes
    nx.draw_networkx_labels(substrate, pos, font_size=10)
    
    # Add mapping information
    mapping_text = "Node Mapping:\n"
    for v_node, s_node in node_mapping.items():
        cpu_req = vnr.nodes[v_node]['cpu_req']
        mapping_text += f"v{v_node} → s{s_node} (CPU: {cpu_req})\n"
    
    plt.text(0.02, 0.98, mapping_text, transform=plt.gca().transAxes, 
             verticalalignment='top', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.title(title)
    plt.axis('off')
    
    if filename is None:
        filename = title.replace(" ", "_").lower() + ".png"
    
    filepath = os.path.join("pictures", filename)
    os.makedirs("pictures", exist_ok=True)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.show()