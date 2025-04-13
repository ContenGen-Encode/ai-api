# import fastapi
import json
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

def generate(params):
    #get value of Name from paarams json obj
    # name = 
    params = json.loads(params)
    token = params["AccessToken"]
    output_audio_path = "output.mp3"
    fileName = params["FileName"]
    
    # Generate the script and TTS audio
    if(fileName is not None and fileName != ""):
        # Construct the endpoint URI
        file_url = f"https://congen-api.ofneill.com/storage/get-file?fileName={fileName}"
        headers = {
            "Authorization": f"Bearer {token}"
        }

        # ignore SSL certificate warnings
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

        # Get the file stream
        response = requests.get(file_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses

        # Read the stream and decode as text
        script = response.content.decode('utf-8')
        output_audio_path = tts.tts(script, params["Tone"])
    else:
        script = scriptgen(params["Prompt"], params["Tone"])
        output_audio_path = tts.tts(script.content, params["Tone"])

    subtitle = tts.transcribe(output_audio_path)

    print("Script:", script, subtitle)

    # Prepare headers with Authorization token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "audio/mpeg"
    }

    audioRes = ""
    subRes = ""

    # Stream the file
    with open(output_audio_path, 'rb') as f:
        audioRes = requests.post("https://congen-api.ofneill.com/storage/save-file", headers=headers, data=f)

    with open(subtitle, 'rb') as f:
        subRes = requests.post("https://congen-api.ofneill.com/storage/save-file", headers=headers, data=f)

    # print("Response status:", response.status_code)
    print("Response body:", response.text)

    return [audioRes, subRes]