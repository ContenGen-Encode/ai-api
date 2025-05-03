import os
from openai import AsyncAzureOpenAI
import dotenv
import aiofiles
from utils.file_lib import generate_unique_filename


# Load environment variables from .env file
dotenv.load_dotenv()

# Get API key from environment variable
TTS_API_KEY = os.getenv("TTS_API_KEY")
AZURE_ENDPOINT_TTS = os.getenv("AZURE_ENDPOINT_TTS")

async def tts(prompt: str, voice: str = "alloy", instructions: str = None):
    """
    Converts a given text prompt into speech, saves it as an audio file, 
    and returns the path to the saved file.

    Args:
        prompt (str): The text input to be converted into speech.
        voice (str): The voice to use for speech synthesis.
        instructions (str): Additional instructions that can change Accent, Emotional range, Intonation, Impressions, Speed of speechTone, Whispering.
    Returns:
        str: The file path to the saved audio output.
    """

    TTS_API_KEY = os.getenv("TTS_API_KEY")
    AZURE_ENDPOINT_TTS = os.getenv("AZURE_ENDPOINT_TTS")
    clientTTS = AsyncAzureOpenAI(
        api_version="2024-12-01-preview",
        azure_endpoint=AZURE_ENDPOINT_TTS,
        api_key=TTS_API_KEY,
        
    )

    output_audio_path = "output.mp3"

    response = await clientTTS.audio.speech.create(
        model = "tts-hd",
        voice = voice,
        input = prompt,
        instructions = instructions,
    )

    if hasattr(response, 'read') and callable(response.aread):
        audio_data = await response.aread()
    else:
        audio_data = response.content 

    output_file_name = generate_unique_filename()
    output_dir = os.getenv("FILE_DIR")
    path_to_file = f"{output_dir}/{output_file_name}"


    async with aiofiles.open(path_to_file, 'wb') as f:
        await f.write(audio_data)

    print(f"Audio saved to: {output_file_name}")
    await clientTTS.close()

    return path_to_file



