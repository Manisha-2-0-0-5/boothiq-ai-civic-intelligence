# backend/knowledge_graph.py
import networkx as nx

def build_graph(voters):
    G = nx.Graph()

    for v in voters:
        voter_node = f"{v['voter_id']} - {v['name']}"
        booth_node = f"Booth {v['booth_id']}"

        G.add_node(voter_node, type="voter")
        G.add_node(booth_node, type="booth")

        G.add_edge(voter_node, booth_node, relation="lives_in")

        for scheme in v.get("schemes_enrolled", []):
            G.add_node(scheme, type="scheme")
            G.add_edge(voter_node, scheme, relation="enrolled_in")

    return G