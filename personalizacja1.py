import os
from dotenv import load_dotenv
from groq import Groq

# Wczytuje klucz z pliku .env
load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


MODEL = "openai/gpt-oss-120b" 

PROMPTY = {
    "Wersja A (Biznes)": (
        "Wyjaśnij właścicielowi małej firmy, bez wykształcenia technicznego, "
        "czym jest konteneryzacja aplikacji (Docker) i jakie korzyści biznesowe daje jej wdrożenie. "
        "Użyj codziennej analogii i unikaj żargonu technicznego. Maksymalnie 100 słów."
    ),
    "Wersja B (Student)": (
        "Wyjaśnij studentowi pierwszego roku informatyki, czym jest kontener Dockera i "
        "czym różni się od maszyny wirtualnej. Użyj podstawowych pojęć z systemów "
        "operacyjnych i podaj jedno przykładowe polecenie docker run. Około 150 słów."
    ),
    "Wersja C (Admin)": (
        "Przedstaw doświadczonemu administratorowi systemów zwięzłe porównanie "
        "kontenerów i maszyn wirtualnych na poziomie izolacji zasobów (przestrzenie "
        "nazw, cgroups). Wskaż dwa typowe zastosowania produkcyjne i jedno ryzyko "
        "bezpieczeństwa. Około 150 słów, forma zwięzłych akapitów."
    ),
}

for wersja, prompt in PROMPTY.items():
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    odpowiedz = response.choices[0].message.content
    liczba_slow = len(odpowiedz.split())

    print(f"================== {wersja} ==================")
    print(odpowiedz)
    print(f"\n[Liczba wygenerowanych słów: {liczba_slow}]")
    print("=" * 50 + "\n")