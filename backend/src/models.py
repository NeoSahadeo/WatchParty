from dataclasses import dataclass
from pydantic import BaseModel


class ConnectionForm(BaseModel):
    client_id: str
    room_id: str
    password: str


@dataclass
class Connection:
    client_id: str
    room_id: str

    def __init__(self, client_id, room_id):
        self.client_id = client_id
        self.room_id = room_id

    def to_dict(self):
        return {"room_id": self.room_id, "client_id": self.client_id}
