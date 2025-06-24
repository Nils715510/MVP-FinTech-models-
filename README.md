# 💸 CapitalConnect

**CapitalConnect** is a next-generation peer-to-peer (P2P) investment platform that matches borrowers and lenders using both structured logic and cutting-edge large language models (LLMs). The app is built with **Python** and **Streamlit**, and leverages **OpenAI’s `text-embedding-3-small` model** to create a smarter, context-aware investment experience.

---

## 🚀 Features

- **🔐 User Access Control**: Choose between Admin and User modes (Borrower or Lender), with login and onboarding flows.
- **🧠 Hybrid Matching Engine**:
  - **Structured Matching**: Transparent rule-based matching on numeric and categorical fields (e.g., country, industry, payback method).
  - **LLM-Powered Matching**: Semantic similarity from borrower and lender descriptions via OpenAI embeddings and cosine similarity.
- **📊 Match Explanations**: Combined, structured, and semantic scores shown, along with matched categories and explanations.
- **📬 Messaging System**: Lenders and borrowers can message each other; all messages are stored and retrieved per profile.
- **📁 Cached Embeddings**: Speeds up load time using locally stored vectors for semantic similarity.
- **🤝 Diversification Suggestions**: Smart portfolio building for lenders to allocate their budget across multiple high-fit borrowers.
- **🧪 Admin Dashboard**: View any user, test matching logic, and monitor new entries.

---

## 🛠 Tech Stack

- **Language**: Python
- **Framework**: Streamlit
- **AI/ML**: OpenAI `text-embedding-3-small`
- **Data Storage**: CSV files (borrowers/lenders), JSON (messages), Pickle (embedding cache)

## Limitations & Future Work

- This is a concept version of the MVP; some features are still experimental.

- Real-time investing is not yet functional due to the absence of live users or capital flows.

- Future improvements may include:

    Wallet/budget management for lenders and investment tracking

    Risk scoring

    Enhanced moderation and onboarding UX

    Investor performance analytics


##  Why CapitalConnect?
CapitalConnect introduces a modern FinTech innovation by combining structured, explainable rules with LLM-powered semantic matching. This enables investors and borrowers to connect not just on numeric terms, but on vision, ethics, innovation, and intent — providing an edge over traditional P2P platforms that rely solely on credit scores and hard filters.
---

## 📦 Installation & Setup

### 1. Clone the repository


```bash

# 1. Clone the repo  

git clone https://github.com/Nils715510/MVP-FinTech-models-.git
cd MVP-FinTech-models-

# 2. Navigate into the project folder in your terminal

# Ensure you have Python 3.10+ and install dependencies:
pip install -r requirements.txt

# Create a .env file in the root directory with the following:
OPENAI_API_KEY=your_openai_api_key_here

# File structure overview should look like this:
.
├── streamlit_app.py         # Main Streamlit interface
├── main.py                  # Optional alternate entry point
├── .env                     # Contains your OpenAI API key (not included in repo)
├── /src
│   ├── data_loader.py       # Loads/saves user data and messages
│   ├── match_engine.py      # Structured matching + matched fields
│   ├── text_matcher.py      # LLM embeddings + cosine similarity
│   └── moderation.py        # Optional content moderation logic
├── /data
│   ├── sample_borrowers.csv # Borrower dataset
│   ├── sample_lenders.csv   # Lender dataset
│   ├── cached_embeddings.pkl# Cached embeddings for performance
│   └── messages.json        # Saved messages between users

# Start the app with:
streamlit run streamlit_app.py