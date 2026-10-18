import sqlite3

from config import DB_PATH


def _connect():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = _connect()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        date TEXT NOT NULL,
        price INTEGER NOT NULL,
        seats_left INTEGER NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        code TEXT UNIQUE NOT NULL,
        paid INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()


def get_events():
    conn = _connect()
    rows = conn.execute(
        "SELECT id, title, date, price, seats_left FROM events"
    ).fetchall()
    conn.close()
    return rows


def add_event(title, date, price, seats):
    conn = _connect()
    conn.execute(
        "INSERT INTO events (title, date, price, seats_left) VALUES (?,?,?,?)",
        (title, date, price, seats),
    )
    conn.commit()
    conn.close()


def get_event(event_id):
    conn = _connect()
    row = conn.execute(
        "SELECT id, title, date, price, seats_left FROM events WHERE id=?",
        (event_id,),
    ).fetchone()
    conn.close()
    return row


def decrement_seats(event_id):
    conn = _connect()
    conn.execute(
        "UPDATE events SET seats_left = seats_left - 1 WHERE id=? AND seats_left > 0",
        (event_id,),
    )
    conn.commit()
    conn.close()
def create_ticket(event_id, user_id, code):
    conn = _connect()
    conn.execute(
        "INSERT INTO tickets (event_id, user_id, code, paid) VALUES (?,?,?,1)",
        (event_id, user_id, code),
    )
    conn.commit()
    conn.close()
