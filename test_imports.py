try:
    from groq import Groq
    import dotenv
    print('OK - wszystkie biblioteki zaimportowane poprawnie.')
except ImportError as e:
    print(f'Blad importu: {e}')