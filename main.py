from src.data_loader import load_borrowers, load_lenders
from src.match_engine import simple_match

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
