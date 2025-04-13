# import fastapi
import os
from dotenv import load_dotenv
# import uvicorn
from scripttest import scriptgen
import tts
import requests
#from api.script import generate_system_prompt
 
load_dotenv()

# class Model(BaseModel)


def file_stream(file):
    with open(file, "rb") as f:
        yield from f   

async def generate(params, endpoint_url: str, token: str):
    output_audio_path = "output.mp3"
    
    # Generate the script and TTS audio
    script = scriptgen(params.prompt, params.tone)
    output_audio_path = tts.tts(script.content, params.tone)
    subtitle = tts.transcribe(output_audio_path)

    print("Script:", script, subtitle)

    # Prepare headers with Authorization token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "audio/mpeg"
    }

    # Stream the file
    with open(output_audio_path, 'rb') as f:
        response = requests.post(endpoint_url, headers=headers, data=f)

    print("Response status:", response.status_code)
    print("Response body:", response.text)

    return response