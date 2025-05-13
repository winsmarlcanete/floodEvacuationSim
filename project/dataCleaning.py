import pandas as pd
from shapely import wkt
import networkx as nx
import pickle

df = pd.read_csv("data/final_data/RoadMapWithHazard.csv")

# === Step 2: Parse Geometry ===
df['geometry'] = df['WKT'].apply(wkt.loads)
df['start'] = df['geometry'].apply(lambda line: line.coords[0])
df['end'] = df['geometry'].apply(lambda line: line.coords[-1])

# === Step 3: Clean & Feature Engineer ===
# Fill missing lane info with 1 (default)
df['lanes'] = pd.to_numeric(df['lanes'], errors='coerce').fillna(1)

# Fill smoothness
df['smoothness'] = df['smoothness'].fillna('intermediate')

# Encode surface as category code (if surface exists)
df['surface'] = df['surface'].fillna('unknown')
df['surface_encoded'] = df['surface'].astype('category').cat.codes

# Fill Var_mean with fallback (default weight = 1)
df['Var_mean'] = pd.to_numeric(df['Var_mean'], errors='coerce').fillna(1.0)

# Optional: compute length
df['length'] = df['geometry'].apply(lambda line: line.length)

# === Step 4: Create Graph ===
G = nx.Graph()

for _, row in df.iterrows():
    start = row['start']
    end = row['end']
    weight = row['Var_mean']  # You can customize this
    G.add_edge(start, end, weight=weight, attr=row.to_dict())

# === Step 5: Export Cleaned Data ===
df.to_csv("data/final_data/preprocessed_Map.csv", index=False)
with open("data/final_data/road_graph.gpickle", "wb") as f:
    pickle.dump(G, f)
with open("data/final_data/road_graph.gpickle", "rb") as f:
    G = pickle.load(f)

print("✅ Preprocessing complete")


