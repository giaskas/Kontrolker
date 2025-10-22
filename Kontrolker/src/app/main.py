# src/app/main.py
from fastapi import FastAPI

app = FastAPI(title="Kontrolker")

@app.get("/health")
def health():
    return {"status": "ok"}
