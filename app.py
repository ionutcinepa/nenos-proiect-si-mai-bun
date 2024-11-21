from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main_chatbot import get_cohere_answer, get_nlp_cloud_answer, load_pdf_text, load_or_summarize_document
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Pydantic model for `/ask` endpoint
class QuestionRequest(BaseModel):
    question: str
    summary: str


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle PDF file upload and summarize its content."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())

        document_content = load_pdf_text(file_path)
        document_summary = load_or_summarize_document(document_content)

        return {"summary": document_summary}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process file: {str(e)}"
        )


@app.post("/ask")
async def ask_question(data: QuestionRequest):
    """Handle question answering based on the document summary."""
    try:
        cohere_answer = get_cohere_answer(data.question, data.summary)
        nlp_cloud_answer = get_nlp_cloud_answer(data.question, data.summary)
        return {
            "cohere_answer": cohere_answer,
            "nlp_cloud_answer": nlp_cloud_answer,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate answer: {str(e)}"
        )


@app.get("/summary")
async def get_summary():
    """Return the cached document summary."""
    try:
        cache_path = os.path.join(os.getcwd(), "../cached_summary.txt")
        # return {"path": cache_path}
        if not os.path.exists(cache_path):
            raise HTTPException(status_code=404, detail="No cached summary found")

        with open(cache_path, "r", encoding="utf-8") as file:
            summary = file.read()

        if not summary.strip():
            raise HTTPException(status_code=404, detail="Cached summary is empty")

        return {"summary": summary}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to load summary: {str(e)}"
        )
    

