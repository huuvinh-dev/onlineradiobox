import os
import requests
from fastapi import FastAPI

app = FastAPI()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://onlineradiobox.com/",
    "Origin": "https://onlineradiobox.com",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}

@app.get("/")
def home():
    return {"message": "API đang chạy! Truy cập /now-playing để lấy tên bài hát."}

@app.get("/now-playing")
def get_now_playing(station: str = "au.cherry"):
    url = f"https://scraper2.onlineradiobox.com/{station}?l=0"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            return {
                "success": True,
                "station": station,
                "title": data.get("title"),
                "artist": data.get("iArtist"),
                "song": data.get("iName"),
                "image": data.get("iImg"),
                "trackId": data.get("trackId")
            }
    except Exception as e:
        return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "Không lấy được dữ liệu"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
