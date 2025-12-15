import pandas as pd
import ast

# Load CSV
df = pd.read_csv("../data_files/emails.csv")


print("Fixing format...")
# Convert strings feilds to actual python lists
for col in ['From', 'To', 'cc', 'X-cc', 'X-bcc']:
    df[col] = df[col].apply(ast.literal_eval)


# Check if email is an Enron email
def is_enron_email(emails):
    if isinstance(emails, tuple):
        emails = [emails]
    for name, email in emails:
        if 'enron' in email.lower():
            return True
    return False


#Create type columns
both_internal_list = []
internal_to_external_list = []
external_to_internal_list = []
both_external_list = []


print("Adding labels...")

for i in range(len(df)):
    from_internal = is_enron_email(df['From'][i])
    to_internal = any(is_enron_email(email) for email in df['To'][i])
    from_external = not from_internal
    to_external = not to_internal

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

df['both_internal'] = both_internal_list
df['internal_to_external'] = internal_to_external_list
df['external_to_internal'] = external_to_internal_list
df['both_external'] = both_external_list


# Save CSV
df.to_csv("../data_files/labeled_emails.csv", index=False)
