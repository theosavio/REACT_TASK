# backend/main.py

import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import torch

app = FastAPI()


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model_path = "distilbert-base-uncased-distilled-squad"
model = AutoModelForQuestionAnswering.from_pretrained(model_path).to(device)
tokenizer = AutoTokenizer.from_pretrained(model_path)
qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer, device=device)

vectorstore = None

def get_pdf_text(pdf_path):
    text = ""
    pdf_reader = PdfReader(pdf_path)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return text_splitter.split_text(text)

def create_faiss_vector_store(chunks):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v2")
    return FAISS.from_texts(texts=chunks, embedding=embeddings)

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    global vectorstore 
    if file.content_type != "application/pdf":
        return JSONResponse(status_code=400, content={"error": "Only PDF files are allowed."})

    file_path = f"./uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
   
    text = get_pdf_text(file_path)
    text_chunks = get_text_chunks(text)
    vectorstore = create_faiss_vector_store(text_chunks)
    
    response = {"file_name": file.filename, "message": "PDF uploaded and processed successfully."}
    return JSONResponse(content=response)

@app.post("/ask-question/")
async def ask_question(question: str = Form(...)):
    global vectorstore
    if vectorstore is None:
        return JSONResponse(status_code=400, content={"error": "No PDF uploaded yet."})
    
    # Retrieve relevant documents
    relevant_docs = vectorstore.similarity_search(question)
    context = " ".join([doc.page_content for doc in relevant_docs])
    
    # Get answer from the QA pipeline
    response = qa_pipeline({"question": question, "context": context})
    return {"answer": response["answer"]}

