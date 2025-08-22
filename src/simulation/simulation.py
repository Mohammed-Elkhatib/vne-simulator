import networkx as nx


def allocate_resources(substrate, node_mapping, link_mapping, vnr):
    # Allocate CPU
    for v_node, s_node in node_mapping.items():
        cpu_req = vnr.nodes[v_node]['cpu_req']
        substrate.nodes[s_node]['cpu_available'] -= cpu_req

    # Allocate bandwidth
    for v_edge, s_path in link_mapping.items():
        bw_req = vnr.edges[v_edge]['bandwidth_req']
        for i in range(len(s_path) - 1):
            edge = (s_path[i], s_path[i + 1])
            if edge in substrate.edges():
                substrate.edges[edge]['bandwidth_available'] -= bw_req
            else:
                substrate.edges[(s_path[i + 1], s_path[i])]['bandwidth_available'] -= bw_req


def deallocate_resources(substrate, node_mapping, link_mapping, vnr):
    # Deallocate CPU
    for v_node, s_node in node_mapping.items():
        cpu_req = vnr.nodes[v_node]['cpu_req']
        substrate.nodes[s_node]['cpu_available'] += cpu_req

    # Deallocate bandwidth
    for v_edge, s_path in link_mapping.items():
        bw_req = vnr.edges[v_edge]['bandwidth_req']
        for i in range(len(s_path) - 1):
            edge = (s_path[i], s_path[i + 1])
            if edge in substrate.edges():
                substrate.edges[edge]['bandwidth_available'] += bw_req
            else:
                substrate.edges[(s_path[i + 1], s_path[i])]['bandwidth_available'] += bw_req


def vne_simulation(substrate, vnr_queue, algorithm_func):
    # Initialize substrate with available resources
    substrate_working = substrate.copy()
    for node in substrate_working.nodes():
        substrate_working.nodes[node]['cpu_available'] = substrate_working.nodes[node]['cpu']
    for edge in substrate_working.edges():
        substrate_working.edges[edge]['bandwidth_available'] = substrate_working.edges[edge]['bandwidth']

    # Create combined event queue
    events = []

    # Add all arrival events
    for vnr in vnr_queue:
        events.append({
            'time': vnr.graph['arrival_time'],
            'type': 'ARRIVAL',
            'vnr': vnr
        })

    # Sort events chronologically
    events.sort(key=lambda x: x['time'])

    # Simulation state
    active_embeddings = {}  # vnr_id -> (node_mapping, link_mapping, vnr)
    results = []

    print("VNE Simulation")
    print("-" * 60)

    # Process events one by one
    for event in events:
        current_time = event['time']

        if event['type'] == 'ARRIVAL':
            vnr = event['vnr']
            print(f"Time {current_time:>3}: {vnr.graph['vnr_id']} ARRIVES")

            # Try embedding
            node_mapping, link_mapping, success = algorithm_func(substrate_working, vnr)

            if success:
                # Allocate resources
                allocate_resources(substrate_working, node_mapping, link_mapping, vnr)
                active_embeddings[vnr.graph['vnr_id']] = (node_mapping, link_mapping, vnr)

                # Add departure event to queue
                departure_time = current_time + vnr.graph['lifetime']
                events.append({
                    'time': departure_time,
                    'type': 'DEPARTURE',
                    'vnr_id': vnr.graph['vnr_id']
                })

                # Re-sort events since we added a departure
                events.sort(key=lambda x: x['time'])

                print(f"         SUCCESS - will depart at time {departure_time}")
            else:
                print(f"         FAILED")

            results.append({
                'vnr_id': vnr.graph['vnr_id'],
                'arrival_time': current_time,
                'success': success,
                'node_mapping': node_mapping,
                'link_mapping': link_mapping,
                'currently_active': len(active_embeddings)
            })

        elif event['type'] == 'DEPARTURE':
            vnr_id = event['vnr_id']
            if vnr_id in active_embeddings:
                node_mapping, link_mapping, vnr = active_embeddings[vnr_id]

                # Deallocate resources
                deallocate_resources(substrate_working, node_mapping, link_mapping, vnr)
                del active_embeddings[vnr_id]

                print(f"Time {current_time:>3}: {vnr_id} DEPARTS")

    print("-" * 60)
    print("Simulation completed")
    return results
