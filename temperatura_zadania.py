import os
import sys
from dotenv import load_dotenv
from groq import Groq, APIError

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
MODEL = 'qwen/qwen3.8-27b'

KOD_Z_BLEDAMI = '''
def suma_listy(liczby):
    suma = 0
    for i in range(len(liczby)
        suma += liczby[i]
    return suma
'''
SCENARIUSZE = {
    'A - analiza kodu': (
        'Przeanalizuj poniższy kod Python i wypisz '
        'wszystkie błędy:\n' + KOD_Z_BLEDAMI
    ),
    'B - tlumaczenie': (
        'Przetłumacz na język angielski: "Uczenie '
        'maszynowe to dziedzina sztucznej inteligencji '
        'zajmująca się tworzeniem algorytmów, które uczą '
        'się na podstawie danych."'
    ),
    'C - zadanie kreatywne': (
        'Wymyśl jedno nietypowe, kreatywne zastosowanie '
        'sztucznej inteligencji ułatwiające życie studentom '
        'Politechniki Lubelskiej. Opisz je w 2-3 zdaniach.'
    ),
}
TEMPERATURY = [0.0, 0.7, 1.2]
for nazwa, prompt in SCENARIUSZE.items():
    print(f'\n\n{"#" * 64}')
    print(f'### SCENARIUSZ {nazwa}')
    print('#' * 64)
    for temp in TEMPERATURY:
        print(f'\n--- temperature = {temp} ---')
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=temp,
                max_tokens=400,
                reasoning_effort='none',
            )
            print(r.choices[0].message.content.strip())
        except APIError as e:
            print(f'[Blad Groq API] {e}')
