import fastapi
import os
from openai import AzureOpenAI
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import uvicorn

load_dotenv()

# class Model(BaseModel)

app = fastapi.FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

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
            yield update.choices[0].delta.content or "" 
    client.close()


@app.get('/generate')
async def generate():
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

    return StreamingResponse(response(client, deployment))

if __name__ == "__main__":
    uvicorn.run(app="__main__:app", host="localhost", port=8000, reload=True, workers=2)