import pandas as pd
import feedparser
import json
import re
from datetime import datetime

# CONFIGURACIÓN
SHEET_ID = "1l5VMGQg-Udh1_auqrJF1r21cE-b5nUPS112muKE6joQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def get_latest_from_rss(channel_id):
    # Limpiamos el ID por si tiene espacios
    channel_id = channel_id.strip()
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)
    
    if feed.entries:
        entry = feed.entries[0]
        # Extraer ID de video de forma segura
        v_id = ""
        if 'yt_videoid' in entry:
            v_id = entry.yt_videoid
        else:
            v_id = entry.link.split('v=')[1].split('&')[0]

        # PROCESO DE FECHA ROBUSTO
        # Intentamos parsear la fecha de YouTube (ej: 2026-03-24T20:00:00+00:00)
        try:
            # Reemplazamos 'Z' por +00:00 para que Python lo entienda siempre
            raw_date = entry.published.replace('Z', '+00:00')
            fecha_obj = datetime.fromisoformat(raw_date)
            timestamp = fecha_obj.timestamp() # Número real para ordenar sin errores
        except:
            timestamp = 0

        return {
            "title": entry.title,
            "videoId": v_id,
            "description": entry.summary[:180] + "..." if 'summary' in entry else "",
            "thumbnail": f"https://img.youtube.com/vi/{v_id}/maxresdefault.jpg",
            "publishedAt": entry.published,
            "timestamp": timestamp,
            "channelTitle": feed.feed.title,
            "url": entry.link
        }
    return None

def main():
    try:
        df = pd.read_csv(SHEET_URL)
        # Aseguramos que lea la primera columna sin importar el nombre
        channel_ids = df.iloc[:, 7].dropna().unique().tolist()
    except Exception as e:
        print(f"Error leyendo Google Sheets: {e}")
        return

    all_videos = []
    for cid in channel_ids:
        print(f"Procesando: {cid}")
        try:
            video = get_latest_from_rss(cid)
            if video:
                all_videos.append(video)
        except Exception as e:
            print(f"Error con canal {cid}: {e}")

    # ORDENAR POR TIMESTAMP (El número más grande es el más reciente)
    all_videos.sort(key=lambda x: x['timestamp'], reverse=True)

    # Guardar JSON
    with open('videos.json', 'w', encoding='utf-8') as f:
        json.dump(all_videos, f, indent=4, ensure_ascii=False)
    print(f"Proceso finalizado. {len(all_videos)} videos guardados.")

if __name__ == "__main__":
    main()
