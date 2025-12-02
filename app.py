from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"status": "Space HF prêt pour ML !"}