from datetime import date, timedelta

COMFORT_LEVELS = ("обычный", "полулюкс", "люкс")

# Скидки по категориям клиента (в процентах).
CATEGORY_DISCOUNTS = {
    "пенсионер": 10,
    "студент": 5,
    "ветеран": 15,
}
LOYALTY_DISCOUNT = 5       # скидка постоянному клиенту (3 и более проживаний)
LOYALTY_MIN_VISITS = 3
MAX_DISCOUNT = 50          # общая скидка не может превышать 50 %


class Client:
    """Клиент гостиницы."""

    def __init__(self, last_name, first_name, patronymic, passport, address,
                 comment="", categories=None):
        self.last_name = last_name
        self.first_name = first_name
        self.patronymic = patronymic
        self.passport = passport
        self.address = address
        self.comment = comment
        self.categories = categories or []   # например ["студент", "ветеран"]
        self.visits = 0                      # сколько раз уже проживал

    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}"

    def discount_percent(self):
        """Скидки СУММИРУЮТСЯ: категории + скидка постоянного клиента."""
        total = 0
        for category in self.categories:
            total += CATEGORY_DISCOUNTS.get(category, 0)
        if self.visits >= LOYALTY_MIN_VISITS:
            total += LOYALTY_DISCOUNT
        return min(total, MAX_DISCOUNT)


class Room:
    """Номер: вместимость (число мест), комфортность, цена за одно место в сутки."""

    def __init__(self, number, capacity, comfort, price):
        if comfort not in COMFORT_LEVELS:
            raise ValueError("Комфортность должна быть одной из: " + ", ".join(COMFORT_LEVELS))
        self.number = number
        self.capacity = capacity
        self.comfort = comfort
        self.price = price

    def __str__(self):
        return f"№{self.number} ({self.comfort}, мест: {self.capacity}, {self.price} руб./место/сутки)"


class Stay:
    """Проживание ОДНОГО клиента на ОДНОМ месте номера."""

    def __init__(self, client, room, check_in):
        self.client = client
        self.room = room
        self.check_in = check_in     # дата заселения
        self.check_out = None        # дата освобождения места (None - ещё живёт)


class Booking:
    """Бронь места в номере на период [date_from, date_to)."""

    def __init__(self, client, room, date_from, date_to):
        self.client = client
        self.room = room
        self.date_from = date_from
        self.date_to = date_to


def overlaps(start1, end1, start2, end2):
    """Пересекаются ли два периода. end = None означает 'без конца'."""
    end1 = end1 or date.max
    end2 = end2 or date.max
    return start1 < end2 and start2 < end1


class Hotel:
    def __init__(self, name):
        self.name = name
        self.rooms = []
        self.clients = []
        self.stays = []
        self.bookings = []

    # ---------- справочники ----------
    def add_room(self, room):
        self.rooms.append(room)

    def add_client(self, client):
        self.clients.append(client)

    # ---------- свободные места ----------
    def free_places(self, room, date_from, date_to):
        """Сколько мест в номере свободно на весь период [date_from, date_to)."""
        busy = 0
        for stay in self.stays:
            if stay.room is room and overlaps(stay.check_in, stay.check_out, date_from, date_to):
                busy += 1
        for booking in self.bookings:
            if booking.room is room and overlaps(booking.date_from, booking.date_to, date_from, date_to):
                busy += 1
        return room.capacity - busy

    def find_rooms(self, places, comfort, max_price, date_from, date_to):
        """Подбор номеров: нужное число свободных мест, комфортность, цена не выше max_price."""
        found = []
        for room in self.rooms:
            if comfort and room.comfort != comfort:
                continue
            if max_price is not None and room.price > max_price:
                continue
            if self.free_places(room, date_from, date_to) >= places:
                found.append(room)
        return found

    # ---------- бронирование ----------
    def book(self, client, room, date_from, date_to):
        if self.free_places(room, date_from, date_to) < 1:
            raise ValueError(f"В номере {room.number} нет свободных мест на этот период")
        booking = Booking(client, room, date_from, date_to)
        self.bookings.append(booking)
        return booking

    # ---------- заселение и выезд ----------
    def check_in(self, client, room, day):
        """Заселение. Если у клиента есть бронь на этот день - она превращается в проживание."""
        for booking in self.bookings:
            if booking.client is client and booking.room is room and \
                    booking.date_from <= day < booking.date_to:
                self.bookings.remove(booking)
                break
        if self.free_places(room, day, day + timedelta(days=1)) < 1:
            raise ValueError(f"В номере {room.number} нет свободных мест")
        stay = Stay(client, room, day)       # фиксируем дату заселения
        self.stays.append(stay)
        return stay

    def check_out(self, client, room, day):
        """Выезд: запоминаем дату освобождения места и считаем стоимость."""
        for stay in self.stays:
            if stay.client is client and stay.room is room and stay.check_out is None:
                stay.check_out = day         # фиксируем дату освобождения
                client.visits += 1
                return stay
        raise ValueError("Такого проживания нет")

    # ---------- расчёт стоимости ----------
    def bill(self, stay, visits_before=None):
        """Возвращает (дней, цена без скидки, скидка %, итог)."""
        days = max(1, (stay.check_out - stay.check_in).days)
        base = days * stay.room.price
        client = stay.client
        if visits_before is not None:
            real = client.visits
            client.visits = visits_before    # скидка считается по визитам ДО этого проживания
            percent = client.discount_percent()
            client.visits = real
        else:
            percent = client.discount_percent()
        total = base * (100 - percent) / 100
        return days, base, percent, total


def print_rooms(rooms):
    print("Номер".ljust(8), "Мест".ljust(6), "Комфорт".ljust(10), "Цена за место".ljust(14))
    for room in rooms:
        print(str(room.number).ljust(8), str(room.capacity).ljust(6),
              room.comfort.ljust(10), str(room.price).ljust(14))


# ====================== ДЕМОНСТРАЦИЯ ======================
if __name__ == "__main__":
    hotel = Hotel("Гостиница «Кавказ»")

    hotel.add_room(Room(101, 2, "обычный", 1500))
    hotel.add_room(Room(102, 3, "обычный", 1200))
    hotel.add_room(Room(201, 2, "полулюкс", 2500))
    hotel.add_room(Room(301, 1, "люкс", 4000))

    ivanov = Client("Иванов", "Пётр", "Сергеевич", "9012 345678", "г. Владикавказ, ул. Мира, 5")
    petrova = Client("Петрова", "Анна", "Ивановна", "9013 111222", "г. Москва, ул. Ленина, 10",
                     "аллергия на ковры", ["пенсионер", "ветеран"])
    sidorov = Client("Сидоров", "Олег", "Петрович", "9014 333444", "г. Беслан, ул. Горная, 3",
                     "", ["студент"])
    sidorov.visits = 3          # постоянный клиент: уже проживал 3 раза
    for c in (ivanov, petrova, sidorov):
        hotel.add_client(c)

    d1 = date(2026, 12, 1)
    d2 = date(2026, 12, 5)

    print("=== 1. Все номера ===")
    print_rooms(hotel.rooms)

    print("\n=== 2. Подбор: 2 места, 'обычный', цена до 1600, период 01.12-05.12 ===")
    print_rooms(hotel.find_rooms(2, "обычный", 1600, d1, d2))

    print("\n=== 3. Бронь: Петрова бронирует место в №201 с 01.12 по 05.12 ===")
    hotel.book(petrova, hotel.rooms[2], d1, d2)
    print("Свободно мест в №201 на этот период:", hotel.free_places(hotel.rooms[2], d1, d2))

    print("\n=== 4. Заселение 01.12 ===")
    hotel.check_in(petrova, hotel.rooms[2], d1)       # по брони
    hotel.check_in(ivanov, hotel.rooms[0], d1)
    hotel.check_in(sidorov, hotel.rooms[1], d1)
    for stay in hotel.stays:
        print(stay.client.full_name().ljust(28), "номер", stay.room.number, "заселён", stay.check_in)

    print("\n=== 5. Попытка заселить ещё одного в люкс №301 (1 место) ===")
    hotel.check_in(ivanov, hotel.rooms[3], d1)
    try:
        hotel.check_in(sidorov, hotel.rooms[3], d1)
    except ValueError as error:
        print("Ошибка:", error)

    print("\n=== 6. Выезд 05.12 и счёт (скидки суммируются) ===")
    for stay in list(hotel.stays):
        before = stay.client.visits
        hotel.check_out(stay.client, stay.room, d2)
        days, base, percent, total = hotel.bill(stay, visits_before=before)
        print(stay.client.full_name().ljust(24), "№" + str(stay.room.number), "|",
              days, "сут. |", base, "руб. | скидка", str(percent) + "% | итого", total, "руб.",
              "| место освобождено", stay.check_out)
