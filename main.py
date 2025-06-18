from dotenv import load_dotenv
load_dotenv()
import os
from src.data_loader import load_borrowers, load_lenders
from src.match_engine import simple_match
from src.moderation import check_moderation
from src.text_matcher import embed_text_list, compute_similarity_matrix
import pandas as pd


borrowers = load_borrowers()
lenders = load_lenders()

print("Borrower-Lender Matches:\n")

for _, borrower in borrowers.iterrows():
    print(f"Borrower {borrower['id']} best matches:")
    scores = []
    for _, lender in lenders.iterrows():
        score, details = simple_match(borrower, lender)
        scores.append((lender['id'], score, details))
    scores.sort(key=lambda x: -x[1])
    for match_id, score, details in scores[:3]:  # Top 3 matches
        print(f"  → Lender {match_id} (score: {score}) | Matched on: {', '.join(details)}")
    print()

print("\n============================")
print("Starting Semantic Matching")
print("============================\n")

# Load CSVs again
borrowers_df = borrowers.copy()
lenders_df = lenders.copy()

# Get descriptions
borrower_texts = borrowers_df['description'].fillna("").tolist()
lender_texts = lenders_df['description'].fillna("").tolist()

print("\n--- Embedding Descriptions ---")
borrower_embeddings = embed_text_list(borrower_texts)
lender_embeddings = embed_text_list(lender_texts)

print("\n--- Text Similarity Scores ---")
similarity_matrix = compute_similarity_matrix(borrower_embeddings, lender_embeddings)

# Display top matches
for i, borrower_id in enumerate(borrowers_df['id']):
    scores = similarity_matrix[i]
    top_indices = scores.argsort()[::-1][:3]
    print(f"\nBorrower {borrower_id} matches (by text):")
    for idx in top_indices:
        lender_id = lenders_df.iloc[idx]['id']
        print(f"  → Lender {lender_id} (similarity: {scores[idx]:.2f})")
