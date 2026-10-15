import json
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from config import VK_TOKEN, GROUP_ID


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


def handle_message(event):
    text = event.text.strip()
    uid = event.user_id

    if text.lower() in ("начать", "/start", "start"):
        send(uid, "Привет! Это бот мероприятий ВШЭ.", KEYBOARD_START)


def main():
    print(f"Bot started. Group ID: {GROUP_ID}")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            handle_message(event)


if __name__ == "__main__":
    main()