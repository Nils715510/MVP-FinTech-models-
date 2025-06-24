from dotenv import load_dotenv
load_dotenv()
import os
import pickle
import hashlib
import numpy as np
from openai import OpenAI

# Initialize OpenAI client using environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY environment variable is not set.")
client = OpenAI(api_key=api_key)

CACHE_PATH = "data/cached_embeddings.pkl"

def _hash(text):
    return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()

def load_or_init_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "rb") as f:
            cache = pickle.load(f)
    else:
        cache = {"borrowers": {}, "lenders": {}}
    if "borrowers" not in cache:
        cache["borrowers"] = {}
    if "lenders" not in cache:
        cache["lenders"] = {}
    return cache

def embed_text_list(text_list):
    """Embeds a list of texts with caching for borrowers and lenders."""
    cache = load_or_init_cache()

    # Determine whether embeddings are for borrowers or lenders
    is_borrower = "borrower" in text_list[0].lower()
    section = "borrowers" if is_borrower else "lenders"

    embeddings = []
    updated = False

    for text in text_list:
        h = _hash(text)
        if h in cache[section]:
            embeddings.append(cache[section][h])
        else:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            emb = response.data[0].embedding
            cache[section][h] = emb
            embeddings.append(emb)
            updated = True

    if updated:
        with open(CACHE_PATH, "wb") as f:
            pickle.dump(cache, f)

    return np.array(embeddings)

def compute_similarity_matrix(borrower_embeddings, lender_embeddings):
    """Computes cosine similarity matrix between borrower and lender embeddings."""
    norm_b = borrower_embeddings / np.linalg.norm(borrower_embeddings, axis=1, keepdims=True)
    norm_l = lender_embeddings / np.linalg.norm(lender_embeddings, axis=1, keepdims=True)
    return norm_b @ norm_l.T
