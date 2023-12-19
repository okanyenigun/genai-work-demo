import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from monitor.services.stream.facade import StreamFacade


class TwoConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.running = False
        self.data_type = "normal"
        await self.accept()
        print("in conncet", self.running)
        asyncio.ensure_future(self.send_data())

    async def send_data(self):
        print("in sden")
        S = StreamFacade()
        tour = 1
        print("tour: ", tour)
        while tour < 1000:
            # print("in while")
            if self.running:
                data = await S.stream(tour, self.data_type)
                await self.send(text_data=data)
                tour += 1
            await asyncio.sleep(0.00001)
        # D = DomainTwo()
        # i = 1
        # while i < 1000:
        #     print("in wigle")
        #     if self.running:
        #         data = await D.do(i)
        #         await self.send(text_data=data)
        #         i += 1
        #     await asyncio.sleep(2)  # Sleep outside the if condition

    async def receive(self, text_data):
        print("in receive")
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        try:
            button_id = text_data_json['buttonId']
        except:
            button_id = None
        if button_id == "data-normal":
            self.data_type = "normal"
        elif button_id == "data-drift":
            self.data_type = "data_drift"
        elif button_id == "concept-drift":
            self.data_type = "concept_drift"
        else:
            self.data_type = "normal"
        if action == 'stop':
            self.running = False
        elif action == 'start':
            self.running = True
        print("running:", self.running)
        print("data_type:", self.data_type)

    # You should also handle disconnects
    async def disconnect(self, close_code):
        # Stop the data sending loop
        self.running = False
