import asyncio
import websockets
import json

matches = []
groups = ["A", "B", "C", "D", "E", "F", "G", "H"]


# async def echo(websocket):
#     async for message in websocket:
#         port = 6000
#         jsonMsg = json.loads(message)
#         await websocket.send('{"return": "Mensagem recebida na porta %s"}' % (port))
#         print('Porta do trabalhador:', jsonMsg['msg1'])


async def worldCupPredict(websocket):
    async for message in websocket:
        allGroups = json.loads(message)
        await groupMatches(allGroups, 0, websocket)


async def groupMatches(teams, groupIndex, websocket):
    await websocket.send('Grupo %s' % groups[groupIndex])
    for team in teams:
        if (team['grupo'] == groups[groupIndex]):
            await websocket.send(team['time'])
    if (groupIndex < len(groups) - 1):
        await websocket.send('-'*8)
        await groupMatches(teams, groupIndex + 1, websocket)


async def resolveMatch():
    print('match')


async def main():
    port = 6000
    async with websockets.serve(worldCupPredict, "localhost", port):
        print('Esperando pedidos...')
        await asyncio.Future()  # run forever

asyncio.run(main())
