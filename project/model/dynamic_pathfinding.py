import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from shapely import wkt
from matplotlib.widgets import Button

# === Load your dataset ===
df = pd.read_csv("../data/final_data/preprocessed_Map.csv")
df['geometry'] = df['geometry'].apply(wkt.loads)

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
        G.add_edge(start, end, weight=segment_length)

# === Fixed end node ===
end_node = (121.109950, 14.697330)
show_nodes = False  # default state

# === Create figure and axis once ===
fig, ax = plt.subplots(figsize=(10, 8))
plt.subplots_adjust(bottom=0.15)  # make room for button

# === Plotting Function ===
def plot_graph(path=None):
    ax.clear()

    for u, v in G.edges():
        x = [u[0], v[0]]
        y = [u[1], v[1]]
        ax.plot(x, y, color='lightgray', zorder=1)

    # Toggle nodes
    if show_nodes:
        for node in G.nodes():
            ax.scatter(*node, color='red', s=10, zorder=3)

    if path:
        px = [p[0] for p in path]
        py = [p[1] for p in path]
        ax.plot(px, py, color='blue', linewidth=3, label='Path', zorder=4)

    ax.scatter(*end_node, color='black', s=60, label='End Node', zorder=5)

    ax.set_title("Click on a point to find path to end node")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend()
    ax.grid(True)
    fig.canvas.draw()

# === Button for toggling node display ===
ax_button = plt.axes([0.8, 0.02, 0.15, 0.05])  # (x-pos, y-pos, width, height)
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

    # Find closest node within threshold
    min_dist = float('inf')
    closest = None
    for node in G.nodes():
        dist = ((node[0] - clicked_point[0]) ** 2 + (node[1] - clicked_point[1]) ** 2) ** 0.5
        if dist < min_dist:
            min_dist = dist
            closest = node

    if min_dist > 0.0005:  # ~50 meters
        print("Too far from road network.")
        return

    if closest not in G or end_node not in G:
        print("Clicked node or end node is not in the graph.")
        return

    try:
        if nx.has_path(G, closest, end_node):
            path = nx.dijkstra_path(G, source=closest, target=end_node, weight='weight')
            print(f"Path: {path}")
            plot_graph(path=path)
        else:
            print("No path found.")
    except nx.NetworkXNoPath:
        print("No path exists between the nodes.")
    except nx.NodeNotFound as e:
        print(f"Node error: {e}")


# === Hook up click ===
fig.canvas.mpl_connect('button_press_event', on_click)

# === Initial plot ===
plot_graph()
plt.show()
