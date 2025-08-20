import speech_recognition as sr
import io

def transcribe_audio_bytes(audio_bytes):
    """
    Transcribes raw audio bytes (from st.audio_recorder) to text.
    Returns the transcribed text and an error message (if any).
    """
    if not audio_bytes:
        return None, "No audio recorded."

    recognizer = sr.Recognizer()
    
    # Use an in-memory buffer to treat the bytes as a file
    with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
        try:
            # Listen for the data from the audio source
            recorded_audio = recognizer.record(source)
            # Use Google's free web speech API for transcription
            text = recognizer.recognize_google(recorded_audio)
            return text, None
        except sr.UnknownValueError:
            return None, "Sorry, I could not understand the audio. Please try again."
        except sr.RequestError as e:
            return None, f"Could not request results from the service; {e}"

