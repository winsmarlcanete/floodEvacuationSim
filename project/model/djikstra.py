import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from shapely import wkt

# === Load and parse dataset ===
df = pd.read_csv("../data/final_data/preprocessed_Map.csv")
df['geometry'] = df['geometry'].apply(wkt.loads)

G = nx.DiGraph()

for _, row in df.iterrows():
    coords = list(row['geometry'].coords)
    length = row['length']
    for i in range(len(coords) - 1):
        start = coords[i]
        end = coords[i + 1]
        G.add_edge(start, end, weight=length / (len(coords) - 1))

# === Define flooded edges ===
flooded_edges = [
    ((121.1117803, 14.7018384), (121.1115968, 14.7017829)),
]
for u, v in flooded_edges:
    if G.has_edge(u, v):
        G[u][v]['weight'] *= 100

# === Dijkstra's Algorithm ===
start_node = (121.112025, 14.7019027)
end_node = (121.1114449, 14.7017247)

# Check if there's a valid path
if nx.has_path(G, start_node, end_node):
    # Get shortest path using Dijkstra
    shortest_path = nx.dijkstra_path(G, source=start_node, target=end_node, weight='weight')
    print("Dijkstra's Shortest Path:", shortest_path)

    # === Visualization ===
    for u, v in G.edges():
        x = [u[0], v[0]]
        y = [u[1], v[1]]
        plt.plot(x, y, color='lightgray')

    for u, v in flooded_edges:
        x = [u[0], v[0]]
        y = [u[1], v[1]]
        plt.plot(x, y, color='red', linewidth=2)

    px = [p[0] for p in shortest_path]
    py = [p[1] for p in shortest_path]
    plt.plot(px, py, color='blue', linewidth=3, label="Dijkstra's Path")

    plt.scatter(*start_node, color='green', s=60, label='Start')
    plt.scatter(*end_node, color='black', s=60, label='End')

    plt.title("Flood Evacuation Dijkstra Simulation")
    plt.legend()
    plt.grid(True)
    plt.show()
else:
    print("No path exists between start and end nodes.")
