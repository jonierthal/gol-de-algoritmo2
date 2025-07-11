# listar_vozes.py

import requests
from config import ELEVENLABS_API_KEY

url = "https://api.elevenlabs.io/v1/voices"
headers = {
    "xi-api-key": ELEVENLABS_API_KEY
}

res = requests.get(url, headers=headers)

if res.status_code == 200:
    dados = res.json()
    for voice in dados["voices"]:
        print(f"{voice['name']}: {voice['voice_id']}")
else:
    print(f"Erro ao listar vozes: {res.status_code} - {res.text}")
