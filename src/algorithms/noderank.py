def compute_noderank(graph, max_iterations=100, epsilon=0.0001, p_jump=0.15, p_forward=0.85):
    # Step 1: Calculate H(u) = CPU(u) × Σ BW(l) for each node (Equation 6)
    H = {}
    for node in graph.nodes():
        cpu = (graph.nodes[node].get('cpu_available', 0) or 
               graph.nodes[node].get('cpu_req', 0) or 
               graph.nodes[node].get('cpu', 0))
        total_bandwidth = sum((graph.edges[node, neighbor].get('bandwidth_available', 0) or 
                              graph.edges[node, neighbor].get('bandwidth_req', 0) or 
                              graph.edges[node, neighbor].get('bandwidth', 0)) 
                             for neighbor in graph.neighbors(node))
        H[node] = cpu * total_bandwidth

    # Step 2: Initialize NR^(0)(u) = H(u) / Σ H(v) (Equation 7)
    total_H = sum(H.values())
    if total_H == 0:
        # No resources available - embedding will definitely fail
        return None
    else:
        node_rank = {node: H[node] / total_H for node in graph.nodes()}

    # Step 3: Iterative refinement (Algorithm 1)
    for iteration in range(max_iterations):
        new_rank = {}

        # Update each node's rank using Equation 10
        for v in graph.nodes():

            # Part 1: Global influence - Σ_{u∈V} p^J_uv · p^J_u · NR^(t)(u)
            # where p^J_uv = H(v) / Σ_{w∈V} H(w) (Equation 8)
            jump_prob_to_v = H[v] / total_H
            global_influence = jump_prob_to_v * p_jump * sum(node_rank.values())

            # Part 2: Local influence - Σ_{u∈nbr1(v)} p^F_uv · p^F_u · NR^(t)(u)
            # where p^F_uv = H(v) / Σ_{w∈nbr1(u)} H(w) (Equation 9)
            local_influence = 0
            neighbors_of_v = list(graph.neighbors(v))

            for u in neighbors_of_v:
                neighbors_of_u = list(graph.neighbors(u))
                total_neighbor_H = sum(H[w] for w in neighbors_of_u)

                if total_neighbor_H > 0:
                    # p^F_uv = H(v) / Σ_{w∈nbr1(u)} H(w)
                    forward_prob = H[v] / total_neighbor_H
                    local_influence += forward_prob * p_forward * node_rank[u]

            # Combine both influences (Equation 10)
            new_rank[v] = global_influence + local_influence

        # Step 4: Check convergence (Algorithm 1, step 6)
        total_diff = sum(abs(new_rank[node] - node_rank[node]) for node in graph.nodes())
        if total_diff < epsilon:
            break

        node_rank = new_rank

    return node_rank
