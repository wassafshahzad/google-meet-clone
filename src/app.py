
from fastapi import FastAPI, staticfiles, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocket, WebSocketDisconnect
from signaling import MeetingManager

import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

app = FastAPI()

app.mount("/static", staticfiles.StaticFiles(directory=f"{dir_path}\\front-end"), name="static")
templates = Jinja2Templates(directory="templates")

meeting_manager = MeetingManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/room/{roomName}")
def read_root(request: Request, roomName:str):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/lobby")
def get_lobby(request: Request):
    return templates.TemplateResponse(request=request, name="lobby.html")

@app.websocket("/ws/{client_id}")
async def connet_websocket(websocket: WebSocket, client_id: str):
    await meeting_manager.join(client_id, websocket)
    await meeting_manager.rooms[client_id].broadcast({"type": "NEW_USER"}, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await meeting_manager.rooms[client_id].broadcast(data, websocket)
    except WebSocketDisconnect:
        meeting_manager.leave(client_id, websocket)
