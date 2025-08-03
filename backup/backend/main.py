from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv
import shutil

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

uploaded_files = []

class ChatRequest(BaseModel):
    message: str

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        os.makedirs("uploads", exist_ok=True)
        file_location = f"uploads/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        uploaded_files.append(file.filename)
        return {"message": f"PDF '{file.filename}' cargado correctamente"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        context = ""
        if uploaded_files:
            context = f"El usuario ha subido estos archivos PDF: {', '.join(uploaded_files)}.\nPuedes mencionarlos en la conversación, pero no puedes leerlos.\n"

        response = client.chat.completions.create(
            model="llama3-8b-8192",  # Modelo gratuito de Groq
            messages=[
                {"role": "system", "content": "Eres Suriel, un asistente amable y servicial."},
                {"role": "user", "content": context + request.message}
            ],
            temperature=0.7
        )

        
        reply = response.choices[0].message.content  
        return {"reply": reply}

    except Exception as e:
        return {"reply": f"Error: {str(e)}"}
