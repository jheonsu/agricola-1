from channels.generic.websocket import AsyncJsonWebsocketConsumer

from core.redis import connection
from play.models.game import Game


class GameConsumer(AsyncJsonWebsocketConsumer):
    id: int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis = connection()
        game = Game.initialize(["1", "2", "3", "4"])
        self.redis.set("game_3", str(game.to_dict()))

    async def connect(self):
        self.id = self.scope['url_route']['kwargs']['pk']
        await self.channel_layer.group_add(
            f"game_{self.id}",
            self.channel_name
        )

        data = self.redis.get(f"game_{self.id}")

        await self.accept()

        await self.send_json(eval(data))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            f"game_{self.id}",
            self.channel_name
        )

    # {
    #     "type": "action",
    #     "player": 0,
    #     "number": "EARN_001"
    # }
    async def receive_json(self, content, **kwargs):
        data = self.redis.get(f"game_{self.id}")
        game = Game.from_dict(**eval(data.decode("utf-8")))
        game.play(content)

        await self.channel_layer.group_send(
            f"game_{self.id}",
            {
                'type': 'game_message',
                'message': {
                    'data': str(game.to_dict())
                }
            }
        )

    async def game_message(self, event):
        await self.send_json(event['message'])
