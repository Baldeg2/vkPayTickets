import random
import string


def generate_ticket_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "HSE-" + "".join(random.choices(alphabet, k=6))

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("ticket-bot")


def is_admin(user_id: int, admin_ids: list) -> bool:
    return user_id in admin_ids
