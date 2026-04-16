from doctest import debug
from fastapi.responses import JSONResponse
from typing import Annotated
import json
import uvicorn
from fastapi import FastAPI, Form, Response, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from src.models import Connection, ConnectionForm
from src.room import RoomController, Room
from src.db import Database

rooms = RoomController()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = Database()
    for x in db.fetchall():
        rooms._create_room(x[0], x[1])
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/video", StaticFiles(directory="/home/neosahadeo/Videos"), name="video")


@app.post("/connect")
def connect(data: Annotated[ConnectionForm, Form()]):
    r = rooms.connect(data.room_id, data.client_id, data.password)
    if r:
        return JSONResponse(r.to_dict())
    return Response(status_code=400)


@app.post("/disconnect")
def disconnect(data: Annotated[ConnectionForm, Form()]):
    rooms.disconnect(data.room_id, data.client_id, data.password)
    return Response(status_code=202)


@app.post("/create_room")
def create_room(password: Annotated[str, Form()]):
    r = rooms.create_room(password)
    if r:
        return JSONResponse(content=r.to_dict(), media_type="application/json")
    return Response(status_code=400)


@app.post("/delete_room")
def delete_room(room_id: Annotated[str, Form()], password: Annotated[str, Form()]):
    rooms.delete_room(room_id, password)
    return Response(status_code=202)


@app.post("/sync")
def sync():
    pass


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        obj = json.loads(data)
        client_id = obj.get("client_id")
        room_id = obj.get("room_id")
        if not client_id or not room_id:
            await websocket.close()
            return None
        if not rooms.query_room(room_id, client_id):
            await websocket.close()
            return None

        dummy = {
            "src": "http://10.10.10.172:8000/video/Movies/Into.the.Wild.2007.1080p.BluRay.x264.YIFY.mp4",
            "timestamp": 0.0,
            "paused": True,
        }
        r = rooms.rooms[room_id]

        while True:
            data = await websocket.receive_text()
            obj = json.loads(data)
            timestamp = obj.get("timestamp")
            leader = obj.get("leader")
            paused = obj.get("paused")
            if leader:
                r.timestamp = timestamp
                r.paused = paused

            dummy["timestamp"] = r.timestamp
            dummy["paused"] = r.paused

            await websocket.send_text(json.dumps(dummy))
    except WebSocketDisconnect:
        rooms._disconnect(client_id, room_id)


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
    print("stuff")
