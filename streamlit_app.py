from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd
import os
import random
import numpy as np
import pickle
import hashlib
from src.data_loader import load_borrowers, load_lenders, save_message, load_messages
from src.match_engine import simple_match, matched_fields
from src.text_matcher import embed_text_list, compute_similarity_matrix

# ========== Session State Initialization ==========
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "selected" not in st.session_state:
    st.session_state.selected = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "mode" not in st.session_state:
    st.session_state.mode = None

# ========== Access Section ==========
if not st.session_state.logged_in:
    st.title("🔐 CapitalConnect Platform Access")
    st.session_state.mode = st.radio("Choose Access Mode:", ["User", "Admin"])

    borrowers_df = load_borrowers()
    lenders_df = load_lenders()

    if st.session_state.mode == "Admin":
        password = st.text_input("Enter Admin Password", type="password")
        if st.button("Enter Admin Area"):
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            correct_hash = hashlib.sha256("mvpfintechmodels".encode()).hexdigest()
            if hashed_password == correct_hash:
                st.success("Admin access granted.")
                st.session_state.logged_in = True
            else:
                st.error("Incorrect password.")

    else:
        user_action = st.radio("Are you logging in or joining as a new user?", ["Login", "Join"])
        user_type = st.radio("User Type", ["Borrower", "Lender"])

        if user_action == "Login":
            login_id = st.text_input("Enter your ID")
            if st.button("Log In"):
                if user_type == "Borrower":
                    match = borrowers_df[borrowers_df['id'] == login_id]
                    if not match.empty:
                        st.session_state.selected = match.iloc[0].to_dict()
                        st.session_state.user_role = "Borrower"
                        st.session_state.logged_in = True
                    else:
                        st.error("Borrower ID not found.")
                else:
                    match = lenders_df[lenders_df['id'] == login_id]
                    if not match.empty:
                        st.session_state.selected = match.iloc[0].to_dict()
                        st.session_state.user_role = "Lender"
                        st.session_state.logged_in = True
                    else:
                        st.error("Lender ID not found.")

        elif user_action == "Join":
            st.sidebar.header("Fill in your profile")
            industries = ["Technology", "Retail", "Finance", "Agriculture", "Healthcare", "Transport"]
            purposes = ["Inventory", "Expansion", "R&D", "Growth", "Working capital"]
            countries = ["Netherlands", "Germany", "France", "Spain", "Italy"]
            methods = ["Interest", "Amortized", "Balloon Payment", "Revenue Share", "Equity"]

            industry = st.sidebar.selectbox("Industry", industries)
            purpose = st.sidebar.selectbox("Purpose", purposes)
            country = st.sidebar.selectbox("Country", countries)
            loan_amount = st.sidebar.number_input("Loan Amount (EUR)", 100, 5_000_000, step=1000)
            loan_term = st.sidebar.selectbox("Loan Term (months)", [12, 24, 36])
            payback_method = st.sidebar.selectbox("Payback Method", methods)
            description = st.sidebar.text_area("Description", height=100)
            currency = "EUR"

            if user_type == "Borrower":
                product_type = st.sidebar.text_input("Product Type")
                interest_rate = st.sidebar.number_input("Interest Rate (%)", 0.1, 20.0, step=0.1)

                if st.sidebar.button("Join as Borrower"):
                    borrower_id = f"B{random.randint(10000, 99999)}"
                    new_borrower = {
                        "id": borrower_id, "industry": industry, "product_type": product_type,
                        "purpose": purpose, "country": country, "loan_amount": loan_amount,
                        "currency": currency, "loan_term": loan_term, "payback_method": payback_method,
                        "interest_rate": interest_rate, "description": description
                    }
                    borrowers_df = pd.concat([borrowers_df, pd.DataFrame([new_borrower])], ignore_index=True)
                    borrowers_df.to_csv("data/sample_borrowers.csv", index=False)
                    st.success(f"Registered as Borrower. Your ID is {borrower_id}.")
                    st.session_state.selected = new_borrower
                    st.session_state.user_role = "Borrower"
                    st.session_state.logged_in = True

            else:
                if st.sidebar.button("Join as Lender"):
                    lender_id = f"L{random.randint(10000, 99999)}"
                    new_lender = {
                        "id": lender_id, "industry": industry, "purpose": purpose, "country": country,
                        "loan_amount": loan_amount, "currency": currency, "loan_term": loan_term,
                        "payback_method": payback_method, "description": description
                    }
                    lenders_df = pd.concat([lenders_df, pd.DataFrame([new_lender])], ignore_index=True)
                    lenders_df.to_csv("data/sample_lenders.csv", index=False)
                    st.success(f"Registered as Lender. Your ID is {lender_id}.")
                    st.session_state.selected = new_lender
                    st.session_state.user_role = "Lender"
                    st.session_state.logged_in = True

# ========== Exit if Not Logged In ==========
if not st.session_state.logged_in:
    st.stop()

# ========== Log Out Button ==========
st.sidebar.markdown("---")
if st.sidebar.button("🔓 Log Out"):
    st.session_state.clear()
    st.rerun()

# ========== Embedding & Matching ==========
borrowers_df = load_borrowers()
lenders_df = load_lenders()
selected = st.session_state.selected
user_role = st.session_state.user_role
mode = st.session_state.mode

cache_file = "data/cached_embeddings.pkl"
if os.path.exists(cache_file):
    with open(cache_file, "rb") as f:
        cache = pickle.load(f)
else:
    cache = {}

borrower_desc = borrowers_df['description'].tolist()
lender_desc = lenders_df['description'].tolist()
cache_key = hash("".join(borrower_desc) + "".join(lender_desc))

if cache.get("key") == cache_key:
    borrower_embeddings, lender_embeddings, similarity_matrix = cache["borrower"], cache["lender"], cache["sim"]
else:
    borrower_embeddings = embed_text_list(borrower_desc)
    lender_embeddings = embed_text_list(lender_desc)
    similarity_matrix = compute_similarity_matrix(borrower_embeddings, lender_embeddings)
    cache = {"key": cache_key, "borrower": borrower_embeddings, "lender": lender_embeddings, "sim": similarity_matrix}
    with open(cache_file, "wb") as f:
        pickle.dump(cache, f)

# ========== Matching Logic ==========
match_mode = user_role if mode == "User" else st.radio("Perspective", ["Borrower", "Lender"])
st.subheader("🔍 Profile Matching")
alpha = st.slider("Alpha: Weight for Text Similarity", 0.0, 1.0, 0.5, step=0.05)

if match_mode == "Borrower":
    if mode == "Admin":
        selected_id = st.selectbox("Select Borrower ID", borrowers_df['id'].unique())
        selected = borrowers_df[borrowers_df['id'] == selected_id].iloc[0].to_dict()
    st.markdown(f"**Description:** {selected['description']}")

    sem_scores = similarity_matrix[borrowers_df[borrowers_df['id'] == selected['id']].index[0]]
    struct_scores = [simple_match(selected, lender)[0] for _, lender in lenders_df.iterrows()]

    struct_scores = np.array(struct_scores)
    struct_scores_norm = struct_scores / struct_scores.max() if struct_scores.max() else struct_scores
    sem_scores_norm = sem_scores / sem_scores.max() if sem_scores.max() else sem_scores
    combined = (1 - alpha) * struct_scores_norm + alpha * sem_scores_norm

    matches = list(zip(lenders_df['id'], struct_scores, sem_scores, combined))
    matches.sort(key=lambda x: -x[3])

    st.write("### 🔗 Top Matches")
    for lid, s, t, c in matches[:3]:
        lender = lenders_df[lenders_df['id'] == lid].iloc[0]
        explanation = matched_fields(selected, lender)
        st.markdown(f"**Lender {lid}**")
        st.markdown(f"- 🧮 Combined Score: **{c:.2f}**, 📊 Structured: {s:.2f}, 📜 Text: {t:.2f}")
        st.markdown(f"- **Matched Fields:** {' | '.join(explanation)}")
        st.markdown(f"- **Description**: {lender['description']}")

        with st.expander(f"📩 Contact Lender {lid}"):
            message = st.text_area(f"Write message to {lid}", key=f"msg_{lid}")
            if st.button(f"Send to {lid}", key=f"send_{lid}"):
                save_message(sender_id=selected['id'], receiver_id=lid, message=message)
                st.success("Message sent!")

elif match_mode == "Lender":
    if mode == "Admin":
        selected_id = st.selectbox("Select Lender ID", lenders_df['id'].unique())
        selected = lenders_df[lenders_df['id'] == selected_id].iloc[0].to_dict()
    st.markdown(f"**Description:** {selected['description']}")

    sem_scores = similarity_matrix[:, lenders_df[lenders_df['id'] == selected['id']].index[0]]
    struct_scores = [simple_match(borrower, selected)[0] for _, borrower in borrowers_df.iterrows()]

    struct_scores = np.array(struct_scores)
    struct_scores_norm = struct_scores / struct_scores.max() if struct_scores.max() else struct_scores
    sem_scores_norm = sem_scores / sem_scores.max() if sem_scores.max() else sem_scores
    combined = (1 - alpha) * struct_scores_norm + alpha * sem_scores_norm

    matches = list(zip(borrowers_df['id'], struct_scores, sem_scores, combined))
    matches.sort(key=lambda x: -x[3])

    st.write("### 🔗 Top Matches")
    for bid, s, t, c in matches[:3]:
        borrower = borrowers_df[borrowers_df['id'] == bid].iloc[0]
        explanation = matched_fields(borrower, selected)
        st.markdown(f"**Borrower {bid}**")
        st.markdown(f"- 🧮 Combined Score: **{c:.2f}**, 📊 Structured: {s:.2f}, 📜 Text: {t:.2f}")
        st.markdown(f"- **Matched Fields:** {' | '.join(explanation)}")
        st.markdown(f"- **Description**: {borrower['description']}")

        with st.expander(f"📩 Contact Borrower {bid}"):
            message = st.text_area(f"Write message to {bid}", key=f"msg_{bid}")
            if st.button(f"Send to {bid}", key=f"send_{bid}"):
                save_message(sender_id=selected['id'], receiver_id=lid, message=message)
                st.success("Message sent!")

# ========== Suggestion Section Based on Match Mode ==========
st.markdown("---")
if match_mode == "Borrower":
    st.write("## 💸 Investor Suggestion")
    need = selected['loan_amount']
    match_df = pd.DataFrame(matches, columns=["id", "struct", "text", "combined"])
    match_df = match_df.merge(lenders_df[['id', 'loan_amount']], on="id").sort_values("combined", ascending=False)

    picks = []
    total = 0
    for _, row in match_df.iterrows():
        if total >= need:
            break
        amt = min(row['loan_amount'], need - total)
        picks.append((row['id'], amt, row['combined']))
        total += amt

    st.write(f"Suggested Investors to Fulfill €{need:,}")
    for lid, amt, score in picks:
        st.markdown(f"- Lender {lid}: €{amt:,} (match score: {score:.2f})")

elif match_mode == "Lender":
    st.write("## 📊 Diversification Portfolio Suggestion")
    budget = selected['loan_amount']
    match_df = pd.DataFrame(matches, columns=["id", "struct", "text", "combined"])
    match_df = match_df.merge(borrowers_df[['id', 'loan_amount']], on="id").sort_values("combined", ascending=False)

    picks = []
    spent = 0
    for _, row in match_df.iterrows():
        if spent >= budget:
            break
        amt = min(row['loan_amount'], budget - spent)
        picks.append((row['id'], amt, row['combined']))
        spent += amt

    st.write(f"Suggested Borrowers for €{budget:,} Investment")
    for bid, amt, score in picks:
        st.markdown(f"- Borrower {bid}: €{amt:,} (match score: {score:.2f})")

# ========== Messages Received ==========
st.markdown("---")
st.subheader("📬 Messages Received")
user_id = selected['id']
all_messages = load_messages(selected['id'])
received_msgs = [m for m in all_messages if m['to'] == user_id]

if received_msgs:
    for msg in received_msgs:
        st.markdown(f"- From {msg['from']}: {msg['content']}")
else:
    st.info("No messages yet.")


