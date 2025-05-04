# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir chamadas do frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Porta do Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"message": "pong"}
