from enum import verify
import uuid
import json
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from src.models import Connection


def generate_id():
    return str(uuid.uuid4())[:6]


def verify_hash(hasher: PasswordHasher, hash, password: str):
    try:
        hasher.verify(hash, password)
        return True
    except VerifyMismatchError:
        return False


class Room:
    id: str
    connections: dict[str, Connection]
    timestamp: float
    timestamps: list[float]
    paused: bool
    hash: str
    hasher: PasswordHasher

    def __init__(self, room_id: str, hash: str, hasher: PasswordHasher):
        self.id = room_id
        self.connections = {}
        self.timestamp = 0
        self.timestamps = []
        self.paused = True
        self.hash = hash
        self.hasher = hasher

    def disconnect(self, client_id: str) -> None:
        if client_id in self.connections:
            del self.connections[client_id]
            return None

    @staticmethod
    def status(room):
        return len(room.connections)

    def pause(self, time: float, password: str):
        ...

        for x in self.connections:
            ...

    def play(self, time: float, password: str):
        ...

        for x in self.connections:
            ...

    def to_dict(self):
        return {
            "room_id": self.id,
            "connections": self.connections,
            "timestamp": self.timestamp,
        }


class RoomController:
    rooms: dict[str, Room]
    hasher: PasswordHasher

    def __init__(self):
        self.rooms = {}
        self.hasher = PasswordHasher()

    def query_room(self, room_id: str, client_id: str) -> bool:
        if self.rooms[room_id] and client_id in self.rooms[room_id].connections:
            return True
        return False

    def _create_room(self, room_id: str, password_hash: str):
        room = Room(room_id, password_hash, self.hasher)
        self.rooms[room_id] = room

    def create_room(self, password: str) -> Room | None:
        id = generate_id()

        if id in self.rooms:
            return None

        hash = self.hasher.hash(password)
        room = Room(id, hash, self.hasher)
        self.rooms[id] = room
        return room

    def _delete_room(self, id: str):
        # Allow password bypass for internal calls
        if id in self.rooms:
            return None

        for x in self.rooms[id].connections:
            self.rooms[id].disconnect(x)

        del self.rooms[id]

    def delete_room(self, room_id: str, password: str) -> None:
        if room_id in self.rooms:
            return None

        room = self.rooms[room_id]

        if verify_hash(self.hasher, room.hash, password):
            return None

        self._delete_room(room_id)

    def _clean(self) -> None:
        for id, obj in self.rooms.items():
            if Room.status(obj) == 0:
                self._delete_room(id)

    def connect(self, room_id: str, client_id: str, password: str) -> Connection | None:
        if not room_id in self.rooms:
            return None

        room = self.rooms[room_id]

        if verify_hash(self.hasher, room.hash, password):
            # if not client_id in room.connections:
            conn = Connection(client_id, room.id)
            room.connections[client_id] = conn
            return conn
        return None

    def _disconnect(self, client_id: str, room_id: str) -> None:
        # Password bypass for internal use
        if room_id in self.rooms:
            return None

        room = self.rooms[room_id]

        if client_id in room.connections:
            del room.connections[client_id]
            return None

    def disconnect(self, client_id: str, room_id: str, password: str) -> None:
        if room_id in self.rooms:
            return None

        room = self.rooms[room_id]

        if verify_hash(self.hasher, room.hash, password):
            return None

        if client_id in room.connections:
            del room.connections[client_id]
            return None
