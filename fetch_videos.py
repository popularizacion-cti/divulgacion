import pandas as pd
import feedparser
import json
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
            if is_short: shorts.append(data)
            else: videos.append(data)
        except: continue

    v = sorted(videos, key=lambda x: x['timestamp'], reverse=True)[0] if videos else None
    s = sorted(shorts, key=lambda x: x['timestamp'], reverse=True)[0] if shorts else None
    return v, s

def main():
    df = pd.read_csv(SHEET_URL)
    canales_info = df.iloc[:, [7, 2]].dropna() # Columna 8 (ID) e índice 2 (Idioma/Col 3)

    res = {"videos": [], "shorts": [], "ingles_v": [], "ingles_s": []}

    for _, row in canales_info.iterrows():
        cid = str(row.iloc[0]).strip()
        idioma = str(row.iloc[1]).lower().strip()
        v, s = get_channel_data(cid)
        
        is_en = any(x in idioma for x in ["Inglés", "Ingles", "English", "en"])

        if is_en:
            if v: res["ingles_v"].append(v)
            if s: res["ingles_s"].append(s)
        else:
            if v: res["videos"].append(v)
            if s: res["shorts"].append(s)

    # Ordenar todas las listas
    for key in res:
        res[key].sort(key=lambda x: x['timestamp'], reverse=True)

    with open('videos.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
