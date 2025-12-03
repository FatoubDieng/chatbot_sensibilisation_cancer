from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import requests
from langchain_community.vectorstores.faiss import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_URL = "http://localhost:1234/v1/chat/completions"
LLM_MODEL_NAME = "qwen2.5-7b-instruct"
FAISS_PATH = "faiss_index"


# Charger FAISS
embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
vector_store = FAISS.load_local(FAISS_PATH,embeddings=embedding_model,allow_dangerous_deserialization=True)

# Création de l’API avec FastAPI
app = FastAPI(
    title="Chatbot sensibilisation cancer API",
    description="Chatbot RAG pour sensibiliser au cancer.",
    version="1.0.0",
    docs_url="/docs"
)

class UserMessage(BaseModel):
    question: str
    
@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.post("/chat")
def chatbot_interaction(user_message: UserMessage):
    query = user_message.question


    # Récupérer les documents pertinents
    retrieved_docs = vector_store.similarity_search(query, k=3)
    if not retrieved_docs:
        return {"reponse": "Je suis désolée, je ne dispose pas d’informations sur ce sujet"
                            "Je suis spécialisée uniquement dans la sensibilisation au cancer. "
                            "Je ne peux pas répondre aux questions sur d’autres sujets. "
                            "Mais je peux t’aider concernant les dépistages, symptômes ou traitements des cancers."}

    # Sélectionner le meilleur document
    best_doc = retrieved_docs[0]
    document_source = best_doc.metadata.get("source", "Document inconnu")

    # Contexte de réponse
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    prompt = f"""Tu es FabiBot, une assistante spécialisée UNIQUEMENT dans:
- le cancer
- les symptômes
- la prévention
- le dépistage
- le soutien psychologique
- les structures de santé du Sénégal
- tu donnes toujours une reponse clair , courte et empathique
Ta mission est : experte en sensibilisation au cancer au Sénégal"
**Document analysé** : {document_source}
Toute question HORS cancer , tu réponds gentiment :
"Je suis là uniquement pour parler du cancer et de sa prévention.\n**Extrait du document** :{context}\n**Question utilisateur** :{query}\n**Réponse détaillée** :"""



    # Appel du modèle local via LM Studio
    payload = {
    "model": LLM_MODEL_NAME,
    "messages": [
        {"role": "system", "content": """"Tu es FabiBot, bienveillante et claire.tu donnes toujours une reponse clair , courte et empathique"""},

        {"role": "user", "content": prompt}
    ],
}

    response = requests.post(LLM_URL, json=payload)

    if response.status_code == 200:
        data = response.json()
        return {"reponse": data["choices"][0]["message"]["content"]}

    return {"reponse": "Erreur : LM Studio ne répond pas. Vérifie qu'un modèle est chargé."}
