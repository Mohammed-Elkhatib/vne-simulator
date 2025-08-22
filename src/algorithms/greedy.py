import networkx as nx

def simple_greedy_algorithm(substrate, vnr):
    node_mapping = {}
    link_mapping = {}

    # Phase 1: Node mapping (greedy by available CPU)
    substrate_nodes = sorted(substrate.nodes(),
                           key=lambda n: substrate.nodes[n]['cpu_available'],
                           reverse=True)

    for v_node in vnr.nodes():
        cpu_req = vnr.nodes[v_node]['cpu_req']
        mapped = False

        for s_node in substrate_nodes:
            # Check intra-VNR separation constraint
            if s_node in node_mapping.values():
                continue

            # Check CPU availability
            if substrate.nodes[s_node]['cpu_available'] >= cpu_req:
                node_mapping[v_node] = s_node
                mapped = True
                break

        if not mapped:
            return None, None, False

    # Phase 2: Link mapping (shortest path)
    for v_edge in vnr.edges():
        v_src, v_dst = v_edge
        s_src = node_mapping[v_src]
        s_dst = node_mapping[v_dst]
        bw_req = vnr.edges[v_edge]['bandwidth_req']

        try:
            path = nx.shortest_path(substrate, s_src, s_dst)
            # Check bandwidth on path
            can_allocate = True
            for i in range(len(path) - 1):
                edge = (path[i], path[i + 1])
                if edge in substrate.edges():
                    if substrate.edges[edge]['bandwidth_available'] < bw_req:
                        can_allocate = False
                        break
                else:
                    edge_rev = (path[i + 1], path[i])
                    if substrate.edges[edge_rev]['bandwidth_available'] < bw_req:
                        can_allocate = False
                        break

            if can_allocate:
                link_mapping[v_edge] = path
            else:
                return None, None, False

        except nx.NetworkXNoPath:
            return None, None, False

    return node_mapping, link_mapping, True
