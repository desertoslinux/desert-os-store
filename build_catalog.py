import json
import urllib.request

# Карта соответствия категорий AppImageHub системным категориям Desert OS
CATEGORY_MAP = {
    "Game": ["Game", "ActionGame", "AdventureGame", "ArcadeGame", "BoardGame", "BlocksGame", "CardGame", "KidsGame", "LogicGame", "RolePlaying", "Simulation", "SportsGame", "StrategyGame"],
    "Network": ["Network", "WebBrowser", "Email", "Chat", "InstantMessaging", "FileTransfer", "P2P"],
    "Graphics": ["Graphics", "3DGraphics", "Photography", "RasterGraphics", "VectorGraphics", "ImageProcessing"],
    "Office": ["Office", "WordProcessor", "Spreadsheet", "Presentation", "Publishing", "Finance", "Dictionary"],
    "AudioVideo": ["AudioVideo", "Audio", "Video", "AudioVideoEditing", "Player", "Recorder", "Music"],
    "Development": ["Development", "Building", "Debugger", "IDE", "Profiling", "Translation", "WebDevelopment"]
}

def map_category(raw_categories):
    if not raw_categories:
        return "Desert" 
    
    for app_cat in raw_categories:
        for desert_cat, keywords in CATEGORY_MAP.items():
            if app_cat in keywords:
                return desert_cat
                
    return "Desert" 

catalog = []
feed_url = "https://appimage.github.io/feed.json"

try:
    req = urllib.request.Request(feed_url, headers={'User-Agent': 'Desert-OS-Builder'})
    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode())
        for app in data.get('items', []):
            links = app.get('links', [])
            download_url = next((link['url'] for link in links if link.get('type') == 'Download'), None)
            
            if download_url and download_url.lower().endswith('.appimage'):
                raw_cats = app.get('categories', [])
                desert_category = map_category(raw_cats)
                
                # Защита от слишком длинных описаний, ломающих интерфейс
                summary_text = app.get("description", "AppImage Package")
                if len(summary_text) > 60:
                    summary_text = summary_text[:57] + "..."
                
                catalog.append({
                    "name": app.get("name", "Unknown"),
                    "summary": summary_text,
                    "desc": app.get("description", ""),
                    "url": download_url,
                    "icon": app.get("name", "").lower().replace(" ", "-"),
                    "category": desert_category
                })
except Exception as e:
    print(f"Ошибка загрузки базы: {e}")

with open('appimages.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=4, ensure_ascii=False)
