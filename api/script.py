import openai as ai
from openai import AzureOpenAI
from langchain.prompts import SystemMessagePromptTemplate, ChatPromptTemplate

class ScriptGen():
    def __init__(self, api_version, azure_endpoint, api_key):
        self.client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=azure_endpoint,
            api_key=api_key,    
        )

    def generate_system_prompt(self, template, **variables):
        template = """
        You are an expert {role} with {years} years of experience.
        Your task is to {task}.
        Please provide {output_format}.
        """
        
        # Example variables
        variables = {
            "role": "software engineer",
            "years": "5",
            "task": "write clean and efficient code",
            "output_format": "detailed explanations with code examples"
        }
        return template.format(**variables) 