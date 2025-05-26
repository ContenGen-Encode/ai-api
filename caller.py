# import fastapi
from builtins import WindowsError
import os
import aiofiles
from dotenv import load_dotenv
# import uvicorn
from scripttest import scriptgen, transcribe
import tts
import requests
import aiohttp

from utils.file_lib import delete_file
#from api.script import generate_system_prompt
 
load_dotenv(override=True)

# class Model(BaseModel)

FILE_DIR=os.getenv("FILE_DIR")



async def generate(params):
    try:
        #get value of Name from paarams json obj
        API_URL = os.getenv("API_URL")

        VERIFY = API_URL.__contains__("https://localhost:")
        VERIFY = False if VERIFY else True

        token = params["AccessToken"]
        output_audio_path = "output.mp3"
        fileName = params["FileName"]
        projectId = params["ProjectId"]
        print(params)
        
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
            output_audio_path = await tts.tts(script, instructions=params["Tone"])
        else:
            print(f">> GENERATING_SCRIPT :: {projectId} ")
            script = await scriptgen(params["Prompt"], params["Tone"])
            if "error" in script:
                raise Exception(script["error"])
            
            print(f">> GENERATING_TTS :: {projectId} ")
            output_audio_path = await tts.tts(script.content, instructions=params["Tone"])
            
        print(f">> TRANSCRIBING_TTS :: {projectId} ")
        output_subtitle_path = await transcribe(output_audio_path)

        # print("Script:", script, subtitle)

        # Prepare headers with Authorization token
        headers = {
            "Authorization": f"Bearer {token}",
            # "Content-Type": "multipart/form-data"
        }


        connector = aiohttp.TCPConnector(verify_ssl=VERIFY)
        async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
            
            tts_form_data = aiohttp.FormData()

            print(f">> READING_FILE :: {projectId} :: {output_audio_path} ")
            async with aiofiles.open(output_audio_path, 'rb') as audio_file:
                audio_data = await audio_file.read()
                tts_form_data.add_field(
                    name="file",
                    value=audio_data,
                    filename=output_audio_path.split("/")[-1],
                    content_type="application/octet-stream"
                )
            print(f">> READING_FILE_COMPLETE :: {projectId} :: {output_audio_path} ")            
            
            print(f">> SENDING_FILE :: {projectId} :: {output_audio_path} ")
            async with session.post(f"{API_URL}/storage/save-file", data=tts_form_data) as audio_response:
                audio_res = await audio_response.json()
            print(f">> SENDING_FILE_COMPLETE :: {projectId} :: {audio_res}")

            srt_form_data = aiohttp.FormData()

            print(f">> READING_FILE :: {projectId} :: {output_audio_path} ")
            async with aiofiles.open(output_subtitle_path, 'rb') as subtitle_file:
                sub_data = await subtitle_file.read()
                srt_form_data.add_field(
                    name="file",
                    value=sub_data,
                    filename=output_subtitle_path.split("/")[-1],
                    content_type="application/octet-stream"
            )
            print(f">> READING_FILE_COMPLETE :: {projectId} :: {output_audio_path} ")
           
            print(f">> SENDING_FILE :: {output_subtitle_path} ")
            async with session.post(f"{API_URL}/storage/save-file", data=srt_form_data) as subtitle_response:
                sub_res = await subtitle_response.json()
            print(f">> SENDING_FILE_COMPLETE :: {projectId} :: {sub_res} ")

            # Prepare the request body
            project_res_body = {
                "id" : projectId,
                "ttsUrl" : audio_res["fileName"],
                "captionsUrl" : sub_res["fileName"],
                "successful" : True
            }

            url = f"{API_URL}/project/update-project"
            
            print(f">> SAVING_PROJECT :: {projectId}")
            async with session.put(url, json=project_res_body) as response:
                update_project_response = await response.json()
            print(f">> SAVING_PROJECT_COMPLETE :: {projectId} :: {update_project_response} ")

        del audio_file, subtitle_file  # explicitly remove reference
        import gc; gc.collect()
        
        
        try:
            delete_file(output_audio_path)
        except WindowsError:
           print(f">> ERROR_DELETING_FILE :: {output_audio_path}")
           
        try:
            delete_file(output_subtitle_path)
        except WindowsError:
           print(f">> ERROR_DELETING_FILE :: {output_subtitle_path}")
           
        return {
            "response" : update_project_response,
        }

        

    except Exception as e:
        print(f">> ERROR :: {e}")
        return {
            "message" : e,
            "error"   : "Error occured when generating"
        }