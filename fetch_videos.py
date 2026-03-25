import pandas as pd
import feedparser
import json
from datetime import datetime

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
        v_id = entry.yt_videoid if 'yt_videoid' in entry else entry.link.split('v=')[1].split('&')[0]
        
        # Detección de Shorts mejorada
        is_short = "/shorts/" in entry.link or "#shorts" in entry.title.lower() or "short" in entry.title.lower()

        raw_date = entry.published.replace('Z', '+00:00')
        fecha_obj = datetime.fromisoformat(raw_date)
        
        data = {
            "title": entry.title,
            "videoId": v_id,
            "description": entry.summary[:120] + "..." if 'summary' in entry else "",
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

    v = sorted(videos, key=lambda x: x['timestamp'], reverse=True)[0] if videos else None
    s = sorted(shorts, key=lambda x: x['timestamp'], reverse=True)[0] if shorts else None
    return v, s

def main():
    df = pd.read_csv(SHEET_URL)
    # CAMBIO: Ahora toma la OCTAVA COLUMNA (índice 7)
    channel_ids = df.iloc[:, 7].dropna().unique().tolist()

    final_videos = []
    final_shorts = []

    for cid in channel_ids:
        v, s = get_channel_data(cid)
        if v: final_videos.append(v)
        if s: final_shorts.append(s)

    final_videos.sort(key=lambda x: x['timestamp'], reverse=True)
    final_shorts.sort(key=lambda x: x['timestamp'], reverse=True)

    with open('videos.json', 'w', encoding='utf-8') as f:
        json.dump({"videos": final_videos, "shorts": final_shorts}, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
