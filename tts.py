import os
from openai import AzureOpenAI, AsyncAzureOpenAI
import dotenv

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

    clientTTS = await AsyncAzureOpenAI(
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

    response.write_to_file(output_audio_path)
    
    print(f"Audio saved to: {output_audio_path}")
    clientTTS.close()
    
    return output_audio_path



