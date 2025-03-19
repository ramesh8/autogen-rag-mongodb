import openai
from dotenv import load_dotenv
import os

from pymongo import MongoClient

load_dotenv()

OPENAI_AI_KEY = os.getenv("OPENAI_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")

EMBEDDING_MODEL = "text-embedding-3-small"

def get_embedding(text):
    """Generate an embedding for the given text using OpenAI's API."""

    # Check for valid input
    if not text or not isinstance(text, str):
        return None

    try:
        # Call OpenAI API to get the embedding
        embedding = openai.embeddings.create(input=text, model=EMBEDDING_MODEL).data[0].embedding
        return embedding
    except Exception as e:
        print(f"Error in get_embedding: {e}")
        return None

uri = "mongodb+srv://root:620750648@demo.zzg5m.mongodb.net/"
client = MongoClient(uri)

# Access your database and collection
database = client["SME"]
collection = database["questions"]

qs = collection.find({})

for q in qs:
    qt = q["question_text"]
    qte = get_embedding(qt)
    # q["question_text_embedding"] = qte
    collection.update_one({"_id":q["_id"]}, {"$set":{"question_text_embedding":qte}})

#create index for vectors