import os
import sys
import time
from dotenv import load_dotenv
from groq import Groq
from groq import APIError
import ollama

# poprawne wyswietlanie polskich znakow w konsoli Windows
sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# wszystkie warianty uruchamiamy na tym samym modelu
MODEL = "openai/gpt-oss-120b"
# aby uzyc modelu lokalnego, ustaw UZYJ_OLLAMA = True
UZYJ_OLLAMA = True
MODEL_LOKALNY = "llama3.1"
# trzy kreatywne warianty promptu
PROMPTY = {
    "A - analogia": (
        "Wyjaśnij, czym jest mechanizm uwagi w transformerach, używając analogii do rozmowy na tłocznym przyjęciu, podczas której słuchasz wielu osób naraz, ale skupiasz się głównie na tych, którzy mówią o czymś istotnym dla ciebie. Zakończ jednym zdaniem, wskazując, co w tej analogii odpowiada zapytaniu (query), kluczom (keys) i wartościom (values). Maksymalnie 120 słów."
    ),
    "B - storytelling": (
        "Opowiedz krótką historię (do 150 słów) o studentce informatyki, która podczas rodzinnego obiadu tłumaczy babci, czym jest mechanizm uwagi w transformerach. Historia ma zawierać poprawne merytorycznie wyjaśnienie pojęcia."
    ),
    "C - zmiana perspektywy": (
        "Jesteś słowem „był” w zdaniu „Kot zjadł rybę, bo był głodny” przetwarzanym przez warstwę uwagi transformera. Opisz w pierwszej osobie, co dzieje się z tobą: gdy pytasz inne słowa o kontekst, gdy obliczasz wagi uwagi (softmax) i jak powstaje twoja nowa reprezentacja. Maksymalnie 120 słów."
    ),
}


def uruchom_groq(prompt):
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=400,
        reasoning_effort="low",
    )
    return r.choices[0].message.content


def uruchom_ollama(prompt):
    r = ollama.chat(
        model=MODEL_LOKALNY,
        messages=[{"role": "user", "content": prompt}],
    )
    return r["message"]["content"]


for opis, prompt in PROMPTY.items():
    print(f'\n\n{"#" * 64}\n### WARIANT {opis}\n{"#" * 64}')
    print(prompt)
    print("-" * 64)
    try:
        start = time.perf_counter()
        if UZYJ_OLLAMA:
            odpowiedz = uruchom_ollama(prompt)
        else:
            odpowiedz = uruchom_groq(prompt)
        print(odpowiedz)
        print(f"Czas odpowiedzi: {time.perf_counter() - start:.2f}s")
    except APIError as e:
        print(f"[Blad Groq API] {e}")
    except Exception as e:
        print(f"[Blad] {e}")
