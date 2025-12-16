import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler


with open("../data_files/graph_object/enron_graph.pkl", "rb") as f:
    G = pickle.load(f)

def get_node_attributes(G, node):
    out_degree = G.out_degree(node)
    in_degree = G.in_degree(node)
    total_degree = out_degree + in_degree

    attributes_vector = [
        in_degree,
        out_degree,
        total_degree,
        out_degree / max(1, in_degree),
        len(list(G.successors(node))),
        len(list(G.predecessors(node))),
    ]


    department = G.nodes[node].get('department', 'Unknown')
    dept_code = hash(department) % 100
    attributes_vector.append(dept_code)

    return np.array(attributes_vector)


def focused_fraudster_network(G, known_fraudster, similarity_threshold=0.7, max_similar_people=100):
    # Start with the known fraudster
    fraudster_set = {known_fraudster}

    # Get all nodes outgoing edges to the fraudster
    neighbors_list = list(G.neighbors(known_fraudster))

    # Convert to set and remove duplicates
    neighbors_set = set(neighbors_list)

    # Combine the fraudster with their direct contacts
    fraudster_direct_contacts = fraudster_set | neighbors_set


    node_features = {}
    #Get a list of all nodes in the graph
    nodes = list(G.nodes())

    for node in nodes:
        #Get attribute vector and store it in corresponding node.
        node_features[node] = get_node_attributes(G, node)

    #Convert all node feature vectors into a single NumPy array
    all_features = np.array(list(node_features.values()))

    #Get scalar
    scaler = StandardScaler()
    all_features_scaled = scaler.fit_transform(all_features)


    # Map each node to its index in the array
    node_to_index = {}
    for i, node in enumerate(nodes):
        node_to_index[node] = i

    # Find the index of the known fraudster
    fraudster_index = node_to_index[known_fraudster]

    # Get the standardized feature vector of the known fraudster
    fraudster_features = all_features_scaled[fraudster_index]

    # Find behaviorally similar nodes
    similar_people = []

    # Loop through all nodes to find behaviorally similar people
    for node in nodes:
        # Avoid including the fraudster themselves or their direct contacts when looking for “behaviorally similar people”
        if (node == known_fraudster) or ( node in fraudster_direct_contacts):
            continue

        # Get the scaled feature vector
        node_features_scaled = all_features_scaled[node_to_index[node]]

        # Compute cosine similarity with the fraudster
        similarity = np.dot(fraudster_features, node_features_scaled) / (
            np.linalg.norm(fraudster_features) * np.linalg.norm(node_features_scaled)
        )

        # If similarity is above threshold, add to similar_people list
        if similarity >= similarity_threshold:
            similar_people.append((node, similarity))



    # Sort similar people by similarity in descending order
    similar_people_sorted = sorted(similar_people, key=lambda pair: pair[1], reverse=True)


    # Take top similar people
    top_similar = []

    for i in range(min(max_similar_people, len(similar_people_sorted))):
        node, similarity = similar_people_sorted[i]
        top_similar.append(node)

    # Combine direct contacts and top similar people
    nodes_of_interest = []
    for node in fraudster_direct_contacts:
        nodes_of_interest.append(node)
    for node in top_similar:
        nodes_of_interest.append(node)

    # new graph that only contains the nodes you care about: the known fraudster and contacts
    G_focused = G.subgraph(nodes_of_interest).copy()



    # Return the focused subgraph and the fraudster's features
    return G_focused, fraudster_features



# Main part
focus_fraudster = 'jeffrey skilling'
G_focused, fraudster_features = focused_fraudster_network(G, focus_fraudster)



with open("../data_files/graph_object/enron_graph_focused.pkl", "wb") as f:
    pickle.dump(G_focused, f)