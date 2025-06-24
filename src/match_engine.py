def simple_match(borrower, lender, verbose=False):
    score = 0
    matched = []

    def match(field_b, field_l):
        return (
            field_b == field_l
            or field_b in str(field_l).split(",")
            or field_l in str(field_b).split(",")
            or "No preference" in (field_b, field_l)
            or "Other" in (field_b, field_l)
        )

    fields = ["industry", "purpose", "country", "loan_amount", "currency", "loan_term", "payback_method"]
    for field in fields:
        if match(borrower.get(field, ""), lender.get(field, "")):
            score += 1
            matched.append(field)

    return (score, matched) if verbose else (score, [])

def matched_fields(borrower, lender):
    """Returns a list of fields where borrower and lender match."""
    fields = ['industry', 'purpose', 'country', 'loan_term', 'payback_method']
    matched = []
    for field in fields:
        if borrower.get(field) == lender.get(field):
            matched.append(field)
    return matched
