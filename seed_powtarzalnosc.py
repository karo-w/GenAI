import os
import sys
from dotenv import load_dotenv
from groq import Groq, APIError
import ollama

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
MODEL = 'qwen/qwen3.8-27b'
MODEL_LOKALNY = 'llama3.1'

PROMPT = ('Zaproponuj oryginalną nazwę robota '
 'sprzątającego laboratorium komputerowe. '
 'Odpowiedz samą nazwą.')
def proby_ollama(opis, opcje, n=3):
 print(f'\n--- Ollama: {opis} ---')
 wyniki = []
 for i in range(n):
    try:
        r = ollama.chat(
            model=MODEL_LOKALNY,
            messages=[{'role': 'user', 'content': PROMPT}],
            options=opcje,
        )
        wyniki.append(r['message']['content'].strip())
        print(f'proba {i + 1}: {wyniki[-1]}')
    except Exception as e:
        print(f'[Blad Ollama] {e}')
 print(f'>>> Unikalne: {len(set(wyniki))} z {len(wyniki)}')
 
 # czesc 1: model lokalny - pelna kontrola ziarna
proby_ollama('temperature=0.8, seed=42',
 {'temperature': 0.8, 'seed': 42})
proby_ollama('temperature=0.8, seed=7',
 {'temperature': 0.8, 'seed': 7})
proby_ollama('temperature=0.8, bez seed',
 {'temperature': 0.8})

# czesc 2: model chmurowy - seed w trybie best effort
print('\n--- Groq: temperature=0.8, seed=42 ---')
wyniki = []
for i in range(3):
 try:
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{'role': 'user', 'content': PROMPT}],
        temperature=0.8,
        seed=42,
        max_tokens=60,
        reasoning_effort='none',
    )
    wyniki.append(r.choices[0].message.content.strip())
    print(f'proba {i + 1}: {wyniki[-1]}')
 except APIError as e:
    print(f'[Blad Groq API] {e}')
print(f'>>> Unikalne: {len(set(wyniki))} z {len(wyniki)}')