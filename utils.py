import random
import string


def generate_ticket_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "HSE-" + "".join(random.choices(alphabet, k=6))
