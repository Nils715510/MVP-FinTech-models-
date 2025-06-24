import pandas as pd

def load_borrowers(path="data/sample_borrowers.csv"):
    df = pd.read_csv(path)
    df.fillna("", inplace=True)
    return df

def load_lenders(path="data/sample_lenders.csv"):
    df = pd.read_csv(path)
    df.fillna("", inplace=True)
    return df

import json
import os

MESSAGE_FILE = "data/messages.json"

def save_message(sender_id, receiver_id, message):
    if os.path.exists(MESSAGE_FILE):
        try:
            with open(MESSAGE_FILE, "r", encoding="utf-8") as f:
                messages = json.load(f)
        except (json.JSONDecodeError, ValueError):
            messages = []
    else:
        messages = []

    messages.append({
        "from": sender_id,
        "to": receiver_id,
        "content": message
    })

    with open(MESSAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)

def load_messages(receiver_id):
    if not os.path.exists(MESSAGE_FILE):
        return []

    try:
        with open(MESSAGE_FILE, "r", encoding="utf-8") as f:
            messages = json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []

    return [msg for msg in messages if msg.get("to") == receiver_id]


