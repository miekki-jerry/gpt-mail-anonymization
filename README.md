# gpt-mail-anonymization
tl;dr
Drag & drop the Excel file with the email body. 
Anonymize sensitive data such as phone numbers, names, and email addresses. 
Structure the data using GPT. De-anonymize if necessary. 
Create the final Excel file with the structured data.

# About the project
The biggest issue with GPT is privacy, so it's useless for real case usage. 
And our use case was as follows: a recruitment company has scheduled interviews through emails. Every email needs to be read, and using the information inside the email, tasks should be created to determine who needs to meet with whom.
The number of emails was large, so creating tasks manually was time-consuming.
That being said, I've created a simple program where you can drag and drop an Excel file with a Body column (the body of the email).
The program finds names, surnames, phone numbers, and email addresses and puts placeholders inside. After this anonymization process, the next step is to send it to GPT - Langchain. I'm using version 3.5 because it's faster, and its accuracy is sufficient.
As output, Langchain returns a JSON structure where the keys will be used as columns for the final Excel file. But before this deanonymization happens, which is an easy, simple process.
At the end of the process, we have a more complex Excel file with 14 columns and structured data. Now I can create tasks using a popular to-do app solution for specific persons.

# Project are using: 
- 100% python
- langchain
- streamlit,
- 'spacy' model for recognizing names (This is necessary for local anonymization.),
- gpt-3.5-turbo-16k
- pandas for excel

