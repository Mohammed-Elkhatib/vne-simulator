import networkx as nx
import itertools
from .noderank import compute_noderank

def rw_maxmatch_algorithm(substrate, vnr):
    # Step 1: Compute NodeRank for both networks
    substrate_noderank = compute_noderank(substrate)
    vnr_noderank = compute_noderank(vnr)

    if substrate_noderank is None or vnr_noderank is None:
        return None, None, False

    # Step 2: Node mapping (Algorithm 2)
    node_mapping, success = rw_maxmatch_node_mapping(substrate, vnr, substrate_noderank, vnr_noderank)
    if not success:
        return None, None, False

    # Step 3: Link mapping (Algorithm 3)
    link_mapping, success = rw_maxmatch_link_mapping(substrate, vnr, node_mapping)

    return node_mapping, link_mapping, success


def rw_maxmatch_node_mapping(substrate, vnr, substrate_noderank, vnr_noderank):
    # Step 1: Sort substrate nodes by NodeRank (decreasing order)
    sorted_substrate_nodes = sorted(substrate.nodes(), key=lambda n: substrate_noderank[n], reverse=True)

    # Step 2: Sort VNR nodes by NodeRank (decreasing order)
    sorted_vnr_nodes = sorted(vnr.nodes(), key=lambda n: vnr_noderank[n], reverse=True)

    # Step 3: L2S2 mapping (large-to-large, small-to-small)
    node_mapping = {}

    for vnr_node in sorted_vnr_nodes:
        cpu_req = vnr.nodes[vnr_node].get('cpu_req', 0)
        mapped = False

        # Try substrate nodes in order of their NodeRank
        for substrate_node in sorted_substrate_nodes:
            # Check if already mapped (intra-VNR separation constraint)
            if substrate_node in node_mapping.values():
                continue

            # Check CPU capacity constraint
            cpu_available = substrate.nodes[substrate_node].get('cpu_available', 0)
            if cpu_available >= cpu_req:
                node_mapping[vnr_node] = substrate_node
                mapped = True
                break

        if not mapped:
            return None, False

    return node_mapping, True


def rw_maxmatch_link_mapping(substrate, vnr, node_mapping):
    link_mapping = {}

    # Map each virtual link to a substrate path
    for v_edge in vnr.edges():
        v_src, v_dst = v_edge
        s_src = node_mapping[v_src]
        s_dst = node_mapping[v_dst]
        bw_req = vnr.edges[v_edge].get('bandwidth_req', 0)

        # Try k-shortest paths (starting with k=1)
        path_found = False
        for k in range(1, 4):
            try:
                # Get only k paths, not ALL paths (critical performance fix)
                paths = list(itertools.islice(nx.shortest_simple_paths(substrate, s_src, s_dst), k))
                if len(paths) < k:
                    break  # No more paths available

                path = paths[k-1]  # Get the k-th shortest path

                # Check if this path has enough bandwidth on all links
                can_allocate = True
                for i in range(len(path) - 1):
                    edge_bw = substrate.edges[path[i], path[i+1]].get('bandwidth_available', 0)
                    if edge_bw < bw_req:
                        can_allocate = False
                        break

                if can_allocate:
                    link_mapping[v_edge] = path
                    path_found = True
                    break  # Found a suitable path, move to next virtual link

            except (nx.NetworkXNoPath, nx.NetworkXError):
                break  # No more paths to try

        if not path_found:
            return None, False

    return link_mapping, True
