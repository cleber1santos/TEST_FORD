from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from gpt4all import GPT4All
import re
from unidecode import unidecode
from palavra_chave import palavras_chaves


llm = GPT4All(model_name="D:/TEST-FORD/models/Meta-Llama-3-8B-Instruct.Q4_0.gguf", device="cpu")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
db = Chroma(persist_directory="D:/TEST-FORD/DB_IA", embedding_function=embeddings)

padrao = r"Causas[:\-]?\s*(.*?)\s*Soluções[:\-]?\s*(.*?)\s*Manutenção preventiva[:\-]?\s*(.*?)(?:$|\n[A-Z])"

def format_resposta(texto: str) -> str:
    texto = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", texto)
    texto = texto.replace("\n", "<br>")  
    return texto

def gerar_resposta(ask: str) -> str:
    """
    Recebe uma pergunta, faz busca RAG e retorna resposta do GPT4All.
    """
    ask_norm = unidecode(ask.lower())

    
    keyword_found = None
    for chave, valor in palavras_chaves.items():
        if chave in ask_norm:
            keyword_found = valor
            break
    consulta = keyword_found if keyword_found else ask

   
    results = db.similarity_search_with_relevance_scores(ask, k=3)
    trechos_relevantes = []

    for item in results:
        if isinstance(item, tuple):
            doc = item[0]
        else:
            doc = item
        matches = re.findall(padrao, doc.page_content, flags=re.DOTALL | re.IGNORECASE)
        if matches:
            for match in matches:
                causas, solucoes, manutencao = match
                trechos_relevantes.append(
                    f"Causas: {causas.strip()}\nSoluções: {solucoes.strip()}\nManutenção preventiva: {manutencao.strip()}"
                )

    
    if not trechos_relevantes and results:
        contexto = "\n\n".join([doc.page_content for doc, _ in results])
    else:
        contexto = "\n\n".join(trechos_relevantes)

    prompt = f"Baseado no contexto abaixo, responda à pergunta de forma clara e objetiva.\n\nContexto:\n{contexto}\n\nPergunta: {ask}\nResposta:"

    
    resposta = llm.generate(prompt)
    return format_resposta(resposta)
