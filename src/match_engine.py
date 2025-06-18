def simple_match(borrower, lender):
    score = 0
    details = []

    if borrower["industry"] in lender["industries"]:
        score += 1
        details.append("industry")
    if borrower["purpose"] == lender["purpose"]:
        score += 1
        details.append("purpose")
    if borrower["country"] == lender["country"]:
        score += 1
        details.append("country")
    if abs(borrower["loan_amount"] - lender["loan_amount"]) / borrower["loan_amount"] <= 0.1:
        score += 1
        details.append("loan_amount")
    if borrower["currency"] == lender["currency"]:
        score += 1
        details.append("currency")
    if abs(borrower["loan_term"] - lender["loan_term"]) <= 6:
        score += 1
        details.append("loan_term")
    if borrower["payback_method"] == lender["payback_method"]:
        score += 1
        details.append("payback_method")

    return score, details

