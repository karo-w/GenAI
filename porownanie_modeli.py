import os
import sys
import time
from dotenv import load_dotenv
from groq import Groq
from groq import APIError
import ollama
# poprawne wyświetlanie polskich znaków w konsoli Windows
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
# nazwy modeli w jednym miejscu - latwiej je podmienic, gdy dostawca
# wycofa model (patrz uwaga pod skryptem)
MODEL = 'openai/gpt-oss-120b'
MODEL_LOKALNY = 'llama3.1'
PROMPT = ('Jesteś ekspertem od sztucznej inteligencji. '
 'Wyjaśnij w 3-4 zdaniach, czym jest transformer '
 'w kontekście modeli językowych. Użyj prostego języka, '
 'zrozumiałego dla studenta pierwszego roku informatyki.')

# --- model zewnetrzny: Groq (API) ---
print(f'=== {MODEL} (model zewnetrzny) ===')
try:
    start = time.perf_counter()
    response = client.chat.completions.create(
    model=MODEL,
    messages=[{'role': 'user', 'content': PROMPT}],
    temperature=0.7,
    max_tokens=1000,
)
    t_groq = time.perf_counter() - start
    print(response.choices[0].message.content)
    print(f'Czas odpowiedzi: {t_groq:.2f} s')
except APIError as e:
 # np. blad 429 (przekroczony limit zapytan) lub problem z kluczem/siecia
    print(f'[Blad Groq API] {e}')
    print('Pomijam Groq i przechodze do modelu lokalnego.')
# --- model lokalny: Ollama ---
print(f'=== {MODEL_LOKALNY} (model lokalny) ===')
try:
    start = time.perf_counter()
    local = ollama.chat(model=MODEL_LOKALNY,
    messages=[{'role': 'user', 'content': PROMPT}])
    t_llama = time.perf_counter() - start
    print(local['message']['content'])
    print(f'Czas odpowiedzi: {t_llama:.2f} s')
except Exception as e:
 # np. serwer Ollama nie dziala lub brak pobranego modelu
    print(f'[Blad Ollama] {e}')
    print(f'Upewnij sie, ze serwer Ollama dziala i model {MODEL_LOKALNY} ' f'jest pobrany (ollama pull {MODEL_LOKALNY}).')
