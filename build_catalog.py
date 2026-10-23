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

def is_safe_appimage_url(url):
    url_lower = url.lower()
    if not url_lower.endswith('.appimage'):
        return False
    wrong_archs = ['arm', 'aarch64', 'i386', 'i686', 'mac', 'win', 'zsync']
    for arch in wrong_archs:
        if arch in url_lower:
            return False
    return True

catalog = []
feed_url = "https://appimage.github.io/feed.json"

try:
    print("Запуск безопасного скрипта...", flush=True)
    req = urllib.request.Request(feed_url, headers={'User-Agent': 'Desert-OS-Builder'})
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode())
        items = data.get('items', [])
        processed_count = 0
        
        for app in items:
            name = app.get('name') or app.get('title') or 'Unknown'
            download_url = None
            
            for link in (app.get('links') or []):
                url = link.get('url', '')
                if is_safe_appimage_url(url):
                    if 'x86_64' in url.lower() or 'amd64' in url.lower():
                        download_url = url
                        break
                    if not download_url:
                        download_url = url

            if not download_url:
                for att in (app.get('attachments') or []):
                    url = att.get('url', '')
                    if is_safe_appimage_url(url):
                        if 'x86_64' in url.lower() or 'amd64' in url.lower():
                            download_url = url
                            break
                        if not download_url:
                            download_url = url
            
            if download_url:
                raw_cats = app.get('tags') or app.get('categories') or []
                if isinstance(raw_cats, str):
                    raw_cats = [raw_cats]
                    
                desc = app.get('summary', '') or app.get('content_text', 'AppImage Package')
                icon = app.get('image') or app.get('icon') or name.lower().replace(" ", "-").replace("-appimage", "")
                
                catalog.append({
                    "name": name,
                    "summary": desc[:57] + "..." if len(desc) > 60 else desc,
                    "desc": desc,
                    "url": download_url,
                    "icon": icon,
                    "category": map_category(raw_cats)
                })
                processed_count += 1
                
        print(f"Обработка завершена. Всего добавлено: {processed_count}", flush=True)

except Exception as e:
    print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}", flush=True)
    sys.exit(1)

with open('appimages.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=4, ensure_ascii=False)
print("Файл appimages.json успешно записан.", flush=True)
