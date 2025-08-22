import networkx as nx
from .noderank import compute_noderank

def rw_bfs_algorithm(substrate, vnr, max_hop=3, max_backtrack=3):
    # Step 1: Compute NodeRank for both networks
    substrate_noderank = compute_noderank(substrate)
    vnr_noderank = compute_noderank(vnr)

    if substrate_noderank is None or vnr_noderank is None:
        return None, None, False

    # Step 2: Construct BFS tree and sort nodes by NodeRank
    bfs_order, bfs_parents = construct_bfs_tree_order(vnr, vnr_noderank)

    # Step 3: Build candidate substrate node lists
    candidate_lists = build_candidate_lists(substrate, vnr, substrate_noderank)

    # Step 4: BFS embedding with backtracking
    node_mapping, link_mapping, success = bfs_embedding_with_backtracking(
        substrate, vnr, bfs_order, bfs_parents, candidate_lists, 
        substrate_noderank, max_hop, max_backtrack)

    return node_mapping, link_mapping, success


def construct_bfs_tree_order(vnr, vnr_noderank):
    # Find root node (highest NodeRank)
    root_node = max(vnr.nodes(), key=lambda n: vnr_noderank[n])

    # BFS traversal
    current_level = [root_node]
    visited = {root_node}
    bfs_order = []
    bfs_parents = {root_node: None}

    while current_level:
        # Sort current level by NodeRank
        current_level.sort(key=lambda n: vnr_noderank[n], reverse=True)
        bfs_order.extend(current_level)

        # Build next level
        next_level = []
        for node in current_level:
            for neighbor in vnr.neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    next_level.append(neighbor)
                    bfs_parents[neighbor] = node

        current_level = next_level

    return bfs_order, bfs_parents


def build_candidate_lists(substrate, vnr, substrate_noderank):
    candidate_lists = {}

    for vnr_node in vnr.nodes():
        cpu_req = vnr.nodes[vnr_node].get('cpu_req', 0)
        
        # Calculate total bandwidth requirement for this VNR node
        total_bw_req = sum(vnr.edges[vnr_node, neighbor].get('bandwidth_req', 0) for neighbor in vnr.neighbors(vnr_node))

        # Find candidate substrate nodes
        candidates = []
        for sub_node in substrate.nodes():
            cpu_available = substrate.nodes[sub_node].get('cpu_available', 0)

            # Calculate total available bandwidth for substrate node
            total_bw_available = sum(substrate.edges[sub_node, neighbor].get('bandwidth_available', 0) for neighbor in substrate.neighbors(sub_node))

            # Check if substrate node can satisfy requirements
            if cpu_available >= cpu_req and total_bw_available >= total_bw_req:
                candidates.append(sub_node)

        # Sort candidates by NodeRank (decreasing order)
        candidates.sort(key=lambda n: substrate_noderank[n], reverse=True)
        candidate_lists[vnr_node] = candidates

    return candidate_lists


def bfs_embedding_with_backtracking(substrate, vnr, bfs_order, bfs_parents, 
                                    candidate_lists, substrate_noderank, max_hop, max_backtrack):
    node_mapping = {}
    link_mapping = {}
    backtrack_count = 0
    current_index = 0
    # Track which candidates have been tried for each VNR node
    tried_candidates = {vnr_node: set() for vnr_node in bfs_order}

    while current_index < len(bfs_order):
        vnr_node = bfs_order[current_index]

        # Get candidates that haven't been tried yet
        available_candidates = [cand for cand in candidate_lists[vnr_node] if cand not in tried_candidates[vnr_node]]

        # Try to match current VNR node
        match_result = match_vnr_node(substrate, vnr, vnr_node, available_candidates, 
                                    node_mapping, link_mapping, bfs_parents, max_hop)

        if match_result['success']:
            # Update mappings
            node_mapping[vnr_node] = match_result['substrate_node']
            if match_result['link_mappings']:
                link_mapping.update(match_result['link_mappings'])
            current_index += 1
        else:
            # No more candidates available for this node
            if backtrack_count < max_backtrack and current_index > 0:
                # Clear tried candidates for current and future nodes (fresh start for them)
                for i in range(current_index, len(bfs_order)):
                    tried_candidates[bfs_order[i]].clear()

                # Go back to previous node
                current_index -= 1
                prev_vnr_node = bfs_order[current_index]

                # Mark the previous choice as tried and remove its mapping
                if prev_vnr_node in node_mapping:
                    tried_candidates[prev_vnr_node].add(node_mapping[prev_vnr_node])
                    del node_mapping[prev_vnr_node]

                # Remove related link mappings
                link_mapping = {k: v for k, v in link_mapping.items() if prev_vnr_node not in k}

                backtrack_count += 1
            else:
                # Exceeded backtrack limit or at root - fail
                return None, None, False

    return node_mapping, link_mapping, True


def match_vnr_node(substrate, vnr, vnr_node, candidates, current_node_mapping, 
                current_link_mapping, bfs_parents, max_hop):
    cpu_req = vnr.nodes[vnr_node].get('cpu_req', 0)

    # If this is the root node (first node), map to best candidate
    if not current_node_mapping:
        for sub_node in candidates:
            if substrate.nodes[sub_node].get('cpu_available', 0) >= cpu_req:
                return {
                    'success': True,
                    'substrate_node': sub_node,
                    'link_mappings': {}
                }
        return {'success': False}

    # For non-root nodes, consider hop constraints
    for k in range(1, max_hop + 1):
        for sub_node in candidates:
            # Check if already used
            if sub_node in current_node_mapping.values():
                continue

            # Check CPU constraint
            if substrate.nodes[sub_node].get('cpu_available', 0) < cpu_req:
                continue

            # Check hop constraint - find if there's a path within k hops from parent
            hop_constraint_satisfied = check_hop_constraint(substrate, vnr_node, sub_node, 
                                                            current_node_mapping, bfs_parents, k)

            if hop_constraint_satisfied:
                # Try to map all edges from this VNR node to already mapped neighbors
                link_mappings = {}
                all_links_mappable = True

                for neighbor in vnr.neighbors(vnr_node):
                    if neighbor in current_node_mapping:
                        # Need to map edge (vnr_node, neighbor)
                        neighbor_sub_node = current_node_mapping[neighbor]
                        bw_req = vnr.edges[vnr_node, neighbor].get('bandwidth_req', 0)

                        # Find shortest path
                        try:
                            path = nx.shortest_path(substrate, sub_node, neighbor_sub_node)

                            # Check bandwidth availability on path
                            path_feasible = True
                            for i in range(len(path) - 1):
                                edge_bw = substrate.edges[path[i], path[i+1]].get('bandwidth_available', 0)
                                if edge_bw < bw_req:
                                    path_feasible = False
                                    break

                            if path_feasible:
                                link_mappings[(vnr_node, neighbor)] = path
                            else:
                                all_links_mappable = False
                                break

                        except nx.NetworkXNoPath:
                            all_links_mappable = False
                            break

                if all_links_mappable:
                    return {
                        'success': True,
                        'substrate_node': sub_node,
                        'link_mappings': link_mappings
                    }

    return {'success': False}


def check_hop_constraint(substrate, vnr_node, sub_node, current_node_mapping, bfs_parents, max_k):
    parent_node = bfs_parents.get(vnr_node)

    # Root node has no parent - always satisfies constraint
    if parent_node is None:
        return True

    # Check distance to parent's substrate node
    parent_sub_node = current_node_mapping[parent_node]
    try:
        distance = nx.shortest_path_length(substrate, sub_node, parent_sub_node)
        return distance <= max_k
    except nx.NetworkXNoPath:
        return False
