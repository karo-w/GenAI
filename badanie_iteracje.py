import os
import sys
import time
from dotenv import load_dotenv
from groq import Groq, APIError
import ollama

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

MODEL_GROQ = 'openai/gpt-oss-120b'
MODEL_LOKALNY = 'gemma3:1b' 

ITERACJA_1 = "Przeanalizuj zgłoszenie serwisowe: 'Nie działa mi system dziekanatowy, wyskakuje błąd 500 przy logowaniu.' Określ priorytet i przypisz zespół."

ITERACJA_2 = (
    "Przeanalizuj zgłoszenie serwisowe: 'Nie działa mi system dziekanatowy, wyskakuje błąd 500 przy logowaniu.' "
    "Zwróć wynik jako JSON z polami: priorytet (Niski, Średni, Wysoki, Krytyczny), zespół oraz uzasadnienie. "
    "Nie dodawaj żadnego tekstu poza obiektem JSON."
)

PROMPT_ITERACJA_3 = (
    "Jesteś zaawansowanym systemem klasyfikacji zgłoszeń Helpdesk w uczelni wyższej. "
    "Przeanalizuj poniższe zgłoszenie i zwróć odpowiedź wyłącznie w formacie czystego JSON "
    "(bez znaczników markdown typu ```json, bez dodatkowego tekstu).\n\n"
    "Zgłoszenie: 'Nie działa mi system dziekanatowy, wyskakuje błąd 500 przy logowaniu i nie mogę złożyć podania.'\n\n"
    "Wymagany schemat JSON:\n"
    "{\n"
    '  "priorytet": "Krytyczny | Wysoki | Średni | Niski",\n'
    '  "zespol_docelowy": "S_DEV | S_SYS | S_HELP",\n'
    '  "uzasadnienie": "Krótkie wyjaśnienie w języku polskim"\n'
    "}"
)

def wykonaj_zapytanie_groq(tytul: str, prompt: str):
    print(f"\n{'=' * 70}\n### [CLOUD - GROQ] {tytul}\n{'=' * 70}")
    try:
        start = time.perf_counter()
        response = client.chat.completions.create(
            model=MODEL_GROQ,
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.1,
            max_tokens=800,
        )
        czas = time.perf_counter() - start
        print(response.choices[0].message.content)
        print(f"\n[Czas odpowiedzi: {czas:.2f} s]")
    except APIError as e:
        print(f"[Błąd Groq API] {e}")


def wykonaj_zapytanie_lokalne(tytul: str, prompt: str):
    print(f"\n{'=' * 70}\n### [LOCAL - OLLAMA] {tytul}\n{'=' * 70}")
    try:
        start = time.perf_counter()
        response = ollama.chat(
            model=MODEL_LOKALNY,
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.1}
        )
        czas = time.perf_counter() - start
        print(response['message']['content'])
        print(f"\n[Czas odpowiedzi: {czas:.2f} s]")
    except Exception as e:
        print(f"[Model lokalny niedostępny / Brak Ollama] {e}")


if __name__ == '__main__':
    wykonaj_zapytanie_groq("ITERACJA 1 – PROMPT BAZOWY", ITERACJA_1)
    wykonaj_zapytanie_groq("ITERACJ 2 – DOPRECYZOWANIE (JSON)", ITERACJA_2)
    wykonaj_zapytanie_groq("ITERACJA 3 – WERSJA FINALNA", PROMPT_ITERACJA_3)
    
    wykonaj_zapytanie_lokalne("ITERACJA 1 – PROMPT BAZOWY (LOKALNIE)", ITERACJA_1)
    wykonaj_zapytanie_lokalne("ITERACJA 2 – DOPRECYZOWANIE (LOKALNIE)", ITERACJA_2)
    wykonaj_zapytanie_lokalne("ITERACJA 3 – WERSJA FINALNA (LOKALNIE)", PROMPT_ITERACJA_3)