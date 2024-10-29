from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from typing import Optional, Literal
import openai
import os
import json
import logging
from dotenv import load_dotenv
from chatbot.rag import query_faq

# Retrieve the logger that was created in the app's __init__.py
logger = logging.getLogger("flask-app")

# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()
#---- Set OpenAI API key 
# Change environment variable name from "OPENAI_API_KEY" to the name given in 
# your .env file.

openai.api_key = os.environ['OPENAI_API_KEY']

# Initialize the LLM (GPT model)
template = """
You are an online assistance at Hong Kong University of Science and Technology (HKUST).
Students will ask questions about a new course, FINA3001, and you will answer their inquiries with relevant information.

Question:
{query}

Below are relevant information from the website FAQ.
{faq_result}

{instruction}
"""

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_chain = PromptTemplate.from_template(template) | llm

def invoke_bot(user_query: str) -> str:    
    # first do vector search
    faq_data = query_faq(user_query)
    faq_result = "\n\n".join([f"Relevance score: {qa_pair['relevance_score']}\nQ: {qa_pair['question']}\nA: {qa_pair['answer']}" for qa_pair in faq_data])

    if all(qa_pair["relevance_score"] < 0.5 for qa_pair in faq_data):
        instruction = "None of the FAQs above solve the user query. Please suggest the user to contact the faculty office for further inquiries."
    else:
        instruction = "Based on the FAQs above, solve the inquiry for the student."
    
    result = llm_chain.invoke({"query": user_query, "faq_result": faq_result, "instruction": instruction})

    return result.content

if __name__ == "__main__":
    result = invoke_bot("What is the weather today?")
    print(result)