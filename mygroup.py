groupmates = [
    {
        "name": "Александр",
        "surname": "Иванов",
        "exams": ["Информатика", "ЭЭиС", "Web"],
        "marks": [4, 3, 5]
    },
    {
        "name": "Иван",
        "surname": "Петров",
        "exams": ["История", "АиГ", "КТП"],
        "marks": [4, 4, 4]
    },
    {
        "name": "Кирилл",
        "surname": "Смирнов",
        "exams": ["Философия", "ИС", "КТП"],
        "marks": [5, 5, 5]
    },
    {
        "name": "Мария",
        "surname": "Кузнецова",
        "exams": ["Информатика", "История", "Web"],
        "marks": [3, 3, 4]
    },
    {
        "name": "Анна",
        "surname": "Соколова",
        "exams": ["Философия", "АиГ", "ИС"],
        "marks": [5, 4, 5]
    },
    {
        "name": "Дмитрий",
        "surname": "Попов",
        "exams": ["Информатика", "КТП", "Web"],
        "marks": [3, 4, 3]
    }
]


def average_mark(student):
    """Возвращает средний балл одного студента."""
    return sum(student["marks"]) / len(student["marks"])


def print_students(students):
    """Выводит таблицу со студентами."""
    print(u"Имя".ljust(15), u"Фамилия".ljust(12), u"Экзамены".ljust(40),
          u"Оценки".ljust(12), u"Ср. балл".ljust(8))
    for student in students:
        print(student["name"].ljust(15),
              student["surname"].ljust(12),
              str(student["exams"]).ljust(40),
              str(student["marks"]).ljust(12),
              str(round(average_mark(student), 2)).ljust(8))


def filter_students(students, min_average):
    """Возвращает новый список студентов, у которых средний балл ВЫШЕ min_average."""
    result = []
    for student in students:
        if average_mark(student) > min_average:
            result.append(student)
    return result


def read_number(prompt):
    """Просит ввести число с клавиатуры, пока пользователь не введёт его правильно."""
    while True:
        text = input(prompt).replace(",", ".")   # разрешаем запятую: 4,5 -> 4.5
        try:
            return float(text)
        except ValueError:
            print("Ошибка: нужно ввести число, например 4 или 4.5. Попробуйте ещё раз.")


print("Все студенты группы:")
print_students(groupmates)
print()

threshold = read_number("Введите средний балл для фильтрации: ")
selected = filter_students(groupmates, threshold)

print()
if selected:
    print("Студенты, у которых средний балл выше", threshold, ":")
    print_students(selected)
else:
    print("Студентов со средним баллом выше", threshold, "нет.")
