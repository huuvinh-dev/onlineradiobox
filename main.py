import time
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://onlineradiobox.com/",
    "Origin": "https://onlineradiobox.com",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}

def fetch_current_song(station_alias="au.cherry"):
    url = f"https://scraper2.onlineradiobox.com/{station_alias}?l=0"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print(f"Lỗi kết nối: {e}")
    return None

def monitor_station(station_alias="au.cherry", interval_seconds=10):
    last_track_id = None
    print(f"Bắt đầu theo dõi kênh: {station_alias}...")

    while True:
        data = fetch_current_song(station_alias)
        if data:
            current_track_id = data.get("trackId")
            
            # Chỉ thông báo khi đổi sang bài hát mới
            if current_track_id != last_track_id:
                last_track_id = current_track_id
                print("=" * 50)
                print(f"🎵 BÀI HÁT ĐANG PHÁT: {data.get('title')}")
                print(f"🎤 Ca sĩ: {data.get('iArtist')}")
                print(f"🎼 Tên bài: {data.get('iName')}")
                print(f"🖼️  Ảnh bìa: {data.get('iImg')}")
                print("=" * 50)
        
        time.sleep(interval_seconds)

if __name__ == "__main__":
    monitor_station("au.cherry", interval_seconds=10)
