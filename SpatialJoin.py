import pandas as pd
from shapely.geometry import Point
from geopy.distance import geodesic

# Load both CSVs
roads_df = pd.read_csv("project/data/flood_roads_with_coords.csv")  # Has longitude, latitude columns
points_df = pd.read_csv("project/data/AEGISDataset.csv")  # Has latitude, longitude, flood_height, elevation, precipitation


# Create a function to find the nearest point (within max_distance in meters)
def find_nearest_flood_data(road_lat, road_lon, flood_points, max_distance=200):
    road_point = (road_lat, road_lon)
    nearest = None
    min_dist = float('inf')

    print(f"Road: ({road_lat}, {road_lon})")

    for _, row in flood_points.iterrows():
        flood_point = (row['latitude'], row['longitude'])
        dist = geodesic(road_point, flood_point).meters

        print(f"  Flood: ({flood_point[0]}, {flood_point[1]}) => Distance: {dist:.2f}m")

        if dist < min_dist and dist <= max_distance:
            min_dist = dist
            nearest = row

    return nearest if nearest is not None else pd.Series([None, None, None],
                                                         index=['flood_height', 'elevation', 'precipitation'])


# Apply nearest matching
merged_data = roads_df.copy()
merged_data[['flood_height', 'elevation', 'precipitation']] = roads_df.apply(
    lambda row: find_nearest_flood_data(row['latitude'], row['longitude'], points_df), axis=1
)

# Save the result
merged_data.to_csv("project/data/flood_roads_enriched.csv", index=False)
print("Merged dataset saved to 'flood_roads_enriched.csv'")
