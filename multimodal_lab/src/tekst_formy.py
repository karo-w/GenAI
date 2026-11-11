
import os
import sys

import ollama
from dotenv import load_dotenv
from groq import Groq


# Poprawne wyświetlanie polskich znaków w konsoli Windows
sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

MODEL_GROQ = "openai/gpt-oss-120b"
MODEL_LOKALNY = "llama3.1"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


FORMY = {
    "definicja": (
        "Jesteś autorem skryptu akademickiego. Napisz zwięzłą "
        'definicję pojęcia "token" w modelach językowych: '
        "3-4 zdania, styl formalny, bez wypunktowań, z jednym "
        "przykładem liczbowym."
    ),

    "post": (
        "Jesteś popularyzatorem technologii. Napisz post (do 500 "
        'znaków) o tym, czym jest "token" w modelach językowych: '
        "lekki ton, jedna analogia z życia codziennego, na końcu "
        "pytanie angażujące czytelników."
    ),

    "e-mail": (
        "Jesteś studentem piszącym do wykładowcy. Napisz uprzejmy "
        "e-mail z prośbą o wyjaśnienie, dlaczego ten sam tekst ma "
        "różną liczbę tokenów w różnych modelach. Temat "
        "wiadomości, zwroty grzecznościowe, maksymalnie 120 "
        "słów."
    ),
}


def zapytaj_groq(prompt):
    r = client.chat.completions.create(
        model=MODEL_GROQ,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1500,
        reasoning_effort="low",
        include_reasoning=False,
    )

    return r.choices[0].message.content


def zapytaj_ollama(prompt):
    r = ollama.chat(
        model=MODEL_LOKALNY,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    return r["message"]["content"]


# Wykonanie zapytań dla każdej formy
for nazwa, prompt in FORMY.items():

    print(f'\n{"#" * 60}\n### FORMA: {nazwa.upper()}')

    print("--- Groq (model zewnętrzny) ---")
    print(zapytaj_groq(prompt))

    print("--- Ollama (model lokalny) ---")
    print(zapytaj_ollama(prompt))
