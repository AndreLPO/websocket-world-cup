import asyncio
import json
import random

import websockets

grupos = ["A", "B", "C", "D", "E", "F", "G", "H"]
# Bla


async def previsaoDaCopa(websocket):
    async for message in websocket:
        todosOsGrupos = json.loads(message)
        await partidasPorGrupo(todosOsGrupos, 0, websocket)


async def partidasPorGrupo(teams, groupIndex, websocket):
    timesNoGrupo = list(
        filter(lambda t: t['grupo'] == grupos[groupIndex], teams))
    await faseDeGrupos(grupos[groupIndex], timesNoGrupo, [], websocket)
    if (groupIndex < len(grupos) - 1):
        await partidasPorGrupo(teams, groupIndex + 1, websocket)


async def faseDeGrupos(grupo, timesDoGrupo, partidasJogadas, websocket):
    rodada = len(partidasJogadas) + 1
    await websocket.send(f"Rodada {rodada}")
    partida = 1
    resultadoDaRodada = {
        "grupo": grupo,
        "resultados": []
    }
    for i in range(0, 4, 2):
        x = i
        print("Partida %s" % str(partida))
        resultadoDaPartida = await jogarPartida(timesDoGrupo[x:x+2])
        resultadoDaRodada["resultados"].append(resultadoDaPartida)
        partida += 1
    print(resultadoDaRodada)
    await websocket.send(json.dumps(resultadoDaRodada))
    partidasJogadas.append(resultadoDaRodada["resultados"])
    if (rodada < 3):
        await faseDeGrupos(grupo, timesDoGrupo, partidasJogadas, websocket)


def verificaSeOsTimesJaJogaram(times, partidasJogadas):
    print("bla")


async def jogarPartida(timesDaPartida):
    resultadosDosJogos = []
    for j in timesDaPartida:
        golsDoTime = (j['forca'] / 10) * random.randint(0, 6)
        resultadosDosJogos.append({
            "time": j['time'],
            "gols": int(golsDoTime),
            "pontos": 0
        })

    if (resultadosDosJogos[0]['gols'] > resultadosDosJogos[1]['gols']):
        resultadosDosJogos[0]['pontos'] = 3

    if (resultadosDosJogos[0]['gols'] == resultadosDosJogos[1]['gols']):
        resultadosDosJogos[0]['pontos'] = 1

    if (resultadosDosJogos[1]['gols'] > resultadosDosJogos[0]['gols']):
        resultadosDosJogos[1]['pontos'] = 3

    if (resultadosDosJogos[1]['gols'] == resultadosDosJogos[0]['gols']):
        resultadosDosJogos[1]['pontos'] = 1

    return resultadosDosJogos


async def main():
    port = 6000
    async with websockets.serve(previsaoDaCopa, "localhost", port):
        print(f'Servidor iniciado na porta {port}, aguardando times')
        await asyncio.Future()  # run forever

asyncio.run(main())
