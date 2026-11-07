import os
import re
import sys
import time
from dotenv import load_dotenv
from groq import Groq
from groq import APIError, RateLimitError
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
ETYKIETY = ['POZYTYWNA', 'NEUTRALNA', 'NEGATYWNA', 'MIESZANA']
# opinie wraz z etykieta wzorcowa (ustalona przez czlowieka);
# polowa zbioru to przypadki trudne: sarkazm, zaprzeczenie, opinie mieszane
OPINIE = [
 ('Świetnie prowadzone laboratoria, wszystko było '
 'jasno wyjaśnione.', 'POZYTYWNA'),
 ('Wykład jak wykład, da się przeżyć.', 'NEUTRALNA'),
 ('Materiały były nieaktualne, a terminy oddania '
 'projektów zmieniano bez uprzedzenia.', 'NEGATYWNA'),
 ('Sala 205 ma 40 miejsc, zajęcia odbywały się '
 'we wtorki o 8:00.', 'NEUTRALNA'),
 ('No super, kolokwium znowu przełożone, '
 'bardzo dziękuję.', 'NEGATYWNA'), # sarkazm
 ('Nie mogę powiedzieć, żebym czegokolwiek się '
  'na tych zajęciach nauczył.', 'NEGATYWNA'), # zaprzeczenie
 ('Zajęcia bywały chaotyczne, ale zaliczenie '
 'przebiegło bez problemów.', 'MIESZANA'),
 ('Ciekawy wykład, szkoda tylko, że prowadzący nie '
 'przyszedł na 4 z 10 zajęć.', 'MIESZANA'),
]
LISTA = 'POZYTYWNA, NEUTRALNA, NEGATYWNA albo MIESZANA'
ROLA = ('Jesteś analitykiem ankiet ewaluacyjnych '
 'na uczelni technicznej. ')
ZADANIE = 'Sklasyfikuj wydźwięk poniższej opinii studenta. '
FORMAT = f'Odpowiedz wyłącznie jednym słowem: {LISTA}.'
# definicje etykiet - doprecyzowanie kontekstu dla przypadkow granicznych
DEFINICJE = ('MIESZANA oznacza opinię zawierającą jednocześnie '
 'wyraźną pochwałę i wyraźny zarzut; NEUTRALNA - opinię '
 'bez ocen albo obojętną. Zwróć uwagę na sarkazm '
 'i zaprzeczenia. ')
# kazdy wariant zmienia JEDEN element wzgledem poprzedniego
# tryb: 'wolny' - bez wymagan formatu, 'slowo' - jedno slowo,
# 'etykieta' - krotka analiza + ostatnia linia ETYKIETA: ...
WARIANTY = {
 # A i A2: odpowiedz swobodna - trafnosc ocenia czlowiek, bo program
 # nie wie, ktore ze wspomnianych slow jest wlasciwa etykieta
 'A - bazowy': dict(instrukcja=ZADANIE, tryb='wolny', max_tokens=300),
 'A2 - z lista etykiet': dict(instrukcja=ZADANIE + f'Wybierz jedną z etykiet: {LISTA}.', tryb='wolny', max_tokens=300),
 'B - z formatem': dict(instrukcja=ZADANIE + FORMAT, tryb='slowo', max_tokens=10),
 'C - z rola': dict(instrukcja=ROLA + ZADANIE + FORMAT, tryb='slowo', max_tokens=10),
 'C2 - z rola i definicjami': dict(instrukcja=ROLA + ZADANIE + DEFINICJE + FORMAT, tryb='slowo', max_tokens=10),
 # samoweryfikacja dostaje miejsce na sprawdzenie (2 zdaniaanalizy),
 # a etykieta trafia do stalego formatu w ostatniej linii
 'D - z samoweryfikacja': dict(instrukcja=(ROLA + ZADANIE + DEFINICJE + 'Najpierw w 1-2 zdaniach wskaż, które fragmenty '
 'opinii są pozytywne, a które negatywne, i sprawdź, '
 'czy nie ma w niej sarkazmu. Następnie w ostatniej '
 'linii podaj wynik w formacie: ETYKIETA: <' + LISTA + '>'), tryb='etykieta', max_tokens=200),
}

def zapytaj(dostawca, model, prompt, max_tokens):
 """Zwraca odpowiedz modelu albo None przy bledzie. Bez
zastepowania  modelu innym - wyniki obu modeli nie moga sie mieszac."""
 try:
    if dostawca == 'groq':
        for proba in range(1, PROBY_429 + 1):
            try:
                r = client.chat.completions.create(
                    model=model,   
                    messages=[{'role': 'user', 'content':
                    prompt}],
                    temperature=0.0,
                    max_tokens=max_tokens,
                    reasoning_effort='none',
                )
                return r.choices[0].message.content.strip()
            except RateLimitError:
 # blad 429 - limit tokenow na minute darmowej
 # warstwie; odczekaj i ponow zapytanie
                if proba == PROBY_429:
                    raise
                print(f'[Limit 429] czekam {PAUZA_429} s '  f'(proba {proba}/{PROBY_429})')
                time.sleep(PAUZA_429)
    import ollama
    lok = ollama.generate(model=model, prompt=prompt, options={'temperature': 0.0,'num_predict': max_tokens})
    return lok['response'].strip()
 except APIError as e:
 # np. blad 429 (limit zapytan) lub problem z kluczem
    print(f'[Blad Groq API] {e}')
 except Exception as e:
 # np. serwer Ollama nie dziala lub brak pobranego modelu
    print(f'[Blad {dostawca}] {e}')
 return None

def format_poprawny(odp, tryb):
 """Scisla kontrola formatu - tak, jak sprawdzalby ja
program."""
 if tryb == 'slowo':
    return odp in ETYKIETY
 if tryb == 'etykieta':
    ostatnia = odp.splitlines()[-1].strip() if odp else ''
    return re.fullmatch(r'ETYKIETA: (' + '|'.join(ETYKIETY) +')', ostatnia) is not None
 return None # wariant bez wymagan formatu

def wyodrebnij_etykiete(odp, tryb):
 """Lagodna ekstrakcja etykiety do oceny trafnosci (niezalezna
od
 scislego formatu, np. toleruje kropke lub male litery)."""
 if tryb == 'wolny':
    return None # ocena reczna
 if tryb == 'etykieta':
    m = re.search(r'ETYKIETA:\W*(\w+)', odp, re.IGNORECASE)
    if m:
        odp = m.group(1)
 m = re.search(r'(pozytywn|neutraln|negatywn|mieszan)', odp,re.IGNORECASE)
 if not m:
    return '?'
 rdzen = m.group(1).lower()
 return next(e for e in ETYKIETY if
e.lower().startswith(rdzen))
# podsumowanie[nazwa_wariantu][model] = 'trafnosc / format'
podsumowanie = {nazwa: {} for nazwa in WARIANTY}

for dostawca, model in MODELE:
 for nazwa, w in WARIANTY.items():
    print(f'\n\n{"#" * 64}')
    print(f'### {model} | WARIANT {nazwa}')
    print('#' * 64)
    trafne, poprawny_format, bledy = 0, 0, 0
    for i, (opinia, wzorzec) in enumerate(OPINIE, start=1):
        prompt = f'{w["instrukcja"]}\nOpinia: """{opinia}"""'
        odp = zapytaj(dostawca, model, prompt, w['max_tokens'])
        if odp is None:
            bledy += 1
            print(f'opinia {i} [BLAD API] - brak odpowiedzi')
            continue
        if w['tryb'] == 'wolny':
            print(f'opinia {i} [ocena reczna] wzorzec={wzorzec}')
            print(' ' + odp.replace('\n', '\n '))
            continue
        etykieta = wyodrebnij_etykiete(odp, w['tryb'])
        fmt = format_poprawny(odp, w['tryb'])
        trafne += etykieta == wzorzec
        poprawny_format += fmt
        znak = 'OK ' if etykieta == wzorzec else 'ZLE'
        print(f'opinia {i} [{znak}] wzorzec={wzorzec:<9} ' f'wynik={etykieta:<9} format={"tak" if fmt else "NIE"}')
        print(' ' + odp.replace('\n', ' | ')[:160])
    if w['tryb'] == 'wolny':
        wynik = 'recznie'
    else:
        wynik = f'{trafne}/{len(OPINIE)} / {poprawny_format}/{len(OPINIE)}'
    if bledy:
        wynik += f' ({bledy} bl.)'
    podsumowanie[nazwa][model] = wynik
    
print(f'\n\n{"#" * 64}')
print('### PODSUMOWANIE (trafnosc / format)')
print('#' * 64)
print(f'{"WARIANT":<28}' + ''.join(f'{m:<22}' for _, m in MODELE))
for nazwa, wyniki in podsumowanie.items():
    print(f'{nazwa:<28}' + ''.join(f'{wyniki.get(m, "-"):<22}' for _, m in MODELE))