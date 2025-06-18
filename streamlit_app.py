import streamlit as st
import pandas as pd
import numpy as np
import uuid
from src.data_loader import load_borrowers, load_lenders
from src.match_engine import simple_match
from src.text_matcher import embed_text_list, compute_similarity_matrix

st.title("🤝 CapitalConnect Matching Platform")
st.sidebar.header("Upload or Enter Data")

input_mode = st.sidebar.radio("📅 Input Mode", ["Upload CSV", "Manual Entry"])

uploaded_borrowers = st.sidebar.file_uploader("Upload Borrower CSV", type="csv", key="borrowers_csv")
uploaded_lenders = st.sidebar.file_uploader("Upload Lender CSV", type="csv", key="lenders_csv")

borrowers_df = load_borrowers()
lenders_df = load_lenders()

if uploaded_borrowers is not None:
    borrowers_df = pd.read_csv(uploaded_borrowers)
if uploaded_lenders is not None:
    lenders_df = pd.read_csv(uploaded_lenders)

if input_mode == "Manual Entry":
    user_type = st.sidebar.radio("User Type", ["Borrower", "Lender"])

    if user_type == "Borrower":
        st.sidebar.markdown("### 💪 Loan Details")
        industry = st.sidebar.selectbox("Industry", ["Technology", "Retail", "Finance", "Agriculture", "Other"])
        product_type = st.sidebar.text_input("Product Type")
        purpose = st.sidebar.selectbox("Purpose of Loan", ["No preference", "Inventory", "Expansion", "R&D"])
        country = st.sidebar.selectbox("Registered Country", ["Germany", "Netherlands", "France", "Spain"])
        loan_amount = st.sidebar.number_input("Loan Amount (EUR)", min_value=10000, max_value=5000000, step=10000)
        currency = "EUR"
        loan_term = st.sidebar.selectbox("Loan Term (months)", [12, 24, 36])
        payback_method = st.sidebar.selectbox("Payback Method", ["Interest", "Amortized"])
        interest_rate = st.sidebar.number_input("Interest Rate (%)", min_value=0.1, max_value=20.0, step=0.1)
        description = st.sidebar.text_area("Borrower Description", height=100)

        borrower_id = f"B{np.random.randint(10000, 99999)}"

        new_borrower = {
            "id": borrower_id,
            "industry": industry,
            "product_type": product_type,
            "purpose": purpose,
            "country": country,
            "loan_amount": loan_amount,
            "currency": currency,
            "loan_term": loan_term,
            "payback_method": payback_method,
            "interest_rate": interest_rate,
            "description": description
        }

        if st.sidebar.button("➕ Add Borrower"):
            borrowers_df = pd.concat([borrowers_df, pd.DataFrame([new_borrower])], ignore_index=True)
            borrowers_df.to_csv("data/sample_borrowers.csv", index=False)
            st.success(f"Borrower {borrower_id} added!")

    elif user_type == "Lender":
        lender_id = f"L{np.random.randint(10000, 99999)}"

        new_lender = {
            "id": lender_id,
            "industry": st.sidebar.selectbox("Industry Preference", ["No preference", "Technology", "Retail", "Finance", "Agriculture", "Transport", "Healthcare"]),
            "purpose": st.sidebar.selectbox("Purpose of Loan", ["No preference", "Inventory", "Expansion", "R&D", "Growth", "Working capital"]),
            "country": st.sidebar.selectbox("Target Country", ["Germany", "Netherlands", "France", "Spain", "UK"]),
            "loan_amount": st.sidebar.number_input("Target Loan Amount (EUR)", min_value=10000, max_value=5000000, step=10000),
            "currency": "EUR",
            "loan_term": st.sidebar.selectbox("Target Loan Term (months)", [12, 24, 36]),
            "payback_method": st.sidebar.selectbox("Preferred Payback Method", ["Interest", "Amortized"]),
            "description": st.sidebar.text_area("Lender Description", height=100)
        }

        if st.sidebar.button("➕ Add Lender"):
            lenders_df = pd.concat([lenders_df, pd.DataFrame([new_lender])], ignore_index=True)
            lenders_df.to_csv("data/sample_lenders.csv", index=False)
            st.success(f"Lender {lender_id} added!")

# -- Match Selection and Score Computation --
st.subheader("🔍 Profile Matching")
match_mode = st.radio("Perspective", ["Borrower", "Lender"])
alpha = st.slider("Alpha: Weight for Text Similarity", 0.0, 1.0, 0.5, step=0.05)

borrower_texts = borrowers_df['description'].tolist()
lender_texts = lenders_df['description'].tolist()

borrower_embeddings = embed_text_list(borrower_texts)
lender_embeddings = embed_text_list(lender_texts)
similarity_matrix = compute_similarity_matrix(borrower_embeddings, lender_embeddings)

if match_mode == "Borrower":
    borrower_id = st.selectbox("Select Borrower ID", borrowers_df['id'].unique())
    selected = borrowers_df[borrowers_df['id'] == borrower_id].iloc[0]
    st.markdown(f"**Description:** {selected['description']}")

    semantic_scores = similarity_matrix[borrowers_df[borrowers_df['id'] == borrower_id].index[0]]
    struct_scores = []
    for _, lender in lenders_df.iterrows():
        score, _ = simple_match(selected, lender)
        struct_scores.append(score)

    struct_scores = np.array(struct_scores)
    struct_scores_norm = struct_scores / struct_scores.max() if struct_scores.max() else struct_scores
    sem_scores_norm = semantic_scores / semantic_scores.max() if semantic_scores.max() else semantic_scores
    combined = (1 - alpha) * struct_scores_norm + alpha * sem_scores_norm

    matches = list(zip(lenders_df['id'], struct_scores, semantic_scores, combined))
    matches.sort(key=lambda x: -x[3])

    st.write("### 🔗 Top Combined Matches:")
    for lid, ss, ts, cs in matches[:3]:
        st.markdown(f"- Lender {lid} | Structured: {ss:.2f}, Text: {ts:.2f}, Combined: **{cs:.2f}**")

elif match_mode == "Lender":
    lender_id = st.selectbox("Select Lender ID", lenders_df['id'].unique())
    selected = lenders_df[lenders_df['id'] == lender_id].iloc[0]
    st.markdown(f"**Description:** {selected['description']}")

    semantic_scores = similarity_matrix[:, lenders_df[lenders_df['id'] == lender_id].index[0]]
    struct_scores = []
    for _, borrower in borrowers_df.iterrows():
        score, _ = simple_match(borrower, selected)
        struct_scores.append(score)

    struct_scores = np.array(struct_scores)
    struct_scores_norm = struct_scores / struct_scores.max() if struct_scores.max() else struct_scores
    sem_scores_norm = semantic_scores / semantic_scores.max() if semantic_scores.max() else semantic_scores
    combined = (1 - alpha) * struct_scores_norm + alpha * sem_scores_norm

    matches = list(zip(borrowers_df['id'], struct_scores, semantic_scores, combined))
    matches.sort(key=lambda x: -x[3])

    st.write("### 🔗 Top Combined Matches:")
    for bid, ss, ts, cs in matches[:3]:
        st.markdown(f"- Borrower {bid} | Structured: {ss:.2f}, Text: {ts:.2f}, Combined: **{cs:.2f}**")

# --- Diversification Suggestion ---
st.markdown("---")
st.write("## 💡 Diversification Portfolio Suggestion")

if match_mode == "Borrower":
    need = selected['loan_amount']
    match_df = pd.DataFrame(matches, columns=["id", "struct", "text", "combined"])
    match_df = match_df.merge(lenders_df[['id', 'loan_amount']], on="id")
    match_df = match_df.sort_values("combined", ascending=False)

    picks = []
    total = 0
    for _, row in match_df.iterrows():
        if total >= need:
            break
        amount = min(row['loan_amount'], need - total)
        picks.append((row['id'], amount, row['combined']))
        total += amount

    st.write(f"Suggested Lenders to Fulfill €{need:,}")
    for lid, amt, score in picks:
        st.markdown(f"- Lender {lid}: €{amt:,} (match score: {score:.2f})")

elif match_mode == "Lender":
    budget = selected['loan_amount']
    match_df = pd.DataFrame(matches, columns=["id", "struct", "text", "combined"])
    match_df = match_df.merge(borrowers_df[['id', 'loan_amount']], on="id")
    match_df = match_df.sort_values("combined", ascending=False)

    picks = []
    spent = 0
    for _, row in match_df.iterrows():
        if spent >= budget:
            break
        amount = min(row['loan_amount'], budget - spent)
        picks.append((row['id'], amount, row['combined']))
        spent += amount

    st.write(f"Suggested Borrowers for €{budget:,} Investment")
    for bid, amt, score in picks:
        st.markdown(f"- Borrower {bid}: €{amt:,} (match score: {score:.2f})")