#! /usr/bin/python3

import re

def get_yt_thumbnail(url):
    """Generiert automatisch den Thumbnail-Link aus einer YouTube-URL."""
    # Sucht nach der 11-stelligen Video-ID in verschiedenen YouTube-Linkformaten
    pattern = r'(?:v=|\/([0-9A-Za-z_-]{11}).*|youtu\.be\/|embed\/|live\/)([0-9A-Za-z_-]{11})'
    match = re.search(pattern, url)
    if match:
        video_id = match.group(1) or match.group(2)
        return f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
    return ""

def get_channel_name(url):
    """Liest den YouTube-Kanalnamen dynamisch aus der Seite aus."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        resp = requests.get(url, headers=headers, timeout=10).text
        match = re.search(r'"author":"([^"]+)"', resp)
        if match:
            return match.group(1)
        match_meta = re.search(r'<meta itemprop="name" content="([^"]+)">', resp)
        if match_meta:
            return match_meta.group(1)
    except Exception:
        pass
    return None

# M3U Header
print('#EXTM3U')

with open('../youtube_channel_info.txt', errors="ignore") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('~~'):
            continue
        
        parts = [p.strip() for p in line.split('|')]
        
        # Flexibel: Funktioniert mit 3 oder 4 Parametern
        if len(parts) >= 3:
            ch_name = parts[0]
            grp_title = parts[1].title()
            
            # Falls nur 3 Parameter da sind (Name | Gruppe | URL)
            if len(parts) == 3:
                yt_url = parts[2]
                tvg_logo = get_yt_thumbnail(yt_url)
            else:
                # Falls 4 Parameter da sind (Name | Gruppe | Logo | URL)
                # Nimmt das angegebene Logo, oder generiert es falls das Feld leer ist
                tvg_logo = parts[2] if parts[2] else get_yt_thumbnail(parts[3])
                yt_url = parts[3]
            
            # Kanalname automatisch ermitteln
            extracted_channel = get_channel_name(yt_url)
            tvg_id = extracted_channel if extracted_channel else ch_name
            
            # 1. Zeile der M3U
            print(f'\n#EXTINF:-1 tvg-id="{tvg_id}" group-title="{grp_title}" tvg-logo="{tvg_logo}", {ch_name}')
            
            # 2. Zeile: Stream-URL
            if 'youtube.com' in yt_url or 'youtu.be' in yt_url:
                stream_url = grab(yt_url)
                print(stream_url if stream_url else yt_url)
            else:
                print(yt_url)  os.remove('temp.txt')
