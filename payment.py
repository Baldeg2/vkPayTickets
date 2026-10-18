import uuid


def process_payment(user_id: int, event_id: int, amount: int) -> str:

    print(f"[PAYMENT STUB] user={user_id} event={event_id} amount={amount}₽")
    return f"STUB-{uuid.uuid4().hex[:8].upper()}"
