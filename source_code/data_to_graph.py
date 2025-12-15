import pandas as pd
import networkx as nx
import pickle
import ast

def get_python_list_format(field):
    if isinstance(field, list):
        return field
    if pd.isna(field) or not isinstance(field, str):
        return []
    return ast.literal_eval(field)

# List of POIs
person_of_interest_words = [
    ('jeff', 'skilling'), 
    ('jeffrey', 'skilling'),
    ('ken', 'lay'), 
    ('kenneth', 'lay'),
    ('andrew', 'fastow'),
    ('andrew', 's', 'fastow'),
    ('andy', 'fastow'),
    ('fastow',),
    ('richard', 'causey'),
    ('ben', 'glisan'),
    ('glisan',),
    ('michael', 'kopper'),
    ('tim', 'despain'), 
    ('mark', 'koenig'),
    ('ken', 'rice'), 
    ('kenneth', 'rice'), 
    ('joe', 'hirko'),
    ('kevin', 'hannon'), 
    ('kevin', 'howard'), 
    ('rex', 'shelby'),
    ('tim', 'belden'), 
    ('jeff', 'richter'), 
    ('john', 'forney'),
    ('forney',), 
    ('m..forney',)
]

def contains_email_of_interest(email_list, poi_words_list):
    if not email_list:
        return False
    for item in email_list:
        if isinstance(item, tuple) and len(item) > 0:
            name = item[0]
        elif isinstance(item, str):
            name = item
        else:
            continue
        clean_name = name.lower().replace('.', ' ').replace('_', ' ')
        name_words = set(clean_name.split())
        for poi in poi_words_list:
            required_matches = 1 if len(poi) == 1 else 2
            if len(name_words & set(poi)) >= required_matches:
                return True
    return False

# Canonicalize sender/recipient
def canonical_name(node):
    if isinstance(node, tuple) and len(node) > 0:
        raw_name = node[0]
    elif isinstance(node, str) and node.strip():
        raw_name = node
    else:
        return "Unknown"
    return raw_name.lower().replace('.', ' ').replace('_', ' ').strip()

# Clean recipient tuple
def clean_recipient_tuple(recipient):
    if isinstance(recipient, tuple) and len(recipient) == 2:
        name, email = recipient
        name = name.replace("'", "").replace('"', '').replace('\\', '').strip()
        email = email.replace("'", "").replace('"', '').replace('\\', '').strip()
        email = email.lstrip('<').rstrip('>')
        return (name, email)
    elif isinstance(recipient, str):
        return recipient.strip().replace("'", "").replace('"', '').replace('\\', '')
    else:
        return recipient

def build_enron_graph_normalized(df):
    count_poi = 0
    G = nx.DiGraph()

    for idx, row in df.iterrows():
        # Parse sender
        senders = get_python_list_format(row['From'])
        if not senders:
            continue
        sender = canonical_name(senders[0])

        # Initialize node
        if not G.has_node(sender):
            G.add_node(sender)
            G.nodes[sender]['name'] = sender.title()
            G.nodes[sender]['department'] = row['X-Origin']
            is_poi = contains_email_of_interest([senders[0]], person_of_interest_words)
            G.nodes[sender]['is_poi'] = is_poi
            if is_poi:
                count_poi += 1

        # Parse recipients
        recipients = []
        for col in ['To','X-cc','X-bcc','cc']:
            recipients.extend(get_python_list_format(row[col]))
        recipients = [canonical_name(clean_recipient_tuple(r)) for r in recipients]

        for rec in recipients:
            if sender == rec:
                continue

            # Merge node if new
            if not G.has_node(rec):
                G.add_node(rec)
                G.nodes[rec]['name'] = rec.title()
                G.nodes[rec]['department'] = row['X-Origin']
                is_poi = contains_email_of_interest([rec], person_of_interest_words)
                G.nodes[rec]['is_poi'] = is_poi
                if is_poi:
                    count_poi += 1

            # Merge edges (sum weights)
            if G.has_edge(sender, rec):
                G[sender][rec]['weight'] += 1
                G[sender][rec]['emails'].append(idx)
            else:
                G.add_edge(sender, rec, weight=1, emails=[idx])

    print(f"Total POIs flagged: {count_poi}")
    print(f"Total nodes: {len(G.nodes)}")
    print(f"Total edges: {len(G.edges)}")
    return G

if __name__ == "__main__":
    df = pd.read_csv("../data_files/labeled_emails.csv")
    G = build_enron_graph_normalized(df)

    output_path = "../data_files/graph_object/enron_graph.pkl"
    with open(output_path, "wb") as f:
        pickle.dump(G, f)
    print("Saved graph")
