import os
import re
import sys
import time
from dotenv import load_dotenv
from groq import Groq
from groq import APIError, RateLimitError
import json
# poprawne wyswietlanie polskich znakow w konsoli Windows
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
# nazwy modeli - kazdy wariant jest uruchamiany na obu modelach
MODEL = 'qwen/qwen3.8-27b' # rozumowanie wyłączone (reasoning_effort='none')
MODEL_LOKALNY = 'llama3.1' # model lokalny (Ollama)
MODELE = [('groq', MODEL), ('ollama', MODEL_LOKALNY)]
# ponawianie zapytan po bledzie 429 (limit tokenow na minute w Groq)
PROBY_429 = 4
PAUZA_429 = 15 # sekundy

import ollama


ZADANIA = {
    'A - zlozonosc algorytmu': (
        'Wyznacz złożoność czasową poniższego kodu:\n'
        'for i in range(n):\n'
        '    for j in range(i):\n'
        '        op()'
    ),
    'B - zadanie tekstowe': (
        'Do pracowni zamówiono 4 zestawy po 6 '
        'komputerów. Pięć komputerów okazało się '
        'wadliwych i je zwrócono, a następnie '
        'domówiono połowę liczby zwróconych '
        '(zaokrąglając w górę). Ile komputerów '
        'trafiło ostatecznie do pracowni?'
    ),
}

WARIANTY = {
    'bez CoT': 'Podaj samą odpowiedź, bez wyjaśnień.',
    'zero-shot CoT': (
        'Myślmy krok po kroku. Na końcu '
        'podaj odpowiedź w osobnej linii '
        'w formacie: ODPOWIEDŹ: ...'
    ),
}


def zapytaj(dostawca, model, prompt):
    """Zwraca (odpowiedz, tokeny wyjsciowe) albo (None, 0) przy bledzie."""
    try:
        if dostawca == 'groq':
            for proba in range(1, PROBY_429 + 1):
                try:
                    r = client.chat.completions.create(
                        model=model,
                        messages=[{'role': 'user', 'content': prompt}],
                        temperature=0.0,
                        max_tokens=800,
                        reasoning_effort='none',
                    )
                    return (
                        (r.choices[0].message.content or '').strip(),
                        r.usage.completion_tokens,
                    )
                except RateLimitError:
                    # blad 429 - odczekaj i ponow zapytanie
                    if proba == PROBY_429:
                        raise
                    print(f'[Limit 429] czekam {PAUZA_429} s '
                          f'(proba {proba}/{PROBY_429})')
                    time.sleep(PAUZA_429)

        lok = ollama.generate(
            model=model,
            prompt=prompt,
            options={'temperature': 0.0, 'num_predict': 800},
        )
        return lok['response'].strip(), lok['eval_count']

    except APIError as e:
        print(f'[Blad Groq API] {e}')
    except Exception as e:
        # np. serwer Ollama nie dziala lub brak pobranego modelu
        print(f'[Blad {dostawca}] {e}')
    return None, 0


# eksperyment wykonywany najpierw na qwen/qwen3.8-27b,
# a nastepnie powtarzany na modelu lokalnym llama3.1
for dostawca, model in MODELE:
    for nazwa, tresc in ZADANIA.items():
        print(f'\n{"#" * 64}')
        print(f'### {model} | ZADANIE {nazwa}')
        print('#' * 64)
        for opis, dopisek in WARIANTY.items():
            prompt = f'{tresc}\n{dopisek}'
            print(f'\n--- wariant: {opis} ---')
            odp, tok_wy = zapytaj(dostawca, model, prompt)
            if odp is None:
                print('[BLAD] brak odpowiedzi')
                continue
            print(odp)
            print(f'>>> tokeny wyjsciowe: {tok_wy}')