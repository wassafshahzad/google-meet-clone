from fastapi.websockets import WebSocket
class SignalManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    @property
    def is_empty(self):
        return len(self.active_connections) == 0

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict, websocket: WebSocket):
        for connection in self.active_connections:
            if connection != websocket:
                await connection.send_json(message)

# Use reddis to handle channel subscriptions
class MeetingManager:
    def __init__(self) -> None:
        self.rooms: dict[str, SignalManager] = {} 

    async def join(self, id: str, websocket: WebSocket):
        if id in self.rooms:
            await self.rooms[id].connect(websocket)
        else:
            self.rooms[id] = SignalManager()
            await self.rooms[id].connect(websocket)
        await self.rooms[id].broadcast({"type":"USER_JOIN"}, websocket)
    
    def leave(self, id: str, websocket: WebSocket):
        self.rooms[id].disconnect(websocket)
        if self.rooms[id].is_empty:
            del self.rooms[id]
        

