# Test connection to OSM Overpass API mirrors with full browser headers to bypass strict WAF blocks.

import requests
import time

mirrors = [
    "https://overpass-api.de/api/status",
    "https://lz4.overpass-api.de/api/status",
    "https://overpass.openstreetmap.fr/api/status"
]

# Full browser spoof to bypass strict WAF blocks
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

print("Testing Overpass API Mirrors with Full Browser Headers...\n" + "-"*40)

for url in mirrors:
    print(f"Testing: {url}")
    try:
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"  [SUCCESS] HTTP 200 - Connected in {time.time() - start_time:.2f}s\n")
        else:
            print(f"  [FAILED] HTTP {response.status_code}\n")
            
    except Exception as e:
        print(f"  [FAILED] Error: {e}\n")