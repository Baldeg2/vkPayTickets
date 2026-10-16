from dataclasses import dataclass


@dataclass
class Event:
    id: int
    title: str
    date: str
    price: int
    seats_left: int


@dataclass
class Ticket:
    id: int
    event_id: int
    user_id: int
    code: str
    paid: bool
