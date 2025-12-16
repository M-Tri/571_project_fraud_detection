import re
import pandas as pd
def remove_special_chars(text_line):
    """Remove all special characters from the list"""
    # Handle Windows \r\n first
    text_line = text_line.replace('\r\n', '')
    
    # Remove each special character
    for char in ['\r', '\n', '\v', '\f', '\t', '=']:
        text_line = text_line.replace(char, '')
    
    return text_line

def replace_newlines_with_commas(text_line):
    """Replace all end of line characters with commas"""
    #Remove all special characters
    text_line = remove_special_chars(text_line)
    
    # Your original code
    result = ""
    for char in text_line:
        if char == '\n':  
            result += ','
        else:
            result += char
    return result
#Get Text from Comma to Comma
def get_email_chunks(text_line):
    """Split by comma and return each chunk using regular loops"""
    chunks = []
    
    # Split by comma
    split_parts = text_line.split(',')
    
    for part in split_parts:
        # Remove whitespace from start and end only
        cleaned_part = part.strip()
        
        # Skip empty strings
        if cleaned_part:
            chunks.append(cleaned_part)
    
    return chunks

def filter_non_emails(email_list):
    """remove items without @"""
    filtered_emails = []
    
    for item in email_list:
        # Split each item by comma (in case cleaning created multiple items)
        parts = item.split(',')
        
        for part in parts:
            part = part.strip()
            if part and '@' in part:
                filtered_emails.append(part)
    
    return filtered_emails


#Replace Spaces Between Words with Dots
def replace_internal_spaces(chunk):
    """Replace spaces INSIDE the chunk, not at edges"""
    # Example: "Kenneth Lay@ENRON" → "Kenneth.Lay@ENRON"
    # But NOT: " Kenneth Lay@ENRON " → "Kenneth.Lay@ENRON" (edges trimmed)
    
    # First trim edges
    chunk = chunk.strip()
    
    # Replace spaces between words with dots
    # Keep @ and everything after it unchanged
    if '@' in chunk:
        # Split at @
        before_at, after_at = chunk.split('@', 1)
        # Replace spaces before @
        before_at = before_at.replace(' ', '.')
        # Replace spaces after @
        after_at = after_at.replace(' ', '.')

        return f"{before_at}@{after_at}"
    else:
        # No @ found, just replace all spaces
        return chunk.replace(' ', '.')

def process_all_test_lines(test_lines):
    all_results = []
    
    for line in test_lines: 
        result = process_email_line(line)
        all_results.extend(result)
    
    return all_results 

#Main Processing Function
def process_email_line(line_text):
    # Remove end of line \n from string and replace with a comma.
    line_text = replace_newlines_with_commas(line_text)

    # Split by comma
    chunks = get_email_chunks(line_text)
    
    # Clean each chunk
    cleaned_chunks = []
    for chunk in chunks:
        cleaned = replace_internal_spaces(chunk)
        cleaned_chunks.append(cleaned)
    
    final_emails = filter_non_emails(cleaned_chunks)

    return final_emails

    

def split_email_list(emails):
    results = []
    for email in emails:
        email = email.strip().lstrip('<').rstrip('>')

        if not email or not re.search(r'[a-zA-Z0-9]', email):
          continue
        if '@' not in email:
            results.append((email, ''))
            continue

        local_part, domain_part = email.split('@', 1)
        # Remove any leading non-letter characters
        local_part = re.sub(r'^[^a-zA-Z]+', '', local_part)
        # Take up to first / or \
        local_part = re.split(r'[\\/<]', local_part)[0]

        results.append((local_part, domain_part))

    return results


def split_emails(email_list):
    results = []
    for email in email_list:
        local, domain = split_email_list(email)
        results.append((local, domain))
    return results

def clean_brackets(values):
    return ','.join(
        v.split('/', 1)[0]
         .replace('<', '')
         .replace('>', '')
         .replace('"', '')
         .replace("'", '')
         .replace(':', '')
         .strip()
        for v in values
        if v.strip()
    )


