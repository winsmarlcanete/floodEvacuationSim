import networkx as nx
from shapely.geometry import LineString

# Create an empty graph
G = nx.Graph()

# Loop through each road segment
for idx, row in road_map.iterrows():
    geom = row['geometry']

    # If the geometry is a LineString, process it
    if isinstance(geom, LineString):
        coords = list(geom.coords)
        for i in range(len(coords) - 1):
            start = coords[i]
            end = coords[i + 1]
            distance = LineString([start, end]).length
            G.add_edge(start, end, weight=distance)

print(f"Graph created with {len(G.nodes)} nodes and {len(G.edges)} edges.")