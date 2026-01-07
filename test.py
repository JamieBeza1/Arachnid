## Test file to run PoC scripts on before integration

import requests

url = "https://www.bleepingcomputer.com/news/hardware/logitech-options-plus-g-hub-macos-apps-break-after-certificate-expires/"
headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8"
        }

data = requests.get(url, headers=headers)

print(data.content)