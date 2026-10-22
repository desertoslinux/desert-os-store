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
        return "Tools"
    for app_cat in raw_categories:
        for desert_cat, keywords in CATEGORY_MAP.items():
            if app_cat in keywords:
                return desert_cat
    return "Tools"

def is_valid_appimage_url(url):
    url_lower = url.lower()
    return '.appimage' in url_lower or ('appimage' in url_lower and ('github.com' in url_lower or 'gitlab.com' in url_lower))

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
            name = app.get('name') or app.get('title') or 'Unknown'
            download_url = None
            
            links = app.get('links') or []
            for link in links:
                url = link.get('url', '')
                if is_valid_appimage_url(url):
                    download_url = url
                    break
            
            if not download_url:
                attachments = app.get('attachments') or []
                for att in attachments:
                    url = att.get('url', '')
                    if is_valid_appimage_url(url):
                        download_url = url
                        break
            
            if download_url:
                raw_cats = app.get('tags') or app.get('categories') or []
                if isinstance(raw_cats, str):
                    raw_cats = [raw_cats]
                    
                desert_category = map_category(raw_cats)
                desc = app.get('summary', '') or app.get('content_text', 'AppImage Package')
                summary_text = desc
                if len(summary_text) > 60:
                    summary_text = summary_text[:57] + "..."
                
                icon = app.get('image') or app.get('icon') or name.lower().replace(" ", "-")
                
                catalog.append({
                    "name": name,
                    "summary": summary_text,
                    "desc": desc,
                    "url": download_url,
                    "icon": icon,
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
