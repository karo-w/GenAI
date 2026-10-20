import re
from typing import Final

# ---------------------------------------------------------------------------
# Regular expression that describes a valid address.
# ---------------------------------------------------------------------------
#   ^                                 – start of string
#   (?:                               – non‑capturing group for the local part
#       [a-z]+\\.[a-z]+               – name.surname (lower‑case latin letters)
#     | \\d{6}                        – or exactly six digits (album number)
#   )
#   @pollub\\.edu\\.pl                – literal domain, dots escaped
#   $                                 – end of string
# ---------------------------------------------------------------------------
_EMAIL_PATTERN: Final[re.Pattern] = re.compile(
    r'^(?:[a-z]+\.[a-z]+|\d{6})@pollub\.edu\.pl$'
)


def validate_student_email(email: str) -> bool:
    """
    Validate a student e‑mail address.

    Parameters
    ----------
    email: str
        The e‑mail address to validate.

    Returns
    -------
    bool
        ``True`` if *email* matches the required pattern, ``False`` otherwise.
    """
    # ``fullmatch`` guarantees that the whole string conforms to the pattern.
    return bool(_EMAIL_PATTERN.fullmatch(email))