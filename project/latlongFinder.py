import pandas as pd
import requests
import time
from tqdm import tqdm  # For progress bars (install with: pip install tqdm)

# Load the CSV
df = pd.read_csv('data/Bagong Silangan Road Map - FixedRoadMap.csv')


def get_way_coordinates(osm_id):
    try:
        # Extract the numeric ID (e.g., "way/24158513" → 24158513)
        way_id = osm_id.split('/')[-1]

        # Overpass API query to fetch the way's nodes (coordinates)
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        way({way_id});
        out geom;
        """

        response = requests.get(overpass_url, params={'data': query})
        data = response.json()

        if not data['elements']:
            print(f"No data for {osm_id}")
            return None, None

        # Extract all nodes (coordinates) of the way
        geometry = data['elements'][0].get('geometry', [])
        if not geometry:
            print(f"No geometry for {osm_id}")
            return None, None

        # Calculate centroid (average of all coordinates)
        lats = [point['lat'] for point in geometry]
        lons = [point['lon'] for point in geometry]
        avg_lat = sum(lats) / len(lats)
        avg_lon = sum(lons) / len(lons)

        return avg_lat, avg_lon

    except Exception as e:
        print(f"Error for {osm_id}: {str(e)}")
        return None, None


# Apply the function with a progress bar
tqdm.pandas()  # Enable progress_apply
df['latitude'], df['longitude'] = zip(*df['id'].progress_apply(get_way_coordinates))

# Save to CSV
df.to_csv('data/Bagong_Silangan_Road_Map_with_coordinates.csv', index=False)
print("Done! Coordinates saved.")