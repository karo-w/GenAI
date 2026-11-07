
import os
import re
import sys
import time
from dotenv import load_dotenv
from groq import Groq
from groq import APIError, RateLimitError
import ollama

# poprawne wyswietlanie polskich znakow w konsoli Windows
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# testujemy dwa modele: zewnetrzny (API) i lokalny (Ollama)
MODEL = 'qwen/qwen3.8-27b'  # rozumowanie wyłączone
MODEL_LOKALNY = 'llama3.1'

MODELE = [('groq', MODEL), ('ollama', MODEL_LOKALNY)]

# ponawianie zapytan po bledzie 429 (limit tokenow na minute w Groq)
PROBY_429 = 4
PAUZA_429 = 15  # sekundy

KATEGORIE = ['SIEĆ', 'SPRZĘT', 'OPROGRAMOWANIE', 'KONTO']
PRIORYTETY = ['WYSOKI', 'NORMALNY']

# scisly format wymagany w wariancie few-shot: KATEGORIA | PRIORYTET
WZOR_FORMATU = re.compile(
    r'(' + '|'.join(KATEGORIE) + r') \| ('
    + '|'.join(PRIORYTETY) + r')'
)

# rdzenie slow do lagodnej ekstrakcji (odmiana, male litery)
RDZENIE_KAT = {
    'SIEĆ': r'sie[cć]',
    'SPRZĘT': r'sprz[eę]t',
    'OPROGRAMOWANIE': r'oprogramowani',
    'KONTO': r'\bkont[oau]\b'
}

RDZENIE_PRI = {
    'WYSOKI': r'wysok',
    'NORMALNY': r'normaln'
}

# zgloszenia testowe z etykieta wzorcowa (ustalona przez prowadzacego);
# 1-3 to zgloszenia z krokow recznych, 4-5 to przypadki graniczne
ZGLOSZENIA = [
    (
        'W sali 305 nie działa rzutnik – komputer nie wykrywa urządzenia.',
        ('SPRZĘT', 'NORMALNY')
    ),
    (
        'Od rana nie mogę zalogować się do poczty uczelnianej mimo '
        'zresetowania hasła, a jutro mija termin zapisów na zajęcia.',
        ('KONTO', 'WYSOKI')
    ),
    (
        'W laboratorium 102 co kilka minut przerywa się połączenie '
        'Wi-Fi podczas zajęć.',
        ('SIEĆ', 'WYSOKI')
    ),
    (
        'Po zmianie hasła laptop przestał łączyć się z siecią '
        'eduroam, inne sieci działają.',
        ('KONTO', 'NORMALNY')
    ),  # granica SIEĆ / KONTO
    (
        'Drukarka sieciowa na 2. piętrze drukuje puste strony, a za '
        'godzinę muszę oddać wydruk pracy dyplomowej.',
        ('SPRZĘT', 'WYSOKI')
    )  # pułapka: slowo "sieciowa"
]


def prompt_zero_shot(zgloszenie):
    return (
        'Zaklasyfikuj poniższe zgłoszenie do jednej z kategorii: '
        'SIEĆ, SPRZĘT, OPROGRAMOWANIE, KONTO oraz określ '
        'priorytet (WYSOKI lub NORMALNY).\n'
        f'Zgłoszenie: """{zgloszenie}"""'
    )


def prompt_few_shot(zgloszenie):
    # przyklady identyczne z promptem z kroku 2
    return (
        'Klasyfikujesz zgłoszenia serwisowe działu IT. '
        'Odpowiadaj wyłącznie w formacie: KATEGORIA | PRIORYTET.'
        '\n\n'
        'Zgłoszenie: """Monitor w pokoju 112 nie włącza się mimo '
        'wymiany kabla zasilającego."""\n'
        'Odpowiedź: SPRZĘT | NORMALNY\n\n'

        'Zgłoszenie: """Nie mogę uzyskać dostępu do systemu USOS '
        '– konto zostało zablokowane, a dziś kończy się '
        'rejestracja na seminaria."""\n'
        'Odpowiedź: KONTO | WYSOKI\n\n'

        'Zgłoszenie: """Po instalacji aktualizacji pakiet Office '
        'przestał otwierać pliki .docx."""\n'
        'Odpowiedź: OPROGRAMOWANIE | NORMALNY\n\n'

        f'Zgłoszenie: """{zgloszenie}"""\n'
        'Odpowiedź:'
    )


# zero-shot dostaje miejsce na swobodna odpowiedz (bez ucinania),
# few-shot wymaga tylko kilku tokenow
WARIANTY = [
    ('zero-shot', prompt_zero_shot, 300),
    ('few-shot', prompt_few_shot, 20)
]


def zapytaj(dostawca, model, prompt, max_tokens):
    """Zwraca odpowiedz modelu albo None przy bledzie."""
    try:
        if dostawca == 'groq':
            for proba in range(1, PROBY_429 + 1):
                try:
                    r = client.chat.completions.create(
                        model=model,
                        messages=[{'role': 'user', 'content': prompt}],
                        temperature=0.0,
                        max_tokens=max_tokens,
                        reasoning_effort='none',
                    )
                    return r.choices[0].message.content.strip()

                except RateLimitError:
                    # blad 429 - odczekaj i ponow zapytanie
                    if proba == PROBY_429:
                        raise

                    print(
                        f'[Limit 429] czekam {PAUZA_429} s '
                        f'(proba {proba}/{PROBY_429})'
                    )
                    time.sleep(PAUZA_429)

        r = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            options={
                'temperature': 0.0,
                'num_predict': max_tokens
            }
        )

        return r['message']['content'].strip()

    except APIError as e:
        print(f'[Blad Groq API] {e}')

    except Exception as e:
        # np. serwer Ollama nie dziala lub brak pobranego modelu
        print(f'[Blad {dostawca}] {e}')

    return None


def najwczesniejsza(odp, etykiety, rdzenie):
    """
    Etykieta wystepujaca najwczesniej w odpowiedzi:
    najpierw dokladne slowa z listy, a gdy ich brak - rdzenie slow.
    """
    trafienia = []

    for e in etykiety:
        m = re.search(r'\b' + e + r'\b', odp)

        if m:
            trafienia.append((m.start(), e))

    if not trafienia:
        for e, wzor in rdzenie.items():
            m = re.search(wzor, odp, re.IGNORECASE)

            if m:
                trafienia.append((m.start(), e))

    return min(trafienia)[1] if trafienia else '?'


# podsumowanie[(wariant, model)] = 'trafnosc / format'
podsumowanie = {}

for dostawca, model in MODELE:
    for opis, buduj, max_tokens in WARIANTY:
        print(f'\n{"#" * 64}')
        print(f'### {model} | {opis}')
        print('#' * 64)

        trafne, fmt_ok, bledy = 0, 0, 0

        for i, (zgl, wzorzec) in enumerate(ZGLOSZENIA, start=1):
            odp = zapytaj(
                dostawca,
                model,
                buduj(zgl),
                max_tokens
            )

            if odp is None:
                bledy += 1
                print(f'{i} [BLAD API] - brak odpowiedzi')
                continue

            kat = najwczesniejsza(odp, KATEGORIE, RDZENIE_KAT)
            pri = najwczesniejsza(odp, PRIORYTETY, RDZENIE_PRI)

            fmt = WZOR_FORMATU.fullmatch(odp) is not None
            ok = (kat, pri) == wzorzec

            trafne += ok
            fmt_ok += fmt

            print(
                f'{i} [{"OK " if ok else "ZLE"}] '
                f'wzorzec={" | ".join(wzorzec):<24} '
                f'wynik={kat} | {pri:<9} '
                f'format={"tak" if fmt else "NIE"}'
            )

            print(' ' + odp.replace('\n', ' | ')[:160])

        n = len(ZGLOSZENIA)

        wynik = f'{trafne}/{n} / {fmt_ok}/{n}'

        if bledy:
            wynik += f' ({bledy} bl.)'

        podsumowanie[(opis, model)] = wynik


print(f'\n{"#" * 64}')
print('### PODSUMOWANIE (trafnosc / format)')
print('#' * 64)

print(
    f'{"WARIANT":<12}'
    + ''.join(f'{m:<22}' for _, m in MODELE)
)

for opis, _, _ in WARIANTY:
    print(
        f'{opis:<12}'
        + ''.join(
            f'{podsumowanie.get((opis, m), "-"):<22}'
            for _, m in MODELE
        )
    )
