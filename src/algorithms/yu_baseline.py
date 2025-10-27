import networkx as nx
import itertools

def calculate_revenue(vnr):
    revenue = total_bandwidth = total_cpu = 0
    alpha = 2  # adjustable for balance
    for node in vnr.nodes():
        total_cpu += vnr.nodes[node]['cpu_req']

    for edge in vnr.edges():
        total_bandwidth += vnr.edges[edge]['bandwidth_req']

    return total_cpu * alpha + total_bandwidth


def create_chunks(vnr_queue, time_window=25):
    chunks = []
    chunk = []
    sorted_vnrs = sorted(vnr_queue, key=lambda vnr: vnr.graph['arrival_time'])
    start_time = 0

    for vnr in sorted_vnrs:
        vnr.graph['retried'] = False  # Normally should be waiting time but we'll consider 1 time window for each vnr
        if vnr.graph['arrival_time'] <= start_time + time_window:
            chunk.append(vnr)
        else:
            chunks.append(chunk)
            chunk = [vnr]
            start_time += time_window
    if chunk:  # Add the last chunk
        chunks.append(chunk)

    return chunks
        

def yu2008_algorithm(substrate, vnr_chunks, time_window=25):
    # Yu 2008 Baseline Algorithm - CHUNKED APPROACH
    # CRITICAL: This algorithm works with time windows/chunks,
    # NOT individual VNRs like the other algorithms.
    
    # Historical mappings for metrics calculation (never deleted)
    historical_node_mapping = {}
    historical_link_mapping = {}
    
    # Store VNR metadata for result generation (FIX: Include arrival_time)
    vnr_metadata = {}
    for chunk in vnr_chunks:
        for vnr in chunk:
            vnr_metadata[vnr.graph['vnr_id']] = {
                'arrival_time': vnr.graph['arrival_time'],
                'vnr_object': vnr
            }

    def get_node_rank(node):
        node_total_bandwidth = 0
        for neighbor in substrate.neighbors(node):
            edge = (node, neighbor)
            if edge in substrate.edges():
                node_total_bandwidth += substrate.edges[edge]['bandwidth_available']
            else:
                node_total_bandwidth += substrate.edges[(neighbor, node)]['bandwidth_available']
        return node_total_bandwidth * substrate.nodes[node]['cpu_available']

    # Iterate through the chunks
    node_mapping = {}
    link_mapping = {}
    active_embeddings = {}
    successfully_embedded_vnrs = set()  # Track VNR IDs that were successfully embedded
    
    # Track all VNRs processed (for final results)
    all_processed_vnrs = set()
    for chunk in vnr_chunks:
        for vnr in chunk:
            all_processed_vnrs.add(vnr.graph['vnr_id'])
    
    for i, chunk in enumerate(vnr_chunks):
        current_time = (i + 1) * time_window
        failed_vnrs = []
        successfully_mapped_vnrs = []

        # Process departures
        for vnr_id, embedding_info in list(active_embeddings.items()):
            departure_time = embedding_info['departure_time']
            vnr = embedding_info['vnr']
            if departure_time <= current_time:

                # Deallocate already allocated CPU for this VNR
                for v_node in vnr.nodes():
                    s_node = node_mapping[(vnr.graph['vnr_id'], v_node)]
                    substrate.nodes[s_node]['cpu_available'] += vnr.nodes[v_node]['cpu_req']
                    node_mapping.pop((vnr.graph['vnr_id'], v_node))

                # Deallocate already allocated Bandwidth for this VNR
                for v_mapped_edge in vnr.edges():
                    if (vnr.graph['vnr_id'], v_mapped_edge) in link_mapping:
                        mapped_path = link_mapping[(vnr.graph['vnr_id'], v_mapped_edge)]
                        link_mapping.pop((vnr.graph['vnr_id'], v_mapped_edge))
                        for j in range(len(mapped_path) - 1):
                            edge = (mapped_path[j], mapped_path[j + 1])
                            substrate.edges[edge]['bandwidth_available'] += vnr.edges[v_mapped_edge]['bandwidth_req']

                del active_embeddings[vnr_id]

        # Sort based on revenue
        chunk.sort(key=calculate_revenue, reverse=True)

        # Phase 1: Node mapping (greedy by available CPU)
        for vnr in chunk:
            vnr_node_mapping = {}  # Only for intra-VNR constraint checking
            vnr_cpu_requirements = [vnr.nodes[v_node]['cpu_req'] for v_node in vnr.nodes()]
            min_cpu_req = min(vnr_cpu_requirements)

            # Filter substrate nodes: each node in S can host at least one virtual node
            S = [node for node in substrate.nodes() if substrate.nodes[node]['cpu_available'] >= min_cpu_req]

            if not S:  # If S is empty, defer this request
                if not vnr.graph['retried']:
                    failed_vnrs.append(vnr)
                    vnr.graph['retried'] = True
                continue  # Go to next VNR

            substrate_nodes = sorted(S, key=get_node_rank, reverse=True)
            node_mapping_successful = True

            for v_node in vnr.nodes():
                cpu_req = vnr.nodes[v_node]['cpu_req']
                mapped = False

                for s_node in substrate_nodes:
                    # Check intra-VNR separation constraint
                    if s_node in vnr_node_mapping.values():
                        continue

                    # Check CPU availability
                    if substrate.nodes[s_node]['cpu_available'] >= cpu_req:
                        node_mapping[(vnr.graph['vnr_id'], v_node)] = s_node
                        vnr_node_mapping[v_node] = s_node
                        substrate.nodes[s_node]['cpu_available'] -= cpu_req
                        mapped = True
                        break

                if not mapped:
                    node_mapping_successful = False
                    # Deallocate already allocated CPU for this VNR
                    for allocated_v_node in vnr_node_mapping:
                        allocated_s_node = vnr_node_mapping[allocated_v_node]
                        substrate.nodes[allocated_s_node]['cpu_available'] += vnr.nodes[allocated_v_node]['cpu_req']
                        node_mapping.pop((vnr.graph['vnr_id'], allocated_v_node))
                    if not vnr.graph['retried']:
                        failed_vnrs.append(vnr)
                        vnr.graph['retried'] = True
                    break

            if node_mapping_successful:
                successfully_mapped_vnrs.append(vnr)

        # Phase 2: Link mapping (k-shortest)
        successfully_mapped_vnrs.sort(key=calculate_revenue, reverse=True)

        for vnr in successfully_mapped_vnrs:
            vnr_fully_embedded = True
            for v_edge in vnr.edges():
                v_src, v_dst = v_edge
                s_src = node_mapping[(vnr.graph['vnr_id'], v_src)]
                s_dst = node_mapping[(vnr.graph['vnr_id'], v_dst)]
                bandwidth_req = vnr.edges[v_edge]['bandwidth_req']

                path_found = False
                for k in range(1, 4):  # keep k small
                    try:
                        # Get only k paths, not ALL paths (critical performance fix)
                        paths = list(itertools.islice(nx.shortest_simple_paths(substrate, s_src, s_dst), k))
                        for path in paths:
                            # Check bandwidth
                            can_allocate = True
                            for j in range(len(path) - 1):
                                edge = (path[j], path[j + 1])
                                if substrate.edges[edge]['bandwidth_available'] < bandwidth_req:
                                    can_allocate = False
                                    break

                            # Allocate bandwidth
                            if can_allocate:
                                path_found = True
                                link_mapping[(vnr.graph['vnr_id'], v_edge)] = path
                                for j in range(len(path) - 1):
                                    edge = (path[j], path[j + 1])
                                    substrate.edges[edge]['bandwidth_available'] -= bandwidth_req
                                break
                    except nx.NetworkXNoPath:
                        break

                    if path_found:  # don't try more k values
                        break

                if not path_found:
                    vnr_fully_embedded = False
                    # Deallocate already allocated CPU for this VNR
                    for v_node in vnr.nodes():
                        s_node = node_mapping[(vnr.graph['vnr_id'], v_node)]
                        substrate.nodes[s_node]['cpu_available'] += vnr.nodes[v_node]['cpu_req']
                        node_mapping.pop((vnr.graph['vnr_id'], v_node))

                    # Deallocate already allocated Bandwidth for this VNR
                    for v_mapped_edge in vnr.edges():
                        if (vnr.graph['vnr_id'], v_mapped_edge) in link_mapping:
                            mapped_path = link_mapping[(vnr.graph['vnr_id'], v_mapped_edge)]
                            link_mapping.pop((vnr.graph['vnr_id'], v_mapped_edge))
                            for j in range(len(mapped_path) - 1):
                                edge = (mapped_path[j], mapped_path[j + 1])
                                substrate.edges[edge]['bandwidth_available'] += vnr.edges[v_mapped_edge]['bandwidth_req']

                    if not vnr.graph['retried']:
                        failed_vnrs.append(vnr)
                        vnr.graph['retried'] = True
                    break

            if vnr_fully_embedded:
                departure_time = current_time + vnr.graph['lifetime']
                active_embeddings[vnr.graph['vnr_id']] = {
                    'vnr': vnr,
                    'departure_time': departure_time
                }
                successfully_embedded_vnrs.add(vnr.graph['vnr_id'])

                # CRITICAL FIX: Store actual embedding time (not arrival time)
                # This is needed for correct utilization visualization
                vnr_metadata[vnr.graph['vnr_id']]['embedding_time'] = current_time

                # Save to historical mappings for metrics calculation
                for k, v in node_mapping.items():
                    if k[0] == vnr.graph['vnr_id']:
                        historical_node_mapping[k] = v
                for k, v in link_mapping.items():
                    if k[0] == vnr.graph['vnr_id']:
                        historical_link_mapping[k] = v

        # Add failed VNRs to next chunk (if there is one)
        if failed_vnrs:
            if i < len(vnr_chunks) - 1:  # Not the last chunk
                vnr_chunks[i+1].extend(failed_vnrs)
            else:
                vnr_chunks.append(failed_vnrs)
    
    # Return standardized results format for visualization/metrics
    results = []
    for vnr_id in all_processed_vnrs:
        if vnr_id in successfully_embedded_vnrs:
            # Extract mappings for this VNR from historical storage
            vnr_node_mapping = {k[1]: v for k, v in historical_node_mapping.items() if k[0] == vnr_id}
            vnr_link_mapping = {k[1]: v for k, v in historical_link_mapping.items() if k[0] == vnr_id}

            results.append({
                'vnr_id': vnr_id,
                'arrival_time': vnr_metadata[vnr_id]['arrival_time'],
                'embedding_time': vnr_metadata[vnr_id].get('embedding_time', vnr_metadata[vnr_id]['arrival_time']),  # CRITICAL FIX
                'success': True,
                'node_mapping': vnr_node_mapping,
                'link_mapping': vnr_link_mapping
            })
        else:
            results.append({
                'vnr_id': vnr_id,
                'arrival_time': vnr_metadata[vnr_id]['arrival_time'],
                'embedding_time': None,  # Failed VNRs have no embedding time
                'success': False,
                'node_mapping': None,
                'link_mapping': None
            })
    
    return results