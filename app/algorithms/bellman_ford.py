import pandas as pd
import numpy as np
import networkx as nx
import os
import time
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors


def bellman_ford_algorithm(features: dict):
    #Normalizing the ideal features and creating the graph is basically 
    #the same as the process in Dijkstra's algorithm

    file_path = os.path.join(os.path.dirname(__file__), "../../app/data/county_demographics.csv")
    data = pd.read_csv(file_path)

    feature_names = list(features.keys())

    #Extract relevant columns
    subset = data[["County", "State"] + feature_names].dropna()

    scaler = MinMaxScaler()
    normalized = scaler.fit_transform(subset[feature_names])
    subset[feature_names] = normalized

    #Array of weights
    ideal = np.array(list(features.values()))

    #Normalize the weights
    subset["distance_to_ideal"] = np.linalg.norm(subset[feature_names].values - ideal, axis=1)

    X = subset[feature_names].values
    k = 5  #number of neighbors, make it so it's not too clustered
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
    
    def bellman_ford(graph, start):
        #Initialize distances and predecessors
        dist = {node: float('inf') for node in graph.nodes}
        pred = {node: None for node in graph.nodes}
        dist[start] = 0

        #Extract all edges
        edges = []
        for u, v, data in graph.edges(data=True):
            weight = data.get('weight', 1.0)
            edges.append((u, v, weight))
            #For undirected graphs, add both directions
            if not isinstance(graph, nx.DiGraph):
                edges.append((v, u, weight))

        V = len(graph.nodes)

        #Relax edges repeatedly
        for _ in range(V - 1):
            updated = False
            for u, v, w in edges:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    pred[v] = u
                    updated = True
            if not updated:
                break  #Stop when no more updates

        return dist
    

    start_time = time.time()
    shortest_distances = bellman_ford(G, perfect_index)
    end_time = time.time()
    time_elapsed = end_time - start_time

    #Accessing the distances from shortest_distances
    distance_map = {node: dist for node, dist in shortest_distances.items() if node in subset.index}

    #Creating the new column
    data["DistanceToIdeal"] = data.index.map(distance_map)

    #Saving it to the data folder
    output_path = "app/data/county_demographics_with_distances.csv"
    data.to_csv(output_path, index=False)

    #Find node with smallest distance
    closest_idx = min(
        (i for i in shortest_distances if i != perfect_index),
        key=lambda i: shortest_distances[i]
    )

    best_county = subset.loc[closest_idx]
    print("Closest to Perfect County:")
    print(best_county[["County", "State"]])
    print("Time elapsed:", time_elapsed)

    return best_county[["County", "State"]], time_elapsed