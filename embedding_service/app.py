import os
os.environ['HF_ENDPOINT'] = "https://hf-mirror.com"

from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
import torch

app = FastAPI()

# Load model
device = "cuda" if torch.cuda.is_available() else "cpu"
# model = SentenceTransformer("moka-ai/m3e-large").to(device)
# model = SentenceTransformer("moka-ai/m3e-large")
model = SentenceTransformer("BAAI/bge-large-zh-v1.5").to(device)
# model = SentenceTransformer("BAAI/bge-large-zh-v1.5").to("cpu")


@app.post("/embed/")
async def embed_text(text: str):
    embedding = model.encode(text, convert_to_tensor=True).cpu().tolist()
    return {"embedding": embedding}

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
