import os
import sys
from dotenv import load_dotenv
from groq import Groq

# poprawne wyswietlanie polskich znakow w konsoli Windows
sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = 'openai/gpt-oss-120b'

KONTEKST = """\
Platforma: uczelniana platforma e-learningowa (Moodle)
Termin przerwy: sobota, 15 listopada 2026, od 22:00 do niedzieli, 16 listopada 2026, do 02:00
Czas trwania: 4 godziny
Powód: aktualizacja systemu Moodle do nowszej wersji, migracja bazy danych
i wymiana serwera plików
Skutki: brak dostępu do platformy, kursów, testów i przesyłania prac
Kontakt: helpdesk@uczelnia.pl, tel. 42 000 00 00
"""


ROLA = (
    "Jesteś pracownikiem Centrum Informatyki uczelni odpowiedzialnym za "
    "komunikację z użytkownikami systemów IT. Piszesz jasne, uprzejme "
    "i rzeczowe komunikaty w języku polskim."
)


ZADANIE = (
    "Napisz komunikat o planowanej przerwie technicznej platformy "
    "e-learningowej, wykorzystując wyłącznie dane z sekcji kontekst. "
    "Nie zmieniaj ani nie dodawaj dat, godzin i czasu trwania przerwy. "
    "Nie wymyślaj dodatkowych faktów."
)


WARIANTY = {
    'studenci': {
        'odbiorca': 'studenci',
        'szczegolowosc': (
            'Poziom techniczny: minimalny. Bez żargonu IT. Skup się na tym, '
            'co przerwa oznacza dla studenta i jak się przygotować '
            '(np. zapisać pracę, nie planować testów w tym czasie).'
        ),
        'format': (
            'Temat wiadomości (1 linia), następnie 3-4 krótkie zdania '
            'i lista 2-3 punktów "Co warto zrobić". Maksymalnie 100 słów. '
            'Ton przyjazny.'
        ),
    },
    'wykladowcy': {
        'odbiorca': 'wykładowcy',
        'szczegolowosc': (
            'Poziom techniczny: średni. Wspomnij ogólnie o charakterze prac '
            '(aktualizacja systemu), bez szczegółów infrastruktury. Skup się '
            'na wpływie na zajęcia: testy, terminy zadań, materiały.'
        ),
        'format': (
            'Temat wiadomości, krótkie wprowadzenie, sekcja "Wpływ na zajęcia" '
            'oraz sekcja "Zalecane działania" w formie listy. '
            'Maksymalnie 150 słów. Ton formalny, uprzejmy.'
        ),
    },
    'administratorzy_it': {
        'odbiorca': 'administratorzy IT',
        'szczegolowosc': (
            'Poziom techniczny: wysoki. Podaj zakres prac technicznych '
            '(aktualizacja Moodle, migracja bazy danych, wymiana serwera '
            'plików), zalecenia dotyczące kopii zapasowych, monitoringu '
            'i weryfikacji po zakończeniu prac. Możesz użyć terminologii IT.'
        ),
        'format': (
            'Temat wiadomości, sekcje: "Zakres prac", "Harmonogram", '
            '"Wymagane działania przed/po przerwie" (listy punktowane). '
            'Maksymalnie 200 słów. Ton techniczny, zwięzły.'
        ),
    },
}


def zbuduj_prompt(wariant: dict) -> str:
    """Składa pełny prompt: rola, zadanie, kontekst, format."""
    return f"""\
# ROLA
{ROLA}

# ZADANIE
{ZADANIE}
Odbiorcy komunikatu: {wariant['odbiorca']}.
{wariant['szczegolowosc']}

# KONTEKST
{KONTEKST}

# FORMAT ODPOWIEDZI
{wariant['format']}
Termin oraz czas trwania przerwy muszą być wyraźnie podane w treści.
"""


for nazwa, wariant in WARIANTY.items():
    prompt = zbuduj_prompt(wariant)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {'role': 'user', 'content': prompt},
        ],
        max_tokens=64000,
    )
    print(f'=== {nazwa.upper()} ===')
    print(response.choices[0].message.content, end='\n\n')