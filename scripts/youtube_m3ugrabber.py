#! /usr/bin/python3

import requests
import os
import sys

windows = False
if 'win' in sys.platform:
    windows = True

def grab(url):
    try:
        response = requests.get(url, timeout=15).text
        if '.m3u8' not in response:
            if windows:
                return 'https://raw.githubusercontent.com/vijay6672/YT2M3U/main/assets/moose_na.m3u'
            os.system(f'wget "{url}" -O temp.txt')
            with open('temp.txt', errors="ignore") as tf:
                response = tf.read()
            if '.m3u8' not in response:
                return 'https://raw.githubusercontent.com/vijay6672/YT2M3U/main/assets/moose_na.m3u'
        
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
        return 'https://raw.githubusercontent.com/vijay6672/YT2M3U/main/assets/moose_na.m3u'

# M3U Header (Banner entfernt)
print('#EXTM3U')

with open('../youtube_channel_info.txt', errors="ignore") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('~~'):
            continue
        
        # Zeile aufteilen
        parts = [p.strip() for p in line.split('|')]
        
        if len(parts) >= 4:
            ch_name = parts[0]
            grp_title = parts[1].title()
            tvg_logo = parts[2]
            yt_url = parts[3]  # Die YouTube-URL an 4. Stelle
            
            # 1. Zeile: Metadaten
            print(f'\n#EXTINF:-1 group-title="{grp_title}" tvg-logo="{tvg_logo}", {ch_name}')
            
            # 2. Zeile: Stream-URL auflösen oder direkte URL ausgeben
            if 'youtube.com' in yt_url or 'youtu.be' in yt_url:
                stream_url = grab(yt_url)
                print(stream_url if stream_url else yt_url)
            else:
                print(yt_url)

# Aufräumen
if 'temp.txt' in os.listdir():
    os.remove('temp.txt')
