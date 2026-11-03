import os
import sys
from dotenv import load_dotenv
from groq import Groq, APIError

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
MODEL = 'qwen/qwen3.8-27b'

PROMPT = ('Opisz jednym zdaniem, czym jest głębokie '
 'uczenie (deep learning).')
PROBY = 3
import ollama
# uwaga: interfejs Groq (zgodny z API OpenAI) obsluguje top_p,
# ale nie udostepnia parametru top_k - dlatego top_k testujemy
# na modelu lokalnym (Ollama), ktory ten parametr obsluguje
MODEL_LOKALNY = 'llama3.1'
def testuj_groq(opis, **parametry):
    print(f'\n\n{"#" * 64}')
    print(f'### {opis} (Groq: {MODEL})')
    print('#' * 64)
    odpowiedzi = []
    for i in range(1, PROBY + 1):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{'role': 'user', 'content': PROMPT}],
                temperature=1.0,
                max_tokens=120,
                reasoning_effort='none',
                **parametry,
            )
            tekst = r.choices[0].message.content.strip()
            odpowiedzi.append(tekst)
            print(f'proba {i}: {tekst}')
        except APIError as e:
            print(f'[Blad Groq API] {e}')
    print(f'>>> Unikalne odpowiedzi: {len(set(odpowiedzi))} '
          f'z {len(odpowiedzi)}')
    
def testuj_ollama(opis, **opcje):
    print(f'\n\n{"#" * 64}')
    print(f'### {opis} (Ollama: {MODEL_LOKALNY})')
    print('#' * 64)
    odpowiedzi = []
    for i in range(1, PROBY + 1):
        try:
            r = ollama.chat(
                model=MODEL_LOKALNY,
                messages=[{'role': 'user', 'content': PROMPT}],
                options={'temperature': 1.0, 'num_predict': 120, **opcje},
            )
            tekst = r['message']['content'].strip()
            odpowiedzi.append(tekst)
            print(f'proba {i}: {tekst}')
        except Exception as e:
            print(f'[Blad Ollama] {e}')
    print(f'>>> Unikalne odpowiedzi: {len(set(odpowiedzi))} '
          f'z {len(odpowiedzi)}')
    
# Test A: rozne wartosci top_p na modelu zewnetrznym (temp. = 1.0)
for p in [0.1, 0.5, 0.95]:
 testuj_groq(f'TOP_P = {p}', top_p=p)
 
# Test B: rozne wartosci top_k na modelu lokalnym (temp. = 1.0)
for k in [1, 5, 40]:
 testuj_ollama(f'TOP_K = {k}', top_k=k)