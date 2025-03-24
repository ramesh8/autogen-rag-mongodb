import ast
import json
from prompts.mognoexpert import mongo_expert_prompt

import autogen
from tools.mongo_executor import execute_mongo_queries, get_document
from utils import llmconfig
from autogen import Agent, register_function

mongo_expert_agent = autogen.AssistantAgent(
        name="Mongo_Expert_Agent",
        system_message=mongo_expert_prompt,
        llm_config=llmconfig,
        human_input_mode="NEVER" 
    )

query_check_agent = autogen.AssistantAgent(
        name="Query_Check_Agent",
        system_message="You are a helpful AI Assistant."
        "You have to check the given query is valid and passes the QA using the provided tool.",
        llm_config=llmconfig,
        human_input_mode="NEVER"
    )

user_proxy = autogen.UserProxyAgent(
        name="User_Proxy",
        llm_config=False,
        human_input_mode="NEVER",
        code_execution_config={
            "work_dir": "coding",
            "use_docker": False,
        },
        max_consecutive_auto_reply=10
    )

register_function(
        execute_mongo_queries,
        caller=query_check_agent,
        executor=user_proxy,
        name="execute_mongo_queries", 
        description="A validator for given mongo queries",  
    )

def custom_speaker_selection(last_speaker:Agent, groupchat:autogen.GroupChat):
    messages = groupchat.messages
    if len(messages)<=1:
        return mongo_expert_agent
    
    if last_speaker is mongo_expert_agent:
        return query_check_agent
    
    if last_speaker is query_check_agent:
        return user_proxy
    
    if last_speaker is user_proxy:
        last_response = user_proxy.last_message()
        try:            
            last_response_json = ast.literal_eval(last_response['content'])
            if last_response_json['status'] == 'QUERYPASS':
                return None
            else:
                return mongo_expert_agent
        except Exception as ex:
            print("🤞 unhandled exception in custom speaker selection : ",str(ex))
            return None
        

groupchat = autogen.GroupChat(
    agents=[mongo_expert_agent, query_check_agent, user_proxy],
    messages=[],
    max_round=10,
    speaker_selection_method= custom_speaker_selection,
)

manager = autogen.GroupChatManager(
    groupchat=groupchat, 
    llm_config=llmconfig,
    silent=False
    )

def get_dbagent_response(query):
    group_chat_result = user_proxy.initiate_chat(
        manager, message=query
    )
    res = group_chat_result.chat_history[-1]
    alldocs = []
    if 'content' in res:
        res_json = ast.literal_eval(res['content'])
        docs  = res_json['result']
        col_name = res_json["collection"]
        #sometimes the agent will bring direct answers instead of ids.
        #handle this case
        for doc in docs:
            document = get_document(doc, col_name)
            if "_id" in document:
                del document["_id"]
            alldocs.append(document)
        return alldocs
    else:
        return{"error":f"invalid response from agent: {res}"}

# if __name__ == "__main__":
#     try:
#         res = group_chat_result.chat_history[-1]
#         if 'content' in res:
#             res_json = ast.literal_eval(res['content'])
#             docs  = res_json['result']
#             col_name = res_json["collection"]
#             for doc in docs:
#                 document = get_document(doc, col_name)
#                 print(document)
#         else:
#             print("invalid response from agent", res)
#     except Exception as ex:
#         print("exception at chat result", str(ex))

