from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import openai
from dotenv import load_dotenv
import os
import json
import requests
import zipfile
import logging

# Load environment variables (assuming you have an .env file with your OpenAI API key)
load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

logger = logging.getLogger("flask-app")

# Define file paths

current_dir = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(current_dir, "../chroma/fina3001_faq_db")
upper_dir = os.path.join(current_dir, "..")

# Function to load the FAQ JSON data
def load_faq_json_from_chroma_path():
    if os.path.exists(CHROMA_PATH):
        logger.info(f"Loading FAQ data from {CHROMA_PATH}...")
        with open(CHROMA_PATH, 'r', encoding='utf-8') as file:
            faq_data = json.load(file)
        return faq_data
    else:
        logger.info(f"{CHROMA_PATH} does not exist. Proceeding to download.")
        try:
            download_github_release_zip()
            with open(CHROMA_PATH, 'r', encoding='utf-8') as file:
                faq_data = json.load(file)
            return faq_data
        except Exception as e:
            logger.info(f"Fail to download from github release: {e}")
            return None
    
def download_github_release_zip(url="https://github.com/Nester-Chik/fina-demo/releases/download/v1.0.241028/chroma.zip", zip_filename="chroma.zip"):
    response = requests.get(url)
    
    if response.status_code == 200:
        # Write the zip file to the output directory
        with open(zip_filename, 'wb') as file:
            file.write(response.content)

        # Extract the zip file
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall(upper_dir)
        logger.info(f"Extracted zip file contents from github.")
    else:
        logger.info(f"Failed to download file: Status code {response.status_code}")

def create_faq_chroma_db(faq_data):
    # Set up the specific directory for this Chroma DB
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Initialize an empty list to store Document objects
    faq_documents = []
    
    # Process each FAQ entry in the parsed data
    for faq in faq_data:
        # Create a description by combining the question and answer
        faq_description = f"Q: {faq['question']}\nA: {faq['answer']}"
        
        # Create a Document object for each entry
        document = Document(page_content=faq_description, metadata={
            "question": faq['question'],
            "answer": faq['answer']
        })
        faq_documents.append(document)

    # Create Chroma DB and add all documents in the specific directory
    db = Chroma.from_documents(
        documents=faq_documents, 
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    
    logger.info(f"Saved {len(faq_documents)} FAQ vectors to Chroma DB at {CHROMA_PATH}.")

def query_faq(user_question):
    if not os.path.exists(CHROMA_PATH):
        raise FileNotFoundError("Chroma path does not exist.")
    # Load the ChromaDB
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    
    # Query the ChromaDB to find the closest matching FAQs
    results = db.similarity_search_with_relevance_scores(user_question, k=3)

    output = []

    # Display the closest FAQ results
    for i, (document, score) in enumerate(results):
        output.append({
            "relevance_score": round(score, 2),
            "question": document.metadata['question'],
            "answer": document.metadata['answer']
        })
    
    return output

# Example usage
if __name__ == "__main__":
    # Step 1: Parse the markdown file into question-answer pairs
    faq_data = load_faq_json_from_chroma_path("FAQ.json")

    if faq_data:
        # Step 2: Create Chroma DB with FAQ data
        # create_faq_chroma_db(faq_data)

        # Step 3: Query the database with a sample question
        query_faq("Can I join the same competition to earn more points?")

    else:
        logger.info("Failed to load the chroma db. Task aborted.")
