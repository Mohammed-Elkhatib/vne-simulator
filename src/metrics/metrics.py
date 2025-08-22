"""
VNE Metrics Module
Literature-compliant metrics calculations for Virtual Network Embedding
"""


def calculate_revenue(vnr):
    """Calculate VNR revenue."""
    cpu_revenue = sum(vnr.nodes[node]['cpu_req'] for node in vnr.nodes())
    bw_revenue = sum(vnr.edges[edge]['bandwidth_req'] for edge in vnr.edges())
    return cpu_revenue + bw_revenue


def calculate_cost(vnr, node_mapping, link_mapping):
    """Calculate embedding cost."""
    # CPU cost
    cpu_cost = sum(vnr.nodes[vnode]['cpu_req'] for vnode in node_mapping)
    
    # Bandwidth cost
    bw_cost = 0
    for vedge, spath in link_mapping.items():
        bw_req = vnr.edges[vedge]['bandwidth_req']
        path_length = len(spath) - 1 if len(spath) > 1 else 1
        bw_cost += bw_req * path_length
    
    return cpu_cost + bw_cost


def calculate_acceptance_ratio(results):
    """Calculate acceptance ratio."""
    if not results:
        return 0.0
    successful = sum(1 for r in results if r['success'])
    return successful / len(results)


def calculate_blocking_probability(results):
    """Calculate blocking probability."""
    return round(1.0 - calculate_acceptance_ratio(results), 3)


def calculate_revenue_cost_ratio(results):
    """Calculate revenue-to-cost ratio."""
    total_revenue = sum(r['revenue'] for r in results if r['success'])
    total_cost = sum(r['cost'] for r in results)
    return round(total_revenue / total_cost, 3) if total_cost > 0 else 0.0


def calculate_metrics_summary(results):
    """Calculate comprehensive metrics summary."""
    if not results:
        return {
            'total_requests': 0,
            'successful_requests': 0,
            'acceptance_ratio': 0.0,
            'blocking_probability': 0.0,
            'total_revenue': 0.0,
            'total_cost': 0.0,
            'revenue_cost_ratio': 0.0
        }
    
    total_requests = len(results)
    successful_requests = sum(1 for r in results if r['success'])
    total_revenue = sum(r['revenue'] for r in results if r['success'])
    total_cost = sum(r['cost'] for r in results)
    
    return {
        'total_requests': total_requests,
        'successful_requests': successful_requests,
        'acceptance_ratio': calculate_acceptance_ratio(results),
        'blocking_probability': calculate_blocking_probability(results),
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'revenue_cost_ratio': calculate_revenue_cost_ratio(results)
    }
