import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from shapely import wkt
from geopy.distance import geodesic
from matplotlib.widgets import Button

# === Load and preprocess data ===
df = pd.read_csv("../data/final_data/preprocessed_Map.csv")
df['geometry'] = df['geometry'].apply(wkt.loads)

def round_coords(geom, decimals=5):
    return [(round(x, decimals), round(y, decimals)) for x, y in geom.coords]

# === Build the graph ===
G = nx.DiGraph()

for _, row in df.iterrows():
    coords = round_coords(row['geometry'])
    for i in range(len(coords) - 1):
        start = coords[i]
        end = coords[i + 1]
        if start == end:
            continue
        if not G.has_edge(start, end):
            distance = geodesic((start[1], start[0]), (end[1], end[0])).meters
            G.add_edge(start, end, weight=distance)

# === Remove isolated nodes and save clean node list ===
isolated = list(nx.isolates(G))
G.remove_nodes_from(isolated)
cleaned_nodes = list(G.nodes())
pd.DataFrame(cleaned_nodes, columns=["lon", "lat"]).to_csv("cleaned_nodes.csv", index=False)

print(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# === Define the fixed end node ===
end_node = (round(121.1114449, 5), round(14.7017247, 5))  # Make sure this matches rounding
show_nodes = False  # toggle flag

# === Plotting function ===
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

    ax.set_title("Click a point to find path to end node")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend()
    ax.grid(True)
    fig.canvas.draw()

# === Button to toggle nodes ===
ax_button = plt.axes([0.8, 0.01, 0.15, 0.05])
toggle_button = Button(ax_button, 'Toggle Nodes')

def toggle_nodes(event):
    global show_nodes
    show_nodes = not show_nodes
    plot_graph()

toggle_button.on_clicked(toggle_nodes)

# === Click event to find path ===
def on_click(event):
    if event.inaxes != ax:
        return
    clicked = (round(event.xdata, 5), round(event.ydata, 5))
    print(f"Clicked: {clicked}")

    # Find closest node
    closest = None
    min_dist = float('inf')
    for node in G.nodes():
        dist = ((node[0] - clicked[0])**2 + (node[1] - clicked[1])**2) ** 0.5
        if dist < min_dist:
            min_dist = dist
            closest = node

    if min_dist > 0.0005:  # ~50m tolerance
        print("Too far from road network.")
        return

    if end_node not in G:
        print("End node not in graph.")
        return

    try:
        path = nx.dijkstra_path(G, source=closest, target=end_node, weight='weight')
        print(f"Path found: {path}")
        plot_graph(path=path)
    except nx.NetworkXNoPath:
        print("No path found.")
    except nx.NodeNotFound:
        print("Node not in graph.")

# === Initialize ===
fig.canvas.mpl_connect('button_press_event', on_click)
plot_graph()
plt.show()
