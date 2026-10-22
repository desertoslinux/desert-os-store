import json
import urllib.request
import sys

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
        raw_data = response.read()
        data = json.loads(raw_data.decode())
        items = data.get('items', [])
        processed_count = 0
        
        for app in items:
            name = app.get('title', 'Unknown')
            download_url = None
            attachments = app.get('attachments', [])
            for att in attachments:
                url = att.get('url', '')
                if url.lower().endswith('.appimage'):
                    download_url = url
                    break
            
            if download_url:
                raw_cats = app.get('tags', [])
                desert_category = map_category(raw_cats)
                desc = app.get('summary', '') or app.get('content_text', 'AppImage Package')
                summary_text = desc
                if len(summary_text) > 60:
                    summary_text = summary_text[:57] + "..."
                
                catalog.append({
                    "name": name,
                    "summary": summary_text,
                    "desc": desc,
                    "url": download_url,
                    "icon": name.lower().replace(" ", "-"),
                    "category": desert_category
                })
                processed_count += 1
                
except Exception as e:
    sys.exit(1)

with open('appimages.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=4, ensure_ascii=False)
    
