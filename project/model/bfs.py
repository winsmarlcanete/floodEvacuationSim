import pandas as pd

# === Load the cleaned nodes CSV ===
nodes_df = pd.read_csv("../data/final_data/cleaned_nodes.csv")  # Adjust the file path if needed

# Print the first few rows to inspect the contents
print("Cleaned Nodes Data:")
print(nodes_df.head())

# === Convert the DataFrame rows to node tuples ===
# Assuming the CSV columns are the node coordinates (e.g., longitude and latitude).
# If the CSV has column names like 'lon' and 'lat', you can use:
# nodes_list = list(zip(nodes_df['lon'], nodes_df['lat']))

# For a CSV with no headers or default numeric column names:
nodes_list = [tuple(row) for row in nodes_df.values]

print("\nNode List:")
print(nodes_list)

# === Example: Using the nodes list to highlight these nodes in an existing graph ===
# If you already have a graph 'G', you can check if these nodes exist in it.
import networkx as nx
import matplotlib.pyplot as plt

# For demonstration, assume you have a graph G built previously:
G = nx.DiGraph()
# (This snippet assumes that you have constructed G already with your full data)

# Let's say you want to mark the clean nodes in your existing plot:
node_positions = {node: node for node in G.nodes()}  # In this example, node is a tuple

plt.figure(figsize=(10, 8))
# Draw all edges in light gray
nx.draw_networkx_edges(G, pos=node_positions, edge_color='lightgray', alpha=0.5)
# Draw all nodes in red
nx.draw_networkx_nodes(G, pos=node_positions, node_color='red', node_size=5)

# Draw the nodes from the cleaned CSV with a different color and larger size for highlighting
clean_positions = {node: node for node in nodes_list if node in G.nodes()}
nx.draw_networkx_nodes(G, pos=clean_positions, node_color='blue', node_size=50)

plt.title("Graph with Cleaned Nodes Highlighted")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)
plt.show()
