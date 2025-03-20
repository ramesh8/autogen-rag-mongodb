import autogen

config_list_gpt4 = autogen.config_list_from_dotenv(
    ".env",
    {"gpt-4o-mini": "OPENAI_API_KEY"}
)

llmconfig = {
    "cache_seed": 41,
    "config_list": config_list_gpt4,
    "temperature": 0,
}