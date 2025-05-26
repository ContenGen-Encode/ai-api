import aiofiles
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from openai import OpenAIError, AsyncAzureOpenAI
from dotenv import load_dotenv

from utils.file_lib import generate_unique_filename
load_dotenv(override=True)
import os 


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHISPER_API_KEY = os.getenv("WHISPER_API_KEY")
AZURE_ENDPOINT_WHISPER = os.getenv("AZURE_ENDPOINT_WHISPER")
AZURE_ENDPOINT_GPT = os.getenv("AZURE_ENDPOINT_GPT")

async def scriptgen(prompt, tone):
    """
    Generate a script with a story for a popular instagram reel with subtitles and Narrates it
    using the Azure Chat OpenAI model.

    Parameters:
        prompt (str): Prompt to generate a script for
        tone (str): The tone of the script to generate

    Returns:
        dict: A dictionary with the generated script and the tone of the script
              or an error message and the error code
    """
    llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",  # or your deployment
    api_version = "2024-12-01-preview",
    azure_endpoint=AZURE_ENDPOINT_GPT,
    api_key=OPENAI_API_KEY,
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


    #chain = prompt | llm | 
   
    try:
        prompt = await prompt_template.ainvoke({
            "input":prompt, 
            "tone":tone
        })
        res = await llm.ainvoke(prompt)
        return res
    except OpenAIError as ai_err:
        ai_response_msg = ai_err.body["message"]
        return {"message": ai_response_msg,
                "error" : ai_err.body["error"]}
    

async def transcribe(output_audio_path):
    """
    Transcribe an audio file using the Whisper model from OpenAI.

    Given a path to an audio file, this function will transcribe it using the Whisper model
    from OpenAI and save the transcription to a file named "subtitles.srt" in the same
    directory.

    Args:
        output_audio_path: str, the path to the audio file to transcribe
    """
    key = os.getenv("OPENAI_API_KEY")

    clientSUB: AsyncAzureOpenAI = AsyncAzureOpenAI(
        api_version="2024-12-01-preview",
        azure_endpoint=AZURE_ENDPOINT_WHISPER,
        api_key=WHISPER_API_KEY,
    )


    response: str = await clientSUB.audio.transcriptions.create(

        file=open(output_audio_path, "rb"),            
        model="whisper",
        response_format="srt"
    )

    output_file_name = generate_unique_filename(".srt")
    output_dir = os.getenv("FILE_DIR")
    path_to_file = f"{output_dir}/{output_file_name}"

    async with aiofiles.open(path_to_file, 'wb') as f:
        await f.write(bytes(response, encoding="utf-8"))
    
    return path_to_file


if __name__ == "__main__": 
    prompt = input("Enter prompt: ")
    tone = input("Enter tone: ")
    print(scriptgen(prompt, tone).content )

