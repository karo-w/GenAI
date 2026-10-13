import os
import sys
from dotenv import load_dotenv
from groq import Groq
from groq import APIError
# poprawne wyswietlanie polskich znakow w konsoli Windows
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
MODEL = 'openai/gpt-oss-120b'
# ceny platnej warstwy API w USD za 1 mln tokenow (stan na 2026r.)
CENA_WE = 0.15
CENA_WY = 0.60
PROMPT = ('Jesteś ekspertem od sztucznej inteligencji. Wyjaśnij szczegółowo, co to agent AI' 
'w kontekście sztucznej inteligencji. Powiedz, czym są i na czym polegają narzędzia' 
'agentyczne, podając ich najważniejsze cechy i sposób działania. Wymień wady i zalety' 
'zastosowania takiego rozwiązania. Następnie porównaj agenta AI z innymi rozwiązaniami,' 
'takimi jak chatboty i modele LLM bez agenta. Swoją odpowiedź podziel na sekcje:' 
'definicja, mechanizm działania, 3-4 przykłady, zastosowanie w praktyce, typowe błędy' 
'oraz podsumowanie. Każdą sekcję rozwiń w co najmniej 3-4 zdaniach i podaj konkretne' 
'przykłady z życia. Omów także ograniczenia i wyzwania związane z wdrożeniem. Użyj' 
'prostego języka, zrozumiałego dla studenta pierwszego roku informatyki, ale nie' 
'pomijaj szczegółów technicznych.')

try:
 # wyslanie zadania i odczyt statystyk z pola usage
    response = client.chat.completions.create(
    model=MODEL,
    messages=[{'role': 'user', 'content': PROMPT}],
    temperature=0.7,
    max_tokens=1000,
    )
    print(response.choices[0].message.content)
    tok_we = response.usage.prompt_tokens
    tok_wy = response.usage.completion_tokens
    print(f'Tokeny wejsciowe: {tok_we} | tokeny wyjsciowe:{tok_wy}')
     # szacunkowy koszt pojedynczego zapytania
    koszt = (tok_we * CENA_WE + tok_wy * CENA_WY) / 1_000_000
    print(f'Szacunkowy koszt zapytania: {koszt:.6f} USD')
except APIError as e:
 # np. blad 429 (przekroczony limit zapytan) lub problem z kluczem/siecia
    print(f'[Blad Groq API] {e}')
    
# porownanie tokenizacji: polski vs angielski
zdania = {
 'PL': 'Sztuczna inteligencja zmienia współczesną informatykę.',
 'EN': 'Artificial intelligence is changing modern computing.',
}
for jezyk, tekst in zdania.items():
    r = client.chat.completions.create(model=MODEL,
    messages=[{'role': 'user', 'content': tekst}], max_tokens=1)
    print(f'{jezyk}: {r.usage.prompt_tokens} tokenów | {len(tekst)} znaków')
    
# tokeny w modelu lokalnym (Ollama)
import ollama
local = ollama.chat(model='llama3.1', messages=[{'role': 'user', 'content': PROMPT}])
print('Tokeny wejściowe (Ollama):', local['prompt_eval_count'])
print('Tokeny wyjściowe (Ollama):', local['eval_count'])
