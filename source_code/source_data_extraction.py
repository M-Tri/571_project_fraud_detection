import pandas as pd
import os
from extract_emails import process_all_test_lines, split_email_list, clean_brackets

df = pd.DataFrame()
all_data = []
file_count = 0

# Change to match your project file structure
input_path_folder = "../maildir"
output_path_folder = "../data_files/emails.csv"

def extract_body_between(lines, start_marker, stop_marker):
    body_lines = []
    after_xfilename = False
    started = False

    for line in lines:
        stripped = line.lstrip()

        #Wait for end of headers
        if not after_xfilename:
            if stripped.startswith("X-FileName:"):
                after_xfilename = True
            continue

        #Wait for start_marker
        if not started:
            if stripped.startswith(start_marker) or stripped.startswith(start_marker + '='):
                started = True
                line = line.replace(start_marker, '', 1).lstrip(':= \t')
                body_lines.append(line.rstrip("\n"))
            continue

        #Stop at stop_marker
        if stripped.startswith(stop_marker) or stripped.startswith(stop_marker + '='):
            break

        #Collect lines inside block
        body_lines.append(line.rstrip("\n"))

    return "\n".join(body_lines)


for root, dirs, files in os.walk(input_path_folder):
    for file in files:
        if file.startswith('.'):
            continue

        file_count += 1
        if file_count % 100 == 0:
            print(f"Processing file {file_count} ...")

        with open(os.path.join(root, file), 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        # Initialize dictionary with all fields as lists
        data = {
            'Message-ID': [],
            'Subject': [],
            'Date': [],
            'From': [],
            'To': [],
            'cc': [],
            'X-Folder': [],
            'X-Origin': [],
            'X-FileName': [],
            'X-cc': [],
            'X-bcc': [],
        }

        headers_done = False
        for line in lines:
            if not headers_done:
                if line.startswith('Message-ID:'):
                    data['Message-ID'].append(line.split(':', 1)[1].strip())
                elif line.startswith('Subject:'):
                    data['Subject'].append(line.split(':', 1)[1].strip())
                elif line.startswith('Date:'):
                    data['Date'].append(line.split('Date:')[1].strip())
                elif line.startswith('From:'):
                    data['From'].append(line.split('From:')[1].strip())
                elif line.startswith('To:'):
                    header_to = line.split('To:', 1)[1].strip()
                    if header_to:
                        data['To'].extend(process_all_test_lines([header_to]))
                elif line.startswith('X-cc:'):
                    data['X-cc'].append(line.split('X-cc:')[1].strip())
                elif line.startswith('X-bcc:'):
                    data['X-bcc'].append(line.split('X-bcc:')[1].strip())
                elif line.startswith('X-Folder:'):
                    data['X-Folder'].append(line.split('X-Folder:')[1].strip())
                elif line.startswith('X-Origin:'):
                    data['X-Origin'].append(line.split('X-Origin:')[1].strip())
                elif line.startswith('X-FileName:'):
                    data['X-FileName'].append(line.split('X-FileName:')[1].strip())
                    headers_done = True

        # Extract body parts and process
        to_body = extract_body_between(lines, start_marker="To:", stop_marker="cc:")
        data['To'].extend(process_all_test_lines(to_body.splitlines()))

        cc_body = extract_body_between(lines, start_marker="cc:", stop_marker="Subject:")
        data['cc'].extend(process_all_test_lines(cc_body.splitlines()))

        # Convert using function that deals with string body and returns tuples (sender, email)
        data['To'] = split_email_list(data['To'])
        data['cc'] = split_email_list(data['cc'])

        # Convert using function that deals <>, and /, and headers
        data['X-bcc'] = clean_brackets(data['X-bcc'])
        data['X-bcc'] = data['X-bcc'].split(',')

        data['X-cc'] = clean_brackets(data['X-cc'])
        data['X-cc'] = data['X-cc'].split(',')

        data['X-Origin'] = clean_brackets(data['X-Origin'])
        data['X-Origin'] = data['X-Origin'].split(',')
        
        # Convert using header but it returns tuples list (sender, email)
        data['From'] = split_email_list(data['From'])


        all_data.append(data)

print(f"Folder Processed and is being saved to {output_path_folder}")

df = pd.DataFrame(all_data)
df.to_csv(output_path_folder, index=False)