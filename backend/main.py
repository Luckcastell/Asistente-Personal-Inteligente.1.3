from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings
from groq import Groq
import os, shutil
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

DB_DIR = "vector_db"
os.makedirs(DB_DIR, exist_ok=True)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

class ChatRequest(BaseModel):
    message: str

def add_pdf_to_vectorstore(file_path: str):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(documents)
    vectorstore.add_documents(chunks)
    vectorstore.persist()

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        add_pdf_to_vectorstore(file_path)
        return {"message": f"PDF '{file.filename}' cargado y agregado al índice."}
    except Exception as e:
        return {"error": str(e)}

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        results = vectorstore.similarity_search(req.message, k=3)
        context = "\n\n".join([doc.page_content for doc in results])

        prompt = f"""Eres Suriel, un asistente que responde SOLO con la información de la base de datos privada.
Si la respuesta no está en la base, responde "No tengo esa información".

Contexto relevante de la base de datos:
{context}

Pregunta: {req.message}
Respuesta:
"""

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "Eres Suriel, un asistente amable y servicial."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )

        reply = response.choices[0].message.content
        return {"reply": reply}

    except Exception as e:
        return {"reply": f"Error: {str(e)}"}
