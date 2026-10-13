import os
from dotenv import load_dotenv
from groq import Groq
# wczytanie klucza z pliku .env do zmiennej srodowiskowej
load_dotenv()
# odczyt klucza API z pliku .env
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    raise SystemExit('Nie znaleziono klucza. Sprawdz, czy plik .env znajduje sie w tym katalogu i czy zawiera GROQ_API_KEY.')
client = Groq(api_key=api_key)

temperatures = [0.0, 0.7, 1.5]
results = {}

for temp in temperatures:
    response = client.chat.completions.create(
        model='openai/gpt-oss-120b',
        messages=[
            {'role': 'system', 'content': 'Odpowiadaj zwiezle, w jezyku polskim.'},
            {'role': 'user', 'content': 'Witaj! Kim jesteś? Opisz krótko swoje możliwości.'},
 ],
    temperature=temp,
    max_tokens=1000,
)
    results[temp] = response.choices[0].message.content
    
for temp, text in results.items():
    print(f'\n===== temperature = {temp} =====')
    print(text)