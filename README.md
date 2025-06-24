# Real Estate Voice AI Agent

A voice-enabled AI assistant for Dubai real estate.  
Users can call a Twilio phone number, ask property-related questions, and get spoken answers powered by OpenAI GPT-4 and ElevenLabs text-to-speech.

---

## Features

- Voice-based interaction via phone calls (Twilio)
- Real-time speech-to-text using OpenAI Whisper
- Conversational AI powered by GPT-4 with contextual memory
- Property data search with Dubai listings (CSV-based)
- Natural speech response via ElevenLabs TTS
- Easily deployable FastAPI backend

---

## Tech Stack

- Python 3.13+
- FastAPI (web framework)
- Twilio (voice calls & webhook)
- OpenAI API (GPT-4 and Whisper)
- ElevenLabs API (text-to-speech)
- Pandas (data processing)

---

## Setup Instructions

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/realestate-voice-agent.git
   cd realestate-voice-agent
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Create a .env file in the project root with the following environment variables:

ini
Copy
Edit
OPENAI_API_KEY=your_openai_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
ELEVENLABS_API_KEY=your_elevenlabs_api_key
Place your Dubai properties CSV file (dubai_properties_500.csv) in the project folder.

Run the app locally:

bash
Copy
Edit
uvicorn app:app --reload
Configure Twilio phone number webhook to point to:

arduino
Copy
Edit
https://your-deployment-url/voice
Usage
Call your Twilio phone number.

Speak your property questions (e.g., "Find me a villa under 2 million in Dubai Hills").

Listen to the AI voice assistant’s spoken reply.

License
This project is open source under the MIT License.

Acknowledgements
OpenAI for GPT-4 and Whisper APIs

ElevenLabs for high-quality TTS

Twilio for telephony services

yaml
Copy
Edit

---

You can save this content as `README.md` in your project root folder and push it to GitHub.

If you want, I can also generate the full project zip with this README included. Just ask!
