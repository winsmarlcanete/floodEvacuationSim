import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from shapely import wkt
from geopy.distance import geodesic

# === Load dataset ===
df = pd.read_csv("../data/final_data/preprocessed_Map.csv")
df['geometry'] = df['geometry'].apply(wkt.loads)

# === Helper function: Round coordinates ===
def round_coords(geom, decimals=5):
    return [(round(x, decimals), round(y, decimals)) for x, y in geom.coords]

# === Initialize graph ===
G = nx.DiGraph()

# === Build the graph with real geodesic distances and cleaned nodes ===
for _, row in df.iterrows():
    coords = round_coords(row['geometry'])  # rounding to reduce floating point noise
    for i in range(len(coords) - 1):
        start = coords[i]
        end = coords[i + 1]

        if start == end:
            continue  # skip self-loops

        if not G.has_edge(start, end):
            distance = geodesic((start[1], start[0]), (end[1], end[0])).meters
            G.add_edge(start, end, weight=distance)

# === Clean up: remove any isolated nodes ===
isolated_nodes = list(nx.isolates(G))
G.remove_nodes_from(isolated_nodes)

# === Debugging: Print some graph info ===
print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
print(f"Removed {len(isolated_nodes)} isolated nodes.")

# === Optional: Save node list for inspection ===
pd.DataFrame(G.nodes()).to_csv("../data/final_data/cleaned_nodes.csv", index=False)

# === Plot the graph ===
pos = {node: (node[0], node[1]) for node in G.nodes()}
plt.figure(figsize=(10, 8))
nx.draw(G, pos, node_size=5, edge_color='gray', with_labels=False)
plt.title("Cleaned Road Network")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)
plt.show()
