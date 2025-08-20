import speech_recognition as sr

def transcribe_audio(audio_segment):
    """
    Transcribes an audio segment object from audiorecorder to text.
    Returns the transcribed text and an error message (if any).
    """
    if not audio_segment:
        return None, "No audio recorded."

    recognizer = sr.Recognizer()
    
    # Create an AudioData object directly from the pydub segment
    audio_data = sr.AudioData(
        frame_data=audio_segment.raw_data,
        sample_rate=audio_segment.frame_rate,
        sample_width=audio_segment.sample_width
    )
    
    try:
        # Use Google's free web speech API for transcription
        text = recognizer.recognize_google(audio_data)
        return text, None
    except sr.UnknownValueError:
        return None, "Sorry, I could not understand the audio. Please try again."
    except sr.RequestError as e:
        return None, f"Could not request results from the service; {e}"
