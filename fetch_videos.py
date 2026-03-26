import pandas as pd
import feedparser
import json
import re
from datetime import datetime

# CONFIGURACIÓN
SHEET_ID = "1l5VMGQg-Udh1_auqrJF1r21cE-b5nUPS112muKE6joQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def get_channel_data(channel_id):
    if not isinstance(channel_id, str) or len(channel_id.strip()) < 5:
        return None, None
    
    channel_id = channel_id.strip()
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)
    
    if not feed.entries:
        return None, None

    videos = []
    shorts = []

    for entry in feed.entries:
        try:
            v_id = entry.yt_videoid if 'yt_videoid' in entry else entry.link.split('v=')[1].split('&')[0]
            
            # Detección de Shorts
            is_short = "/shorts/" in entry.link or "#shorts" in entry.title.lower() or "short" in entry.title.lower()

            raw_date = entry.published.replace('Z', '+00:00')
            fecha_obj = datetime.fromisoformat(raw_date)
            
            data = {
                "title": entry.title,
                "videoId": v_id,
                "thumbnail": f"https://img.youtube.com/vi/{v_id}/maxresdefault.jpg",
                "backup_thumb": f"https://img.youtube.com/vi/{v_id}/hqdefault.jpg",
                "publishedAt": fecha_obj.strftime("%d/%m/%Y"),
                "timestamp": fecha_obj.timestamp(),
                "channelTitle": feed.feed.title,
                "url": entry.link
            }

            if is_short:
                shorts.append(data)
            else:
                videos.append(data)
        except:
            continue

    # Obtenemos el más reciente de cada tipo por canal
    v = sorted(videos, key=lambda x: x['timestamp'], reverse=True)[0] if videos else None
    s = sorted(shorts, key=lambda x: x['timestamp'], reverse=True)[0] if shorts else None
    return v, s

def main():
    try:
        df = pd.read_csv(SHEET_URL)
        # Columna 8 (índice 7) es ID, Columna 3 (índice 2) es Idioma
        canales_info = df.iloc[:, [7, 2]].dropna()
    except Exception as e:
        print(f"Error leyendo Google Sheets: {e}")
        return

    final_videos = []
    final_shorts = []
    final_ingles = []

    for _, row in canales_info.iterrows():
        cid = str(row.iloc[0]).strip()
        idioma = str(row.iloc[1]).lower().strip()
        
        print(f"Procesando: {cid} | Idioma: {idioma}")
        v, s = get_channel_data(cid)
        
        if v or s:
            # Si el idioma es inglés, mandamos el video a la lista de inglés
            if "inglés" in idioma or "ingles" in idioma or "english" in idioma:
                if v: final_ingles.append(v)
                # Si quisieras shorts en inglés por separado, podrías crear otra lista
            else:
                # Si es español u otro, va a las secciones normales
                if v: final_videos.append(v)
                if s: final_shorts.append(s)

    # Ordenar todas las listas por fecha (lo más nuevo primero)
    final_videos.sort(key=lambda x: x['timestamp'], reverse=True)
    final_shorts.sort(key=lambda x: x['timestamp'], reverse=True)
    final_ingles.sort(key=lambda x: x['timestamp'], reverse=True)

    # Guardar el JSON estructurado
    resultado = {
        "videos": final_videos,
        "shorts": final_shorts,
        "ingles": final_ingles
    }

    with open('videos.json', 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=4, ensure_ascii=False)
    
    print(f"Proceso completado. Videos: {len(final_videos)}, Shorts: {len(final_shorts)}, Inglés: {len(final_ingles)}")

if __name__ == "__main__":
    main()
