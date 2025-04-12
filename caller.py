import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# class Model(BaseModel)

def response(client, deployment):
    response = client.chat.completions.create(
    stream=True,
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "I am going to Paris, what should I see? in 15 words",
        }
    ],
    max_tokens=800,
    temperature=1.0,
    top_p=1.0,
    model=deployment,
    )

    for update in response:
        if update.choices:
            print(update.choices[0].delta.content or "")
    client.close()

def generate():
    endpoint = "https://ai-sebimomir-3123.cognitiveservices.azure.com/"
    model_name = "gpt-4o-mini"
    deployment = "gpt-4o-mini"

    key = os.getenv("OPENAI_API_KEY")
    # print(key)

    subscription_key =key
    #str(key)
    
    api_version = "2024-12-01-preview"

    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=subscription_key,
    )

    return print(response(client, deployment))



generate()