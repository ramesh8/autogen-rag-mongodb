import json
import os
from typing import Any, Dict
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
database = client["SME"]

collection_projections = {
    "questions": {"_id":0, "content":0, "embedding":0},
    #todo: remaining collections
}

def get_document(id, collection_name):
    try:
        collection = database[collection_name]
        
        doc = collection.find_one({"_id":ObjectId(id)},collection_projections[collection_name] if collection_name in collection_projections else {})
        return doc
    except Exception as ex:
        # return { "source":"get_document", "error": str(ex) }
        return id


def run_query(query, collection_name):
    try:
        collection = database[collection_name]
        res = collection.aggregate(query)
        result = []
        for item in res:
            if "_id" in item:
                result.append(str(item["_id"]))
        return { "result": result, "collection": collection_name, "status":"QUERYPASS" }
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