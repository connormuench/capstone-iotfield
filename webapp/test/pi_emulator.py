import asyncio
import websockets

async def hello():
    async with websockets.connect('ws://192.168.0.11:3001') as websocket:
       
        msg = "hi"
        await websocket.send(msg)

        while (True):
            msg = await websocket.recv()
            print(msg)

            if msg =="ping":
                print ("pong")
            if msg=="pong":
                print ("ping")


asyncio.get_event_loop().run_until_complete(hello())