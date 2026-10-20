import os
import sys
from dotenv import load_dotenv
from groq import Groq

# poprawne wyswietlanie polskich znakow w konsoli Windows
sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = 'openai/gpt-oss-120b'
PERSONY = {
 'biznes': 'Jesteś doradcą biznesowym. Tłumaczysz technologie '
 'językiem korzyści, bez żargonu technicznego.',
 'student': 'Jesteś asystentem dydaktycznym na kierunku informatyka. '
 'Tłumaczysz precyzyjnie, z prostymi przykładami.',
 'admin': 'Jesteś starszym inżynierem DevOps. '
 'Odpowiadasz technicznie i zwięźle.',
}

PYTANIE = "Czym jest konteneryzacja aplikacji (Docker)?"

for nazwa, instrukcja in PERSONY.items():
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {'role': 'system', 'content': instrukcja},
            {'role': 'user', 'content': PYTANIE},
        ],
        max_tokens=1000,
    )
    print(f'=== {nazwa.upper()} ===')
    print(response.choices[0].message.content, end='\n\n')