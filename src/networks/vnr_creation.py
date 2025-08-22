import networkx as nx


def create_vnr_queue():
    vnr_queue = []

    # VNR 1: 3-node path
    vnr1 = nx.Graph()
    vnr1.graph.update({'vnr_id': 'VNR_1', 'arrival_time': 5, 'lifetime': 20})
    vnr1.add_node(1, cpu_req=15)
    vnr1.add_node(2, cpu_req=25)
    vnr1.add_node(3, cpu_req=20)
    vnr1.add_edge(1, 2, bandwidth_req=10)
    vnr1.add_edge(2, 3, bandwidth_req=15)
    vnr_queue.append(vnr1)

    # VNR 2: 3-node triangle
    vnr2 = nx.Graph()
    vnr2.graph.update({'vnr_id': 'VNR_2', 'arrival_time': 10, 'lifetime': 30})
    vnr2.add_node(1, cpu_req=20)
    vnr2.add_node(2, cpu_req=15)
    vnr2.add_node(3, cpu_req=25)
    vnr2.add_edge(1, 2, bandwidth_req=8)
    vnr2.add_edge(2, 3, bandwidth_req=12)
    vnr2.add_edge(1, 3, bandwidth_req=10)
    vnr_queue.append(vnr2)

    # VNR 3: 4-node path
    vnr3 = nx.Graph()
    vnr3.graph.update({'vnr_id': 'VNR_3', 'arrival_time': 15, 'lifetime': 25})
    vnr3.add_node(1, cpu_req=18)
    vnr3.add_node(2, cpu_req=22)
    vnr3.add_node(3, cpu_req=16)
    vnr3.add_node(4, cpu_req=28)
    vnr3.add_edge(1, 2, bandwidth_req=12)
    vnr3.add_edge(2, 3, bandwidth_req=9)
    vnr3.add_edge(3, 4, bandwidth_req=14)
    vnr_queue.append(vnr3)

    # VNR 4: 4-node star
    vnr4 = nx.Graph()
    vnr4.graph.update({'vnr_id': 'VNR_4', 'arrival_time': 20, 'lifetime': 35})
    vnr4.add_node(1, cpu_req=30)  # Center node
    vnr4.add_node(2, cpu_req=12)
    vnr4.add_node(3, cpu_req=18)
    vnr4.add_node(4, cpu_req=14)
    vnr4.add_edge(1, 2, bandwidth_req=16)
    vnr4.add_edge(1, 3, bandwidth_req=11)
    vnr4.add_edge(1, 4, bandwidth_req=13)
    vnr_queue.append(vnr4)

    # VNR 5: 5-node path
    vnr5 = nx.Graph()
    vnr5.graph.update({'vnr_id': 'VNR_5', 'arrival_time': 25, 'lifetime': 40})
    vnr5.add_node(1, cpu_req=14)
    vnr5.add_node(2, cpu_req=26)
    vnr5.add_node(3, cpu_req=19)
    vnr5.add_node(4, cpu_req=23)
    vnr5.add_node(5, cpu_req=17)
    vnr5.add_edge(1, 2, bandwidth_req=7)
    vnr5.add_edge(2, 3, bandwidth_req=11)
    vnr5.add_edge(3, 4, bandwidth_req=9)
    vnr5.add_edge(4, 5, bandwidth_req=13)
    vnr_queue.append(vnr5)

    # VNR 6: 3-node path (high requirements)
    vnr6 = nx.Graph()
    vnr6.graph.update({'vnr_id': 'VNR_6', 'arrival_time': 30, 'lifetime': 15})
    vnr6.add_node(1, cpu_req=35)
    vnr6.add_node(2, cpu_req=40)
    vnr6.add_node(3, cpu_req=32)
    vnr6.add_edge(1, 2, bandwidth_req=25)
    vnr6.add_edge(2, 3, bandwidth_req=20)
    vnr_queue.append(vnr6)

    # VNR 7: 4-node cycle
    vnr7 = nx.Graph()
    vnr7.graph.update({'vnr_id': 'VNR_7', 'arrival_time': 35, 'lifetime': 28})
    vnr7.add_node(1, cpu_req=21)
    vnr7.add_node(2, cpu_req=17)
    vnr7.add_node(3, cpu_req=24)
    vnr7.add_node(4, cpu_req=19)
    vnr7.add_edge(1, 2, bandwidth_req=8)
    vnr7.add_edge(2, 3, bandwidth_req=12)
    vnr7.add_edge(3, 4, bandwidth_req=10)
    vnr7.add_edge(4, 1, bandwidth_req=15)
    vnr_queue.append(vnr7)

    # VNR 8: 5-node star
    vnr8 = nx.Graph()
    vnr8.graph.update({'vnr_id': 'VNR_8', 'arrival_time': 40, 'lifetime': 45})
    vnr8.add_node(1, cpu_req=35)  # Center
    vnr8.add_node(2, cpu_req=10)
    vnr8.add_node(3, cpu_req=12)
    vnr8.add_node(4, cpu_req=15)
    vnr8.add_node(5, cpu_req=11)
    vnr8.add_edge(1, 2, bandwidth_req=14)
    vnr8.add_edge(1, 3, bandwidth_req=9)
    vnr8.add_edge(1, 4, bandwidth_req=17)
    vnr8.add_edge(1, 5, bandwidth_req=12)
    vnr_queue.append(vnr8)

    # VNR 9: 3-node triangle (low requirements)
    vnr9 = nx.Graph()
    vnr9.graph.update({'vnr_id': 'VNR_9', 'arrival_time': 45, 'lifetime': 22})
    vnr9.add_node(1, cpu_req=8)
    vnr9.add_node(2, cpu_req=12)
    vnr9.add_node(3, cpu_req=10)
    vnr9.add_edge(1, 2, bandwidth_req=5)
    vnr9.add_edge(2, 3, bandwidth_req=6)
    vnr9.add_edge(1, 3, bandwidth_req=4)
    vnr_queue.append(vnr9)

    # VNR 10: 4-node partial mesh
    vnr10 = nx.Graph()
    vnr10.graph.update({'vnr_id': 'VNR_10', 'arrival_time': 50, 'lifetime': 33})
    vnr10.add_node(1, cpu_req=22)
    vnr10.add_node(2, cpu_req=18)
    vnr10.add_node(3, cpu_req=25)
    vnr10.add_node(4, cpu_req=20)
    vnr10.add_edge(1, 2, bandwidth_req=11)
    vnr10.add_edge(1, 3, bandwidth_req=14)
    vnr10.add_edge(2, 4, bandwidth_req=9)
    vnr10.add_edge(3, 4, bandwidth_req=16)
    vnr10.add_edge(1, 4, bandwidth_req=12)
    vnr_queue.append(vnr10)

    # VNR 11: 5-node cycle
    vnr11 = nx.Graph()
    vnr11.graph.update({'vnr_id': 'VNR_11', 'arrival_time': 55, 'lifetime': 38})
    vnr11.add_node(1, cpu_req=16)
    vnr11.add_node(2, cpu_req=21)
    vnr11.add_node(3, cpu_req=14)
    vnr11.add_node(4, cpu_req=19)
    vnr11.add_node(5, cpu_req=23)
    vnr11.add_edge(1, 2, bandwidth_req=7)
    vnr11.add_edge(2, 3, bandwidth_req=10)
    vnr11.add_edge(3, 4, bandwidth_req=8)
    vnr11.add_edge(4, 5, bandwidth_req=12)
    vnr11.add_edge(5, 1, bandwidth_req=9)
    vnr_queue.append(vnr11)

    # VNR 12: 3-node path
    vnr12 = nx.Graph()
    vnr12.graph.update({'vnr_id': 'VNR_12', 'arrival_time': 60, 'lifetime': 18})
    vnr12.add_node(1, cpu_req=13)
    vnr12.add_node(2, cpu_req=27)
    vnr12.add_node(3, cpu_req=15)
    vnr12.add_edge(1, 2, bandwidth_req=18)
    vnr12.add_edge(2, 3, bandwidth_req=11)
    vnr_queue.append(vnr12)

    # VNR 13: 4-node tree
    vnr13 = nx.Graph()
    vnr13.graph.update({'vnr_id': 'VNR_13', 'arrival_time': 65, 'lifetime': 42})
    vnr13.add_node(1, cpu_req=24)
    vnr13.add_node(2, cpu_req=16)
    vnr13.add_node(3, cpu_req=29)
    vnr13.add_node(4, cpu_req=12)
    vnr13.add_edge(1, 2, bandwidth_req=13)
    vnr13.add_edge(1, 3, bandwidth_req=15)
    vnr13.add_edge(2, 4, bandwidth_req=8)
    vnr_queue.append(vnr13)

    # VNR 14: 5-node partial mesh
    vnr14 = nx.Graph()
    vnr14.graph.update({'vnr_id': 'VNR_14', 'arrival_time': 70, 'lifetime': 50})
    vnr14.add_node(1, cpu_req=20)
    vnr14.add_node(2, cpu_req=15)
    vnr14.add_node(3, cpu_req=25)
    vnr14.add_node(4, cpu_req=18)
    vnr14.add_node(5, cpu_req=22)
    vnr14.add_edge(1, 2, bandwidth_req=10)
    vnr14.add_edge(1, 3, bandwidth_req=14)
    vnr14.add_edge(2, 4, bandwidth_req=7)
    vnr14.add_edge(3, 5, bandwidth_req=11)
    vnr14.add_edge(4, 5, bandwidth_req=13)
    vnr14.add_edge(1, 5, bandwidth_req=9)
    vnr_queue.append(vnr14)

    # VNR 15: 3-node triangle (medium requirements)
    vnr15 = nx.Graph()
    vnr15.graph.update({'vnr_id': 'VNR_15', 'arrival_time': 75, 'lifetime': 26})
    vnr15.add_node(1, cpu_req=18)
    vnr15.add_node(2, cpu_req=22)
    vnr15.add_node(3, cpu_req=16)
    vnr15.add_edge(1, 2, bandwidth_req=12)
    vnr15.add_edge(2, 3, bandwidth_req=14)
    vnr15.add_edge(1, 3, bandwidth_req=8)
    vnr_queue.append(vnr15)

    # VNR 16: 4-node path (high bandwidth)
    vnr16 = nx.Graph()
    vnr16.graph.update({'vnr_id': 'VNR_16', 'arrival_time': 80, 'lifetime': 35})
    vnr16.add_node(1, cpu_req=17)
    vnr16.add_node(2, cpu_req=21)
    vnr16.add_node(3, cpu_req=14)
    vnr16.add_node(4, cpu_req=26)
    vnr16.add_edge(1, 2, bandwidth_req=22)
    vnr16.add_edge(2, 3, bandwidth_req=18)
    vnr16.add_edge(3, 4, bandwidth_req=25)
    vnr_queue.append(vnr16)

    # VNR 17: 5-node tree
    vnr17 = nx.Graph()
    vnr17.graph.update({'vnr_id': 'VNR_17', 'arrival_time': 85, 'lifetime': 44})
    vnr17.add_node(1, cpu_req=28)  # Root
    vnr17.add_node(2, cpu_req=13)
    vnr17.add_node(3, cpu_req=19)
    vnr17.add_node(4, cpu_req=15)
    vnr17.add_node(5, cpu_req=11)
    vnr17.add_edge(1, 2, bandwidth_req=16)
    vnr17.add_edge(1, 3, bandwidth_req=12)
    vnr17.add_edge(2, 4, bandwidth_req=9)
    vnr17.add_edge(2, 5, bandwidth_req=7)
    vnr_queue.append(vnr17)

    # VNR 18: 3-node path (short lifetime)
    vnr18 = nx.Graph()
    vnr18.graph.update({'vnr_id': 'VNR_18', 'arrival_time': 90, 'lifetime': 12})
    vnr18.add_node(1, cpu_req=31)
    vnr18.add_node(2, cpu_req=19)
    vnr18.add_node(3, cpu_req=24)
    vnr18.add_edge(1, 2, bandwidth_req=17)
    vnr18.add_edge(2, 3, bandwidth_req=21)
    vnr_queue.append(vnr18)

    # VNR 19: 4-node diamond
    vnr19 = nx.Graph()
    vnr19.graph.update({'vnr_id': 'VNR_19', 'arrival_time': 95, 'lifetime': 37})
    vnr19.add_node(1, cpu_req=20)
    vnr19.add_node(2, cpu_req=14)
    vnr19.add_node(3, cpu_req=18)
    vnr19.add_node(4, cpu_req=25)
    vnr19.add_edge(1, 2, bandwidth_req=10)
    vnr19.add_edge(1, 3, bandwidth_req=12)
    vnr19.add_edge(2, 4, bandwidth_req=14)
    vnr19.add_edge(3, 4, bandwidth_req=11)
    vnr_queue.append(vnr19)

    # VNR 20: 4-node line with branch
    vnr20 = nx.Graph()
    vnr20.graph.update({'vnr_id': 'VNR_20', 'arrival_time': 100, 'lifetime': 48})
    vnr20.add_node(1, cpu_req=16)
    vnr20.add_node(2, cpu_req=23)
    vnr20.add_node(3, cpu_req=20)
    vnr20.add_node(4, cpu_req=17)
    vnr20.add_node(5, cpu_req=21)
    vnr20.add_edge(1, 2, bandwidth_req=8)
    vnr20.add_edge(2, 3, bandwidth_req=13)
    vnr20.add_edge(3, 4, bandwidth_req=15)
    vnr20.add_edge(3, 5, bandwidth_req=10)
    vnr_queue.append(vnr20)
    
    return vnr_queue


def print_vnr_summary(vnr_queue):
    """
    Print summary statistics of VNR queue
    
    Args:
        vnr_queue: List of VNR graphs
    """
    print(f"✓ Created {len(vnr_queue)} VNRs")

    # Summary statistics
    sizes = [len(vnr.nodes()) for vnr in vnr_queue]
    arrival_times = [vnr.graph['arrival_time'] for vnr in vnr_queue]
    lifetimes = [vnr.graph['lifetime'] for vnr in vnr_queue]

    print(f"Node sizes: {min(sizes)}-{max(sizes)} nodes")
    print(f"Arrival times: {min(arrival_times)}-{max(arrival_times)}")
    print(f"Lifetimes: {min(lifetimes)}-{max(lifetimes)}")

    print("\nVNR Queue Summary:")
    print("-" * 80)
    for vnr in vnr_queue:
        total_cpu = sum(vnr.nodes[n]['cpu_req'] for n in vnr.nodes())
        total_bw = sum(vnr.edges[e]['bandwidth_req'] for e in vnr.edges())

        # Simple topology detection
        nodes = len(vnr.nodes())
        edges = len(vnr.edges())

        print(f"{vnr.graph['vnr_id']:>6}: {nodes} nodes, {edges} edges, "
              f"CPU={total_cpu:>3}, BW={total_bw:>3}, "
              f"Arrives={vnr.graph['arrival_time']:>3}, Life={vnr.graph['lifetime']:>2} ")
              