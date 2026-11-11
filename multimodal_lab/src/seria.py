import os

from obraz import generuj_obraz


# Stały przewodnik stylu (po angielsku - FLUX najlepiej rozumie angielski).
# Tłumaczenie:
# Minimalistyczna płaska ikona w stylu grafiki wektorowej,
# grube zaokrąglone kontury, paleta granatowo-biała z jednym
# pomarańczowym akcentem, białe tło, bez tekstu, bez cieni,
# kompozycja wyśrodkowana. Podmiot:
STYL = (
    "Minimalist flat icon in vector graphic style, thick rounded "
    "outlines, navy blue and white palette with a single orange "
    "accent, white background, no shadows, centered "
    "composition. Subject: "
)

# Zmienne podmioty serii
# (laptop z otwartym terminalem, chmura obliczeniowa, klucz API)
PODMIOTY = [
    # "a laptop with an open terminal window",
    # "a computing cloud",
    # "an API key",
    'a shield with the text "PROMPT ENGINEERING"',
]


if __name__ == "__main__":

    os.makedirs("out", exist_ok=True)

    for i, podmiot in enumerate(PODMIOTY, start=1):
        print(f"[{i}/{len(PODMIOTY)}] {podmiot}...")
        generuj_obraz(STYL + podmiot, f"out/ikona_bez_no_text_{i}.png")