import uuid


def process_payment(user_id: int, event_id: int, amount: int) -> str:
    """
    ЗАГЛУШКА платёжной системы.
    В реальном проекте здесь был бы вызов ЮKassa / VK Pay / СБП.
    """
    print(f"[PAYMENT STUB] user={user_id} event={event_id} amount={amount}₽")
    return f"STUB-{uuid.uuid4().hex[:8].upper()}"
