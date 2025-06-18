def simple_match(borrower, lender, verbose=False):
    score = 0
    details = []

    def match_or_no_preference(val1, val2):
        return val1 == "No preference" or val2 == "No preference" or val1 == val2

    if match_or_no_preference(borrower["industry"], lender["industry"]):
        score += 1
        details.append("industry")

    if match_or_no_preference(borrower["purpose"], lender["purpose"]):
        score += 1
        details.append("purpose")

    if match_or_no_preference(borrower["country"], lender["country"]):
        score += 1
        details.append("country")

    try:
        if abs(float(borrower["loan_amount"]) - float(lender["loan_amount"])) / float(borrower["loan_amount"]) <= 0.1:
            score += 1
            details.append("loan_amount")
    except (ValueError, ZeroDivisionError, TypeError):
        pass

    if borrower["currency"] == lender["currency"]:
        score += 1
        details.append("currency")

    try:
        if abs(int(borrower["loan_term"]) - int(lender["loan_term"])) <= 6:
            score += 1
            details.append("loan_term")
    except:
        pass

    if match_or_no_preference(borrower["payback_method"], lender["payback_method"]):
        score += 1
        details.append("payback_method")

    if verbose:
        print(f"Matching borrower {borrower.get('id')} with lender {lender.get('id')} → Score: {score}")

    return score, details


