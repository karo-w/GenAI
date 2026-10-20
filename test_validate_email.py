import pytest
from validate_email import validate_student_email


@pytest.mark.parametrize(
    "email,expected",
    [
        # 1. poprawny adres z nazwiskiem
        ("jan.kowalski@pollub.edu.pl", True),
        # 2. poprawny adres z numerem albumu
        ("123456@pollub.edu.pl", True),
        # 3. zła domena
        ("jan.kowalski@other.edu.pl", False),
        # 4. brak znaku @
        ("jan.kowalski.pollub.edu.pl", False),
        # 5. wielkie litery w części lokalnej
        ("Jan.Kowalski@pollub.edu.pl", False),
        # 6. polskie znaki w części lokalnej
        ("ąbc.def@pollub.edu.pl", False),
        # 7. pusty łańcuch
        ("", False),
        # 8. dwie kropki w części lokalnej
        ("jan..kowalski@pollub.edu.pl", False),
        # dodatkowe przypadki graniczne
        ("a.b@pollub.edu.pl", True),          # minimalna długość imienia i nazwiska
        ("abcdef@pollub.edu.pl", False),      # brak kropki i nie jest liczbą 6‑cyf.
        ("12345@pollub.edu.pl", False),       # za krótki numer albumu
        ("1234567@pollub.edu.pl", False),     # za długi numer albumu
        ("jan.kowalski@pollub.edu.pl ", False),  # spacja na końcu
        (" jan.kowalski@pollub.edu.pl", False),  # spacja na początku
    ],
)
def test_validate_email(email: str, expected: bool) -> None:
    """Parametrized test covering all required scenarios."""
    assert validate_student_email(email) is expected