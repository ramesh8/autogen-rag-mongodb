import json
import os
from typing import Any, Dict
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
database = client["SME"]

# collection_projections = {
#     "questions": {"_id":0, "content":0, "embedding":0},
#     "users" : {""}

# }

def run_query(query, collection_name):
    try:
        collection = database[collection_name]
        res = collection.aggregate(query)
        #todo: process res, _id, ...?
        #remove embeddings and content
        result = []
        for item in res:
            # if "content" in item:
            #     del item["content"]
            # if "embedding" in item:
            #     del item["embedding"]
            if "_id" in item:
                result.append(str(item["_id"]))
        return { "result": result, "status":"QUERYPASS" }
    except Exception as ex:
        return { "result": str(ex), "status":"QUERYFAIL" }

from typing import TypedDict

QueryResponse = TypedDict('QueryResponse', {'query': list, 'title':list, 'base_collection': str})

def execute_mongo_queries(response:QueryResponse) -> Any:
    if response == None:
        return "Query is missing"
    if isinstance(response, str):
        try:
            response = json.loads(response)        
        except Exception as ex:
            return str(ex)
    if "query" not in response:
        return "query is missing"
    
    if "base_collection" not in response:
        return "base collection is missing"
    
    return run_query(response["query"], response["base_collection"])

if __name__ == "__main__":
    query = {
            "query": [
                {
                    "$lookup": {
                        "from": "skills",
                        "localField": "skill_id",
                        "foreignField": "skill_id",
                        "as": "skill_info"
                    }
                },
                {
                    "$match": {
                        "skill_info.name": "Java"
                    }
                },
                {
                    "$limit": 10
                }
            ],
            "title": ["question_id", "question_text", "question_type", "difficulty_level"],
            "base_collection": "questions"
        }
    

    res = execute_mongo_queries(query)

    print(res)