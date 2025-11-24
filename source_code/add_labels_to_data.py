import pandas as pd

# Load CSV
df = pd.read_csv("../data_files/emails.csv")

# List of people who were found guilty used to label data
person_of_interest = [
    'jeff.skilling@enron.com',
    'jeffrey.skilling@enron.com',
    'ken.lay@enron.com',
    'kenneth.lay@enron.com',
    'andrew.fastow@enron.com',
    'andrew.s.fastow@enron.com',
    'andy.fastow@enron.com',
    'fastow@enron.com',
    'richard.causey@enron.com',
    'ben.glisan@enron.com',
    'glisan@enron.com',
    'michael.kopper@enron.com',
    'tim.despain@enron.com',
    'mark.koenig@enron.com',
    'ken.rice@enron.com',
    'kenneth.rice@enron.com',
    'joe.hirko@enron.com',
    'kevin.hannon@enron.com',
    'kevin.howard@enron.com',
    'rex.shelby@enron.com',
    'tim.belden@enron.com',
    'jeff.richter@enron.com',
    'john.forney@enron.com',
    'forney@enron.com',
    'm..forney@enron.com'
]

# 1. Check if email is from Enron
def is_enron_email(email):
    email_string_format = str(email)
    if 'enron.com' in email_string_format:
        return True
    return False

# 2. Check if contains person from the list
def contains_email_of_interest(person_email_address):
    str_email_address = str(person_email_address)
    for email in person_of_interest:
        if email in str_email_address:
            return 1
    return 0

# 3. Add from_enron column
from_enron_list = []
for from_email in df['From']:
    if is_enron_email(from_email):
        from_enron_list.append(1)
    else:
        from_enron_list.append(0)
df['from_enron'] = from_enron_list

# 4. Create new list and add as column to table
to_enron_list = []
for to_email in df['To']:
    if is_enron_email(to_email):
        to_enron_list.append(1)
    else:
        to_enron_list.append(0)
df['to_enron'] = to_enron_list

# Create separate columns for each type
both_internal_list = []
internal_to_external_list = []
external_to_internal_list = []
both_external_list = []

for i in range(len(df)):
    from_email = df['From'][i]
    to_emails = df['To'][i]
    
    from_internal = is_enron_email(from_email)
    # At least one of the recipient is in enron
    to_internal = any(is_enron_email(email) for email in to_emails)
    from_external = not from_internal
    to_external = not to_internal

    # Set 1 for matching type, 0 for others
    if from_internal and to_internal:
        both_internal_list.append(1)
        internal_to_external_list.append(0)
        external_to_internal_list.append(0)
        both_external_list.append(0)
    elif from_internal and to_external:
        both_internal_list.append(0)
        internal_to_external_list.append(1)
        external_to_internal_list.append(0)
        both_external_list.append(0)
    elif from_external and to_internal:
        both_internal_list.append(0)
        internal_to_external_list.append(0)
        external_to_internal_list.append(1)
        both_external_list.append(0)
    else:
        both_internal_list.append(0)
        internal_to_external_list.append(0)
        external_to_internal_list.append(0)
        both_external_list.append(1)

# Add columns
df['both_internal'] = both_internal_list
df['internal_to_external'] = internal_to_external_list
df['external_to_internal'] = external_to_internal_list
df['both_external'] = both_external_list

count = 0
# # 6. Add email_of_interest column
email_of_interest_list = []
for i in range(len(df)):

    # Check if email is in any of the following, then mark as email of interest
    guilty = 0
    if contains_email_of_interest(df['From'][i]):
        guilty = 1
    if any(is_enron_email(email) for email in df['To'][i]):
        guilty = 1
    if any(is_enron_email(email) for email in df['X-cc'][i]):
        guilty = 1
    if any(is_enron_email(email) for email in df['X-bcc'][i]):
        guilty = 1
    email_of_interest_list.append(guilty)
    if(guilty):
        count = count + 1
df['email_of_interest'] = email_of_interest_list
print(f"Total count is {count}")


print("Saving data to CSV file")
# Save CSV
df.to_csv("../data_files/labeled_emails.csv")
