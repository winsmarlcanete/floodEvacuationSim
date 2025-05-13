import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from shapely import wkt
from matplotlib.widgets import Button
from sklearn.neighbors import KDTree
from geopy.distance import geodesic

# === Load Dataset ===
df = pd.read_csv("../data/final_data/preprocessed_Map.csv")
df['geometry'] = df['geometry'].apply(wkt.loads)

# === Build Graph ===
G = nx.DiGraph()
positions = set()

def round_coords(geom, decimals=5):
    return [(round(x, decimals), round(y, decimals)) for x, y in geom.coords]

# Add edges from geometries
for _, row in df.iterrows():
    coords = round_coords(row['geometry'])
    length = row['length']
    for i in range(len(coords) - 1):
        start = coords[i]
        end = coords[i + 1]
        positions.add(start)
        positions.add(end)
        segment_length = length / (len(coords) - 1)
        G.add_edge(start, end, weight=segment_length)
        G.add_edge(end, start, weight=segment_length)  # Bidirectional

# Add missing node connections using KDTree (nearest neighbors)
coords_list = list(positions)
tree = KDTree(coords_list)

for i, point in enumerate(coords_list):
    distances, indices = tree.query([point], k=4)  # 3 nearest neighbors + self
    for j in indices[0][1:]:
        neighbor = coords_list[int(j)]
        if not G.has_edge(point, neighbor):
            dist = geodesic((point[1], point[0]), (neighbor[1], neighbor[0])).meters
            G.add_edge(point, neighbor, weight=dist)
            G.add_edge(neighbor, point, weight=dist)  # Bidirectional

# === End Node ===
# Build KDTree for all node positions
coords_list = list(G.nodes)
tree = KDTree(coords_list)

# Snap to nearest actual graph node
target = (121.1114449, 14.7017247)
_, index = tree.query([target], k=1)
end_node = coords_list[int(index[0][0])]

print(f"Snapped end_node: {end_node}")
show_nodes = False

# === Plotting Function ===
fig, ax = plt.subplots(figsize=(10, 8))

def plot_graph(path=None):
    ax.clear()
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
        ax.scatter(px[0], py[0], color='green', s=50, label='Start Node', zorder=4)
        ax.scatter(px[-1], py[-1], color='black', s=60, label='End Node', zorder=5)
    else:
        ax.scatter(*end_node, color='black', s=60, label='End Node', zorder=5)

    ax.set_title("Click on a point to find path to end node")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend()
    ax.grid(True)
    fig.canvas.draw()

# === Button for Node Toggle ===
ax_button = plt.axes([0.8, 0.01, 0.15, 0.05])
toggle_button = Button(ax_button, 'Toggle Nodes')

def toggle_nodes(event):
    global show_nodes
    show_nodes = not show_nodes
    plot_graph()

toggle_button.on_clicked(toggle_nodes)

# === Click Event Handler ===
def on_click(event):
    if event.inaxes != ax:
        return

    clicked_point = (event.xdata, event.ydata)
    print(f"Clicked: {clicked_point}")

    # Find closest node
    min_dist = float('inf')
    closest = None
    for node in G.nodes():
        dist = ((node[0] - clicked_point[0]) ** 2 + (node[1] - clicked_point[1]) ** 2) ** 0.5
        if dist < min_dist:
            min_dist = dist
            closest = node

    if min_dist > 0.0005:  # approx 50m
        print("Too far from road network.")
        return

    if end_node not in G:
        print("End node not in graph.")
        return

    try:
        path = nx.dijkstra_path(G, source=closest, target=end_node, weight='weight')
        print(f"Path: {path}")
        plot_graph(path=path)
    except nx.NetworkXNoPath:
        print("No path found.")
    except nx.NodeNotFound:
        print("Node not found in graph.")

fig.canvas.mpl_connect('button_press_event', on_click)

# === Initial Plot ===
plot_graph()
plt.show()
