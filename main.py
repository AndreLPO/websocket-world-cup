import asyncio
import websockets
import json
import sys


async def echo(websocket):
    async for message in websocket:
        port = sys.argv[1]
        jsonMsg = json.loads(message)
        await websocket.send('{"return": "Mensagem recebida na porta %s"}' % (port))

        print('Porta do trabalhador:', jsonMsg['msg1'])


async def createTournamentBracket(websocket):
    print(websocket)


async def main():
    port = sys.argv[1]
    async with websockets.serve(echo, "localhost", port):
        print('Esperando pedidos...')
        await asyncio.Future()  # run forever

asyncio.run(main())
