from dotenv import load_dotenv
import os
import requests
import logging
import pdfplumber

env_path = os.path.join("/mnt/c/Users/developer/Desktop/proiect/my-app/backend", ".env")

# Load environment variables
load_dotenv(dotenv_path=env_path)
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
NLP_CLOUD_API_KEY = os.getenv("NLP_CLOUD_API_KEY")
NLP_CLOUD_MODEL = os.getenv("NLP_CLOUD_MODEL", "gpt-j")

print(f"Cohere API key: {COHERE_API_KEY}")
print(f"NLP CLOUD API key: {NLP_CLOUD_API_KEY}")

# Set up logging
logging.basicConfig(level=logging.INFO, filename="chatbot.log", filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")


# Load text from a PDF file
def load_pdf_text(file_path):
    if not os.path.exists(file_path):
        print(f"Error: PDF file not found at {file_path}")
        return ""
    
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        print("PDF loaded successfully.")
    except Exception as e:
        print(f"Error loading PDF: {e}")
    return text


# Summarize document with caching and real API call (using Cohere)
def load_or_summarize_document(text, retries=3, delay=10):
    # Explicitly set the cache file location in the root of the project
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    cache_path = os.path.join(project_root, "cached_summary.txt")

    print(f"Using cache path: {cache_path}")
    
    # Check if the cached summary already exists
    if os.path.exists(cache_path):
        print("Loading cached summary from existing file...")
        with open(cache_path, "r", encoding="utf-8") as file:
            return file.read()

    # If cache doesn't exist, save extracted text first and attempt summarization
    print("Cache not found. Attempting to save the extracted summary.")
    try:
        with open(cache_path, "w", encoding="utf-8") as file:
            # Save the extracted text as a fallback
            file.write(text[:1000])
        print("Fallback summary written to cache.")
    except Exception as e:
        print(f"Failed to write fallback cache file: {e}")

    # Attempt to generate a summary via Cohere API
    print("Attempting to generate a new summary via Cohere API.")
    headers = {"Authorization": f"Bearer {COHERE_API_KEY}"}
    summarization_data = {
        "model": "summarize-xlarge",
        "prompt": text[:1000],  # Limited input length for summarization
        "max_tokens": 200,
        "temperature": 0.3
    }

    try:
        summary_response = requests.post(
            "https://api.cohere.ai/generate",
            headers=headers,
            json=summarization_data
        )
        summary_response.raise_for_status()
        summary_text = summary_response.json()["text"]

        print("Writing Cohere summary to cache file...")
        with open(cache_path, "w", encoding="utf-8") as file:
            file.write(summary_text)
        print("Cache file created successfully with the real summary.")
        return summary_text
    except requests.exceptions.HTTPError as e:
        print(f"Error summarizing with Cohere: {e}")
        return text[:1000]  # Fallback summary if the API call fails


# Function to get an answer from NLP Cloud API using gpt-j
def get_nlp_cloud_answer(question, document_summary):
    # Check if document_summary is valid
    if not document_summary:
        print("No document summary available.")
        return "No document summary available to answer the question."

    # Truncate document_summary and question to avoid exceeding character limits
    if len(document_summary) > 4000:
        document_summary = document_summary[:4000]
    if len(question) > 500:
        question = question[:500]
    
    headers = {
        "Authorization": f"Token {NLP_CLOUD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prepare prompt for text generation
    prompt = f"{document_summary}\n\nQ: {question}\nA:"
    data = {
        "text": prompt,
        "min_length": 50,
        "max_length": 150
    }

    # Adjusted URL to use text-generation endpoint
    url = f"https://api.nlpcloud.io/v1/gpu/{NLP_CLOUD_MODEL}/generation"
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        answer = response_json.get("generated_text", "No answer available from NLP Cloud API.").strip()
        logging.info(f"NLP Cloud API Answer to '{question}': {answer}")
        return answer
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error accessing NLP Cloud API: {e}")
        print(f"Response content: {e.response.text}")
        return "No answer available from NLP Cloud API."


# Cohere answer function for alternative questions
def get_cohere_answer(question, document_summary):
    headers = {"Authorization": f"Bearer {COHERE_API_KEY}"}
    data = {
        "model": "command-medium-nightly",
        "prompt": f"Context: {document_summary}\nQuestion: {question}\nAnswer:",
        "max_tokens": 50,
        "temperature": 0.3
    }

    try:
        response = requests.post("https://api.cohere.ai/generate", headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        return response_json.get("text", "No answer available from Cohere API.").strip()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error accessing Cohere API: {e}")
        return "No answer available from Cohere API."
    except Exception as e:
        print(f"General error accessing Cohere API: {e}")
        return "No answer available from Cohere API."
