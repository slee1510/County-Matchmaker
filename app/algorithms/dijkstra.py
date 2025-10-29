import pandas as pd
import numpy as np
import networkx as nx
import random
import csv
import os
import time
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
import heapq

file_path = os.path.join(os.path.dirname(__file__), "../../app/data/county_demographics.csv")
data = pd.read_csv(file_path)

#Features that we will get from the user, placeholders for now...
features = [
    "Education.Bachelor's Degree or Higher",
    "Income.Median Houseold Income",
    "Miscellaneous.Mean Travel Time to Work",
    "Age.Percent 65 and Older",
    "Ethnicities.Asian Alone",
    "Housing.Households",
    "Miscellaneous.Percent Female",
    "Employment.Firms.Minority-Owned"
]

#Extract relevant columns
subset = data[["County", "State"] + features].dropna()

scaler = MinMaxScaler()
normalized = scaler.fit_transform(subset[features])
subset[features] = normalized

#Array of weights
ideal = np.array([1.0, 1.0, 0.0, 0.5, 0.7, 0.9, 0.3, 0.8])

#Normalize the weights
subset["distance_to_ideal"] = np.linalg.norm(subset[features].values - ideal, axis=1)

best = subset.loc[subset["distance_to_ideal"].idxmin()]

X = subset[features].values
k = 5  # number of neighbors, make it so it's not too clustered
nbrs = NearestNeighbors(n_neighbors=k+1).fit(X)
distances, indices = nbrs.kneighbors(X)

G = nx.Graph()

#Add counties as nodes
for i, row in subset.iterrows():
    G.add_node(i, county=row["County"], state=row["State"])

#Add weighted edges
for i in range(len(subset)):
    for j, d in zip(indices[i][1:], distances[i][1:]):
        G.add_edge(i, j, weight=d)

perfect_index = len(subset)
#Adding the perfect county node based on user's preferences
G.add_node(perfect_index, county="Perfect County", state="Ideal")

#Adding the edges of perfect county to the graph, edge weight using distance_to_ideal
for i, row in subset.iterrows():
    G.add_edge(perfect_index, i, weight=row["distance_to_ideal"])

def dijkstra(graph, start):
    #initializing the starting distance:
    distances = {node: float('inf') for node in graph} #assume all routes are infinity
    distances[start] = 0 #route from ideal index to ideal index is 0
    prev_nodes = {node: None for node in graph} #keep track of the previous nodes
    pq = [(0, start)]  #using a priority queue, adding pairs like (distance, node)
    
    while pq:
        current_dist, current_node = heapq.heappop(pq) #O(logn) time, use a min heapq to pop the shortest distance
        
        #Skip if we already found a shorter path before
        if current_dist > distances[current_node]:
            continue
        
        for neighbor, weight in graph[current_node].items():
            new_dist = current_dist + weight['weight'] #add the distances
            if new_dist < distances[neighbor]: #found a better distance, reset the min distance and previous node
                distances[neighbor] = new_dist
                prev_nodes[neighbor] = current_node
                heapq.heappush(pq, (new_dist, neighbor)) #O(logn) time, add in new neighbor, smallest distance will be in first
    
    return distances, prev_nodes


start_time = time.time()
distances, prev_nodes = dijkstra(G, perfect_index)
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