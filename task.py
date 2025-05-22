import uuid
from datetime import datetime

class Task:

    # параметры класса
    STATUS_ACTIVE = "active"
    STATUS_DONE = "done"

    # коструктор
    def __init__(self, id, descr, date, date_created, status):
        self.id = id
        self.descr = descr
        self.date = date
        self.date_created = date_created
        self.status = status

    # метод экземпляра класса
    def to_output(self):
        return ("✓" if self.status == self.STATUS_ACTIVE else "✕") + " " + self.descr + " " + self.date + " " + self.date_created


    # метод класса, эмулирующий упрощённый конструктор
    @classmethod
    def new_from_user(cls, description, date):
        return cls(uuid.uuid4(), description, date, str(datetime.now()), cls.STATUS_ACTIVE)