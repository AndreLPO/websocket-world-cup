import asyncio
import json
import math
import random

import pandas
import websockets

grupos = ["A", "B", "C", "D", "E", "F", "G", "H"]
classificacaoGeral = []


async def previsaoDaCopa(websocket):
    async for message in websocket:
        todosOsGrupos = json.loads(message)
        await partidasPorGrupo(todosOsGrupos, 0, websocket)
        await websocket.send(json.dumps(classificacaoGeral , ensure_ascii=False))


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
    return e['pontos'], e['gols']


async def classificacaoFinalDaFaseDeGrupos(grupo, partidas, websocket):
    classificacao = []
    for p in partidas:
        for t in p:
            for c in t:
                classificacao.append(c)

    df = pandas.DataFrame(classificacao)
    g = df.groupby(['time', 'fifa', 'forca'], as_index=False)['gols','pontos'].sum(numeric_only=False)
    d = g.to_dict('records')
    d.sort(
        reverse=True, key=defineChaveParaOrdenacaoDaClassificacao)
    
    resultadoFinalDoGrupo = {"grupo": grupo, "classificacao": d, "classificados": d[0:2]}
    classificacaoGeral.append(resultadoFinalDoGrupo)
    await websocket.send(json.dumps(resultadoFinalDoGrupo , ensure_ascii=False))


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
        timeAdiversario = list(filter(lambda ta: ta['time'] != j['time'], timesDaPartida))[0]
        mediaDaForcaAdversario = (timeAdiversario['fifa']*timeAdiversario['forca'])/2
        mediaDaForca = (j['fifa']*j['forca'])/2

        chanceDeVitoriaEmPorcentagem = (mediaDaForca * 100) / (mediaDaForca + mediaDaForcaAdversario)
        golsDoTime = (mediaDaForca/1000 * random.uniform(0, chanceDeVitoriaEmPorcentagem))/100
        resultadosDaPartidaPorTime.append({
            **j,
            "gols": math.floor(golsDoTime) if (golsDoTime % 2 <= 0.5) else math.ceil(golsDoTime),
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


# for i in range(0, len(grupos)-1,2):
# ...     print(f"Grupo {grupos[i]} x Grupo {grupos[i+1]}")