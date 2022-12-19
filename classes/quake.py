import datetime

class Quake:
    def __init__(self, place: str, mag: float, date: datetime):
        self.place = place
        self.mag = mag
        self.date = date

    def __repr__(self):
        return f"{self.__class__}(place={self.place}, mag={self.mag}, date={self.date})"

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return (self.place, self.mag, self.date) == (other.place, other.mag, other.date)
        else:
            return NotImplemented
