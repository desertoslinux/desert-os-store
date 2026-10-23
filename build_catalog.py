import json
import urllib.request
import sys
import re

# Вставьте сюда ваш GitHub Personal Access Token (classic) для обхода лимита в 60 запросов/час.
# Оставьте пустым "", если токена пока нет (добавится около 60-80 приложений).
GITHUB_TOKEN = ""

CATEGORY_MAP = {
    "Game": ["Game", "ActionGame", "AdventureGame", "ArcadeGame", "BoardGame"],
    "Network": ["Network", "WebBrowser", "Email", "Chat", "P2P"],
    "Graphics": ["Graphics", "3DGraphics", "Photography", "ImageProcessing"],
    "Office": ["Office", "WordProcessor", "Spreadsheet", "Finance"],
    "AudioVideo": ["AudioVideo", "Audio", "Video", "Player"],
    "Development": ["Development", "Building", "Debugger", "IDE"]
}

def map_category(raw_categories):
    if not raw_categories: return "Tools"
    for app_cat in raw_categories:
        for desert_cat, keywords in CATEGORY_MAP.items():
            if app_cat in keywords: return desert_cat
    return "Tools"

def get_github_direct_link(github_url):
    match = re.search(r'github\.com/([^/]+)/([^/]+)', github_url)
    if not match: return None
    
    owner, repo = match.groups()
    repo = repo.replace('.git', '').replace('releases', '').strip('/')
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    
    headers = {'User-Agent': 'Desert-OS-Builder'}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
        
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            release_data = json.loads(response.read().decode())
            assets = release_data.get('assets', [])
            
            best_url = None
            for asset in assets:
                url = asset.get('browser_download_url', '')
                url_lower = url.lower()
                if url_lower.endswith('.appimage'):
                    if 'x86_64' in url_lower or 'amd64' in url_lower:
                        return url
                    best_url = url
            return best_url
    except Exception:
        return None

catalog = []
feed_url = "https://appimage.github.io/feed.json"

try:
    print("Запуск продвинутого скрипта (проверка GitHub API)...", flush=True)
    req = urllib.request.Request(feed_url, headers={'User-Agent': 'Desert-OS-Builder'})
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode())
        items = data.get('items', [])
        processed_count = 0
        
        for app in items:
            name = app.get('name') or app.get('title') or 'Unknown'
            download_url = None
            all_links = (app.get('links') or []) + (app.get('attachments') or [])
            
            # 1. Ищем готовую прямую ссылку
            for link in all_links:
                url = link.get('url', '')
                if url.lower().endswith('.appimage'):
                    if 'x86_64' in url.lower() or 'amd64' in url.lower():
                        download_url = url
                        break
                    elif not download_url:
                        download_url = url
            
            # 2. Если прямой ссылки нет, парсим GitHub
            if not download_url:
                for link in all_links:
                    url = link.get('url', '')
                    if 'github.com' in url:
                        print(f"Поиск релиза для {name} через GitHub API...", flush=True)
                        download_url = get_github_direct_link(url)
                        break
            
            if download_url:
                raw_cats = app.get('tags') or app.get('categories') or []
                if isinstance(raw_cats, str): raw_cats = [raw_cats]
                
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
