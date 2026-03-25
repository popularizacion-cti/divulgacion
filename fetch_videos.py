import pandas as pd
import feedparser
import json
from datetime import datetime

SHEET_ID = "1l5VMGQg-Udh1_auqrJF1r21cE-b5nUPS112muKE6joQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def get_channel_data(channel_id):
    channel_id = channel_id.strip()
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)
    
    if not feed.entries:
        return None

    videos = []
    shorts = []

    for entry in feed.entries:
        v_id = entry.yt_videoid if 'yt_videoid' in entry else entry.link.split('v=')[1].split('&')[0]
        
        # Determinar si es Short (Probamos buscando la palabra en el título o descripción, 
        # aunque el RSS de YT no lo etiqueta perfecto, es una buena aproximación)
        is_short = "/shorts/" in entry.link or "#shorts" in entry.title.lower()

        raw_date = entry.published.replace('Z', '+00:00')
        fecha_obj = datetime.fromisoformat(raw_date)
        
        data = {
            "title": entry.title,
            "videoId": v_id,
            "description": entry.summary[:150] + "..." if 'summary' in entry else "",
            "thumbnail": f"https://img.youtube.com/vi/{v_id}/maxresdefault.jpg",
            "backup_thumb": f"https://img.youtube.com/vi/{v_id}/hqdefault.jpg",
            "publishedAt": fecha_obj.strftime("%d/%m/%Y"), # Fecha formateada
            "timestamp": fecha_obj.timestamp(),
            "channelTitle": feed.feed.title,
            "url": entry.link
        }

        if is_short:
            shorts.append(data)
        else:
            videos.append(data)

    # Devolvemos solo el más reciente de cada categoría por canal
    latest_video = sorted(videos, key=lambda x: x['timestamp'], reverse=True)[0] if videos else None
    latest_short = sorted(shorts, key=lambda x: x['timestamp'], reverse=True)[0] if shorts else None
    
    return latest_video, latest_short

def main():
    df = pd.read_csv(SHEET_URL)
    channel_ids = df.iloc[:, 7].dropna().unique().tolist()

    final_videos = []
    final_shorts = []

    for cid in channel_ids:
        v, s = get_channel_data(cid)
        if v: final_videos.append(v)
        if s: final_shorts.append(s)

    # Ordenar globales por fecha
    final_videos.sort(key=lambda x: x['timestamp'], reverse=True)
    final_shorts.sort(key=lambda x: x['timestamp'], reverse=True)

    with open('videos.json', 'w', encoding='utf-8') as f:
        json.dump({"videos": final_videos, "shorts": final_shorts}, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
