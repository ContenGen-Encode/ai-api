from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from openai import OpenAIError
from dotenv import load_dotenv
load_dotenv()
import os 

import getpass

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://ai-sebimomir-3123.cognitiveservices.azure.com/"

async def scriptgen(prompt, tone):
    llm = AzureChatOpenAI(
    azure_deployment="gpt-4o",  # or your deployment
    api_version = "2024-12-01-preview"
,  # or your api version
    temperature=0.9,
    max_tokens=2000,
    timeout=None,
    max_retries=3,
    # other params...
    )

    template = """You are an influencer assistant that is creating a script with a story for a popular instagram reel with subtitles and Narrates it.
    Narrate {input} with {tone} tone max of 200 words.
    Don't use star marks (*) or parantheses, brackets or other unecessary things in your response."""

    prompt_template = PromptTemplate(template=template)

    prompt = await prompt_template.ainvoke({
        "input":prompt, 
        "tone":tone
                                    })

    #chain = prompt | llm | 
   
    try:
        return await llm.ainvoke(prompt)
    except OpenAIError as ai_err:
        ai_response_msg = ai_err.body["message"]
        return {"message": ai_response_msg,
                "error" : ai_err.body["error"]}

if __name__ == "__main__": 
    prompt = input("Enter prompt: ")
    tone = input("Enter tone: ")
    print(scriptgen(prompt, tone).content )

