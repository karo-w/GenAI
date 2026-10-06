import os
import groq
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    raise SystemExit('Nie znaleziono klucza. Sprawdz, czy plik .env zawiera GROQ_API_KEY.')

client = Groq(api_key=api_key)
MODEL = 'openai/gpt-oss-120b'
PYTANIE = 'Czym jest rekurencja w programowaniu?'       # Pytanie 

PERSONY = {
    'Lakoniczny ekspert techniczny': (
        'Jestes doswiadczonym inzynierem oprogramowania. Odpowiadaj maksymalnie '
        'zwiezle i precyzyjnie, uzywajac poprawnej terminologii. Bez wstepow, '
        'bez analogii, bez zbednych wyjasnien. Po polsku.'
    ),
    'Nauczyciel prostym jezykiem': (
        'Jestes cierpliwym nauczycielem informatyki. Tlumacz pojecia prostym '
        'jezykiem dla poczatkujacego, uzywaj codziennej analogii i krotkiego '
        'przykladu. Unikaj zargonu, a jesli musisz go uzyc, wyjasnij go. Po polsku.'
    ),
}

wyniki = []

for nazwa, instrukcja in PERSONY.items():
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {'role': 'system', 'content': instrukcja},
                {'role': 'user', 'content': PYTANIE},
            ],
            temperature=0.0,
            max_tokens=2000,
        )
    except groq.APIError as e:
        print(f'Blad API dla persony "{nazwa}": {e}')
        continue

    u = response.usage
    wyniki.append((nazwa, u.prompt_tokens, u.completion_tokens, u.total_tokens))

    print(f'\n===== {nazwa} =====')
    print(response.choices[0].message.content)
    print(f'\n[tokeny wejsciowe: {u.prompt_tokens}, '
          f'wyjsciowe: {u.completion_tokens}, lacznie: {u.total_tokens}]')

print('\n===== PODSUMOWANIE =====')
print(f'{"Persona":<32}{"wejsciowe":>10}{"wyjsciowe":>11}{"lacznie":>9}')
for nazwa, wej, wyj, lacz in wyniki:
    print(f'{nazwa:<32}{wej:>10}{wyj:>11}{lacz:>9}')