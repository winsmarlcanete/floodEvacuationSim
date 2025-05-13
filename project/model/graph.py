import pandas as pd
from shapely import wkt
import networkx as nx

# Load dataset
df = pd.read_csv("../data/final_data/preprocessed_Map.csv")

# Initialize graph
G = nx.DiGraph()

# Helper to round coordinates
def round_coord(coord):
    return (round(coord[0], 6), round(coord[1], 6))  # 6 decimal places = ~10cm precision

# Build graph from LINESTRING geometries
for i, row in df.iterrows():
    flood_risk = row['Var_mean']
    length = row['length']
    geometry = wkt.loads(row['geometry'])

    coords = list(geometry.coords)
    for a, b in zip(coords[:-1], coords[1:]):
        a_r = round_coord(a)
        b_r = round_coord(b)

        G.add_node(a_r)
        G.add_node(b_r)

        # Add forward and reverse links (optional)
        G.add_edge(a_r, b_r, flood_risk=flood_risk, length=length)
        G.add_edge(b_r, a_r, flood_risk=flood_risk, length=length)

print(f"Graph has {len(G.nodes)} nodes and {len(G.edges)} edges.")
