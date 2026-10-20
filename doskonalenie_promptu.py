import os
import sys
import time
from dotenv import load_dotenv
from groq import Groq, APIError

# Poprawne wyświetlanie polskich znaków w konsoli Windows
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

MODEL = 'openai/gpt-oss-120b'

ITERACJA_1 = "Napisz funkcję Python do walidacji adresu e-mail."

ITERACJA_2 = (
    "Napisz funkcję Python walidującą studencki adres e-mail. Adres jest poprawny "
    "wyłącznie w domenie pollub.edu.pl. Funkcja ma używać wyrażeń regularnych i "
    "zwracać True lub False. Dodaj testy jednostkowe dla przypadków: adres "
    "poprawny, zła domena, brak znaku @, pusty łańcuch znaków."
)

PROMPT_ITERACJA_3 = (
    "Jesteś doświadczonym programistą Python w dziale IT uczelni. "
    "Napisz funkcję validate_student_email(email: str) -> bool z użyciem modułu re. Wymagania: "
    "– adres jest poprawny wyłącznie w domenie pollub.edu.pl; "
    "– część lokalna to imie.nazwisko (małe litery łacińskie, bez polskich znaków) "
    "albo sześciocyfrowy numer albumu; "
    "– dodaj docstring z trzema przykładami użycia; "
    "– przygotuj co najmniej 8 testów jednostkowych w pytest, obejmujących m.in.: "
    "poprawny adres z nazwiskiem, poprawny adres z numerem albumu, złą domenę, "
    "brak znaku @, wielkie litery, polskie znaki, pusty łańcuch, dwie kropki w części lokalnej; "
    "– kod ma być zgodny z PEP 8 i zawierać komentarz wyjaśniający wyrażenie regularne."
)


def wykonaj_zapytanie(tytul: str, prompt: str):
    print(f"\n{'=' * 70}\n### {tytul}\n{'=' * 70}")
    try:
        start = time.perf_counter()
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.2,
            max_tokens=1500,
        )
        czas = time.perf_counter() - start
        print(response.choices[0].message.content)
        print(f"\n[Czas odpowiedzi: {czas:.2f} s]")
    except APIError as e:
        print(f"[Błąd Groq API] {e}")


if __name__ == '__main__':
    wykonaj_zapytanie("ITERACJA 1 – PROMPT BAZOWY", ITERACJA_1)
    wykonaj_zapytanie("ITERACJA 2 – DOPRECYZOWANIE WYMAGAŃ", ITERACJA_2)
    wykonaj_zapytanie("ITERACJA 3 – WERSJA FINALNA ZE STRUKTURĄ", PROMPT_ITERACJA_3)