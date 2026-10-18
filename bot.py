
import json
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from config import VK_TOKEN, GROUP_ID, ADMIN_IDS
from database import (init_db, get_events, get_event, create_ticket,
                      decrement_seats, get_user_tickets, add_event)
from payment import process_payment
from utils import generate_ticket_code, log, is_admin


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

KEYBOARD_BACK = {
    "one_time": False,
    "buttons": [
        [{"action": {"type": "text", "label": "🏠 В меню"}, "color": "secondary"}]
    ],
}


def send(user_id, text, keyboard=None):
    try:
        vk.messages.send(
            user_id=user_id,
            message=text,
            random_id=0,
            keyboard=json.dumps(keyboard, ensure_ascii=False) if keyboard else None,
        )
    except Exception as e:
        log.error(f"send failed to {user_id}: {e}")


def events_keyboard(events):
    buttons = [
        [{
            "action": {"type": "text", "label": f"#{eid} {title[:30]}"},
            "color": "primary",
        }]
        for eid, title, date, price, seats in events
    ]
    buttons.append([{"action": {"type": "text", "label": "🏠 В меню"}, "color": "secondary"}])
    return {"one_time": False, "buttons": buttons}


def handle_message(event):
    text = event.text.strip()
    uid = event.user_id

    if text.lower() in ("начать", "/start", "start", "🏠 в меню"):
        send(uid, "Привет! Это бот мероприятий ВШЭ.\nВыбери действие:", KEYBOARD_START)

    elif text == "🎟 Мероприятия":
        events = get_events()
        if not events:
            send(uid, "Пока нет мероприятий.", KEYBOARD_BACK)
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
            send(uid, "Мероприятие не найдено.", KEYBOARD_BACK)
            return
        _, title, date, price, seats = ev
        if seats <= 0:
            send(uid, "Мест больше нет 😢", KEYBOARD_BACK)
            return

        tx = process_payment(uid, eid, price)
        code = generate_ticket_code()
        create_ticket(eid, uid, code)
        decrement_seats(eid)
        log.info(f"Ticket {code} sold to {uid} (tx={tx})")
        send(
            uid,
            f"✅ Билет на «{title}» куплен!\n"
            f"📅 {date}\n"
            f"🎫 Код: {code}\n\n"
            f"Покажи этот код на входе.",
            KEYBOARD_BACK,
        )

    elif text == "📋 Мои билеты":
        tickets = get_user_tickets(uid)
        if not tickets:
            send(uid, "У тебя пока нет билетов.", KEYBOARD_BACK)
        else:
            body = "\n\n".join(
                f"🎫 {t}\n📅 {d}\nКод: {c}" for c, t, d in tickets
            )
            send(uid, body, KEYBOARD_BACK)

    elif text.startswith("/add_event"):
        if not is_admin(uid, ADMIN_IDS):
            send(uid, "⛔ Команда только для админов.", KEYBOARD_BACK)
            return
        try:
            _, payload = text.split(" ", 1)
            title, date, price, seats = [x.strip() for x in payload.split("|")]
            add_event(title, date, int(price), int(seats))
            send(uid, f"✅ Мероприятие '{title}' добавлено.", KEYBOARD_BACK)
            log.info(f"Event added by {uid}: {title}")
        except Exception as e:
            send(
                uid,
                "Ошибка формата.\n"
                "Используй: /add_event Название | Дата | Цена | Мест\n"
                "Пример: /add_event ДОД | 2025-12-01 | 0 | 50",
                KEYBOARD_BACK,
            )
            log.error(f"add_event error: {e}")

    elif text == "/myid":
        send(uid, f"Твой ID: {uid}", KEYBOARD_BACK)

    else:
        send(uid, "Не понял команду. Используй меню ниже.", KEYBOARD_START)


def main():
    init_db()
    log.info(f"Bot started. Group ID: {GROUP_ID}")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            try:
                handle_message(event)
            except Exception as e:
                log.exception(f"Handler error: {e}")


if __name__ == "__main__":
    main()
