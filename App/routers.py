from fastapi import FastAPI
from pydantic import BaseModel
from prompt import gerar_resposta

app = FastAPI(title="API Assistente IA RAG")


class QueryRequest(BaseModel):
    pergunta: str

@app.post("/pergunta")
async def responder_pergunta(request: QueryRequest):
    ask = request.pergunta
    resposta = gerar_resposta(ask)
    return {"pergunta": ask, "resposta": resposta}
