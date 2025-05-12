import pandas as pd
from shapely.wkt import loads

# Load your CSV file (change the filename as needed)
df = pd.read_csv("data/roadMapWithHarzard.csv")

# Define empty lists to store coordinates
longitudes = []
latitudes = []

# Loop through each row and extract the first coordinate from the LINESTRING
for geom in df['WKT']:  # Assumes 'geometry' column holds the LINESTRING
    try:
        line = loads(geom)  # Parse WKT
        first_point = line.coords[0]  # Get first (lon, lat)
        longitudes.append(first_point[0])
        latitudes.append(first_point[1])
    except Exception as e:
        print("Error parsing geometry:", geom)
        longitudes.append(None)
        latitudes.append(None)

# Add new columns to the DataFrame
df['longitude'] = longitudes
df['latitude'] = latitudes

# Save to new CSV
df.to_csv("data/flood_roads_with_coords.csv", index=False)

print("Coordinates extracted and saved to 'flood_roads_with_coords.csv'")