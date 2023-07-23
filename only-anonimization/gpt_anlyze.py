import os
import globalvars
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


load_dotenv()  # take environment variables from .env.
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model_name ='gpt-3.5-turbo-16k', temperature=0, max_tokens=8000)

# Define the prompt template
template = """based on email provided in user message answer the questions honestly. Lets think step by step. If you are not sure return 'null'
Based on given email:
###
1. From subject line exctract number started with 'JR...'
2. Request received always return 'null'
3. Find candidate number started with 'C...'. 
4. Find candidate names. (can be multiple names, in this case return as a array) 
5.  Based on the tone of this message, is recruitment internal or external? 
6. When is interview date?
7. Timeslot Start always return 'null'
8. Timeslot End always return 'null'
9. Is there any info about  duration of the interview?
10. is there any info about  Location/Venue (+ where Candidates need to report on arrivals)
11. Interviewers E-mails
12. Interviewers full name (you can scrap from email):
13. How many interviewers will be involved?
14. Is there any information about recruiter name?
15. Is there any information about hiring manager name?
16. Type of the interview (Telephone / F2F / Assessment / WebEx / MS Teams)
17. Any additional information to be communicated to Candidates?
18. Travel expenses: Yes / No (if yes, please provide us with cost centre)
19. Cost centre always return 'null'
20. Any important additional comment?
21. Here write things you are not sure about.
###
result should be in json and nothing more, be consist, no comments. If you are not 100% sure return 'null'
### example json structure ###
{{
    "Req number": "JR...",
    "Request Received": "null",
    "Candidate ref/application ref": "null",
    "Candidate name": ["Anastasia Sharapova", "Megan Laterlord", "Laura Bailey"],
    "External / Internal": "External",
    "Interview Date": ["22nd June - 12:00", "22nd June - 13:30", "23rd June - 10:00"],
    "Timeslot Start": "null",
    "Timeslot end": "null",
    "Duration of the interview": "1h",
    "Location/Venue (+ where Candidates need to report on arrivals)": "Poland, Warsaw",
    "Interviewers NAME": ["John Smith", "Dwight Shrute>"],
    "Interviewers E-mails": ["john.smith@gmail.com", "dwight.shrute@office.com"],
    "Number of extra Interviewers": 1,
    "Recruiter": "Mark Smith",
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
        status_message = response
    except Exception as e:
        status_message = {"status": "Failed to reflect conversation history", "error": str(e)}
    return status_message



if __name__ == "__main__":
    print(create_reflection())