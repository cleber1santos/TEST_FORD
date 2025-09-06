from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prompt import gerar_resposta

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
from langchain.schema import Document
from pathlib import Path
import os

app = FastAPI(title="API Assistente IA RAG")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

DB_PATH = Path("D:/TEST-FORD/DB_IA")
db = Chroma(
    persist_directory=str(DB_PATH),
    embedding_function=embeddings,
    collection_name="docs"  
)


UPLOAD_DIR = Path("D:/TEST-FORD/Base_docs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)



class QueryRequest(BaseModel):
    pergunta: str


@app.post("/pergunta")
async def responder_pergunta(request: QueryRequest):
    """
    Endpoint para fazer perguntas ao assistente.
    """
    ask = request.pergunta
    resposta = gerar_resposta(ask)
    return {"pergunta": ask, "resposta": resposta}


@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Endpoint para upload de PDF e adição ao banco vetorial.
    """
    try:
        
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(await file.read())

       
        reader = PdfReader(file_path)
        texto = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                texto += page_text + "\n"

        if not texto.strip():
            return {"status": "error", "message": "PDF não contém texto legível"}

        
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_text(texto)

        
        documentos = [
            Document(page_content=c, metadata={"source": file.filename}) for c in chunks
        ]
        db.add_documents(documentos)  

        return {"status": "ok", "message": f"{file.filename} adicionado ao banco vetorial"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
