import openai
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPEN_API_KEY"))

def check_moderation(text):
    response = client.moderations.create(input=text)
    result = response.results[0]
    flagged = result.flagged
    categories = [k for k in result.categories.__dict__ if getattr(result.categories, k)]
    return flagged, categories

