import pandas as pd

def parse_cluster_analysis(input_txt, output_excel):
    rows = []
    start_reading = False

    with open(input_txt, "r") as f:
        for line in f:
            line = line.strip()

             
            if "-----" in line:
                start_reading = True
                continue

            
            if start_reading and line:
                
                parts = [p.strip() for p in line.split("|")]

                
                if len(parts) == 4:
                    cluster, nodes, poi_found, pct = parts
                    rows.append([cluster, nodes, poi_found, pct])

    
    df = pd.DataFrame(rows, columns=[
        "Cluster",
        "Nodes",
        "POI Found",
        "Percentage"
    ])

    
    df.to_excel(output_excel, index=False)
    print(f"Excel created: {output_excel}")



parse_cluster_analysis("Kmean_clustering_output.txt", "Kmean_clustering_output.xlsx")
