import fastapi
import os
from openai import AzureOpenAI, BaseModel
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import uvicorn
from scripttest import scriptgen
import tts
#from api.script import generate_system_prompt
 
load_dotenv()

# class Model(BaseModel)

app = fastapi.FastAPI()


# class GetScript(BaseModel):
#     subtitles: str

@app.get("/")
async def root():
    return {"message": "Hello World"}


class GenParams(BaseModel):
    prompt: str
    tone: str

def file_stream(file):
    with open(file, "rb") as f:
        yield from f   

@app.post('/generate')
async def generate(params: GenParams):
    
    output_audio_path = "output.mp3"
    script = scriptgen(params.prompt, params.tone)
    output_audio_path = tts.tts(script.content , params.tone)
    subtitle = tts.transcribe(output_audio_path)

    print("Script:", script, subtitle)
    return StreamingResponse(file_stream(output_audio_path), media_type="audio/mpeg")

if __name__ == "__main__":
    uvicorn.run(app="__main__:app", host="localhost", port=8000, reload=True, workers=2)