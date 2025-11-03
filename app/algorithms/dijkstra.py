import pandas as pd
import numpy as np
import networkx as nx
import os
import time
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
import heapq

def dijkstra_algorithm(features: dict):
    # Print provided features as "key: value" for debugging
    print("Provided features:")
    for k, v in features.items():
        print(f"{k}: {v}")
    
    file_path = os.path.join(os.path.dirname(__file__), "../../app/data/county_demographics.csv")
    data = pd.read_csv(file_path)

    #Extract the keys from features (dict), will serve as a list of the column names
    feature_names = list(features.keys())

    #Extract relevant columns
    subset = data[["County", "State"] + feature_names].dropna()

    scaler = MinMaxScaler()
    normalized = scaler.fit_transform(subset[feature_names])
    subset[feature_names] = normalized

    #Extract the weights from the values of features (dict), make into numpy array
    ideal = np.array(list(features.values()))

    #Normalize the weights
    subset["distance_to_ideal"] = np.linalg.norm(subset[feature_names].values - ideal, axis=1)

    X = subset[feature_names].values
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

    #Isolate the dijkstra search algorithm in order to time it
    def dijkstra(graph, start):
        #initializing the starting distance:
        dist = {node: float('inf') for node in graph} #assume all routes are infinity
        dist[start] = 0 #route from ideal index to ideal index is 0
        prev_nodes = {node: None for node in graph} #keep track of the previous nodes
        pq = [(0, start)]  #using a priority queue, adding pairs like (distance, node)
        
        while pq:
            current_dist, current_node = heapq.heappop(pq) #O(logn) time, use a min heapq to pop the shortest distance
            
            #Skip if we already found a shorter path before
            if current_dist > dist[current_node]:
                continue
            
            for neighbor, weight in graph[current_node].items():
                new_dist = current_dist + weight['weight'] #add the distances
                if new_dist < dist[neighbor]: #found a better distance, reset the min distance and previous node
                    dist[neighbor] = new_dist
                    prev_nodes[neighbor] = current_node
                    heapq.heappush(pq, (new_dist, neighbor)) #O(logn) time, add in new neighbor, smallest distance will be in first
        
        return dist


    start_time = time.time()
    shortest_distances = dijkstra(G, perfect_index)
    end_time = time.time()
    time_elapsed = end_time - start_time

    #Accessing the distances from shortest_distances
    distance_map = {node: dist for node, dist in shortest_distances.items() if node in subset.index}

    #Creating the new column
    data["DistanceToIdeal"] = data.index.map(distance_map)

    #Saving it to the data folder
    output_path = "app/data/county_demographics_with_distances.csv"
    data.to_csv(output_path, index=False)

    #Finding node with shortest distance from the dict
    closest_idx = min(
        (i for i in shortest_distances if i != perfect_index),
        key=lambda i: shortest_distances[i]
    )

    best_county = subset.loc[closest_idx]
    print("Closest to Perfect County:")
    print(best_county[["County", "State"]])
    print("Time elapsed:", time_elapsed)

    return best_county[["County", "State"]], time_elapsed