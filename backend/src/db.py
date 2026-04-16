from pdb import help
import sqlite3
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from src.room import generate_id


class Database:
    """
    Used of persistent/reserved rooms. Rooms are stored as in-memory
    and therefore this should not be used a primary room storage.
    """

    conn: sqlite3.Connection
    cursor: sqlite3.Cursor

    def __init__(self):
        self.conn = sqlite3.connect("storage.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
           CREATE TABLE IF NOT EXISTS rooms (
               room_id VARCHAR(6) PRIMARY KEY,
               password_hash BLOB NOT NULL
            )
        """)

    def insert(self, room_id, password) -> bool:
        self.cursor.execute("SELECT * FROM rooms WHERE room_id = ?", (room_id,))
        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute(
                "INSERT INTO rooms VALUES (?, ?)", (room_id, ph.hash(password))
            )
            self.conn.commit()
            print("Inserted successfully")
            print(f"Room ID: {room_id}")
            print(f"Password: {password}")
            return True
        return False

    def delete(self, room_id) -> bool:
        self.cursor.execute(
            "SELECT password_hash FROM rooms WHERE room_id = ?", (room_id,)
        )
        try:
            # ph.verify(self.cursor.fetchone()[0], password)
            self.cursor.execute("DELETE FROM rooms WHERE room_id = ?", (room_id,))
            self.conn.commit()
            print("Deleted successfully")
            return True
        except VerifyMismatchError:
            return False

    def fetchall(self):
        self.cursor.execute("SELECT room_id, password_hash FROM rooms")
        return self.cursor.fetchall()

    def list(self):
        self.cursor.execute("SELECT room_id FROM rooms")
        print("List of rooms:")
        for x in self.cursor.fetchall():
            print(f" {x[0]}")

    def __del__(self):
        self.conn.close()


def help_menu():
    print("""Commands:
  insert \t\t\t Interactive room creation
  insert [ROOM_ID] [PASSWORD] \t Create a permenant room
  delete [ROOM_ID] \t\t Delete a permenant room
  list \t\t\t\t List room ids
          """)


if __name__ == "__main__":
    db = Database()
    ph = PasswordHasher()
    print("WatchParty Database Manager:")
    try:
        while True:
            user_input = input("> ").strip().lower().split()
            if len(user_input) == 0:
                help_menu()
                continue
            match (user_input[0]):
                case "help":
                    help_menu()
                case "insert":
                    room_id = None
                    password = None
                    if len(user_input) == 1:
                        room_id = (
                            input("ROOM ID [leave blank to auto generate]:")
                            .strip()
                            .lower()
                        )
                        if room_id == "":
                            room_id = generate_id()
                        password = input("Password: ")
                    elif len(user_input) == 3:
                        room_id = user_input[1]
                        password = user_input[2]
                    else:
                        help_menu()
                        break
                    db.insert(room_id, password)
                case "delete":
                    if len(user_input) == 2:
                        db.delete(user_input[1])
                    else:
                        help_menu()
                case "list":
                    db.list()
                case _:
                    help_menu()
    except KeyboardInterrupt:
        print("\nGoodbye!")
