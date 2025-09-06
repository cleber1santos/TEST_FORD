from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma.vectorstores import Chroma
import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

Docs_base = "Base_docs/"

def read_docs_ia():
    docs = []
    for filename in os.listdir(Docs_base):
        filepath = os.path.join(Docs_base, filename)
        ext = os.path.splitext(filename)[1].lower()

        if ext == ".pdf":
            loader = PyPDFLoader(filepath)
            docs.extend(loader.load())
        elif ext == ".txt":
            loader = TextLoader(filepath, encoding="utf8")
            docs.extend(loader.load())
        else:
            print(f"Atenção: arquivo {filename} com extensão {ext} não suportado")
    return docs

def chunking_ia(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=500,
        length_function=len,
    )
    chunks = text_splitter.split_documents(docs)
    print(f"Chunks gerados: {len(chunks)}")
    return chunks

def vectorstore_ia(chunks):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectordb = Chroma.from_documents(chunks, embeddings, persist_directory="DB_IA")  
    return vectordb

def Db_IA():
    read_docs = read_docs_ia()
    if not read_docs:
        print("Nenhum documento encontrado!")
        return
    chunks = chunking_ia(read_docs)
    vectordb = vectorstore_ia(chunks)
    print("Base de dados vetorial criada com sucesso!")

if __name__ == "__main__":
    Db_IA()
