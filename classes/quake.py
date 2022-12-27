import datetime
from dataclasses import dataclass, field


@dataclass(order=True)
class Quake:
    id: int = field()
    place: str = field()
    mag: float = field()
    date: datetime = field()
