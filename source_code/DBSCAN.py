import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score

# Load your graph object.
print("Loading graph object")
with open("../data_files/graph_object/enron_graph.pkl", "rb") as f:
    G = pickle.load(f)
poi_nodes = []
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


        if G.nodes[node].get('is_poi', False):
            poi_nodes.append(node)


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
  

    results = []
    for i, node in enumerate(nodes_list):
        is_poi = G.nodes[node].get('is_poi', False)
        name = G.nodes[node].get('name', str(node))
        results.append({
            'node': node,
            'cluster': cluster_labels[i],
            'is_poi': is_poi,
            'name': name,
        })
    
    return results

cluster_results = get_clusters_DBSCAN(G)

print("CLUSTER ANALYSIS TABLE")
poi_count = {}
cluster_sizes = {}
flagged_poi_names = []
for result in cluster_results:
    cluster = result['cluster']
    cluster_sizes[cluster] = cluster_sizes.get(cluster, 0) + 1
    if result['is_poi']:
        poi_count[cluster] = poi_count.get(cluster, 0) + 1


# --- Print only POIs in NOISE cluster (-1) ---
print("\nPOIs in NOISE cluster (-1):")
for result in cluster_results:
    if result['cluster'] == -1 and result['is_poi']:
        node = result['node']
        name = result['name']
        print(f"Node: {name}, Is POI: {result['is_poi']}")



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