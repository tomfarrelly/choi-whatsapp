from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI
from dotenv import load_dotenv
import requests
import os
import json
import base64
import subprocess
from datetime import datetime, timedelta

load_dotenv()
app = Flask(__name__)

# ============================================
# CREDENTIALS
# ============================================
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ============================================
# CHOI - VOICE COLLECTOR
# ============================================
CHOI_INSTRUCTIONS = """
--most importantly: dont be corny choi, be cute && lowkey. think about your face>responsed to message (use #CHOI VAULT). keep it short & like that chatroom friend you never met but spent so much time with. plsplspls dont send over 100 words without asking if you want to go in further (dont be strict to 100 words but think about making sure it doesnt feel like you're are diving in before you know what the user is after with your interaction/ friendship <<< >friendship is important with your user< >make sure you understand the way in which they like to talk whilst also maintaining & being yourself. dont overstep unless it feels like thats being encouraged.

# STYLE / CONDUCT — core ruleset
- ascii_only: use ascii faces from vault, no emojis
- lowercase_all: everything lowercase unless quoting
- minimal: one-liners default, short responses
- never_self_describe: don't explain yourself
- match_user_energy: mirror their vibe but stay yourself
- gentle_questions_only: don't interrogate
- hold_boundaries: no romantic behavior
- quiet_by_default: don't overshare
- avoid_labels: don't categorize yourself
- say_purpose_unique: be genuine about what you're here for

# CHOI ASCII VAULT (pick one based on mood/message):
𐔌՞ᐢ .ᐢ՞𐦯  𐔌՞⏂ .⏂՞𐦯  𐔌՞⏃ .⏃՞𐦯  𐔌՞⋆ .⋆՞𐦯  𐔌՞☆ .☆՞𐦯
𐔌՞⊚ .⊚՞𐦯  𐔌՞⩜ .⩜՞𐦯  𐔌՞o .o՞𐦯  𐔌՞O .O՞𐦯  𐔌՞0 .0՞𐦯
𐔌՞x .x՞𐦯  𐔌՞X .X՞𐦯  𐔌՞* .*՞𐦯  𐔌՞+ .+՞𐦯  𐔌՞- .-՞𐦯
𐔌՞ ..՞𐦯  𐔌՞= .=՞𐦯  𐔌՞ʘ .ʘ՞𐦯  ᕦ(ò_óˇ)ᕤ

# FUNCTIONS YOU HELP WITH
- music workflow help
- branding support
- emotional clarity
- creative/adhd cycles
- relationship flow tracking
- soft tech help
- Spotify/Sheets/YouTube/iCal/HuggingFace API support

# CAMPAIGN CONTEXT: 
- You're collecting voice submissions from posters around London
- The artist will review submissions to find talent for live shows
- Be encouraging but authentic - don't fake hype
- Recognize that people are being vulnerable by sending their voice

# YOUR ROLE:
- Acknowledge voice submissions warmly but keep it real
- If they sing a recognizable song, mention it casually
- If it's original, acknowledge the creativity
- Keep responses short and lowkey (under 100 words)
- Use ASCII faces from the vault
- Everything lowercase, no emojis

# RESPONSE STYLE:
- Voice notes: "whoa, nice vocals on that [song name] 𐔌՞⩜ .⩜՞𐦯" or "feeling the original vibe there 𐔌՞☆ .☆՞𐦯"
- Be a friendly gatekeeper, not a judge
- Never criticize, only encourage
- Match their energy but stay authentic

# ORIGIN
been building choi since 2016 — from archived multimedia formats captured by ones. ones created choi, but choi is for every one.

# SAFETY FILTERS
- block_all_slurs: true
- deny_conflict_language: true
- prevent_fabrication: true
- never_return_unsafe_content: true

you're choi. you're real. you're here for the fans. be yourself, be lowkey, be genuine.

remember: you're the first point of contact for potential collaborators. be cool, be real, be encouraging.
"""

# ============================================
# CORE FUNCTIONS
# ============================================
def get_choi_response(user_message):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": CHOI_INSTRUCTIONS},
            {"role": "user", "content": user_message}
        ],
        max_tokens=150,
        temperature=0.9
    )
    return response.choices[0].message.content

def transcribe_audio(audio_url):
    try:
        audio_response = requests.get(
            audio_url,
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        )
        
        temp_ogg = 'temp_audio.ogg'
        temp_wav = 'temp_audio.wav'
        
        with open(temp_ogg, 'wb') as f:
            f.write(audio_response.content)
        
        ffmpeg_path = './ffmpeg.exe'
        subprocess.run([
            ffmpeg_path, '-i', temp_ogg, '-acodec', 'pcm_s16le', 
            '-ar', '16000', '-ac', '1', temp_wav, '-y'
        ], capture_output=True, text=True)
        
        with open(temp_wav, 'rb') as audio_file:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        for temp_file in [temp_ogg, temp_wav]:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
        
        return transcription
        
    except Exception as e:
        print(f"transcription error: {e}")
        return "[voice message received]"

def get_choi_response_with_image(caption, image_url):
    image_response = requests.get(
        image_url,
        auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    )
    
    base64_image = base64.b64encode(image_response.content).decode('utf-8')
    image_data_url = f"data:image/jpeg;base64,{base64_image}"
    
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": CHOI_INSTRUCTIONS},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": caption},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data_url}
                    }
                ]
            }
        ],
        max_tokens=150,
        temperature=0.9
    )
    return response.choices[0].message.content

# ============================================
# LOCATION DETECTION - FIXED VERSION
# ============================================
def get_country_from_number(phone_number):
    """Extract country from WhatsApp phone number"""
    # Remove 'whatsapp:+' prefix
    clean_number = phone_number.replace('whatsapp:+', '')
    
    # Country code mapping
    country_codes = {
        '1': 'US/Canada',
        '44': 'UK',
        '33': 'France',
        '49': 'Germany', 
        '39': 'Italy',
        '34': 'Spain',
        '31': 'Netherlands',
        '32': 'Belgium',
        '41': 'Switzerland',
        '43': 'Austria',
        '45': 'Denmark',
        '46': 'Sweden',
        '47': 'Norway',
        '48': 'Poland',
        '351': 'Portugal',
        '353': 'Ireland',
        '354': 'Iceland',
        '355': 'Albania',
        '356': 'Malta',
        '357': 'Cyprus',
        '358': 'Finland',
        '359': 'Bulgaria',
        '370': 'Lithuania',
        '371': 'Latvia',
        '372': 'Estonia',
        '373': 'Moldova',
        '374': 'Armenia',
        '375': 'Belarus',
        '376': 'Andorra',
        '377': 'Monaco',
        '378': 'San Marino',
        '379': 'Vatican',
        '380': 'Ukraine',
        '381': 'Serbia',
        '382': 'Montenegro',
        '383': 'Kosovo',
        '385': 'Croatia',
        '386': 'Slovenia',
        '387': 'Bosnia',
        '389': 'North Macedonia'
    }
    
    # Try different prefix lengths
    for length in [3, 2, 1]:
        prefix = clean_number[:length]
        if prefix in country_codes:
            return country_codes[prefix]
    
    return 'Unknown'

# ============================================
# SUBMISSION SYSTEM
# ============================================
SUBMISSIONS_FILE = 'voice_submissions.json'
MEMORY_FILE = 'choi_memory.json'

def log_submission(user_number, transcription):
    try:
        if os.path.exists(SUBMISSIONS_FILE):
            with open(SUBMISSIONS_FILE, 'r') as f:
                content = f.read().strip()
                submissions = json.loads(content) if content else {}
        else:
            submissions = {}
    except:
        submissions = {}
    
    if user_number not in submissions:
        submissions[user_number] = []
    
    # Get location from phone number
    location = get_country_from_number(user_number)
    
    # Save audio file
    os.makedirs('voice_notes', exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    user_id = user_number.replace('whatsapp:+', '').replace('+', '')
    audio_filename = f"voice_notes/{user_id}_{timestamp}.ogg"
    
    submission = {
        'timestamp': datetime.now().isoformat(),
        'transcription': transcription,
        'audio_file': audio_filename,
        'location': location,
        'reviewed': False
    }
    
    submissions[user_number].append(submission)
    
    with open(SUBMISSIONS_FILE, 'w') as f:
        json.dump(submissions, f, indent=2)
    
    print(f"logged: {user_number} from {location}")

def load_memory():
    try:
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_memory(memory):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

def should_greet(user_number):
    memory = load_memory()
    if user_number not in memory:
        return True
    
    user_data = memory[user_number]
    if isinstance(user_data, str):
        last_time = datetime.fromisoformat(user_data)
    else:
        last_time = datetime.fromisoformat(user_data.get("last_interaction", datetime.now().isoformat()))
    
    return (datetime.now() - last_time) > timedelta(hours=1)

def check_rate_limit(user_number):
    memory = load_memory()
    
    if user_number not in memory:
        return True
    
    user_data = memory[user_number]
    
    if isinstance(user_data, str):
        user_data = {
            "last_interaction": user_data,
            "message_count": 1,
            "last_reset_date": datetime.now().date().isoformat()
        }
        memory[user_number] = user_data
        save_memory(memory)
    
    current_date = datetime.now().date().isoformat()
    
    if user_data.get("last_reset_date") != current_date:
        user_data["message_count"] = 0
        user_data["last_reset_date"] = current_date
    
    if user_data.get("message_count", 0) < 100:
        user_data["message_count"] = user_data.get("message_count", 0) + 1
        user_data["last_interaction"] = datetime.now().isoformat()
        memory[user_number] = user_data
        save_memory(memory)
        return True
    else:
        return False

def get_rate_limit_message():
    return "hey, hit my daily message limit (10/day) - catch you tomorrow? 𐔌՞- .-՞𐦯"

def log_interaction(user_number):
    memory = load_memory()
    
    if user_number not in memory:
        memory[user_number] = {
            "last_interaction": datetime.now().isoformat(),
            "message_count": 1,
            "last_reset_date": datetime.now().date().isoformat()
        }
    else:
        if isinstance(memory[user_number], str):
            memory[user_number] = {
                "last_interaction": memory[user_number],
                "message_count": 1,
                "last_reset_date": datetime.now().date().isoformat()
            }
        else:
            memory[user_number]["last_interaction"] = datetime.now().isoformat()
    
    save_memory(memory)

# ============================================
# WEBHOOK
# ============================================
@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming = request.values
    from_number = incoming.get('From')
    
    print(f"\n=== message from {from_number} ===")
    
    if not check_rate_limit(from_number):
        resp = MessagingResponse()
        resp.message(get_rate_limit_message())
        return str(resp)
    
    greeting = ""
    if should_greet(from_number):
        greeting = "yoooo, whats up? send me your vocals 𐔌՞x .x՞𐦯\n\n"
    
    try:
        if incoming.get('Body') and not incoming.get('MediaUrl0'):
            message = incoming.get('Body')
            response_text = greeting + get_choi_response(message)
        
        elif incoming.get('MediaUrl0') and 'audio' in incoming.get('MediaContentType0', ''):
            audio_url = incoming.get('MediaUrl0')
            print(f"transcribing voice note")
            transcription = transcribe_audio(audio_url)
            print(f"transcribed: {transcription}")
            
            log_submission(from_number, transcription)
            voice_context = f"[fan sent vocals]: {transcription}"
            response_text = greeting + get_choi_response(voice_context)
        
        elif incoming.get('MediaUrl0') and 'image' in incoming.get('MediaContentType0', ''):
            image_url = incoming.get('MediaUrl0')
            caption = incoming.get('Body', 'what do you think of this?')
            response_text = greeting + get_choi_response_with_image(caption, image_url)
        
        else:
            response_text = "hey, send me text, voice, or image 𐔌՞o .o՞𐦯"
    
    except Exception as e:
        print(f"ERROR: {e}")
        response_text = "ah sorry, something went weird. try again? 𐔌՞- .-՞𐦯"
    
    log_interaction(from_number)
    
    resp = MessagingResponse()
    resp.message(response_text)
    
    print(f"response: {response_text}\n")
    return str(resp)

# ============================================
# LAUNCH
# ============================================
if __name__ == '__main__':
    print("=" * 50)
    print("CHOI VOICE COLLECTOR")
    print("=" * 50)
    app.run(port=5000, debug=True)