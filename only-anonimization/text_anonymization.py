import streamlit as st
import globalvars
import spacy
from spacy import displacy
import re
from itertools import count


# Load the pre-trained model
nlp = spacy.load("en_core_web_lg")

st.title("Personal Data Anonymizer and De-Anonymizer")

uploaded_file = st.file_uploader("Choose a .txt file", type="txt")

# Initialize counters
email_counter = count(1)
phone_counter = count(1)
name_counter = count(1)

# Initialize dictionaries to store extracted data
extracted_emails = {}
extracted_phone_numbers = {}
extracted_names = {}

if uploaded_file is not None:
    email_text = uploaded_file.read().decode()

    view_type = st.radio("Select View Type", ("Anonymized Text", "De-Anonymized Text"))

    if view_type == "Anonymized Text":
        lines = email_text.splitlines()

        processed_lines = []
        for line in lines:
            # Process the text with Spacy
            doc = nlp(line)

            # Extract and replace email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, line)
            for email in emails:
                placeholder = f"<email_{next(email_counter)}>"
                line = line.replace(email, placeholder)
                extracted_emails[email] = placeholder

            # Extract and replace phone numbers
            phone_pattern = r'\+\d{1,4}(?:\s\(\d{1,4}\))?(?:\s\d{1,4}){1,4}'
            phone_numbers = re.findall(phone_pattern, line)
            for phone in phone_numbers:
                placeholder = f"<phone_{next(phone_counter)}>"
                line = line.replace(phone, placeholder)
                extracted_phone_numbers[phone] = placeholder

            # Extract and replace names from the end of the string to keep indices valid
            name_entities = {ent.start_char: ent.end_char for ent in doc.ents if ent.label_ == 'PERSON'}
            for start in sorted(name_entities.keys(), reverse=True):
                end = name_entities[start]
                name = line[start:end]
                placeholder = f"<name_{next(name_counter)}>"
                line = line[:start] + placeholder + line[end:]
                extracted_names[name] = placeholder
            processed_lines.append(line)

        email_text = "\n".join(processed_lines)

        st.write(email_text)
        st.write("Extracted emails:", extracted_emails)
        st.write("Extracted phone numbers:", extracted_phone_numbers)
        st.write("Extracted names:", extracted_names)

    elif view_type == "De-Anonymized Text":
        # Assuming that the order of entities in GPT's output matches the order of entities in the input
        email_pattern = "<email>"
        phone_pattern = "<phone_number>"
        name_pattern = "<name>"

        # Reverse the dictionaries for replacement
        emails_reversed = {v: k for k, v in extracted_emails.items()}
        phones_reversed = {v: k for k, v in extracted_phone_numbers.items()}
        names_reversed = {v: k for k, v in extracted_names.items()}

        # Replace placeholders with original entities
        deanonymized_text = email_text
        for original, placeholder in emails_reversed.items():
            deanonymized_text = deanonymized_text.replace(placeholder, original)

        for original, placeholder in phones_reversed.items():
            deanonymized_text = deanonymized_text.replace(placeholder, original)

        for original, placeholder in names_reversed.items():
            deanonymized_text = deanonymized_text.replace(placeholder, original)

        st.write(deanonymized_text)