def simple_match(borrower, lender):
    score = 0

    if borrower["industry"] in lender["industries"]:
        score += 1
    if borrower["purpose"] == lender["purpose"]:
        score += 1
    if borrower["country"] == lender["country"]:
        score += 1
    if abs(borrower["loan_amount"] - lender["loan_amount"]) / borrower["loan_amount"] <= 0.1:
        score += 1
    if borrower["currency"] == lender["currency"]:
        score += 1
    if abs(borrower["loan_term"] - lender["loan_term"]) <= 6:
        score += 1
    if borrower["payback_method"] == lender["payback_method"]:
        score += 1

    return score
