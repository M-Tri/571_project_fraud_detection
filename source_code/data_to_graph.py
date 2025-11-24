import pandas as pd
import networkx as nx
import pickle
import ast

# Load labeled emails
print("Loading file")
df = pd.read_csv("../data_files/labeled_emails.csv")
print("File loaded successfully")

def get_python_list_format(field):
    return ast.literal_eval(field)

def build_enron_communication_graph(df):
    G = nx.DiGraph()
    
    for table_index_reference, data_table in df.iterrows():
        
        # Get all recipients
        recipients = []
        recipients.extend(get_python_list_format(data_table['To']))
        recipients.extend(get_python_list_format(data_table['X-cc']))
        recipients.extend(get_python_list_format(data_table['X-bcc']))

        # Sender node attributes
        sender = data_table['From']

        # Receiver node attributes
        for receiver in recipients:
            # Avoid self loops
            if sender != receiver:
                if G.has_edge(sender, receiver):
                    G[sender][receiver]['weight'] += 1
                    G[sender][receiver]['emails'].append(table_index_reference)
                else:
                    G.add_edge(sender, receiver, weight = 1, emails =[table_index_reference])
                

                # If email address of receiver contains @enron.com
                if 'enron.com' in receiver:
                    G.nodes[receiver]['type'] = 'Internal'
                else:
                    G.nodes[receiver]['type'] = 'External'

                # add department to node attribute
                G.nodes[receiver]['department'] = data_table['X-Origin']

                # If email address of sender contains @enron.com
                if 'enron.com' in sender:
                    G.nodes[sender]['type'] = 'Internal'
                else:
                    G.nodes[sender]['type'] = 'External'
                    
                # add department to node attribute
                G.nodes[sender]['department'] = data_table['X-Origin']
                # Email is POI
                G.nodes[sender]['is_poi'] = data_table.get('email_of_interest')
    return G

# Build the graph
print("Building communication graph...")
G = build_enron_communication_graph(df)


print("Saving graph object")
with open("../data_files/graph_object/enron_graph.pkl", "wb") as f:
    pickle.dump(G, f)
print("Graph object is successfully saved")
