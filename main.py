import asyncio
import json
import math
import pathlib
import random
import ssl

import pandas
import websockets

grupos = ["A", "B", "C", "D", "E", "F", "G", "H"]
fases = ["Oitavas", "Quartas", "Semi", "Final"]
classificacaoGeral = []
chaveamento = []


async def previsaoDaCopa(websocket):
    async for message in websocket:
        classificacaoGeral.clear()
        chaveamento.clear()
        todosOsGrupos = json.loads(message)
        await partidasPorRodada(todosOsGrupos, 0, websocket)
        await websocket.send(
            json.dumps(
                {
                    "tipo": "classificacao",
                    "fase": "grupos",
                    "dados": classificacaoGeral,
                },
                ensure_ascii=False,
            )
        )
        criaChaveamento(0, 1, classificados=classificacaoGeral)
        await mataMata(chaveamento, 0, websocket)


async def partidasPorRodada(teams, groupIndex, websocket):
    timesNoGrupo = list(filter(lambda t: t["grupo"] == grupos[groupIndex], teams))
    await websocket.send(
        json.dumps({"tipo": "grupo", "fase": "grupos", "dados": timesNoGrupo})
    )
    await faseDeGrupos(grupos[groupIndex], timesNoGrupo, [], websocket)
    if groupIndex < len(grupos) - 1:
        await partidasPorRodada(teams, groupIndex + 1, websocket)


# [
#  {
#   rodada: 1,
#   partidas: [
#     {
#       grupo: A
#       jogos: [
#         [Qatar,Ecuador],
#         [Senegal,Netherlands]
#       ]
#     },
#     {
#       grupo: B
#       jogos: [
#         England,Ecuador],
#         [Senegal,Netherlands]
#       ]
#     },
#   ]
#  },
#  {
#   rodada: 2,
#   partidas: [
#     {
#       grupo: A
#       jogos: [
#         [Qatar,Ecuador],
#         [Senegal,Netherlands]
#       ]
#     },
#     {
#       grupo: B
#       jogos: [
#         England,Ecuador],
#         [Senegal,Netherlands]
#       ]
#     },
#   ]
#  },
#  {
#   rodada: 3,
#   partidas: [
#     {
#       grupo: A
#       jogos: [
#         [Qatar,Ecuador],
#         [Senegal,Netherlands]
#       ]
#     },
#     {
#       grupo: B
#       jogos: [
#         England,Ecuador],
#         [Senegal,Netherlands]
#       ]
#     },
#   ]
#  },
#  {
#   rodada: Oitavas,
#   partidas: [
#     {
#       grupo: Oitavas
#       jogos: [
#         [Qatar,Ecuador],
#         [Senegal,Netherlands]
#         [Senegal,Netherlands]
#         [Senegal,Netherlands]
#         [Senegal,Netherlands]
#         [Senegal,Netherlands]
#         [Senegal,Netherlands]
#         [Senegal,Netherlands]
#       ]
#     },
#   ]
#  },
# ]


async def faseDeGrupos(grupo, timesDoGrupo, partidasJogadas, websocket):
    rodada = len(partidasJogadas) + 1
    print(f"Rodada {rodada} do grupo {grupo}")
    partida = 1
    resultadoDaRodada = {"grupo": grupo, "rodada": rodada, "resultadosDasPartidas": []}
    timesOrdenadosParaNovaRodada = defineAsPartidasDaRodada(timesDoGrupo, rodada)
    for i in range(0, 4, 2):
        x = i
        print("-" * 20)
        print(
            f"{timesOrdenadosParaNovaRodada[x]['time']} x {timesOrdenadosParaNovaRodada[x+1]['time']}"
        )
        resultadoDaPartida = jogarPartida(timesOrdenadosParaNovaRodada[x : x + 2])
        resultadoDaRodada["resultadosDasPartidas"].append(resultadoDaPartida)
        partida += 1
    await websocket.send(
        json.dumps(
            {"tipo": "partida", "fase": "grupos", "dados": resultadoDaRodada},
            ensure_ascii=False,
        )
    )

    partidasJogadas.append(resultadoDaRodada["resultadosDasPartidas"])

    if rodada == 3:
        await classificacaoFinalDaFaseDeGrupos(grupo, partidasJogadas, websocket)

    if rodada < 3:
        await faseDeGrupos(
            grupo, timesOrdenadosParaNovaRodada, partidasJogadas, websocket
        )


def defineChaveParaOrdenacaoDaClassificacao(e):
    return e["pontos"], e["gols"]


async def classificacaoFinalDaFaseDeGrupos(grupo, partidas, websocket):
    classificacao = []
    for p in partidas:
        for t in p:
            for c in t:
                classificacao.append(c)

    dataFrameDaClassificacao = pandas.DataFrame(classificacao)
    classificacaoAgrupadaComPontuacaoSomada = dataFrameDaClassificacao.groupby(
        ["time", "fifa", "forca"], as_index=False
    )[["gols", "pontos"]].sum(numeric_only=False)
    dicionariosDaClassificacao = classificacaoAgrupadaComPontuacaoSomada.to_dict(
        "records"
    )
    dicionariosDaClassificacao.sort(
        reverse=True, key=defineChaveParaOrdenacaoDaClassificacao
    )

    resultadoFinalDoGrupo = {
        "grupo": grupo,
        "classificacao": dicionariosDaClassificacao,
        "classificados": dicionariosDaClassificacao[0:2],
    }
    classificacaoGeral.append(resultadoFinalDoGrupo)


def defineChaveParaOrdenacaoDasRodadas(e):
    return e["time"]


def defineAsPartidasDaRodada(times, rodada):
    times.sort(key=defineChaveParaOrdenacaoDasRodadas)
    ordem = [0, 1, 2, 3]
    if rodada == 2:
        ordem = [0, 2, 1, 3]
    elif rodada == 3:
        ordem = [0, 3, 2, 1]
    return [times[i] for i in ordem]


def criaChaveamento(ladoChaveA, ladoChaveB, classificados):
    for i in range(0, len(grupos) - 1, 2):
        primeiroClassificadoDoGrupo = list(
            filter(
                lambda primeiro: primeiro["grupo"] == grupos[i + ladoChaveA],
                classificacaoGeral,
            )
        )[0]["classificados"][0]
        segundoClassificadoDoOutroGrupo = list(
            filter(
                lambda segundo: segundo["grupo"] == grupos[i + ladoChaveB],
                classificacaoGeral,
            )
        )[0]["classificados"][1]
        chaveamento.append(primeiroClassificadoDoGrupo)
        chaveamento.append(segundoClassificadoDoOutroGrupo)
    if ladoChaveA < 1:
        criaChaveamento(ladoChaveA + 1, ladoChaveB - 1, classificados)


async def mataMata(timesClassificados, indiceFase, websocket):
    vencedores = []
    faseAtual = fases[indiceFase]
    await websocket.send(
        json.dumps(
            {
                "tipo": "chaveamento",
                "fase": faseAtual,
                "dados": timesClassificados,
            },
            ensure_ascii=False,
        )
    )
    print("-" * 20)
    print(f"Chaveamento da {faseAtual}")
    print(timesClassificados)
    print("-" * 20)
    for i in range(0, len(timesClassificados), 2):
        print(f"{timesClassificados[i]['time']} x {timesClassificados[i+1]['time']}")
        partida = jogarPartida(timesClassificados[i : i + 2])
        await websocket.send(
            json.dumps(
                {
                    "tipo": "partida",
                    "fase": faseAtual,
                    "dados": {
                        "grupo": faseAtual,
                        "rodada": 1,
                        "resultadosDasPartidas": partida,
                    },
                },
                ensure_ascii=False,
            )
        )

        vencedor = await defineOVencedorDaPartida(partida, faseAtual, websocket)
        vencedores.append(vencedor)

    if indiceFase < len(fases) - 1:
        await mataMata(vencedores, indiceFase + 1, websocket)
    if fases[indiceFase] == "Final":
        print("🌟" * 20)
        print("TEMOS NOSSO CAMPEÃO!!!!")
        print(f"{'🏆' * 8} {vencedor['time']} {'🏆' * 8}")
        print("🌟" * 20)
        await websocket.send(
            json.dumps(
                {
                    "tipo": "campeao",
                    "fase": faseAtual,
                    "dados": vencedor["time"],
                },
                ensure_ascii=False,
            )
        )


async def defineOVencedorDaPartida(resultado, fase, websocket):
    vencedor = next((sub for sub in resultado if sub["pontos"] == 3), None)
    empates = list(filter(lambda t: t["pontos"] == 1, resultado))
    if len(empates) > 0:
        print("Vamos para as penalidades máximas! 🥅")
        vencedor = await cobrancasDePenaltis(empates, fase, websocket)

    return vencedor


def encontraAdversario(timesDaPartida, time):
    timeAdiversario = next((ta for ta in timesDaPartida if ta["time"] != time))
    return timeAdiversario


async def cobrancasDePenaltis(times, fase, websocket):
    batidasConvertidas = {
        times[0]["time"]: 0,
        times[1]["time"]: 0,
    }
    for p in range(0, 5):
        batePenalti(times, batidasConvertidas, fase, websocket)

    await websocket.send(
        json.dumps(
            {
                "tipo": "resultado_cobrancas",
                "fase": fase,
                "dados": batidasConvertidas,
            },
            ensure_ascii=False,
        )
    )
    print(
        f"{times[0]['time']} {'⚽' * batidasConvertidas[times[0]['time']]} - {times[1]['time']} {'⚽' * batidasConvertidas[times[1]['time']]}"
    )
    while batidasConvertidas[times[0]["time"]] == batidasConvertidas[times[1]["time"]]:
        print("Vamos para as cobranças alternadas!!")
        batePenalti(times, batidasConvertidas, fase, websocket)
        print(
            f"{times[0]['time']} {'⚽' * batidasConvertidas[times[0]['time']]} - {times[1]['time']} {'⚽' * batidasConvertidas[times[1]['time']]}"
        )

    vencedor = (
        times[0]
        if (batidasConvertidas[times[0]["time"]] > batidasConvertidas[times[1]["time"]])
        else times[1]
    )
    return vencedor


def batePenalti(times, batidasConvertidas, fase, websocket):
    for p in times:
        print(f"{p['time']} vai pra cobrança!")
        timeAdiversario = encontraAdversario(times, p["time"])
        chanceDeDefenderOPenalti = (
            timeAdiversario["fifa"] * timeAdiversario["forca"]
        ) / 2
        chanceDeMarcarOGol = (p["fifa"] * p["forca"]) / 2
        chuteDoAtacante = chanceDeMarcarOGol * random.randint(1, 6)
        defesaDoGoleiro = chanceDeDefenderOPenalti * random.randint(1, 6)
        if chuteDoAtacante > defesaDoGoleiro:
            print(f"Gooool!! [{p['time']}] ⚽")
            batidasConvertidas[p["time"]] += 1
        else:
            print(f"Defendeu!! [{timeAdiversario['time']}] 🧤❌")


def jogarPartida(timesDaPartida):
    resultadosDaPartidaPorTime = []

    for j in timesDaPartida:
        timeAdiversario = encontraAdversario(timesDaPartida, j["time"])
        mediaDaForcaAdversario = (
            timeAdiversario["fifa"] * timeAdiversario["forca"]
        ) / 2
        mediaDaForca = (j["fifa"] * j["forca"]) / 2

        chanceDeVitoriaEmPorcentagem = (mediaDaForca * 100) / (
            mediaDaForca + mediaDaForcaAdversario
        )
        golsDoTime = (
            mediaDaForca / 1000 * random.uniform(0, chanceDeVitoriaEmPorcentagem)
        ) / 100
        resultadosDaPartidaPorTime.append(
            {
                **j,
                "gols": math.floor(golsDoTime)
                if (golsDoTime % 2 <= 0.5)
                else math.ceil(golsDoTime),
                "pontos": 0,
            }
        )

    if resultadosDaPartidaPorTime[0]["gols"] > resultadosDaPartidaPorTime[1]["gols"]:
        resultadosDaPartidaPorTime[0]["pontos"] = 3

    if resultadosDaPartidaPorTime[0]["gols"] == resultadosDaPartidaPorTime[1]["gols"]:
        resultadosDaPartidaPorTime[0]["pontos"] = 1

    if resultadosDaPartidaPorTime[1]["gols"] > resultadosDaPartidaPorTime[0]["gols"]:
        resultadosDaPartidaPorTime[1]["pontos"] = 3

    if resultadosDaPartidaPorTime[1]["gols"] == resultadosDaPartidaPorTime[0]["gols"]:
        resultadosDaPartidaPorTime[1]["pontos"] = 1
    print(f"Fim de jogo!")
    print(
        f"{resultadosDaPartidaPorTime[0]['time']} {resultadosDaPartidaPorTime[0]['gols']} - {resultadosDaPartidaPorTime[1]['gols']} {resultadosDaPartidaPorTime[1]['time']}"
    )
    print("-" * 20)
    return resultadosDaPartidaPorTime


async def main():
    port = 8081
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
    ssl_context.load_cert_chain(localhost_pem)
    async with websockets.serve(previsaoDaCopa, "0.0.0.0", port):
        print(f"Servidor iniciado na porta {port}, aguardando times")
        await asyncio.Future()  # run forever


asyncio.run(main())
