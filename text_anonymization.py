import globalvars
import spacy
from spacy import displacy
import re
from itertools import count
import json

nlp = spacy.load("en_core_web_lg")

email_counter = count(1)
phone_counter = count(1)
name_counter = count(1)

extracted_emails = {}
extracted_phone_numbers = {}
extracted_names = {}

def anonymize_text(text):
    lines = text.splitlines()

    processed_lines = []
    for line in lines:
        doc = nlp(line)

         # Remove <mailto:...> pattern
        mailto_link_pattern = r'<mailto:[^>]*>'
        line = re.sub(mailto_link_pattern, '', line)

        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, line)
        for email in emails:
            placeholder = f"<email_{next(email_counter)}>"
            line = line.replace(email, placeholder)
            globalvars.extracted_emails[email] = placeholder

        phone_pattern = r'\+\d{1,4}(?:\s\(\d{1,4}\))?(?:\s\d{1,4}){1,4}'
        phone_numbers = re.findall(phone_pattern, line)
        for phone in phone_numbers:
            placeholder = f"<phone_{next(phone_counter)}>"
            line = line.replace(phone, placeholder)
            globalvars.extracted_phone_numbers[phone] = placeholder

        name_entities = {ent.start_char: ent.end_char for ent in doc.ents if ent.label_ == 'PERSON'}
        for start in sorted(name_entities.keys(), reverse=True):
            end = name_entities[start]
            name = line[start:end]
            placeholder = f"<name_{next(name_counter)}>"
            line = line[:start] + placeholder + line[end:]
            globalvars.extracted_names[name] = placeholder

        processed_lines.append(line)

    return "\n".join(processed_lines)

def de_anonymize_text(json_data):
    emails_reversed = {v: k for k, v in globalvars.extracted_emails.items()}
    phones_reversed = {v: k for k, v in globalvars.extracted_phone_numbers.items()}
    names_reversed = {v: k for k, v in globalvars.extracted_names.items()}

    def replace_placeholders(item):
        if isinstance(item, str):
            for placeholder, original in emails_reversed.items():
                item = item.replace(placeholder, original)
            for placeholder, original in phones_reversed.items():
                item = item.replace(placeholder, original)
            for placeholder, original in names_reversed.items():
                item = item.replace(placeholder, original)
        elif isinstance(item, list):  # handle lists
            for i in range(len(item)):
                item[i] = replace_placeholders(item[i])  # replace placeholders in string elements
        return item

    deanonymized_json = {key: replace_placeholders(value) for key, value in json_data.items()}

    return deanonymized_json
