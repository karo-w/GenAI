
import base64
import io
import os
import sys

import requests
from dotenv import load_dotenv
from PIL import Image


# Poprawne wyświetlanie polskich znaków w konsoli Windows
sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

KONTO = os.getenv("CF_ACCOUNT_ID")
TOKEN = os.getenv("CF_API_TOKEN")

if not KONTO or not TOKEN:
    sys.exit("Brak CF_ACCOUNT_ID lub CF_API_TOKEN w pliku .env")


# Model generowania obrazów w Cloudflare Workers AI
MODEL = "@cf/black-forest-labs/flux-1-schnell"

URL = (
    f"https://api.cloudflare.com/client/v4/accounts/"
    f"{KONTO}/ai/run/{MODEL}"
)

PROMPT = (
    "A small friendly robot standing on a desk next to a laptop, "
    "flat illustration, soft pastel colors"
)

try:
    r = requests.post(
        URL,
        headers={
            "Authorization": f"Bearer {TOKEN}"
        },
        json={
            "prompt": PROMPT,
            "steps": 4
        },
        timeout=120
    )

except requests.RequestException as e:
    sys.exit(f"Brak połączenia z Cloudflare: {e}")


if r.status_code != 200:
    print(f"Błąd {r.status_code}: {r.text[:300]}")

    if r.status_code in (401, 403):
        print(
            "Wskazówka: sprawdź CF_API_TOKEN (cały, bez spacji) "
            "i czy token ma uprawnienie do Workers AI."
        )

    elif r.status_code in (400, 404):
        print(
            "Wskazówka: sprawdź CF_ACCOUNT_ID "
            "(32 znaki, bez spacji)."
        )

    elif r.status_code == 429:
        print(
            "Wskazówka: wyczerpany dzienny limit - "
            "spróbuj jutro."
        )

    sys.exit(1)


# Odpowiedź: {"result": {"image": "<obraz zakodowany w base64>"}, ...}
dane = base64.b64decode(r.json()["result"]["image"])

os.makedirs("out", exist_ok=True)

Image.open(io.BytesIO(dane)).save("out/test_cloudflare.png")

print("OK - zapisano out/test_cloudflare.png")
