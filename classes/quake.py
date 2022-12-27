import datetime
from dataclasses import dataclass, field
from classes.person import Person


@dataclass(order=True)
class Quake:
    id: int = field()
    place: str = field()
    mag: float = field()
    date: datetime = field()
    person: Person = field()
