import os
import io
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import openai
import requests
from dotenv import load_dotenv

load_dotenv()

# Set API keys
openai.api_key = os.getenv("OPENAI_API_KEY")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # Rachel's voice ID

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = FastAPI()

# Load properties CSV
properties_df = pd.read_csv("C:/Users/varma/Desktop/voice/dubai_properties_500.csv")

# Simple property search function
def search_properties(query):
    df = properties_df.copy()
    query_lower = query.lower()
    matched = df[df.apply(lambda row: query_lower in str(row.values).lower(), axis=1)]
    if matched.empty:
        return "Sorry, no properties matched your request."
    top = matched.head(3)
    response = "Here are some properties I found:\n"
    for _, row in top.iterrows():
        response += f"- {row['Type']} in {row['Location']} for AED {row['Price']}\n"
    return response

# Conversation memory (simple dict by caller)
memory_store = {}

def elevenlabs_tts(text: str, output_file: str):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    json_data = {
        "text": text,
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(url, json=json_data, headers=headers)
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        return True
    else:
        print(f"ElevenLabs TTS error: {response.status_code} - {response.text}")
        return False

@app.post("/voice")
async def voice(request: Request):
    form = await request.form()
    from_number = form.get("From")
    recording_url = form.get("RecordingUrl")

    vr = VoiceResponse()

    if not recording_url:
        # First time - prompt user to say something
        vr.say("Welcome to Dubai Real Estate assistant. Please ask your question after the beep.")
        vr.record(max_length=10, transcribe=False, play_beep=True, action="/voice")
        return Response(content=str(vr), media_type="application/xml")

    # Transcribe with OpenAI Whisper
    transcript = await transcribe_audio(recording_url + ".wav")

    if not transcript:
        vr.say("Sorry, I couldn't understand that. Please try again.")
        vr.record(max_length=10, transcribe=False, play_beep=True, action="/voice")
        return Response(content=str(vr), media_type="application/xml")

    # Maintain conversation memory
    if from_number not in memory_store:
        memory_store[from_number] = []
    memory_store[from_number].append(f"User: {transcript}")

    # Search properties + GPT response
    property_info = search_properties(transcript)
    context = "\n".join(memory_store[from_number][-5:])
    prompt = f"""
You are a helpful Dubai real estate assistant.

Conversation so far:
{context}

User asked: {transcript}

Use this property data to answer clearly and professionally:
{property_info}

Answer:
"""
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.7,
    )
    answer = completion.choices[0].message.content.strip()
    memory_store[from_number].append(f"AI: {answer}")

    # Generate ElevenLabs audio
    audio_file = f"response_{from_number}.mp3"
    success = elevenlabs_tts(answer, audio_file)
    if not success:
        vr.say("Sorry, I could not generate the voice response.")
    else:
        vr.play(audio_file)

    vr.record(max_length=10, transcribe=False, play_beep=True, action="/voice")
    return Response(content=str(vr), media_type="application/xml")

async def transcribe_audio(audio_url):
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            audio_bytes = (await client.get(audio_url)).content
        audio_file = io.BytesIO(audio_bytes)
        transcript_resp = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript_resp.text
    except Exception as e:
        print("Transcription error:", e)
        return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
