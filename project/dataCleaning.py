import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Load the dataset
df = pd.read_csv("data/Coordinates.csv")

# Drop highly spare columns
df = df.drop(columns=[
    'FID', 'fixme', 'short_name', 'name:etymology',
    'name:etymology:wikidata', 'source:maxspeed', 'smoothness'
])

# Fill missing numeric values with defaults
df['lanes'] = df['lanes'].fillna(2)  # Assume 2 lanes if not specified
df['maxspeed'] = df['maxspeed'].fillna(30)  # Default to 30 km/h

# Fill missing categorical values with 'unknown'
categorical_cols = ['access', 'surface', 'motorcar', 'service', 'bridge', 'oneway', 'foot', 'sidewalk']
for col in categorical_cols:
    df[col] = df[col].fillna('unknown')

# Drop rows missing essential road type info
df = df[df['highway'].notna()]

# Feature engineering: estimated road capacity = lanes * speed
df['capacity'] = df['lanes'] * df['maxspeed']

# Select features for encoding and modeling
features_to_encode = ['access', 'highway', 'surface', 'motorcar', 'bridge', 'oneway', 'foot', 'sidewalk']
numerical_features = ['lanes', 'maxspeed', 'capacity']

# One-hot encode categorical features
encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
encoded_cats = encoder.fit_transform(df[features_to_encode])
encoded_cat_df = pd.DataFrame(encoded_cats, columns=encoder.get_feature_names_out(features_to_encode))

# Scale numerical features
scaler = StandardScaler()
scaled_nums = scaler.fit_transform(df[numerical_features])
scaled_num_df = pd.DataFrame(scaled_nums, columns=numerical_features)

# Combine all processed features
preprocessed_df = pd.concat([df[['@id']], encoded_cat_df, scaled_num_df], axis=1)



