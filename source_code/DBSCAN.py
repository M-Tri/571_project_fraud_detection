import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
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
    plt.tight_layout()

    plt.savefig("../data_files/figures/dbscan_clusters.png", dpi=200)

# Load your graph object.
print("Loading graph object")
with open("../data_files/graph_object/enron_graph.pkl", "rb") as f:
    G = pickle.load(f)

def get_clusters_DBSCAN(G ):
    
    node_features = {}
    
    # Use ALL nodes
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

        # Add department as numerical code
        department = G.nodes[node].get('department', 'Unknown')

        # Convert department to hash code
        dept_code = hash(department) % 100  
        attributes_vector.append(dept_code)

        # Map people to their attribute vector for later retrieval
        node_features[node] = attributes_vector

    
    # Convert to arrays for sklearn
    nodes_list = list(node_features.keys())
    attributes = np.array(list(node_features.values()))
    
    # Pick scaler type
    scaler = StandardScaler()
    # Normalize data
    features_scaled = scaler.fit_transform(attributes)
    
    # Use DBSCAN with very sensitive setting. The point is to use noise to detect and not clusters.
    dbscan = DBSCAN(eps = 0.03, min_samples = 2)
    cluster_labels = dbscan.fit_predict(features_scaled)
    #plot_clusters_2d(features_scaled, cluster_labels, title="DBSCAN clusters (PCA projection)")

    results = []
    for i, node in enumerate(nodes_list):
        is_poi = G.nodes[node].get('is_poi', False)
        results.append({
            'node': node,
            'cluster': cluster_labels[i],
            'is_poi': is_poi,
        })
    
    return results

cluster_results = get_clusters_DBSCAN(G)

print("CLUSTER ANALYSIS TABLE")
poi_count = {}
cluster_sizes = {}

for result in cluster_results:
    cluster = result['cluster']
    cluster_sizes[cluster] = cluster_sizes.get(cluster, 0) + 1
    if result['is_poi']:
        poi_count[cluster] = poi_count.get(cluster, 0) + 1

print("Cluster | Size | POIs | POI % | Type")
print("-" * 50)
for cluster in sorted(cluster_sizes.keys()):
    size = cluster_sizes[cluster]
    pois = poi_count.get(cluster, 0)
    if size > 0:
      poi_percent = (pois / size) * 100
    else:
      poi_percent = 0
    
    if cluster == -1:
        cluster_type = "NOISE"
    else:
        cluster_type = "CLUSTER"
    
    print(f"{cluster:7} | {size:4} | {pois:4} | {poi_percent:5.2f}% | {cluster_type}")