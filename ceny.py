CENA_WE = 0.15   # USD za 1 mln tokenów wejściowych
CENA_WY = 0.60   # USD za 1 mln tokenów wyjściowych

def koszt_zapytania(tok_we, tok_wy):
    return (tok_we * CENA_WE + tok_wy * CENA_WY) / 1_000_000

scenariusze = {
    "Klasyfikacja zgłoszeń": (500, 250, 10),
    "Generowanie raportów":  (500, 150, 1000),
}

for nazwa, (n, we, wy) in scenariusze.items():
    k = koszt_zapytania(we, wy)
    print(f"{nazwa}: {k:.8f} USD za zapytanie, {k * n:.4f} USD za miesiąc")