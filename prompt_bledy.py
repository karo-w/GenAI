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

print("Wpisz prompt i nacisnij Enter. Aby zakonczyc, wpisz 'koniec'.")

while True:
    try:
        prompt = input('\nTy: ').strip()
    except (EOFError, KeyboardInterrupt):
        print('\nPrzerwano przez uzytkownika.')
        break

    if prompt.lower() == 'koniec':
        print('Koniec programu. Do zobaczenia!')
        break
    if not prompt:
        print('Pusty prompt, wpisz cos lub "koniec".')
        continue

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {'role': 'system', 'content': 'Odpowiadaj zwiezle, w jezyku polskim.'},
                {'role': 'user', 'content': prompt},
            ],
            max_tokens=1000,
        )
        print(f'\nModel: {response.choices[0].message.content}')
    except groq.APIStatusError as e:
        print(f'\nBlad API (kod {e.status_code}): {e.message}')
        print('Mozesz wpisac kolejny prompt lub "koniec".')
    except groq.APIConnectionError:
        print('\nBlad polaczenia z serwerem. Sprawdz internet i sprobuj ponownie.')
    except groq.APIError as e:
        print(f'\nBlad API: {e.message}')