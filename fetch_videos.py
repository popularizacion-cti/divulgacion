import pandas as pd
import feedparser
import json
import requests
from datetime import datetime

# CONFIGURACIÓN
# Sustituye esto por el ID de tu hoja de cálculo
SHEET_ID = "1l5VMGQg-Udh1_auqrJF1r21cE-b5nUPS112muKE6joQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def get_latest_from_rss(channel_id):
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)
    if feed.entries:
        entry = feed.entries[0]
        v_id = entry.link.split('v=')[1]
        return {
            "title": entry.title,
            "videoId": v_id,
            "description": entry.summary[:200] + "...", # Descripción corta
            "thumbnail": f"https://img.youtube.com/vi/{v_id}/maxresdefault.jpg",
            "publishedAt": entry.published,
            "channelTitle": feed.feed.title,
            "url": entry.link
        }
    return None

def main():
    # 1. Leer IDs desde Google Sheets
    df = pd.read_csv(SHEET_URL)
    channel_ids = df.iloc[:, 7].tolist() # Toma la primera columna

    all_videos = []
    for cid in channel_ids:
        try:
            video = get_latest_from_rss(cid.strip())
            if video:
                all_videos.append(video)
        except:
            print(f"Error con canal: {cid}")

    # 2. Ordenar por fecha (más recientes primero)
    all_videos.sort(key=lambda x: x['publishedAt'], reverse=True)

    # 3. Guardar en JSON
    with open('videos.json', 'w', encoding='utf-8') as f:
        json.dump(all_videos, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
