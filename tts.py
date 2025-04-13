import os
from openai import AzureOpenAI
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# Get API key from environment variable
def tts(prompt,tone):
    """
    Converts a given text prompt into speech, saves it as an audio file, 
    and returns the path to the saved file.

    Args:
        prompt (str): The text input to be converted into speech.

    Returns:
        str: The file path to the saved audio output.
    """

    key = os.getenv("TTS_API_KEY")
    clientTTS = AzureOpenAI(
        api_version="2024-12-01-preview",
        azure_endpoint="https://sebi-m9edwlj5-northcentralus.cognitiveservices.azure.com/",
        api_key=key,
    )

    output_audio_path = "output.mp3"
    response = clientTTS.audio.speech.create(
        model = "tts-hd",
        voice = "alloy",
        input = prompt,
        instruction = tone,
    )

    response.write_to_file(output_audio_path)
    
    print(f"Audio saved to: {output_audio_path}")
    clientTTS.close()
    
    return output_audio_path


def transcribe(output_audio_path):
    """
    Transcribe an audio file using the Whisper model from OpenAI.

    Given a path to an audio file, this function will transcribe it using the Whisper model
    from OpenAI and save the transcription to a file named "subtitles.srt" in the same
    directory.

    Args:
        output_audio_path: str, the path to the audio file to transcribe
    """
    key = os.getenv("OPENAI_API_KEY")

    clientSUB = AzureOpenAI(
        api_version="2024-12-01-preview",
        azure_endpoint="https://ai-sebimomir-3123.cognitiveservices.azure.com/",
        api_key=key,
    )

    result = clientSUB.audio.transcriptions.create(

        file=open(output_audio_path, "rb"),            
        model="whisper",
        response_format="srt"
    )

    with open("subtitles.srt", 'w', encoding='utf-8') as f:
        f.write(result)
