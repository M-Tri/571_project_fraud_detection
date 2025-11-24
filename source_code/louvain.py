import numpy as np
import pickle
import networkx as nx
import community as community_louvain
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors


"""
Transforms email communication graph into behavioral similarity graph for Louvain clustering.
Uses original graph's email patterns to create new graph where edges connect 
people with similar communication behavior.
"""

with open("../data_files/graph_object/enron_graph.pkl", "rb") as f:
    G = pickle.load(f)

def build_new_similarity_graph_based_on_old(original_graph):
    
    node_features = {}
    
    for node in G.nodes():
        out_degree = G.out_degree(node)
        in_degree = G.in_degree(node)
        total_degree = out_degree + in_degree
        
        feature_vector = [
            out_degree,                          
            in_degree,
            # Ratio of sent vs received                    
            out_degree / max(1, in_degree),
            # Number of unique people this person sent
            len(list(G.successors(node))),
            # Number of unique people this person received email from
            len(list(G.predecessors(node))),
            total_degree,
        ]
        
        node_features[node] = feature_vector
    
    # Convert to arrays for sklearn
    nodes = list(node_features.keys())
    features = np.array([node_features[node] for node in nodes])
    
    # Pick scaler type: Standard
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Create new graph based on behavioral similarity
    new_similarity_graph = nx.Graph()
    
    for node in nodes:
        new_similarity_graph.add_node(node,
            department = G.nodes[node].get('department', 'Unknown'),
            is_poi = G.nodes[node].get('is_poi', False))
    

    print("Connect similar people")
    # Person connects to 5 similar people
    n_neighbors = 5
    n_neighbors_with_self = n_neighbors + 1
    behavior_matcher = NearestNeighbors(n_neighbors=n_neighbors_with_self)
    behavior_matcher.fit(features_scaled)
    
    # Person relative to neighbors Example: indices = [[0, 1, 2]], distances[[0.0, 0.2, 0.3]]
    distances, indices = behavior_matcher.kneighbors(features_scaled)
    

    for person_idx in range(len(nodes)):
        current_person = nodes[person_idx]
        # Skip one self
        similar_people_indices = indices[person_idx][1:]
        
        for similar_person_index in similar_people_indices:
            # Find position of this neighbor in the list to get corresponding distance
            neighbor_position = list(indices[person_idx]).index(similar_person_index)
            distance_to_similar = distances[person_idx][neighbor_position]
            # Get max value to normalize with
            max_possible_distance = np.max(distances)
            
            # Normalize distance to 0-1 range
            similarity_score = 1 - (distance_to_similar / max_possible_distance)
            
            similar_person = nodes[ similar_person_index]
            
            # Connect the two similar people
            new_similarity_graph.add_edge(current_person, similar_person, weight = similarity_score)
    
    print(f"Similarity graph is created")
    return new_similarity_graph, features_scaled, nodes

def detect_communities(new_similarity_graph):
    
    print("Run Louvain on new similarity graph")
    
    # Run Louvain with similarly scores as edge weights
    partition = community_louvain.best_partition(new_similarity_graph, weight='weight')
    
    # Get labels
    community_labels = list(partition.values())
    
    
    return partition, community_labels

# Build behavioral similarity graph and run Louvain
print("Starting Behavioral Similarity Analysis...")
new_similarity_graph, features_scaled, nodes = build_new_similarity_graph_based_on_old(G)
partition, community_labels = detect_communities(new_similarity_graph)

############### Print Results ##################
# Calculate silhouette score
silhouette = silhouette_score(features_scaled, community_labels)
print(f"Silhouette Score: {silhouette:.2f}")

# Count fraudsters per community
community_fraudsters = {}
for node, community_id in partition.items():
    if new_similarity_graph.nodes[node].get('is_poi'):
        current_count = community_fraudsters.get(community_id, 0)
        new_count = current_count + 1
        community_fraudsters[community_id] = new_count

# Simple results table
print("-------------------------")
print("Community   Fraudsters")
print("-------------------------")

for community_id in sorted(community_fraudsters.keys()):
    fraudster_count = community_fraudsters[community_id]
    print(f"{community_id:<12} {fraudster_count:<12}")

# Total summary
print(f"\nTotal communities with fraudsters: {len(community_fraudsters)}")
