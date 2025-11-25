import pandas as pd

def parse_similarity_table(input_txt, output_excel):
    rows = []
    start_reading = False

    with open(input_txt, "r") as f:
        for line in f:
            line = line.strip()

            
            if "-----" in line:
                if start_reading is False:
                    start_reading = True
                    continue
                else:
                    
                    continue

            if start_reading and line:
                
                if "Total communities" in line or line == "":
                    break

                parts = line.split()
                if len(parts) == 2:
                    community, fraudsters = parts
                    rows.append([community, fraudsters])

    
    df = pd.DataFrame(rows, columns=["Community", "Fraudsters"])

    
    df.to_excel(output_excel, index=False)
    print(f"Excel created: {output_excel}")



parse_similarity_table("louvain_output.txt", "louvain_outputTable.xlsx")
