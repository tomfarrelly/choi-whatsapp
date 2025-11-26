import json
from datetime import datetime

def review_voices():
    try:
        with open('voice_submissions.json', 'r') as f:
            submissions = json.load(f)
    except FileNotFoundError:
        print("no submissions yet")
        return
    
    print("=== VOICE SUBMISSIONS ===\n")
    total = 0
    
    for user_number, user_subs in submissions.items():
        location = user_subs[0].get('location', 'unknown') if user_subs else 'unknown'
        
        print(f"{user_number} ({location})")
        
        for sub in user_subs:
            total += 1
            time = datetime.fromisoformat(sub['timestamp']).strftime("%m/%d %H:%M")
            
            print(f"  {time}")
            print(f"  {sub['transcription']}")
            print(f"  audio: {sub.get('audio_file', '')}")
            print()
    
    print(f"📊 total: {total} submissions from {len(submissions)} users")

if __name__ == '__main__':
    review_voices()