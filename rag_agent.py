import os
import getpass
from dotenv import load_dotenv
import os
import json
import autogen
from autogen import AssistantAgent
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.retrieve_utils import TEXT_FORMATS
import openai

load_dotenv()

OPENAI_AI_KEY = os.getenv("OPENAI_API_KEY")
MONGODB_URI  = os.getenv("MONGODB_URI")

# print(MONGODB_URI)

config_list = [{"model": "gpt-4o-mini", "api_key": OPENAI_AI_KEY, "api_type": "openai"}]
assert len(config_list) > 0
# print("models to use: ", [config_list[i]["model"] for i in range(len(config_list))])


# print("Accepted file formats for `docs_path`:")
# print(TEXT_FORMATS)

assistant = AssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant. Answer the questions using only provided context. Do not answer from your pre existining knowledge.",
    llm_config={
        "timeout": 600,
        "cache_seed": 42,
        "config_list": config_list,
    },
)

def get_embedding(text):
    """Generate an embedding for the given text using OpenAI's API."""
    EMBEDDING_MODEL = "text-embedding-3-small"
    # Check for valid input
    if not text or not isinstance(text, str):
        if isinstance(text,list):
            es = []
            for t in text:
                embedding = openai.embeddings.create(input=t, model=EMBEDDING_MODEL).data[0].embedding
                es.append(embedding)
            return es

    try:
        # Call OpenAI API to get the embedding
        embedding = openai.embeddings.create(input=text, model=EMBEDDING_MODEL).data[0].embedding
        return embedding
    except Exception as e:
        print(f"Error in get_embedding: {e}")
        return None



# qem = get_embedding(code_problem)
# print(qem)

ragproxyagent = RetrieveUserProxyAgent(
    name="MongoRAGagent",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3,
    retrieve_config={
        "task": "code",
        "custom_text_types": ["non-existent-type"],
        "chunk_token_size": 2000,
        "model": config_list[0]["model"],
        "vector_db": "mongodb",  # MongoDB Atlas database
        "collection_name": "questions",
        "embedding_function": get_embedding,
        "db_config": {
            "connection_string": MONGODB_URI,  # MongoDB Atlas connection string
            "database_name": "SME",  # MongoDB Atlas database
            "index_name": "question_vector_index",
            "wait_until_index_ready": 120.0,  # Setting to wait 120 seconds or until index is constructed before querying
            "wait_until_document_ready": 120.0,  # Setting to wait 120 seconds or until document is properly indexed after insertion/update
        },
        "get_or_create": True,  # set to False if you don't want to reuse an existing collection
        "overwrite": False,  # set to True if you want to overwrite an existing collection, each overwrite will force a index creation and reupload of documents
    },
    code_execution_config=False,  # set to False if you don't want to execute the code
)

def get_ragagent_response(query):
    assistant.reset()
    # code_problem = "give me questions with difficulty level above 3"
    chat_result = ragproxyagent.initiate_chat(assistant, message=ragproxyagent.message_generator, problem=query)
    #todo: instead of sending chat_result, process it and send docs only
    return chat_result.chat_history[-1]

# print(chat_result)