import os
import re
import sys
import time
from dotenv import load_dotenv
from groq import Groq
from groq import APIError, RateLimitError
import ollama
from collections import Counter
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
N = 5  # liczba niezaleznych sciezek rozumowania
TEMPERATURA = 0.7  # przy 0 wszystkie sciezki bylyby identyczne
MAX_TOKENS = 800
# zadania z wynikiem wzorcowym; B jest trudniejsze (wieloetapowe
# zliczanie), wiec bledne sciezki pojawiaja sie czesciej
ZADANIA = [
    ('A - bledy w testach',
     'Trzej studenci testują aplikację. Każdy '
     'z nich zgłosił 8 błędów, ale 5 błędów '
     'powtórzyło się u dokładnie dwóch osób, '
     'a 2 błędy zgłosili wszyscy trzej. Ile '
     'unikalnych błędów zgłoszono łącznie?', '15'),
    ('B - podzielnosc',
     'Ile liczb całkowitych od 1 do 1000 (włącznie) '
     'jest podzielnych przez 3 lub przez 5, ale nie '
     'jest podzielnych przez 7?', '401'),
]
DOPISEK = (' Rozwiąż zadanie i podaj krótkie uzasadnienie, '
           'maksymalnie w 3 zdaniach. '
           'Ostatnia linia odpowiedzi musi mieć format: WYNIK: '
           '<liczba>. '
           'Nie dodawaj niczego po tej linii.')
# akceptuje tez warianty z Markdown, np. **WYNIK:** 15 lub WYNIK: **15**
WZOR_WYNIKU = re.compile(r'WYNIK\W*?(-?\d+)')


def zapytaj(dostawca, model, prompt):
    """Zwraca odpowiedz modelu albo None przy bledzie."""
    try:
        if dostawca == 'openrouter':
            for proba in range(1, PROBY_429 + 1):
                try:
                    r = client.chat.completions.create(
                        model=model,
                        messages=[{'role': 'user', 'content': prompt}],
                        temperature=TEMPERATURA,
                        max_tokens=MAX_TOKENS,
                        extra_body={'reasoning': {'effort': 'none'}},
                    )
                    return r.choices[0].message.content.strip()
                except RateLimitError:
                    # blad 429 - odczekaj i ponow zapytanie
                    if proba == PROBY_429:
                        raise
                    print(f'[Limit 429] czekam {PAUZA_429} s '
                          f'(proba {proba}/{PROBY_429})')
                    time.sleep(PAUZA_429)
        r = ollama.chat(model=model,
                        messages=[{'role': 'user', 'content': prompt}],
                        options={'temperature': TEMPERATURA,
                                 'num_predict': MAX_TOKENS})
        return r['message']['content'].strip()
    except APIError as e:
        print(f'[Blad OpenRouter API] {e}')
    except Exception as e:
        # np. serwer Ollama nie dziala lub brak pobranego modelu
        print(f'[Blad {dostawca}] {e}')
    return None


def wynik_koncowy(odp):
    """Ostatnia liczba po slowie WYNIK albo 'brak'."""
    trafienia = WZOR_WYNIKU.findall(odp)
    return trafienia[-1] if trafienia else 'brak'

# podsumowanie: (model, zadanie, rozklad, finalny, wzorzec)
podsumowanie = []
for dostawca, model in MODELE:
    for nazwa, tresc, wzorzec in ZADANIA:
        print(f'\n\n{"#" * 64}')
        print(f'### {model} | ZADANIE {nazwa}')
        print('#' * 64)
        glosy = []
        for i in range(1, N + 1):
            odp = zapytaj(dostawca, model, tresc + DOPISEK)
            if odp is None:
                glosy.append('blad')
                print(f'\n--- sciezka {i} -> [BLAD] brak odpowiedzi ---')
                continue
            wynik = wynik_koncowy(odp)
            glosy.append(wynik)
            znak = 'OK ' if wynik == wzorzec else 'ZLE'
            print(f'\n--- sciezka {i} -> wynik: {wynik} [{znak}] ---')
            # koncowka odpowiedzi: ostatnie kroki i linia WYNIK
            print('...' + odp[-300:])
        rozklad = Counter(glosy)
        liczbowe = Counter({k: v for k, v in rozklad.items()
                            if k not in ('brak', 'blad')})
        if liczbowe:
            kandydat, liczba = liczbowe.most_common(1)[0]
            finalny = kandydat if liczba >= N // 2 + 1 else 'brak konsensusu'
        else:
            finalny, liczba = 'brak', 0
        print(f'\nRozklad glosow: {dict(rozklad)}')
        print(f'Odpowiedz finalna: {finalny} ({liczba} z {N} glosow)')
        podsumowanie.append((model, nazwa, dict(rozklad), finalny, wzorzec))

print(f'\n\n{"#" * 64}')
print('### PODSUMOWANIE GLOSOWANIA')
print('#' * 64)
for model, nazwa, rozklad, finalny, wzorzec in podsumowanie:
    ocena = 'OK' if finalny == wzorzec else 'ZLE'
    print(f'{model:<18} {nazwa:<22} finalny={finalny:<6} '
          f'wzorzec={wzorzec:<5} [{ocena}] {rozklad}')
