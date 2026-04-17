import os
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

PORT = 8000

rooms = RoomController()

base_dir = "/home/neosahadeo/Videos"
video_files = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = Database()
    for x in db.fetchall():
        rooms._create_room(x[0], x[1])

    for root, dirs, files in os.walk(base_dir):
        dirs.sort()
        files.sort()
        for f in files:
            for exten in [".mp4", ".mkv", ".mp3"]:
                if exten in f:
                    video_files[f] = os.path.relpath(os.path.join(root, f), base_dir)
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/video", StaticFiles(directory=base_dir), name="video")


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
    client_host = websocket.url.hostname

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

    r = rooms.rooms[room_id]
    dummy = {"timestamp": r.timestamp, "paused": r.paused, "src": r.src}

    try:
        while True:
            data = await websocket.receive_text()
            obj = json.loads(data)
            req_type = obj.get("type")
            if req_type == "sync":
                timestamp = obj.get("timestamp")
                leader = obj.get("leader")

                if leader:
                    r.timestamp = timestamp

                dummy["timestamp"] = r.timestamp
                dummy["paused"] = r.paused
                dummy["src"] = r.src

                await websocket.send_text(json.dumps(dummy))
            elif req_type == "command":
                command = obj.get("command")
                # print("command received:", command)
                match (command):
                    case "pause":
                        r.paused = True

                    case "play":
                        r.paused = False

                    case "request src":
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "src": f"http://{client_host}:{PORT}/video/{r.src}",
                                }
                            )
                        )
                    case "request video files":
                        await websocket.send_text(
                            json.dumps({"video_files": list(video_files.keys())})
                        )
                    case "load video":
                        data = obj.get("data")
                        r.src = (
                            f"http://{client_host}:{PORT}/video/{video_files.get(data)}"
                        )

    except WebSocketDisconnect:
        rooms._disconnect(client_id, room_id)


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=PORT, reload=True)
