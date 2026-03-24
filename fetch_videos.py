import pandas as pd
import feedparser
import json
from datetime import datetime

# CONFIGURACIÓN
SHEET_ID = "1l5VMGQg-Udh1_auqrJF1r21cE-b5nUPS112muKE6joQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def get_latest_from_rss(channel_id):
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)
    if feed.entries:
        entry = feed.entries[0]
        v_id = entry.link.split('v=')[1]
        
        # Convertimos la fecha de texto a un objeto de fecha real para ordenar bien
        # YouTube usa el formato ISO 8601
        fecha_obj = datetime.fromisoformat(entry.published.replace('Z', '+00:00'))

        return {
            "title": entry.title,
            "videoId": v_id,
            "description": entry.summary[:200] + "...",
            "thumbnail": f"https://img.youtube.com/vi/{v_id}/maxresdefault.jpg",
            "publishedAt": fecha_obj.isoformat(), # Guardamos como ISO estándar
            "channelTitle": feed.feed.title,
            "url": entry.link
        }
    return None

def main():
    df = pd.read_csv(SHEET_URL)
    channel_ids = df.iloc[:, 7].tolist()

    all_videos = []
    for cid in channel_ids:
        try:
            video = get_latest_from_rss(cid.strip())
            if video:
                all_videos.append(video)
        except Exception as e:
            print(f"Error con canal {cid}: {e}")

    # ORDENAR CRÍTICAMENTE: Aquí nos aseguramos que el más nuevo esté arriba
    all_videos.sort(key=lambda x: x['publishedAt'], reverse=True)

    with open('videos.json', 'w', encoding='utf-8') as f:
        json.dump(all_videos, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
