import os
import globalvars
import json
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from text_anonymization import de_anonymize_text

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model_name ='gpt-3.5-turbo-16k', temperature=0, max_tokens=8000)

template = """based on provided email from user message answer the questions honestly. 
Lets think step by step. If you are not sure, return 'null'. Information will be placeholders < ...>, keep them.
Based on given email:
###
1. From subject line extract number started with 'JR...'
2. Request received always return 'null'
3.  Is there any info about candidate number started with 'C...'. 
4. Find candidate names. (can be multiple names, in this case return as an array) 
5. Is recruitment internal or external?
6. When is interview date?
7.  Interview start:
8. Interview end: 
9. Is there any info about  duration of the interview?
10. is there any info about  location/Venue (+ where Candidates need to report on arrivals)
11. Interviewers E-mails
12. Interviewers full name (you can scrap from email):
13. How many interviewers will be involved?
14. Is there any information about recruiter name?
15. Is there any information about hiring manager name?
16. Type of the interview (Telephone / F2F / Assessment / WebEx / MS Teams)
17. Any additional information candidates should know?
18. Any information about travel expenses? Return: Yes / No 
19. Any information about cost centre?
20. Any important additional comment based on mail?
21. Here write things you are not sure about.
###
result should be in json and nothing more, be consistent, no comments. If you are not 100% sure return 'null'
### example json structure ###
{{
    "Req number": "JR...",
    "Request Received": "null",
    "Candidate ref/application ref": "C....",
    "Candidate name": ["<name_1>", "<name_2>", "<name_3>"],
    "External / Internal": "External",
    "Interview Date": ["22nd June - 12:00", "22nd June - 13:30", "23rd June - 10:00"],
    "Timeslot Start": "15th, after 12.30pm",
    "Timeslot end": "16th, 17:00",
    "Duration of the interview": "1h",
    "Location/Venue (+ where Candidates need to report on arrivals)": "Poland, Warsaw",
    "Interviewers NAME": ["<name_4>", "<name_5>"],
    "Interviewers E-mails": ["<email_1>", "<email_2>"],
    "Number of extra Interviewers": "1",
    "Recruiter": "<name_3>",
    "Hiring Manager": "null",
    "Type of the interview (Telephone / F2F / Assessment / WebEx/Ms Teams)": "F2F",
    "Any additional information to be communicated to Candidates": "null",
    "Travel expenses: Yes / No (if yes, please provide us with cost centre)": "No",
    "Cost Centre": "null",
    "Additional Comment": "null",
    "Not sure + info": "I'm not sure about..."
}}
user message:
"
{human_input}
"
###
your json formatted message:
"""
prompt = PromptTemplate(
    input_variables=["human_input"], 
    template=template
)

llm_chain = LLMChain(
    llm=llm, 
    prompt=prompt, 
    verbose=True
)

def create_reflection():
    try:
        response = llm_chain.predict(human_input=globalvars.excel_input_test)
        # Check if response is a string
        if isinstance(response, str):
            # Convert string to dictionary
            response = json.loads(response)
        # De-anonymize the response
        de_anonymized_response = de_anonymize_text(response)
        status_message = de_anonymized_response
        print(response)
    except Exception as e:
        status_message = {"status": "Failed to reflect conversation history", "error": str(e)}
    return status_message

if __name__ == "__main__":
    print(create_reflection())