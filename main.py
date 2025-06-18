from src.data_loader import load_borrowers, load_lenders
from src.match_engine import simple_match
from src.moderation import check_moderation


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

print("\n--- Moderation Filter Test ---")
example_text = "I want to fund a campaign to fuck people who disagree with my beliefs."

flagged, categories = check_moderation(example_text)

if flagged:
    print(f"⚠️ Text flagged for: {', '.join(categories)}")
else:
    print("✅ Text passed moderation.")