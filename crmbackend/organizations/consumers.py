from channels.generic.websocket import AsyncJsonWebsocketConsumer

class OrganizationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.org_id = self.scope["url_route"]["kwargs"]["org_id"]
        self.group_name = f"org_{self.org_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def member_joined(self, event):
        await self.send_json({
            "type": "member_joined",
            "user": event["user"],
        })