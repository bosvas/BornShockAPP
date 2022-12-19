from dataclasses import dataclass, field


@dataclass(order=True)
class Person:
    id: int = field()
    name: str = field()
    date_of_birth: str = field()
    address: str = field()



