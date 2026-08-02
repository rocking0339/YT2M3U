#! /usr/bin/python3

import requests
import os
import sys
import re

windows = False
if 'win' in sys.platform:
    windows = True

def grab(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=15).text
        if '.m3u8' not in response:
            if not windows:
                os.system(f'wget "{url}" -O temp.txt')
                with open('temp.txt', errors="ignore") as tf:
                    response = tf.read()
            
            # Falls immer noch keine m3u8 gefunden wurde: originale YouTube-URL nutzen
            if '.m3u8' not in response:
                return url
        
        end = response.find('.m3u8') + 5
        tuner = 100
        while True:
            if 'https://' in response[end-tuner : end]:
                link = response[end-tuner : end]
                start = link.find('https://')
                end = link.find('.m3u8') + 5
                return link[start : end]
            else:
                tuner += 5
    except Exception:
        # Bei einem Verbindungsfehler ebenfalls die direkte URL zurückgeben
        return url
        
        end = response.find('.m3u8') + 5
        tuner = 100
        while True:
            if 'https://' in response[end-tuner : end]:
                link = response[end-tuner : end]
                start = link.find('https://')
                end = link.find('.m3u8') + 5
                return link[start : end]
            else:
                tuner += 5
    except Exception:
        return url

def get_yt_thumbnail(url):
    """Generiert automatisch den Thumbnail-Link aus einer YouTube-URL."""
    try:
        match = re.search(r'(?:v=|\/([0-9A-Za-z_-]{11}).*|youtu\.be\/|embed\/|live\/)([0-9A-Za-z_-]{11})', url)
        if match:
            video_id = match.group(1) or match.group(2)
            if video_id:
                return f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
    except Exception:
        pass
    return ""

def get_channel_name(url):
    """Liest den YouTube-Kanalnamen dynamisch aus der Seite aus."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        resp = requests.get(url, headers=headers, timeout=8).text
        match = re.search(r'"author":"([^"]+)"', resp)
        if match:
            return match.group(1)
        match_meta = re.search(r'<meta itemprop="name" content="([^"]+)">', resp)
        if match_meta:
            return match_meta.group(1)
    except Exception:
        pass
    return None

# M3U Header ausgeben
print('#EXTM3U')

# txt-Datei einlesen
try:
    with open('../youtube_channel_info.txt', errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('~~'):
                continue
            
            parts = [p.strip() for p in line.split('|')]
            
            # Mindestens 3 Teile erforderlich (Titel | Gruppe | URL oder Logo)
            if len(parts) >= 3:
                ch_name = parts[0]
                grp_title = parts[1].title()
                
                # Wenn 3 Spalten: Name | Gruppe | YouTube-URL
                if len(parts) == 3:
                    yt_url = parts[2]
                    tvg_logo = get_yt_thumbnail(yt_url)
                # Wenn 4 oder mehr Spalten: Name | Gruppe | Logo | YouTube-URL
                else:
                    yt_url = parts[3]
                    tvg_logo = parts[2] if parts[2] else get_yt_thumbnail(yt_url)
                
                # Kanalname als tvg-id abrufen (sonst Titel als Fallback)
                extracted_channel = get_channel_name(yt_url)
                tvg_id = extracted_channel if extracted_channel else ch_name
                
                # 1. Zeile der M3U
                print(f'\n#EXTINF:-1 tvg-id="{tvg_id}" group-title="{grp_title}" tvg-logo="{tvg_logo}", {ch_name}')
                
                # 2. Zeile: Stream-URL
                if 'youtube.com' in yt_url or 'youtu.be' in yt_url:
                    stream_url = grab(yt_url)
                    print(stream_url if stream_url else yt_url)
                else:
                    print(yt_url)
except Exception as e:
    sys.stderr.write(f"Fehler beim Einlesen: {e}\n")

# Aufräumen
if 'temp.txt' in os.listdir():
    try:
        os.remove('temp.txt')
    except Exception:
        pass
