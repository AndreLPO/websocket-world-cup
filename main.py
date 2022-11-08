import asyncio
import websockets
import json

groups = ["A", "B", "C", "D", "E", "F", "G", "H"]


async def worldCupPredict(websocket):
    async for message in websocket:
        allGroups = json.loads(message)
        await groupMatches(allGroups, 0, websocket)


async def groupMatches(teams, groupIndex, websocket):
    await websocket.send('Grupo %s' % groups[groupIndex])
    teamsInGroup = list(
        filter(lambda t: t['grupo'] == groups[groupIndex], teams))
    await resolveGroup(teamsInGroup, websocket)
    if (groupIndex < len(groups) - 1):
        await groupMatches(teams, groupIndex + 1, websocket)


async def resolveGroup(groupTeams, websocket):
    # TODO: aplicar funcionalidade e lógica a função
    await websocket.send(json.dumps(groupTeams))


async def playRounds(matchTeams, round, playedMatches, websocket):
    # TODO: aplicar funcionalidade e lógica a função
    print(matchTeams)


async def main():
    port = 6000
    async with websockets.serve(worldCupPredict, "localhost", port):
        print('Esperando pedidos...')
        await asyncio.Future()  # run forever

asyncio.run(main())
