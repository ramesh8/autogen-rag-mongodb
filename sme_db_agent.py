from prompts.mognoexpert import mongo_expert_prompt

import autogen
from tools.mongo_executor import execute_mongo_queries
from utils import llmconfig
from autogen import register_function

mongo_expert_agent = autogen.AssistantAgent(
        name="Mongo_Expert_Agent",
        system_message=mongo_expert_prompt,
        llm_config=llmconfig,
        human_input_mode="NEVER",
        is_termination_msg=lambda msg: '"status":"querypass"' in msg["content"].lower(), 
        
    )

query_check_agent = autogen.AssistantAgent(
        name="Query_Check_Agent",
        system_message="You are a helpful AI Assistant."
        "You have to check the given query is valid and passes the QA using the provided tool.",
        llm_config=llmconfig,
        human_input_mode="NEVER",
        is_termination_msg=lambda msg: '"status":"querypass"' in msg["content"].lower(), 
    )

user_proxy = autogen.UserProxyAgent(
        name="User_Proxy",
        llm_config=False,
        human_input_mode="NEVER",
        code_execution_config={
            "work_dir": "coding",
            "use_docker": False,
        },
        max_consecutive_auto_reply=10,
        # is_termination_msg=lambda msg: "terminate" in msg["content"].lower(), 
    )

register_function(
        execute_mongo_queries,
        caller=query_check_agent,
        executor=user_proxy,
        name="execute_mongo_queries", 
        description="A validator for given mongo queries",  
    )

groupchat = autogen.GroupChat(
    agents=[mongo_expert_agent, query_check_agent, user_proxy],
    messages=[],
    max_round=10,
    speaker_selection_method= 'round_robin',
    allow_repeat_speaker=False
)

manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llmconfig)

group_chat_result = user_proxy.initiate_chat(
    manager, message=f"Find 10 questions in Python"
)