import os
import sys
from dotenv import load_dotenv
from groq import Groq, APIError

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
MODEL = 'qwen/qwen3.8-27b'

# ceny platnej warstwy API w USD za 1 mln tokenow (stan na 2026 r.)
CENA_WY = 4.00 # USD za 1 mln tokenów wyjściowych (qwen/qwen3.8-27b)
PROMPT = ('Wyjaśnij, czym jest metoda gradientu prostego '
 '(gradient descent) w uczeniu maszynowym. '
 'Uwzględnij definicję, zastosowanie i przykład.')
# czesc 1: rozne limity dlugosci odpowiedzi
for limit in [50, 150, 500]:
 print(f'\n\n{"#" * 64}')
 print(f'### MAX_TOKENS = {limit}')
 print('#' * 64)
 try:
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{'role': 'user', 'content': PROMPT}],
        temperature=0.3,
        max_tokens=limit,
        reasoning_effort='none',
    )
    print(r.choices[0].message.content)

    tok_wy = r.usage.completion_tokens
    powod = r.choices[0].finish_reason
    print(f'\n>>> tokeny wyjsciowe: {tok_wy} | ' f'finish_reason: {powod} | ' f'koszt: {tok_wy * CENA_WY / 1e6:.6f} USD')
 except APIError as e:
    print(f'[Blad Groq API] {e}')
    
# czesc 2: sekwencja stopu konczy generacje
print(f'\n\n{"#" * 64}')
print('### STOP = ["###"]')
print('#' * 64)
PROMPT_STOP = ('Wypisz trzy kroki instalacji interpretera '
 'Python w systemie Windows. Po trzecim kroku '
 'napisz ###, a następnie dodaj szczegółowy '
 'opis każdego kroku.')
try:
 r = client.chat.completions.create(
    model=MODEL,
    messages=[{'role': 'user', 'content': PROMPT_STOP}],
    temperature=0.3,
    max_tokens=500,
    reasoning_effort='none',
    stop=['###'],
 )
 print(r.choices[0].message.content)
 print(f'\n>>> finish_reason: {r.choices[0].finish_reason}')
except APIError as e:
 print(f'[Blad Groq API] {e}')
