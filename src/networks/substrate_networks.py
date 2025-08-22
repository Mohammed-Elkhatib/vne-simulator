import networkx as nx


def create_german_network():
    # Create German substrate network based on Figure 4.6
    G = nx.Graph()

    # Add nodes with CPU capacity only
    G.add_node(1, cpu=100)
    G.add_node(2, cpu=150)
    G.add_node(3, cpu=80)
    G.add_node(4, cpu=120)
    G.add_node(5, cpu=90)
    G.add_node(6, cpu=110)
    G.add_node(7, cpu=140)

    # Add edges with bandwidth capacity and costs
    G.add_edge(1, 2, bandwidth=100, cost=2)
    G.add_edge(1, 3, bandwidth=80, cost=3)
    G.add_edge(2, 4, bandwidth=120, cost=1)
    G.add_edge(2, 5, bandwidth=90, cost=4)
    G.add_edge(2, 6, bandwidth=135, cost=1)
    G.add_edge(3, 4, bandwidth=100, cost=2)
    G.add_edge(4, 5, bandwidth=110, cost=1)
    G.add_edge(6, 1, bandwidth=95, cost=3)
    G.add_edge(7, 5, bandwidth=105, cost=1)
    G.add_edge(7, 4, bandwidth=125, cost=2)
    G.add_edge(2, 3, bandwidth=85, cost=3)
    
    return G


def create_italian_network():
    # Create Italian substrate network based on Figure 4.7
    I = nx.Graph()

    # Add nodes with CPU capacity only
    I.add_node(1, cpu=100)
    I.add_node(2, cpu=150)
    I.add_node(3, cpu=80)
    I.add_node(4, cpu=120)
    I.add_node(5, cpu=90)
    I.add_node(6, cpu=110)
    I.add_node(7, cpu=140)
    I.add_node(8, cpu=200)
    I.add_node(9, cpu=170)
    I.add_node(10, cpu=130)

    # Add edges with bandwidth capacity and costs
    I.add_edge(1, 2, bandwidth=100, cost=2)
    I.add_edge(1, 3, bandwidth=80, cost=3)
    I.add_edge(1, 7, bandwidth=120, cost=1)
    I.add_edge(2, 4, bandwidth=90, cost=4)
    I.add_edge(2, 7, bandwidth=135, cost=1)
    I.add_edge(3, 5, bandwidth=100, cost=2)
    I.add_edge(4, 8, bandwidth=110, cost=1)
    I.add_edge(5, 6, bandwidth=95, cost=3)
    I.add_edge(5, 7, bandwidth=105, cost=1)
    I.add_edge(6, 7, bandwidth=125, cost=2)
    I.add_edge(6, 9, bandwidth=85, cost=3)
    I.add_edge(7, 8, bandwidth=145, cost=5)
    I.add_edge(7, 9, bandwidth=185, cost=3)
    I.add_edge(8, 10, bandwidth=70, cost=1)
    I.add_edge(9, 10, bandwidth=200, cost=4)
    
    return I
    