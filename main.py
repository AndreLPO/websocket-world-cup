import asyncio
import json
import random

import websockets

groups = ["A", "B", "C", "D", "E", "F", "G", "H"]
# Bla


async def worldCupPredict(websocket):
    async for message in websocket:
        allGroups = json.loads(message)
        await groupMatches(allGroups, 0, websocket)


async def groupMatches(teams, groupIndex, websocket):
    await websocket.send('Grupo %s' % groups[groupIndex])
    teamsInGroup = list(
        filter(lambda t: t['grupo'] == groups[groupIndex], teams))
    await resolveGroup(teamsInGroup, [], websocket)
    if (groupIndex < len(groups) - 1):
        await groupMatches(teams, groupIndex + 1, websocket)


async def resolveGroup(groupTeams, playedMatches, websocket):
    print("Rodada 1")
    for i in range(0, 4, 2):
        x = i
        print("Partida %s" % str(i + 1))
        matchResult = await playRounds(groupTeams[x:x+2])
        print(matchResult)
        
    await websocket.send(json.dumps(groupTeams))


async def playRounds(matchTeams):
    gameResults = []
    for j in matchTeams:
        teamGoal = (j['forca'] / 10) * random.randint(0,6)
        gameResults.append({
            "time": j['time'],
            "gols": int(teamGoal),
            "points": 0
            })
    
    if (gameResults[0]['gols'] > gameResults[1]['gols']):
        gameResults[0]['points'] = 3
    
    if (gameResults[0]['gols'] == gameResults[1]['gols']):
        gameResults[0]['points'] = 1

    if (gameResults[1]['gols'] > gameResults[0]['gols']):
        gameResults[1]['points'] = 3
    
    if (gameResults[1]['gols'] == gameResults[0]['gols']):
        gameResults[1]['points'] = 1

    return gameResults


async def main():
    port = 6000
    async with websockets.serve(worldCupPredict, "localhost", port):
        print('Esperando pedidos...')
        await asyncio.Future()  # run forever

asyncio.run(main())
