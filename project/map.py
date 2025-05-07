import geopandas as gpd
import matplotlib.pyplot as plt

# Load the GeoJSON file
road_map = gpd.read_file("/mnt/data/RoadMap.geojson")

# Plot to confirm it looks right
road_map.plot(figsize=(10, 10), color='gray')
plt.title("Road Network - Barangay Bagong Silangan")
plt.show()