import azure.cognitiveservices.speech as speechsdk
import os
import dotenv
from caption import *
from caption.captioning import Captioning
# Creates an instance of a speech config with specified subscription key and service region.

dotenv.load_dotenv()

def tts():
    # Get API key from environment variable
    speech_key = os.getenv("TTS_API_KEY")
    service_region = "uksouth"


    audio_config = speechsdk.audio.AudioOutputConfig(filename="output.mp3")
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_voice_name = "en-US-Aria"

    text = "Hi, this is Aria"

    # use the default speaker as audio output.
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    ssml_string = open("ssml.xml", "r").read()
    result = speech_synthesizer.speak_ssml_async(ssml_string).get()

    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

    params = {
    "input": "output.mp3",
    "format": "any",
    "output": "caption.srt",
    "srt": True,
    "realTime": True,
    "threshold": 5,
    "delay": 0,
    "profanity": "mask",
    "phrases": "Contoso;Jessie;Rehaan"
}

    captioning = Captioning()
    captioning.initialize()
    speech_recognizer_data = captioning.speech_recognizer_from_user_config()
    captioning.captions_from_offline_results(speech_recognizer=speech_recognizer_data["speech_recognizer"], format=speech_recognizer_data["audio_stream_format"], callback=speech_recognizer_data["pull_input_audio_stream_callback"], stream=speech_recognizer_data["pull_input_audio_stream"])
    captioning.finish()

    return result

if __name__ == "__main__":
    tts()



