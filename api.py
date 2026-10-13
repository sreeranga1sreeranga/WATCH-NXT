import requests
import urllib3
import base64
import os
from config import TMDB_API_KEY

# Disables macOS SSL block warnings
urllib3.disable_warnings()

def fetch_image_b64(url):
    """Bypasses ISP blocks by downloading the image in Python and returning raw Base64 data."""
    if not url: return None
    try:
        r = requests.get(url, verify=False, timeout=3)
        if r.status_code == 200:
            return base64.b64encode(r.content).decode('utf-8')
    except:
        pass
    return None

def get_indian_providers(media_type, tmdb_id):
    url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/watch/providers"
    params = {"api_key": TMDB_API_KEY}
    try:
        r = requests.get(url, params=params, verify=False, timeout=3)
        if r.status_code == 200:
            in_data = r.json().get("results", {}).get("IN", {})
            return [p.get("provider_name") for p in in_data.get("flatrate", [])]
    except: pass
    return []

def map_provider_name(tmdb_name):
    mapping = {"Netflix": "Netflix", "Amazon": "Prime Video", "Hotstar": "JioHotstar", "Jio": "JioCinema", "ZEE5": "ZEE5", "Apple": "Apple TV+"}
    for key, val in mapping.items():
        if key.lower() in tmdb_name.lower(): return val
    return None

def tmdb_search_with_providers(query):
    if not query.strip(): return []
    url = "https://api.themoviedb.org/3/search/multi"
    params = {"api_key": TMDB_API_KEY, "query": query, "include_adult": "false"}
    results = []
    
    try:
        r = requests.get(url, params=params, verify=False, timeout=5)
        if r.status_code == 200:
            raw_results = r.json().get("results", [])[:6] 
            
            for item in raw_results:
                media_type = item.get("media_type", "movie")
                if media_type not in ["movie", "tv"]: continue
                    
                tmdb_id = item.get("id")
                raw_providers = get_indian_providers(media_type, tmdb_id)
                mapped_providers = []
                for rp in raw_providers:
                    mp = map_provider_name(rp)
                    if mp and mp not in mapped_providers: mapped_providers.append(mp)
                        
                item["watch_providers"] = mapped_providers
                
                # Fetch Base64 Image safely
                poster_path = item.get('poster_path')
                if poster_path:
                    img_url = f"https://image.tmdb.org/t/p/w342{poster_path}"
                    item["b64_poster"] = fetch_image_b64(img_url)
                else:
                    item["b64_poster"] = None
                    
                results.append(item)
    except: pass
    return results