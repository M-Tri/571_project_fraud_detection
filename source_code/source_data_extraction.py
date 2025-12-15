import pandas as pd
import os
import re

df = pd.DataFrame()
all_data = []
file_count = 0

# Change to match your project file structure
# Source of the raw data folder 
input_path_folder = "../maildir"
# Specify the location to where you want to save your .csv file
output_path_folder = "../data_files/emails.csv"


for root, dirs, files in os.walk(input_path_folder):
    for file in files:
        # Skip hidden files used by OS system.
        if file.startswith('.'):
            continue

        # Track processing
        file_count += 1
        
        # Show progress every 100 files
        if file_count % 100 == 0:
            print(f"Processing file {file_count} ...")
        with open(os.path.join(root, file), 'r', errors='ignore') as f:
            lines = f.readlines()
        
        # Create dictionary
        data = {}
        email_content_lines = []
        headers_done = False
        data['X-bcc'] = []
        data['X-cc'] = []
        data['To'] = []

        # Create structure for data to be used to create table columns.
        for line in lines:
            if not headers_done:
                if line.startswith('Date:'):
                    data['Date'] = line.split('Date:')[1].strip()
                elif line.startswith('From:'):
                    data['From'] = line.split('From:')[1].strip()
                elif line.startswith('To:'):
                    # Extract email format
                    emails_found = re.findall(r'[\w\.-]+@[\w\.-]+', line)
                    data['To'].extend(emails_found)
                elif line.startswith('X-cc:'):
                    # Extract email format
                    emails_found = re.findall(r'[\w\.-]+@[\w\.-]+', line)
                    data['X-cc'].extend(emails_found)
                elif line.startswith('X-bcc:'):
                    # Extract email format
                    emails_found = re.findall(r'[\w\.-]+@[\w\.-]+', line)
                    data['X-bcc'].extend(emails_found)
                elif line.startswith('X-Folder:'):
                    data['X-Folder'] = line.split('X-Folder:')[1].strip()
                elif line.startswith('X-Origin:'):
                    data['X-Origin'] = line.split('X-Origin:')[1].strip()
                elif line.startswith('X-FileName:'):
                    data['X-FileName'] = line.split('X-FileName:')[1].strip()
                    headers_done = True
            else:
                # Collect email content
                if line.strip():
                    email_content_lines.append(line.strip())
        
        data['email_text'] = ' '.join(email_content_lines)
        
        all_data.append(data)

print(f"Folder Processed and is being saved to {output_path_folder}")

# Create spreadsheet
df = pd.DataFrame(all_data)

# Convert to .csv
df.to_csv(output_path_folder, index=False)
