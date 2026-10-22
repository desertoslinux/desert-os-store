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
    print("Запуск скрипта...", flush=True)
    req = urllib.request.Request(feed_url, headers={'User-Agent': 'Desert-OS-Builder'})
    with urllib.request.urlopen(req, timeout=30) as response:
        raw_data = response.read()
        print(f"Получено {len(raw_data)} байт данных.", flush=True)
        data = json.loads(raw_data.decode())
        items = data.get('items', [])
        print(f"Найдено приложений в фиде: {len(items)}", flush=True)
        processed_count = 0
        
        for app in items:
            name = app.get('title', 'Unknown')
            download_url = None
            attachments = app.get('attachments', [])
            for att in attachments:
                url = att.get('url', '')
                if url.lower().endswith('.appimage') or 'appimage' in url.lower():
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
                
        print(f"Обработка завершена. Всего добавлено: {processed_count}", flush=True)

except Exception as e:
    print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}", flush=True)
    sys.exit(1)

with open('appimages.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=4, ensure_ascii=False)
print("Файл appimages.json успешно записан.", flush=True)
