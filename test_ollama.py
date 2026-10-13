import ollama
response = ollama.chat(
    model='llama3.1',
    messages=[
        {'role': 'system','content':'Odpowiadaj zwięźle, w języku polskim.'},
        {'role': 'user','content': 'Czym jest prompt engineering? ''Odpowiedz w trzech zdaniach.'},
        ],
)
print(response['message']['content'])
