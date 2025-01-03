from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, get_db
from models import Document
import os
import shutil

import models
from utils import extract_text_from_pdf
from langchain.chains import RetrievalQA

from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIRECTORY = "./uploaded_files/"

@app.get("/")
def read_root():
    return {"Hello": "World"}

# from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
# from sqlalchemy.orm import Session
# from database import SessionLocal
# import os
# import shutil
# from models import Document  # Assuming you have a Document model
# from utils import extract_text_from_pdf

# app = FastAPI()
# UPLOAD_DIRECTORY = "./uploaded_files/"

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are allowed.")

    # Create the upload directory if it doesn't exist
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    # Generate a unique filename to avoid conflicts
    unique_filename = f"{int(datetime.utcnow().timestamp())}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)

    # Save the uploaded file locally
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Store file information in the database
    new_document = Document(filename=unique_filename, file_path=file_path)
    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return {
        "message": "File uploaded successfully",
        "file_id": new_document.id,
        "path": new_document.file_path
    }


from pydantic import BaseModel
# from database import SessionLocal,  extract_text_from_pdf, CharacterTextSplitter, FAISS, RetrievalQA

# Define the Pydantic model for request body
class AskRequest(BaseModel):
    document_id: int
    question: str


from langchain.embeddings import OpenAIEmbeddings  # or HuggingFaceEmbeddings

# @app.post("/ask")
# async def ask_question(request: AskRequest, db: Session = Depends(get_db)):
#     # Fetch document from the database
#     document = db.query(Document).filter(Document.id == request.document_id).first()
#     if not document:
#         raise HTTPException(status_code=404, detail="Document not found.")

#     # Extract text from the PDF
#     text_content = extract_text_from_pdf(document.file_path)
#     text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
#     chunks = text_splitter.split_text(text_content)

#     # Initialize the embedding model
#     embedding_model = OpenAIEmbeddings()  # or HuggingFaceEmbeddings()

#     # Create a vectorstore and chain
#     vectorstore = FAISS.from_texts(chunks, embedding_model)
#     qa_chain = RetrievalQA(vectorstore=vectorstore)

#     # Process the question
#     answer = qa_chain.run(request.question)
#     return {"question": request.question, "answer": answer}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.post("/ask")
# async def ask_question(request: AskRequest, db: Session = Depends(get_db)):
#     # Fetch document from the database
#     document = db.query(Document).filter(Document.id == request.document_id).first()
#     if not document:
#         raise HTTPException(status_code=404, detail="Document not found.")

#     # Extract text from the PDF
#     try:
#         text_content = extract_text_from_pdf(document.file_path)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error extracting text: {e}")

#     # Chunk the text
#     text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
#     chunks = text_splitter.split_text(text_content)

#     # Initialize embedding model
#     embedding_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

#     # Create vectorstore and chain
#     vectorstore = FAISS.from_texts(chunks, embedding_model)
#     qa_chain = RetrievalQA.from_chain_type(llm=embedding_model, retriever=vectorstore.as_retriever())

#     # Process the question
#     try:
#         answer = qa_chain.run(request.question)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing question: {e}")

#     return {"question": request.question, "answer": answer}

import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class GeminiEmbeddings:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")  # Adjust model name if necessary

    def embed_documents(self, texts):
        embeddings = []
        for text in texts:
            response = self.model.embed_text(text=text)
            embeddings.append(response.vector)  # Assume `vector` is the embedding key in the response
        return embeddings



@app.post("/ask")
async def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    # Fetch document from the database
    document = db.query(Document).filter(Document.id == request.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Extract text from the PDF
    try:
        text_content = extract_text_from_pdf(document.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text: {e}")

    # Chunk the text (optional, if needed)
    text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=200)  # Adjust chunk size for Gemini
    chunks = text_splitter.split_text(text_content)

    # Use Gemini for direct question-answering
    try:
        # Configure Gemini API
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Initialize the generative model
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Concatenate chunks if necessary
        combined_text = "\n".join(chunks)

        # Generate a response from Gemini
        response = model.generate_content(f"Based on the following text, answer the question: '{request.question}'\n\n{combined_text}")

        # Access the response text
        answer = response.text  # Adjust if response structure differs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question with Gemini: {e}")

    return {"question": request.question, "answer": answer}
