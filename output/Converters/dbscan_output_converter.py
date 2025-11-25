import pandas as pd

def txt_to_excel(txt_path, excel_path):
    rows = []
    start_reading = False

    with open(txt_path, 'r') as f:
        for line in f:
            line = line.strip()

           
            if "-----" in line:
                start_reading = True
                continue

            if start_reading and line:
                
                parts = [p.strip() for p in line.split("|")]

                
                if len(parts) == 5:
                    cluster, size, pois, poi_pct, ctype = parts
                    rows.append([int(cluster), int(size), int(pois), poi_pct, ctype])

    
    df = pd.DataFrame(rows, columns=["Cluster", "Size", "POIs", "POI %", "Type"])

    
    df.to_excel(excel_path, index=False)
    print(f"Excel file created at: {excel_path}")



txt_to_excel("dbscan_output.txt", "dbscan_outputTable.xlsx")
