import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import pickle
# MiniBatchKMeans can be used as well
from sklearn.cluster import MiniBatchKMeans
from sklearn.cluster import KMeans 
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

def plot_clusters_2d(features_scaled, labels, title="Cluster visualization (PCA)"):
    pca = PCA(n_components=2)
    reduced = pca.fit_transform(features_scaled)

    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(reduced[:, 0], reduced[:, 1], c=labels, cmap='tab10', alpha=0.8, s=25)
    plt.title(title)
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    cbar = plt.colorbar(scatter)
    cbar.set_label("Cluster ID")

    plt.savefig("../data_files/figures/kmeans_clusters.png", dpi=200)
    


# Load your graph object.
print("Loading graph object")
with open("../data_files/graph_object/enron_graph.pkl", "rb") as f:
    G = pickle.load(f)


def form_clusters(G, num_of_clusters):
    
    node_features = {}
    
    # get all nodes from the graph
    nodes = list(G.nodes())

    for node in nodes:
        # Num of emails this person sent
        out_degree = G.out_degree(node)
        # Num of emails this person received
        in_degree = G.in_degree(node)
        total_degree = out_degree + in_degree
        
        # Vector used to find how similar two node 's behavior is based on given values.
        attributes_vector = [
            in_degree,
            out_degree,
            total_degree,
            # Ratio of sent vs received                    
            out_degree / max(1, in_degree),
            # Number of unique people this person sent
            len(list(G.successors(node))),
            # Number of unique people this person received email from
            len(list(G.predecessors(node))),
        ]

        # Map people to their attribute vector for later retrieval
        node_features[node] = attributes_vector
    
    # Convert to arrays for sklearn
    attributes = np.array(list(node_features.values()))
    
    # Pick scaler type
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(attributes)
    
    # Use K-Means and processes data in batches
    kmeans = KMeans(n_clusters = num_of_clusters, random_state=42)
    # Learn and assign to a cluster
    cluster_labels = kmeans.fit_predict(features_scaled)
    #plot_clusters_2d(features_scaled, cluster_labels, title="KMeans clusters (PCA projection)")
    
    silhouette_avg = silhouette_score(features_scaled, cluster_labels)
    print(f"Silhouette Score: {silhouette_avg}")

    return cluster_labels, node_features

print("Starting clustering")
cluster_labels, node_features = form_clusters(G, 10)

print("\n=== CLUSTER ANALYSIS ===")
cluster_sizes = {}
poi_counts = {}

nodes = list(node_features.keys())

for i in range(len(nodes)):
    node = nodes[i] 
    cluster_number = cluster_labels[i]
    is_poi = G.nodes[node].get('is_poi', False)
    
    current_size = cluster_sizes.get(cluster_number, 0)
    cluster_sizes[cluster_number] = current_size + 1
    
    if is_poi:
        current_poi_count = poi_counts.get(cluster_number, 0)
        poi_counts[cluster_number] = current_poi_count + 1


print("Cluster | Nodes | POI Found in this cluster | Percentage")
print("-" * 55)
for cluster in sorted(cluster_sizes.keys()):
    size = cluster_sizes[cluster]
    pois = poi_counts.get(cluster, 0)
    if size > 0:
        poi_percent = (pois / size) * 100
    else:
        poi_percent = 0

    print(f"{cluster:4} | {size:10} | {pois:20} | {poi_percent:5.2f}%")
