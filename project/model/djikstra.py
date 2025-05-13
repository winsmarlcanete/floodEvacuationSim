import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from shapely import wkt
from matplotlib.widgets import Button
import numpy as np
import geopandas as gpd
# === Load your dataset ===
df = pd.read_csv("../data/final_data/preprocessed_Map.csv")
df['geometry'] = df['geometry'].apply(wkt.loads)
# Round the coordinates to 5 decimal places to avoid precision errors
df['geometry'] = df['geometry'].apply(lambda x: wkt.loads(f"LINESTRING({', '.join([f'{round(coord[0], 5)} {round(coord[1], 5)}' for coord in x.coords])})"))

# Convert the DataFrame to a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry')

# Create a spatial index
spatial_index = gdf.sindex

# Use the spatial index to find nearby nodes
for i, row in df.iterrows():
    point = row['geometry']
    possible_matches_index = list(spatial_index.nearest(point, num_results=2))
    # Use this to avoid redundant distance checks

# === Build the graph ===
G = nx.DiGraph()
positions = set()

for _, row in df.iterrows():
    coords = list(row['geometry'].coords)
    length = row['length']
    for i in range(len(coords) - 1):
        start = tuple(coords[i])
        end = tuple(coords[i + 1])
        positions.add(start)
        positions.add(end)
        segment_length = length / (len(coords) - 1)
        if not G.has_edge(start, end):  # Avoid duplicate edges
            G.add_edge(start, end, weight=segment_length)

# === Define the fixed end node ===
end_node = (121.1114449, 14.7017247)
show_nodes = False  # default state: don't show nodes

# === Function to find closest node in graph ===
def find_closest_node(coords, graph):
    min_dist = float('inf')
    closest_node = None
    for node in graph.nodes():
        dist = np.linalg.norm(np.array(node) - np.array(coords))
        if dist < min_dist:
            min_dist = dist
            closest_node = node
    return closest_node

# === Plotting Function ===
def plot_graph(path=None):
    ax.clear()  # Clears the axes to avoid overlapping figures

    for u, v in G.edges():
        x = [u[0], v[0]]
        y = [u[1], v[1]]
        ax.plot(x, y, color='lightgray', zorder=1)

    if show_nodes:
        for node in G.nodes():
            ax.scatter(*node, color='red', s=10, zorder=2)

    if path:
        px = [p[0] for p in path]
        py = [p[1] for p in path]
        ax.plot(px, py, color='blue', linewidth=3, label='Path', zorder=3)
        ax.scatter(px[0], py[0], color='green', s=50, label='Start Node', zorder=4)  # Start
        ax.scatter(px[-1], py[-1], color='black', s=60, label='End Node', zorder=5)  # End
    else:
        ax.scatter(*end_node, color='black', s=60, label='End Node', zorder=5)

    ax.set_title("Click on a point to find path to end node")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend()
    ax.grid(True)
    fig.canvas.draw()  # Make sure to use this instead of plt.draw()

# === Button for toggling node visibility ===
ax_button = plt.axes([0.8, 0.01, 0.15, 0.05])  # Button axes within the same figure
toggle_button = Button(ax_button, 'Toggle Nodes')

def toggle_nodes(event):
    global show_nodes
    show_nodes = not show_nodes
    plot_graph()

toggle_button.on_clicked(toggle_nodes)

# === Click Event Handler ===
def on_click(event):
    if event.inaxes:
        clicked_point = (event.xdata, event.ydata)
        print(f"Clicked: {clicked_point}")

        # Find closest node to clicked point
        min_dist = float('inf')
        closest = None
        for node in G.nodes():
            dist = ((node[0] - clicked_point[0]) ** 2 + (node[1] - clicked_point[1]) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest = node

        if min_dist > 0.0005:  # 50 meters approx
            print("Too far from road network.")
            return

        # Find closest node to the end_node
        closest_end_node = find_closest_node(end_node, G)
        if not closest_end_node:
            print("End node not found in the graph.")
            return

        try:
            path = nx.dijkstra_path(G, source=closest, target=closest_end_node, weight='weight')
            print(f"Path: {path}")
            plot_graph(path=path)
        except nx.NetworkXNoPath:
            print("No path found.")
        except nx.NodeNotFound:
            print("Node not found in graph.")

# === Start interactive plot ===
fig, ax = plt.subplots(figsize=(10, 8))  # Ensure only one figure and axes is created
fig.canvas.mpl_connect('button_press_event', on_click)

plot_graph()  # Initial plot

# Only one show command for the figure
plt.show()  # Keep this at the end, which ensures only one figure window appears
