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
OGLOSZENIA = [
    'Firma NetSoft z Lublina poszukuje studenta na '
    'praktyki jako junior tester. Mile widziane: '
    'Python i SQL. Wymiar: 2 dni w tygodniu.',

    'Praktyki wakacyjne w dziale IT szpitala '
    'wojewódzkiego - wsparcie helpdesk, wymagana '
    'znajomość systemu Windows. Pełny etat w lipcu.',

    'Startup Medi42 (praca zdalna) przyjmie '
    'praktykanta do zespołu frontend: React oraz '
    'TypeScript. Elastyczne godziny.',
]

POLA = (
    'firma, miasto, stanowisko, technologie '
    '(lista), wymiar'
)

# WARIANT NAIWNY (zero-shot): luźna instrukcja, bez słowa
# "wyłącznie" i bez przykładów. Model często opakowuje JSON
# w blok ```json albo dodaje komentarz, przez co json.loads
# się wywala.

PROMPT_ZERO = (
    'Wyodrębnij z ogłoszenia dane: ' + POLA +
    '. Jeśli danej brak, wpisz null. '
    'Podaj wynik w formacie JSON.\n'
    'Ogłoszenie: """{tekst}"""\n'
    'JSON:'
)

PROMPT_FEW = (
    'Zamieniasz ogłoszenia o praktykach na obiekty '
    'JSON z polami: ' + POLA + '. Jeśli danej brak, '
    'wpisz null. Zwracaj wyłącznie JSON.\n'

    'Ogłoszenie: """Biuro projektowe KOMPAS (Lublin) '
    'szuka praktykanta do działu GIS; wymagany '
    'QGIS; 3 dni w tygodniu."""\n'

    'JSON: {"firma": "KOMPAS", "miasto": "Lublin", '
    '"stanowisko": "praktykant GIS", "technologie": '
    '["QGIS"], "wymiar": "3 dni w tygodniu"}\n'

    'Ogłoszenie: """Zdalne praktyki w zespole DevOps '
    'firmy CloudPol: Docker, Linux."""\n'

    'JSON: {"firma": "CloudPol", "miasto": null, '
    '"stanowisko": "praktykant DevOps", '
    '"technologie": ["Docker", "Linux"], '
    '"wymiar": null}\n'

    'Ogłoszenie: """{tekst}"""\n'
    'JSON:'
)


def wyodrebnij(prompt):
    """Zwraca odpowiedź modelu albo None przy błędzie.
    Po błędzie 429 czeka i ponawia zapytanie - bez
    zastępowania modelu innym."""

    for proba in range(1, PROBY_429 + 1):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.0,
                max_tokens=200,
                reasoning_effort='none',
            )

            return r.choices[0].message.content or ''

        except RateLimitError:
            # błąd 429 - limit tokenów na minutę;
            # odczekaj i ponów

            if proba == PROBY_429:
                print('[Limit 429] limit nadal przekroczony')
                return None

            print(
                f'[Limit 429] czekam {PAUZA_429} s '
                f'(proba {proba}/{PROBY_429})'
            )

            time.sleep(PAUZA_429)

        except APIError as e:
            # np. problem z kluczem API lub nazwą modelu

            print(f'[Blad Groq API] {e}')
            return None


for nazwa, szablon in [
    ('zero-shot', PROMPT_ZERO),
    ('few-shot', PROMPT_FEW)
]:
    print(f'\n\n{"#" * 64}')
    print(f'### WARIANT {nazwa}')
    print('#' * 64)

    poprawne = 0

    for i, tekst in enumerate(OGLOSZENIA, start=1):
        odp = wyodrebnij(szablon.replace('{tekst}', tekst))

        if odp is None:
            print(f'\nogloszenie {i}: BLAD API - brak odpowiedzi')
            continue

        # UWAGA: celowo NIE usuwamy bloków ```json ani prozy wokół
        # JSON.
        #
        # Chcemy zobaczyć, który wariant zwraca czysty, parsowalny
        # JSON, a który psuje parsowanie dodatkowymi
        # znacznikami/tekstem.

        odp = odp.strip()

        try:
            dane = json.loads(odp)
            status = 'OK'
            poprawne += 1

        except json.JSONDecodeError:
            status = 'BLAD PARSOWANIA'

        print(f'\nogloszenie {i}: {status}')
        print(odp)

    print(
        f'\n>>> Parsowalne odpowiedzi: {poprawne} '
        f'z {len(OGLOSZENIA)}'
    )