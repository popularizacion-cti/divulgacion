import pandas as pd
import feedparser
import json
from datetime import datetime

# CONFIGURACIÓN
SHEET_ID = "1l5VMGQg-Udh1_auqrJF1r21cE-b5nUPS112muKE6joQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def get_latest_from_rss(channel_id):
    channel_id = channel_id.strip()
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)
    
    if not feed.entries:
        return None

    best_video = None
    max_timestamp = -1

    # REVISAMOS TODOS LOS VIDEOS DEL FEED (No solo el primero)
    for entry in feed.entries:
        try:
            # Extraer ID
            v_id = entry.yt_videoid if 'yt_videoid' in entry else entry.link.split('v=')[1].split('&')[0]
            
            # Convertir fecha a timestamp para comparar
            raw_date = entry.published.replace('Z', '+00:00')
            fecha_obj = datetime.fromisoformat(raw_date)
            current_timestamp = fecha_obj.timestamp()

            # Si este video es más reciente que el que teníamos guardado del mismo canal
            if current_timestamp > max_timestamp:
                max_timestamp = current_timestamp
                best_video = {
                    "title": entry.title,
                    "videoId": v_id,
                    "description": entry.summary[:180] + "..." if 'summary' in entry else "",
                    "thumbnail": f"https://img.youtube.com/vi/{v_id}/maxresdefault.jpg",
                    "backup_thumb": f"https://img.youtube.com/vi/{v_id}/hqdefault.jpg",
                    "publishedAt": entry.published,
                    "timestamp": current_timestamp,
                    "channelTitle": feed.feed.title,
                    "url": entry.link
                }
        except Exception as e:
            continue # Si un video da error, pasamos al siguiente del feed

    return best_video

def main():
    try:
        df = pd.read_csv(SHEET_URL)
        channel_ids = df.iloc[:, 7].dropna().unique().tolist()
    except Exception as e:
        print(f"Error Google Sheets: {e}")
        return

    all_channels_latest = []
    for cid in channel_ids:
        print(f"Buscando el más actual de: {cid}")
        video = get_latest_from_rss(cid)
        if video:
            all_channels_latest.append(video)

    # ORDENAR LA LISTA FINAL: Los 10 más recientes de toda la colección arriba
    all_channels_latest.sort(key=lambda x: x['timestamp'], reverse=True)

    with open('videos.json', 'w', encoding='utf-8') as f:
        json.dump(all_channels_latest, f, indent=4, ensure_ascii=False)
    
    print(f"Finalizado: {len(all_channels_latest)} canales procesados.")

if __name__ == "__main__":
    main()
