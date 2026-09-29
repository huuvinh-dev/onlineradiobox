import os
import json
import asyncio
import httpx
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://onlineradiobox.com/",
    "Origin": "https://onlineradiobox.com",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}

def format_track_data(station: str, data: dict) -> dict:
    return {
        "success": True,
        "station": station,
        "updated": data.get("updated"),
        "title": data.get("title"),
        "artist": data.get("iArtist"),
        "song": data.get("iName"),
        "image": data.get("iImg"),
        "trackId": data.get("trackId")
    }

@app.get("/")
def home():
    return {
        "message": "API đang chạy!",
        "endpoints": {
            "single_request": "/now-playing?station=au.cherry",
            "continuous_stream": "/now-playing/stream?station=au.cherry"
        }
    }

# 1. Endpoint lấy dữ liệu 1 lần
@app.get("/now-playing")
async def get_now_playing(station: str = "au.cherry", l: int = 0):
    url = f"https://scraper2.onlineradiobox.com/{station}?l={l}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            res = await client.get(url, headers=HEADERS)
            if res.status_code == 200:
                return format_track_data(station, res.json())
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    return {"success": False, "error": "Không lấy được dữ liệu"}

# 2. Generator đẩy dữ liệu liên tục cho SSE
async def song_stream_generator(station: str):
    l_param = 0
    async with httpx.AsyncClient(timeout=60.0) as client:
        while True:
            url = f"https://scraper2.onlineradiobox.com/{station}?l={l_param}"
            try:
                res = await client.get(url, headers=HEADERS)
                if res.status_code == 200:
                    data = res.json()
                    if data and "updated" in data:
                        l_param = data["updated"]
                        payload = format_track_data(station, data)
                        yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                    else:
                        await asyncio.sleep(3)
                else:
                    await asyncio.sleep(5)
            except httpx.ReadTimeout:
                # Timeout long-polling từ phía nguồn, tự động gửi lại request
                continue
            except Exception as e:
                error_payload = {"success": False, "error": str(e)}
                yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"
                await asyncio.sleep(5)

# Endpoint phát stream liên tục
@app.get("/now-playing/stream")
async def stream_now_playing(station: str = "au.cherry"):
    return StreamingResponse(
        song_stream_generator(station), 
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
