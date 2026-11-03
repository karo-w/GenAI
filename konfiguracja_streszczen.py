import os
import sys
from dotenv import load_dotenv
from groq import Groq, APIError


sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
MODEL = 'qwen/qwen3.8-27b'

ABSTRAKT = (
 'Praca przedstawia system wykrywania ataków w sieci '
 'komputerowej (IDS) oparty na uczeniu maszynowym. '
 'Porównano klasyczne metody sygnaturowe z trzema '
 'klasyfikatorami uczonymi na zbiorze CIC-IDS2017: '
 'lasem losowym, maszyną wektorów nośnych oraz siecią '
 'neuronową. Najlepszą skuteczność (98,2% F1) osiągnął '
 'las losowy przy najniższym czasie klasyfikacji. '
 'Zaproponowano architekturę wdrożenia systemu w sieci '
 'laboratoryjnej uczelni oraz omówiono ograniczenia '
 'metody, w tym podatność na ataki dnia zerowego.'
)
PROMPT = ('Streść poniższy abstrakt pracy inżynierskiej '
 'w maksymalnie trzech zdaniach, rzeczowo i bez '
 'ozdobników:\n"""' + ABSTRAKT + '"""')
KONFIGURACJE = {
 'A (temperature=0.0)': dict(temperature=0.0),
 'B (temperature=0.3, top_p=0.8)': dict(temperature=0.3,
 top_p=0.8),
 'C (temperature=1.0)': dict(temperature=1.0),
}

for nazwa, parametry in KONFIGURACJE.items():
    print(f'\n\n{"#" * 64}')
    print(f'### KONFIGURACJA {nazwa}')
    print('#' * 64)
    for i in (1, 2):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{'role': 'user', 'content': PROMPT}],
                max_tokens=200,
                reasoning_effort='none',
                **parametry,
            )
            print(f'\n--- proba {i} ---')
            print(r.choices[0].message.content.strip())
        except APIError as e:
            print(f'[Blad Groq API] {e}')
