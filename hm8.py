from collections import UserDict
from datetime import datetime, timedelta
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if len(value) == 10 and value.isdigit():
            self.__value = value
        else:
            raise ValueError('Invalid phone number')


class Birthday(Field):
    def __init__(self, value):
        try:
            self._date = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if str(phone) == old_phone:
                phone.value = new_phone
                return f"Phone number updated from {old_phone} to {new_phone} for {self.name}."
        return f"Phone number {old_phone} not found for {self.name}."

    def find_phone(self, phone_number):
        for phone in self.phones:
            if str(phone) == phone_number:
                return f"Phone number {phone_number} found for {self.name}."
        return f"Phone number {phone_number} not found for {self.name}."

    def remove_phone(self, phone_number):
        self.phones = [p for p in self.phones if str(p) != phone_number]

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        birthday_info = f", birthday: {self.birthday._date.strftime('%d.%m.%Y')}" if self.birthday else ""
        phones_info = '; '.join(str(phone.value) for phone in self.phones) if self.phones else "No phone numbers"
        return f"Contact name: {self.name.value}, phones: {phones_info}{birthday_info}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return f"Contact '{name}' deleted."
        else:
            return f"Contact '{name}' not found."

    def find_next_weekday(self, weekday):
        days_ahead = weekday - datetime.today().weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return datetime.today() + timedelta(days=days_ahead)

    def get_upcoming_birthdays(self, days=7):
        today = datetime.today().date()
        upcoming_birthdays = []

        for name, record in self.data.items():
            if record.birthday:
                birthday_date = record.birthday._date
                next_birthday_year = today.year if birthday_date.month > today.month or (birthday_date.month == today.month and birthday_date.day >= today.day) else today.year + 1
                next_birthday = birthday_date.replace(year=next_birthday_year)

                if next_birthday.weekday() >= 5:  # If the birthday falls on a weekend
                    next_birthday += timedelta(days=(7 - next_birthday.weekday()))  # Move to the next weekday

                days_until_birthday = (next_birthday - today).days
                if 0 < days_until_birthday <= days:
                    congratulation_date_str = next_birthday.strftime('%Y.%m.%d')
                    upcoming_birthdays.append({
                        "name": name,
                        "congratulation_date": congratulation_date_str
                    })

        return upcoming_birthdays

def parse_input(user_input):
    return user_input.split()

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "KeyError"
        except ValueError:
            return "ValueError"
        except IndexError:
            return "IndexError"
    return wrapper



@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        return "Invalid command format. Usage: add [name] [phone]"
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    if len(args) < 3:
        return "Invalid command format. Usage: change [name] [old phone] [new phone]"
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        if old_phone in [str(phone.value) for phone in record.phones]:
            record.edit_phone(old_phone, new_phone)
            return f"Phone number updated for {name} from {old_phone} to {new_phone}."
        else:
            return f"Phone number {old_phone} not found for {name}."
    else:
        return f"Contact '{name}' not found."


@input_error
def show_phones(args, book: AddressBook):
    if len(args) < 1:
        return "Invalid command format. Usage: phone [name]"
    name = args[0]
    record = book.find(name)
    if record:
        return "; ".join(str(phone.value) for phone in record.phones) if record.phones else f"No phone numbers for {name}."
    else:
        return f"Contact '{name}' not found."


@input_error
def show_all(book: AddressBook):
    if book.data:
        return "\n".join(str(record) for record in book.data.values())
    else:
        return "Address book is empty."


@input_error
def show_birthday(args, book: AddressBook):
    if len(args) < 1:
        return "Invalid command format. Usage: show-birthday [name]"
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday._date.strftime('%d.%m.%Y')}"
    else:
        return f"Contact '{name}' not found or birthday not set."


@input_error
def add_birthday(args, book: AddressBook):
    if len(args) < 2:
        return "Invalid command format. Usage: add-birthday [name] [birthday]"
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}."
    else:
        return f"Contact '{name}' not found."



@input_error
def birthdays(book: AddressBook):
    today = datetime.today().date()
    upcoming_birthdays = book.get_upcoming_birthdays()

    if not upcoming_birthdays:
        return "No upcoming birthdays within the specified days."

    output_lines = []
    for birthday_info in upcoming_birthdays:
        try:
            name = birthday_info["name"]
            next_birthday = datetime.strptime(birthday_info["congratulation_date"], '%Y.%m.%d').date()
            days_until_birthday = (next_birthday - today).days
            output_lines.append(f"Name: {name}, Next Birthday: {next_birthday.strftime('%d.%m.%Y')}, Days Until Birthday: {days_until_birthday}")
        except KeyError as e:
            return f"Unexpected data structure for upcoming birthdays: Missing key {e}."

    return "\n".join(output_lines)



def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
  try:
    with open(filename, "rb") as f:
      return pickle.load(f)
  except FileNotFoundError:
    print("The address book file was not found. A new one is being created.")
    return AddressBook() 


def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book) 
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phones(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()