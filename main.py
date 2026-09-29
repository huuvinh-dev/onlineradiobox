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
def get_now_playing(station: str = "au.cherry", l: int = 0):
    # Truyền tham số l vào URL (mặc định là 0 nếu gọi lần đầu)
    url = f"https://scraper2.onlineradiobox.com/{station}?l={l}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            return {
                "success": True,
                "station": station,
                "updated": data.get("updated"), # Trả về timestamp để dùng cho lần gọi tiếp theo
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
