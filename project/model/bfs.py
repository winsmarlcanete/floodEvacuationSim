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

start_node = None
end_nodes = []
max_ends = 3
colors = ['blue', 'orange', 'purple']

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

# Add missing connections using KDTree
coords_list = list(positions)
tree = KDTree(coords_list)
for i, point in enumerate(coords_list):
    distances, indices = tree.query([point], k=4)
    for j in indices[0][1:]:
        neighbor = coords_list[int(j)]
        if not G.has_edge(point, neighbor):
            dist = geodesic((point[1], point[0]), (neighbor[1], neighbor[0])).meters
            G.add_edge(point, neighbor, weight=dist)
            G.add_edge(neighbor, point, weight=dist)

# === Snap End Node to Graph (for reference/debugging) ===
coords_list = list(G.nodes)
tree = KDTree(coords_list)
target = (121.1114449, 14.7017247)
_, index = tree.query([target], k=1)
end_node = coords_list[int(index[0][0])]
print(f"Snapped end_node: {end_node}")

# === Plotting ===
fig, ax = plt.subplots(figsize=(10, 8))

def plot_graph():
    ax.clear()
    for u, v in G.edges:
        x = [u[0], v[0]]
        y = [u[1], v[1]]
        ax.plot(x, y, color='lightgray', zorder=1)
    ax.set_title("Click: 1 Start + up to 3 End Nodes")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend()
    ax.grid(True)
    fig.canvas.draw()

# === Click Handler ===
def on_click(event):
    global start_node, end_nodes

    if event.inaxes != ax:
        return

    clicked_point = (event.xdata, event.ydata)
    print(f"Clicked: {clicked_point}")

    # Find closest node
    min_dist = float('inf')
    closest = None
    for node in G.nodes:
        dist = ((node[0] - clicked_point[0])**2 + (node[1] - clicked_point[1])**2)**0.5
        if dist < min_dist:
            min_dist = dist
            closest = node

    if min_dist > 0.0005:
        print("Too far from network.")
        return

    if start_node is None:
        start_node = closest
        print(f"Start node set to: {start_node}")
        plot_graph()
        ax.scatter(*start_node, color='green', s=50, label='Start Node', zorder=4)
        fig.canvas.draw()
    elif len(end_nodes) < max_ends:
        if closest in end_nodes:
            print("Already selected as an end node.")
            return
        end_nodes.append(closest)
        print(f"End node {len(end_nodes)} set to: {closest}")

        try:
            path = nx.dijkstra_path(G, source=start_node, target=closest, weight='weight')
            color = colors[len(end_nodes) - 1]
            px = [p[0] for p in path]
            py = [p[1] for p in path]
            ax.plot(px, py, color=color, linewidth=3, label=f'Path {len(end_nodes)}', zorder=3)
            ax.scatter(px[-1], py[-1], color=color, s=60, label=f'End Node {len(end_nodes)}', zorder=5)
            fig.canvas.draw()
        except nx.NetworkXNoPath:
            print("No path found.")
        except nx.NodeNotFound:
            print("Node not in graph.")
    else:
        print("Maximum of 3 end nodes reached.")

# === Reset Button ===
ax_reset = plt.axes([0.8, 0.01, 0.15, 0.05])
reset_button = Button(ax_reset, 'Reset')

def reset_nodes(event):
    global start_node, end_nodes
    start_node = None
    end_nodes = []
    plot_graph()

reset_button.on_clicked(reset_nodes)
fig.canvas.mpl_connect('button_press_event', on_click)

# === Initial Plot ===
plot_graph()
plt.show()
