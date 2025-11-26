import json
from collections import Counter

def show_analytics():
    try:
        with open('voice_submissions.json', 'r') as f:
            submissions = json.load(f)
    except:
        print("no data yet")
        return
    
    locations = []
    songs = []
    
    for user, subs in submissions.items():
        for sub in subs:
            locations.append(sub.get('location_guess', 'unknown'))
            if sub.get('song_detected'):
                songs.append(sub['song_detected'])
    
    print("=== SUBMISSION ANALYTICS ===")
    print(f"Total submissions: {sum(len(subs) for subs in submissions.values())}")
    print(f"Unique users: {len(submissions)}")
    
    print(f"\nLOCATIONS:")
    location_counts = Counter(locations)
    for location, count in location_counts.most_common():
        print(f"  {location}: {count}")
    
    print(f"\nSONGS:")
    song_counts = Counter(songs)
    for song, count in song_counts.most_common():
        if song:  # Skip None/empty
            print(f"  {song}: {count}")
    
    # Popular songs by location
    print(f"\nSONGS BY LOCATION:")
    location_songs = {}
    for user, subs in submissions.items():
        for sub in subs:
            location = sub.get('location_guess', 'unknown')
            song = sub.get('song_detected')
            if song:
                if location not in location_songs:
                    location_songs[location] = []
                location_songs[location].append(song)
    
    for location, song_list in location_songs.items():
        most_common_song = Counter(song_list).most_common(1)
        if most_common_song:
            print(f"  {location}: {most_common_song[0][0]} ({most_common_song[0][1]}x)")

if __name__ == '__main__':
    show_analytics()