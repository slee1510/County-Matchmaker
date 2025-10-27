import pandas as pd
import numpy as np
import networkx as nx
import random
import csv
import os
import time
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors

file_path = os.path.join(os.path.dirname(__file__), "../../app/data/county_demographics.csv")
data = pd.read_csv(file_path)

features = [
    "Education.Bachelor's Degree or Higher",
    "Income.Median Houseold Income",
    "Miscellaneous.Mean Travel Time to Work",
    "Age.Percent 65 and Older"
]

# Extract relevant columns
subset = data[["County", "State"] + features].dropna()

scaler = MinMaxScaler()
normalized = scaler.fit_transform(subset[features])
subset[features] = normalized

ideal = np.array([1.0, 1.0, 0.0, 0.5])

subset["distance_to_ideal"] = np.linalg.norm(subset[features].values - ideal, axis=1)

best = subset.loc[subset["distance_to_ideal"].idxmin()]

X = subset[features].values
k = 5  # number of neighbors
nbrs = NearestNeighbors(n_neighbors=k+1).fit(X)
distances, indices = nbrs.kneighbors(X)

G = nx.Graph()

# Add counties as nodes
for i, row in subset.iterrows():
    G.add_node(i, county=row["County"], state=row["State"])

# Add weighted edges (skip self)
for i in range(len(subset)):
    for j, d in zip(indices[i][1:], distances[i][1:]):
        G.add_edge(i, j, weight=d)

perfect_index = len(subset)
#adding the perfect county based on user's preferences
G.add_node(perfect_index, county="Perfect County", state="Ideal")

# Connect it to all real counties with weight = distance_to_ideal
for i, row in subset.iterrows():
    G.add_edge(perfect_index, i, weight=row["distance_to_ideal"])

start_time = time.time()
####implement own dijkstra algorithm
distances = nx.single_source_dijkstra_path_length(G, perfect_index)
end_time = time.time()
time_elapsed = end_time - start_time

# Find node with smallest distance
closest_idx = min(
    (i for i in distances if i != perfect_index),
    key=lambda i: distances[i]
)

best_county = subset.loc[closest_idx]
print("Closest to Perfect County:")
print(best_county[["County", "State"]])
print("Time elapsed:", time_elapsed)