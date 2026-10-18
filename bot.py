import json
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from config import VK_TOKEN, GROUP_ID
from database import (init_db, get_events, get_event, create_ticket,
                      decrement_seats, get_user_tickets)
from payment import process_payment
from utils import generate_ticket_code


vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


KEYBOARD_START = {
    "one_time": False,
    "buttons": [
        [
            {"action": {"type": "text", "label": "🎟 Мероприятия"}, "color": "primary"},
            {"action": {"type": "text", "label": "📋 Мои билеты"}, "color": "secondary"},
        ]
    ],
}


def send(user_id, text, keyboard=None):
    vk.messages.send(
        user_id=user_id,
        message=text,
        random_id=0,
        keyboard=json.dumps(keyboard, ensure_ascii=False) if keyboard else None,
    )


def events_keyboard(events):
    buttons = [
        [{
            "action": {"type": "text", "label": f"#{eid} {title[:30]}"},
            "color": "primary",
        }]
        for eid, title, date, price, seats in events
    ]
    return {"one_time": False, "buttons": buttons}


def handle_message(event):
    text = event.text.strip()
    uid = event.user_id

    if text.lower() in ("начать", "/start", "start"):
        send(uid, "Привет! Это бот мероприятий ВШЭ.", KEYBOARD_START)

    elif text == "🎟 Мероприятия":
        events = get_events()
        if not events:
            send(uid, "Пока нет мероприятий.")
        else:
            listing = "\n".join(
                f"#{e} {t} | {d} | {p}₽ | мест: {s}"
                for e, t, d, p, s in events
            )
            send(uid, "Выбери мероприятие:\n" + listing, events_keyboard(events))

    elif text.startswith("#"):
        try:
            eid = int(text.split()[0][1:])
        except (ValueError, IndexError):
            send(uid, "Не понял номер мероприятия.")
            return
        ev = get_event(eid)
        if not ev:
            send(uid, "Мероприятие не найдено.")
            return
        _, title, date, price, seats = ev
        if seats <= 0:
            send(uid, "Мест больше нет 😢")
            return

        tx = process_payment(uid, eid, price)
        code = generate_ticket_code()
        create_ticket(eid, uid, code)
        decrement_seats(eid)
        print(f"Ticket {code} sold to {uid} (tx={tx})")
        send(uid, f"✅ Билет на «{title}» куплен!\n📅 {date}\n🎫 Код: {code}")

    elif text == "📋 Мои билеты":
        tickets = get_user_tickets(uid)
        if not tickets:
            send(uid, "У тебя пока нет билетов.")
        else:
            body = "\n\n".join(
                f"🎫 {t}\n📅 {d}\nКод: {c}" for c, t, d in tickets
            )
            send(uid, body)


def main():
    init_db()
    print(f"Bot started. Group ID: {GROUP_ID}")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            handle_message(event)


if __name__ == "__main__":
    main()
