
from fastapi import FastAPI, staticfiles, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocket, WebSocketDisconnect

from signaling import MeetingManager


app = FastAPI()

app.mount("/static", staticfiles.StaticFiles(directory=f"front-end"), name="static")
templates = Jinja2Templates(directory="templates")

meeting_manager = MeetingManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.websocket("/ws/{client_id}")
async def connet_websocket(websocket: WebSocket, client_id: int):
    await meeting_manager.join(client_id, websocket)
    await meeting_manager.rooms[client_id].broadcast({"type": "NEW_USER"}, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await meeting_manager.rooms[client_id].broadcast(data, websocket)
    except WebSocketDisconnect:
        meeting_manager.leave(client_id, websocket)
