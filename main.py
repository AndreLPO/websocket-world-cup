import asyncio
import json
import random
import pandas
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
        # print("Partida %s" % str(partida))
        resultadoDaPartida = await jogarPartida(timesDoGrupo[x:x+2])
        resultadoDaRodada["resultados"].append(resultadoDaPartida)
        partida += 1
    # print(resultadoDaRodada)
    await websocket.send(json.dumps(resultadoDaRodada, ensure_ascii=False))
    partidasJogadas.append(resultadoDaRodada["resultados"])
    timesOrdenadosParaNovaRodada = defineAsPartidasDaRodada(
        timesDoGrupo, rodada)
    if (rodada == 3):
        await websocket.send(f"Fim da fase de grupos! Resultados do Grupo: {grupo}")
        await classificacaoFinalDaFaseDeGrupos(grupo, partidasJogadas, websocket)

    if (rodada < 3):
        await faseDeGrupos(grupo, timesOrdenadosParaNovaRodada, partidasJogadas, websocket)


def defineChaveParaOrdenacaoDaClassificacao(e):
    return e['pontos']


async def classificacaoFinalDaFaseDeGrupos(grupo, partidas, websocket):
    # TODO https://stackoverflow.com/questions/47055259/python-dict-group-and-sum-multiple-values
    classificacao = []
    for p in partidas:
        for t in p:
            for c in t:
                classificacao.append(c)

    df = pandas.DataFrame(classificacao)
    g = df.groupby('time', as_index=False).sum()
    d = g.to_dict('records')
    d.sort(
        reverse=True, key=defineChaveParaOrdenacaoDaClassificacao)
    await websocket.send(json.dumps({"grupo": grupo, "classificacao": d, "classificados": d[0:2]}, ensure_ascii=False))


def defineChaveParaOrdenacaoDasRodadas(e):
    return e['time']


def defineAsPartidasDaRodada(times, rodada):
    times.sort(key=defineChaveParaOrdenacaoDasRodadas)
    ordem = [0, 1, 2, 3]
    if rodada == 2:
        ordem = [0, 2, 1, 3]
    elif rodada == 3:
        ordem = [0, 3, 2, 1]
    return [times[i] for i in ordem]


async def jogarPartida(timesDaPartida):
    resultadosDaPartidaPorTime = []
    for j in timesDaPartida:
        golsDoTime = ((j['forca']*3) + (j['fifa']*2) + (random.randint(0, 6))) / \
            (j['forca'] + 3 + j['fifa'] + 2 + random.randint(0, 6) + 1)
        resultadosDaPartidaPorTime.append({
            "time": j['time'],
            "gols": int(golsDoTime),
            "pontos": 0
        })

    if (resultadosDaPartidaPorTime[0]['gols'] > resultadosDaPartidaPorTime[1]['gols']):
        resultadosDaPartidaPorTime[0]['pontos'] = 3

    if (resultadosDaPartidaPorTime[0]['gols'] == resultadosDaPartidaPorTime[1]['gols']):
        resultadosDaPartidaPorTime[0]['pontos'] = 1

    if (resultadosDaPartidaPorTime[1]['gols'] > resultadosDaPartidaPorTime[0]['gols']):
        resultadosDaPartidaPorTime[1]['pontos'] = 3

    if (resultadosDaPartidaPorTime[1]['gols'] == resultadosDaPartidaPorTime[0]['gols']):
        resultadosDaPartidaPorTime[1]['pontos'] = 1

    return resultadosDaPartidaPorTime


async def main():
    port = 6000
    async with websockets.serve(previsaoDaCopa, "0.0.0.0", port):
        print(f'Servidor iniciado na porta {port}, aguardando times')
        await asyncio.Future()  # run forever

asyncio.run(main())
