import json
from datetime import datetime

def show_stats():
    try:
        with open('voice_submissions.json', 'r') as f:
            data = json.load(f)
    except:
        print("no data yet")
        return
    
    total_subs = 0
    unique_users = len(data)
    songs = {}
    
    for user, subs in data.items():
        total_subs += len(subs)
        for sub in subs:
            song = sub.get('song_detected', 'original')
            songs[song] = songs.get(song, 0) + 1
    
    print(f"=== SUBMISSION STATS ===")
    print(f"users: {unique_users}")
    print(f"total submissions: {total_subs}")
    print(f"\nSONGS:")
    for song, count in songs.items():
        print(f"  {song}: {count}")
    
    # Show latest submissions
    print(f"\nLATEST 5:")
    all_subs = []
    for user, subs in data.items():
        for sub in subs:
            all_subs.append((sub['timestamp'], user, sub['transcription'][:50] + "...", sub.get('song_detected', 'original')))
    
    all_subs.sort(reverse=True)
    for timestamp, user, text, song in all_subs[:5]:
        time = datetime.fromisoformat(timestamp).strftime("%m/%d %H:%M")
        print(f"  {time} - {song}")
        print(f"    {text}")

if __name__ == '__main__':
    show_stats()