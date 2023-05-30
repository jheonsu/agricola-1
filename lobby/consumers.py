from typing import List

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from core.redis import connection
from lobby.models import Room

LOBBY = "lobby"


class LobbyConsumer(AsyncJsonWebsocketConsumer):
    user_id: int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis = connection()

    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['pk']

        await self.channel_layer.group_add(
            LOBBY,
            self.channel_name
        )

        await self.accept()
        await self.send_json(list(map(self.room_in_participant, self.redis.lrange(LOBBY, 0, -1))))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            LOBBY,
            self.channel_name
        )

    async def receive_json(self, content, **kwargs):
        rooms = list(map(self.room_in_participant, self.redis.lrange(LOBBY, 0, -1)))
        command, title, is_chat, mode, password, time_limit = await self.parse_command(content)

        if command == "create" and not any(room["host"] == self.user_id for room in rooms):
            new_room = Room.create_room(
                host=self.user_id,
                options={
                    "title": title,
                    "is_chat": is_chat,
                    "mode": mode,
                    "password": password,
                    "time_limit": time_limit,
                }
            )

            self.redis.lpush(LOBBY, str(new_room.to_lobby_dict()))
            self.redis.sadd(f"rooms:{new_room.get('room_id')}:participant", self.user_id)

            rooms.append(new_room.to_lobby_dict())

        return await self.channel_layer.group_send(
            LOBBY,
            {
                "type": "message",
                "message": {
                    "rooms": rooms,
                }
            }
        )

    def room_in_participant(self, room: str) -> dict:
        return {
            **eval(room),
            "participant": self.redis.scard(f"rooms:{eval(room).get('room_id')}:participant")
        }

    async def parse_command(self, content: dict) -> tuple[str, str, bool, str, str, int]:
        command: str = content.get("command", "create")
        title: str = content.get("title", f"{self.user_id}님의 방")
        is_chat: bool = content.get("is_chat", False)
        mode: str = content.get("mode", "public")
        password: str = content.get("password", "")
        time_limit: int = content.get("time_limit", 30)
        return command, title, is_chat, mode, password, time_limit

    async def message(self, event):
        await self.send_json(event['message'])


class RoomConsumer(AsyncJsonWebsocketConsumer):
    user_id: int
    room_id: int
    room: str

    def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['pk']
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room = f"room_{self.room_id}"

        self.channel_layer.group_add(
            self.room,
            self.channel_name
        )

        self.accept()

    def disconnect(self, code):
        self.channel_layer.group_discard(
            self.room,
            self.channel_name
        )

    def receive_json(self, content, **kwargs):
        pass

    async def message(self, event) -> None:
        return await self.send_json(event['message'])
