import openai
import os
import numpy as np
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

# ✅ This line must be AFTER load_dotenv
api_key = os.getenv("OPENAI_API_KEY")
print("Loaded API key starts with:", api_key[:10])
client = openai.OpenAI(api_key=api_key)

def get_embedding(text, model="text-embedding-3-small"):
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

def embed_text_list(texts):
    return [get_embedding(text) for text in texts]

def compute_similarity_matrix(embeddings_a, embeddings_b):
    return cosine_similarity(embeddings_a, embeddings_b)

