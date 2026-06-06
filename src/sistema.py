#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARES-1 HABITAT MONITORING SYSTEM (HMS)
======================================
Sistema inteligente de monitoramento operacional para um habitat cientifico
experimental em Marte (Missao ARES-1).

Equipe: GRUPO 404 - FIAP
  Fernando dos Santos Motta         - RM570046
  Caetano de Medeiros Bona          - RM569262
  Joedson da Silva Souza            - RM573981
  Mylena Ramalho da Silva Torquato  - RM572383
  Erik Fabiano de Jesus Appe        - RM571067

O programa:
  1. Carrega telemetria de data/dados.csv (4 secoes).
  2. Organiza os dados em estruturas: lista, fila, pilha, dicionario,
     hierarquia (dict de dicts) e matriz (lista de listas).
  3. Detecta inconsistencias fisicas nos sensores.
  4. Classifica cada modulo critico e o estado global da missao
     (NORMAL / ALERTA / CRITICO) com regras booleanas.
  5. Gera alertas automaticos priorizados por severidade.
  6. Faz previsao da reserva de energia (media movel + regressao linear
     implementadas a mao, sem bibliotecas externas).
  7. Emite recomendacoes tecnicas priorizadas e um relatorio no terminal.

Execucao:  python src/sistema.py
Dependencias: apenas a biblioteca padrao do Python (modulos csv e os).
"""

import csv
import os

# ---------------------------------------------------------------------------
# CONFIGURACAO
# ---------------------------------------------------------------------------

# Caminho do CSV resolvido em relacao a este arquivo, para funcionar
# independentemente do diretorio de onde o script for executado.
DIR_BASE = os.path.dirname(os.path.abspath(__file__))
CAMINHO_DADOS = os.path.join(DIR_BASE, "..", "data", "dados.csv")
CAMINHO_LOG = os.path.join(DIR_BASE, "..", "data", "log_sessao.txt")

# Ordem de severidade usada para ordenar alertas (maior numero = mais grave).
PESO_SEVERIDADE = {"NORMAL": 0, "ALERTA": 1, "CRITICO": 2}

# Acumulador do relatorio em texto, para exibir no terminal e exportar ao log.
LINHAS_RELATORIO = []


def emitir(texto=""):
    """Imprime no terminal e tambem guarda a linha para exportar ao log."""
    print(texto)
    LINHAS_RELATORIO.append(texto)


# ---------------------------------------------------------------------------
# 1. LEITURA E INTERPRETACAO DOS DADOS
# ---------------------------------------------------------------------------

def carregar_dados(caminho):
    """
    Le o CSV com 4 secoes separadas por marcadores [NOME].
    Ignora linhas em branco e comentarios iniciados por '#'.
    Retorna um dicionario com as quatro colecoes brutas.

    Tratamento de erro: se o arquivo nao existir, encerra com mensagem clara.
    """
    if not os.path.exists(caminho):
        raise SystemExit(
            f"ERRO: arquivo de dados nao encontrado em '{caminho}'.\n"
            "Verifique se data/dados.csv existe no repositorio."
        )

    secao_atual = None
    modulos = {}              # dicionario: acesso O(1) por nome de modulo
    energia = []              # lista de dicts (uma entrada por ciclo)
    ambiente = {}             # dicionario: variavel ambiental -> (valor, unidade)
    eventos = []              # lista de dicts (log de eventos)

    with open(caminho, "r", encoding="utf-8") as arquivo:
        leitor = csv.reader(arquivo)
        for linha in leitor:
            if not linha:
                continue
            primeiro = linha[0].strip()

            # Ignora comentarios e linhas vazias.
            if primeiro == "" or primeiro.startswith("#"):
                continue

            # Marcadores de secao: [MODULOS], [ENERGIA], [AMBIENTE], [EVENTOS]
            if primeiro.startswith("[") and primeiro.endswith("]"):
                secao_atual = primeiro.strip("[]")
                continue

            # Cabecalhos de coluna sao ignorados (comecam por nomes conhecidos).
            if primeiro in ("modulo", "ciclo", "variavel", "timestamp"):
                continue

            # Distribui a linha para a estrutura correta conforme a secao.
            if secao_atual == "MODULOS":
                nome, status = linha[0].strip(), int(linha[1])
                modulos[nome] = status

            elif secao_atual == "ENERGIA":
                energia.append({
                    "ciclo": int(linha[0]),
                    "geracao": float(linha[1]),
                    "consumo": float(linha[2]),
                    "reserva": float(linha[3]),
                })

            elif secao_atual == "AMBIENTE":
                variavel = linha[0].strip()
                valor = float(linha[1])
                unidade = linha[2].strip()
                ambiente[variavel] = {"valor": valor, "unidade": unidade}

            elif secao_atual == "EVENTOS":
                eventos.append({
                    "timestamp": linha[0].strip(),
                    "tipo": linha[1].strip(),
                    "descricao": linha[2].strip(),
                })

    return {
        "modulos": modulos,
        "energia": energia,
        "ambiente": ambiente,
        "eventos": eventos,
    }


def montar_estruturas(dados):
    """
    A partir dos dados brutos, monta as estruturas computacionais exigidas:
      - lista (serie temporal da reserva de energia);
      - matriz (lista de listas: ciclos x variaveis de energia);
      - hierarquia (dict de dicts agrupando modulos por area da missao);
      - pilha (eventos criticos, em ordem LIFO).
    A fila de alertas e construida depois, em gerar_alertas().
    """
    modulos = dados["modulos"]

    # LISTA - serie temporal usada no forecasting.
    historico_reserva = [registro["reserva"] for registro in dados["energia"]]

    # MATRIZ (lista de listas) - cada linha e um ciclo, colunas sao as variaveis.
    matriz_leituras = [
        [r["ciclo"], r["geracao"], r["consumo"], r["reserva"]]
        for r in dados["energia"]
    ]

    # HIERARQUIA - dict de dicts: representa as areas operacionais da base.
    areas_missao = {
        "vida": {"suporte_vida": modulos.get("suporte_vida")},
        "energia": {"energia": modulos.get("energia")},
        "comunicacao": {"comunicacao": modulos.get("comunicacao")},
        "habitat": {
            "habitat": modulos.get("habitat"),
            "laboratorio": modulos.get("laboratorio"),
            "armazenamento": modulos.get("armazenamento"),
        },
    }

    # PILHA (LIFO) - empilha os eventos marcados como CRITICO; o topo e o mais
    # recente analisado. Implementada com lista + append/pop.
    pilha_eventos_criticos = []
    for evento in dados["eventos"]:
        if evento["tipo"] == "CRITICO":
            pilha_eventos_criticos.append(evento)  # push

    return {
        "historico_reserva": historico_reserva,
        "matriz_leituras": matriz_leituras,
        "areas_missao": areas_missao,
        "pilha_eventos_criticos": pilha_eventos_criticos,
    }


def detectar_inconsistencias(dados):
    """
    Valida faixas fisicas plausiveis das variaveis ambientais.
    Retorna uma lista de anomalias (cada uma e um dicionario).
    Regra de interpretacao baseada em faixas de seguranca (item 8.1 do brief).

    Inconsistencia plantada: pressao interna = -999 kPa (impossivel).
    """
    anomalias = []
    ambiente = dados["ambiente"]

    # Faixas fisicas validas (minimo, maximo) por variavel.
    faixas_validas = {
        "temperatura_interna": (-50.0, 60.0),
        "temperatura_externa": (-140.0, 40.0),
        "radiacao": (0.0, 100.0),
        "qualidade_comunicacao": (0.0, 100.0),
        "velocidade_vento": (0.0, 400.0),
        "pressao_interna": (0.0, 200.0),  # pressao nunca pode ser negativa
    }

    for variavel, faixa in faixas_validas.items():
        if variavel in ambiente:
            valor = ambiente[variavel]["valor"]
            mini, maxi = faixa
            # NOT dentro da faixa  ->  leitura invalida.
            if not (mini <= valor <= maxi):
                anomalias.append({
                    "variavel": variavel,
                    "valor": valor,
                    "faixa": faixa,
                    "descricao": (
                        f"Leitura de '{variavel}' = {valor} fora da faixa "
                        f"fisica valida {faixa}. Sensor possivelmente com falha."
                    ),
                })
    return anomalias


# ---------------------------------------------------------------------------
# 2. CLASSIFICACAO DE MODULOS E ESTADO DA MISSAO (REGRAS LOGICAS)
# ---------------------------------------------------------------------------

def classificar_modulos(modulos):
    """
    Monta a tabela de status dos modulos criticos.
    Modulos essenciais offline -> CRITICO; demais offline -> ALERTA;
    operantes -> NORMAL. Retorna uma lista de tuplas (nome, status, situacao).
    """
    essenciais = ("suporte_vida", "energia")
    tabela = []
    for nome, status in modulos.items():
        if status == 1:
            situacao = "NORMAL"
        elif nome in essenciais:        # essencial desligado e sempre critico
            situacao = "CRITICO"
        else:
            situacao = "ALERTA"
        tabela.append((nome, status, situacao))
    return tabela


def classificar_estado_missao(modulos, ambiente, reserva, ha_inconsistencia):
    """
    Aplica as regras booleanas de diagnostico (if/elif/else + and/or/not).
    Retorna o estado global: 'CRITICO', 'ALERTA' ou 'NORMAL'.

    Expressao booleana principal (CRITICO):
        CRITICO = (suporte_vida == 0) OR (energia == 0) OR
                  (reserva < 20 AND comunicacao == 0) OR
                  (radiacao > 8.0 AND reserva < 30)
    """
    radiacao = ambiente["radiacao"]["valor"]
    temp_interna = ambiente["temperatura_interna"]["valor"]

    suporte_vida = modulos.get("suporte_vida", 1)
    energia = modulos.get("energia", 1)
    comunicacao = modulos.get("comunicacao", 1)

    # ---- REGRA 1 (CRITICO): usa OR e AND combinados -------------------------
    critico = (
        suporte_vida == 0
        or energia == 0
        or (reserva < 20 and comunicacao == 0)
        or (radiacao > 8.0 and reserva < 30)
    )

    # ---- REGRA 2 (ALERTA): so e avaliada se NAO for critico (usa NOT) -------
    alerta = (not critico) and (
        reserva < 40
        or comunicacao == 0
        or radiacao > 5.0
        or temp_interna < 18
        or temp_interna > 28
        or ha_inconsistencia
    )

    # ---- REGRA 3 (NORMAL): nem critico nem alerta ---------------------------
    if critico:
        return "CRITICO"
    elif alerta:
        return "ALERTA"
    else:
        return "NORMAL"


# ---------------------------------------------------------------------------
# 3. ALERTAS AUTOMATICOS
# ---------------------------------------------------------------------------

def gerar_alertas(modulos, ambiente, reserva, anomalias):
    """
    Avalia todas as condicoes de risco e popula a FILA de alertas (FIFO).
    A fila e uma lista usada com append() (enqueue). Cada alerta e um dict
    com severidade, modulo, descricao e acao recomendada.
    """
    fila_alertas = []  # FILA (FIFO): primeiro alerta gerado e o primeiro tratado

    def enfileirar(severidade, modulo, descricao, acao):
        fila_alertas.append({
            "severidade": severidade,
            "modulo": modulo,
            "descricao": descricao,
            "acao": acao,
        })

    radiacao = ambiente["radiacao"]["valor"]
    temp_interna = ambiente["temperatura_interna"]["valor"]

    # --- Modulos essenciais -------------------------------------------------
    if modulos.get("suporte_vida") == 0:
        enfileirar("CRITICO", "suporte_vida",
                   "Suporte a vida offline.",
                   "Evacuar habitat e acionar redundancias de oxigenio.")
    if modulos.get("energia") == 0:
        enfileirar("CRITICO", "energia",
                   "Modulo de energia offline.",
                   "Acionar baterias de emergencia imediatamente.")

    # --- Reserva de energia (faixas de seguranca) ---------------------------
    if reserva < 20:
        enfileirar("CRITICO", "energia",
                   f"Reserva de energia critica ({reserva:.0f}%).",
                   "Desligar laboratorio e sistemas nao essenciais.")
    elif reserva < 40:
        enfileirar("ALERTA", "energia",
                   f"Reserva de energia baixa ({reserva:.0f}%).",
                   "Ativar modo economia de energia.")

    # --- Comunicacao --------------------------------------------------------
    if modulos.get("comunicacao") == 0:
        enfileirar("ALERTA", "comunicacao",
                   "Modulo de comunicacao primario offline.",
                   "Ativar backup e priorizar contato de emergencia com a Terra.")

    # --- Radiacao -----------------------------------------------------------
    if radiacao > 8.0:
        enfileirar("CRITICO", "ambiente",
                   f"Radiacao muito elevada ({radiacao} mSv/h).",
                   "Recolher equipe ao abrigo e proteger equipamentos sensiveis.")
    elif radiacao > 5.0:
        enfileirar("ALERTA", "ambiente",
                   f"Radiacao acima do normal ({radiacao} mSv/h).",
                   "Reduzir atividades externas e monitorar exposicao.")

    # --- Temperatura interna (conforto/seguranca do habitat) ----------------
    if temp_interna < 18 or temp_interna > 28:
        enfileirar("ALERTA", "habitat",
                   f"Temperatura interna fora da faixa ideal ({temp_interna} C).",
                   "Verificar sistema de climatizacao do habitat.")

    # --- Inconsistencias de sensores ----------------------------------------
    for anomalia in anomalias:
        enfileirar("ALERTA", anomalia["variavel"],
                   anomalia["descricao"],
                   "Marcar sensor como nao confiavel e usar leitura redundante.")

    return fila_alertas


def ordenar_alertas_por_severidade(fila_alertas):
    """Retorna os alertas ordenados do mais grave para o menos grave."""
    return sorted(
        fila_alertas,
        key=lambda a: PESO_SEVERIDADE[a["severidade"]],
        reverse=True,
    )


# ---------------------------------------------------------------------------
# 4. FORECASTING - MEDIA MOVEL + REGRESSAO LINEAR (sem bibliotecas externas)
# ---------------------------------------------------------------------------

def media_movel(serie, janela=3):
    """
    Media movel simples: suaviza a serie para revelar a tendencia real,
    eliminando ruido ciclo a ciclo. Retorna a lista de medias.
    """
    resultado = []
    for i in range(len(serie) - janela + 1):
        media = sum(serie[i:i + janela]) / janela
        resultado.append(media)
    return resultado


def regressao_linear(x, y):
    """
    Regressao linear simples pelo metodo dos minimos quadrados, feita a mao.
    Resolve  y = a + b*x  retornando os coeficientes (a, b).
        b = (n*Sxy - Sx*Sy) / (n*Sxx - Sx^2)
        a = (Sy - b*Sx) / n
    """
    n = len(x)
    soma_x = sum(x)
    soma_y = sum(y)
    soma_xy = sum(x[i] * y[i] for i in range(n))
    soma_x2 = sum(xi ** 2 for xi in x)

    denominador = (n * soma_x2 - soma_x ** 2)
    if denominador == 0:                # evita divisao por zero
        return y[-1], 0.0
    b = (n * soma_xy - soma_x * soma_y) / denominador
    a = (soma_y - b * soma_x) / n
    return a, b


def executar_forecasting(historico_reserva):
    """
    Aplica as duas tecnicas na serie de reserva de energia e projeta os
    proximos 3 ciclos. Retorna um dicionario com tudo que sera exibido e
    a flag 'esgotamento_previsto' que pode influenciar o estado da missao.
    """
    ciclos = list(range(1, len(historico_reserva) + 1))

    # Tecnica 1 - media movel (janela de 3 ciclos).
    medias = media_movel(historico_reserva, janela=3)
    # Tendencia: variacao media entre as ultimas duas medias moveis.
    if len(medias) >= 2:
        tendencia_mm = medias[-1] - medias[-2]
    else:
        tendencia_mm = 0.0

    # Tecnica 2 - regressao linear sobre toda a serie.
    a, b = regressao_linear(ciclos, historico_reserva)

    # Projecao dos proximos 3 ciclos (extrapolacao da reta).
    previsoes = []
    ultimo_ciclo = ciclos[-1]
    for proximo in range(ultimo_ciclo + 1, ultimo_ciclo + 4):
        valor_previsto = a + b * proximo
        previsoes.append((proximo, valor_previsto))

    # Decisao influenciada: se a reta projeta reserva <= 0 nos proximos ciclos,
    # significa esgotamento iminente -> sinaliza para elevar o estado.
    esgotamento_previsto = any(valor <= 0 for _, valor in previsoes)

    return {
        "ciclos": ciclos,
        "medias_moveis": medias,
        "tendencia_mm": tendencia_mm,
        "coef_a": a,
        "coef_b": b,
        "previsoes": previsoes,
        "esgotamento_previsto": esgotamento_previsto,
    }


# ---------------------------------------------------------------------------
# 5. RECOMENDACOES
# ---------------------------------------------------------------------------

def gerar_recomendacoes(estado, alertas_ordenados, forecast):
    """
    Gera recomendacoes priorizadas com base no estado final da missao,
    nos alertas criticos pendentes e na previsao de energia.
    Retorna lista de tuplas (prioridade, texto).
    """
    recomendacoes = []

    if estado == "CRITICO":
        recomendacoes.append(
            ("CRITICA", "Manter suporte a vida e comunicacao de emergencia ativos."))
        recomendacoes.append(
            ("ALTA", "Desligar laboratorio e sistemas nao essenciais."))
        recomendacoes.append(
            ("ALTA", "Redirecionar energia para habitat e carregamento de baterias."))
    elif estado == "ALERTA":
        recomendacoes.append(
            ("ALTA", "Ativar modo economia de energia e monitorar reserva."))
        recomendacoes.append(
            ("MEDIA", "Reduzir atividades externas ate normalizacao ambiental."))
    else:
        recomendacoes.append(
            ("NORMAL", "Operacao nominal. Manter monitoramento de rotina."))

    # Recomendacao derivada diretamente da PREVISAO (rastreabilidade do impacto).
    if forecast["esgotamento_previsto"]:
        recomendacoes.append((
            "CRITICA",
            "Previsao indica esgotamento da reserva nos proximos ciclos: "
            "racionar consumo agora e priorizar recarga das baterias."))

    # Acrescenta a acao do alerta mais grave da fila, se houver.
    if alertas_ordenados:
        mais_grave = alertas_ordenados[0]
        recomendacoes.append(
            (mais_grave["severidade"],
             f"Acao prioritaria ({mais_grave['modulo']}): {mais_grave['acao']}"))

    return recomendacoes


# ---------------------------------------------------------------------------
# 6. RELATORIO NO TERMINAL
# ---------------------------------------------------------------------------

def linha_separadora(caractere="-", largura=62):
    return caractere * largura


def exibir_relatorio(dados, estruturas, anomalias, tabela_modulos,
                     fila_alertas, alertas_ordenados, forecast,
                     estado, recomendacoes):
    """Imprime o relatorio completo, seccao por seccao."""

    emitir("=" * 62)
    emitir("        ARES-1 HABITAT MONITORING SYSTEM")
    emitir("        Missao: Habitat em Marte - Ciclo 6")
    emitir("=" * 62)

    # [1/7] Carregamento ------------------------------------------------------
    emitir("\n[1/7] CARREGAMENTO DE DADOS")
    emitir(linha_separadora())
    emitir(f"  Modulos lidos........: {len(dados['modulos'])}")
    emitir(f"  Ciclos de energia....: {len(dados['energia'])}")
    emitir(f"  Variaveis ambientais.: {len(dados['ambiente'])}")
    emitir(f"  Eventos no log.......: {len(dados['eventos'])}")

    # [2/7] Status dos modulos ------------------------------------------------
    emitir("\n[2/7] STATUS DOS MODULOS CRITICOS")
    emitir(linha_separadora())
    emitir(f"  {'MODULO':<16}{'BINARIO':<10}{'SITUACAO'}")
    for nome, status, situacao in tabela_modulos:
        emitir(f"  {nome:<16}{status:<10}{situacao}")

    # [3/7] Variaveis ambientais ---------------------------------------------
    emitir("\n[3/7] VARIAVEIS AMBIENTAIS")
    emitir(linha_separadora())
    for variavel, info in dados["ambiente"].items():
        emitir(f"  {variavel:<24}{info['valor']:>8} {info['unidade']}")
    if anomalias:
        emitir("\n  >> INCONSISTENCIA DETECTADA:")
        for anomalia in anomalias:
            emitir(f"     - {anomalia['descricao']}")

    # [4/7] Log de eventos ----------------------------------------------------
    emitir("\n[4/7] LOG DE EVENTOS")
    emitir(linha_separadora())
    for evento in dados["eventos"]:
        emitir(f"  {evento['timestamp']}  [{evento['tipo']:<7}] "
               f"{evento['descricao']}")
    emitir(f"\n  Eventos criticos na PILHA (LIFO): "
           f"{len(estruturas['pilha_eventos_criticos'])}")
    if estruturas["pilha_eventos_criticos"]:
        topo = estruturas["pilha_eventos_criticos"][-1]
        emitir(f"  Topo da pilha (mais recente): {topo['descricao']}")

    # [5/7] Alertas automaticos ----------------------------------------------
    emitir("\n[5/7] ALERTAS AUTOMATICOS (ordenados por severidade)")
    emitir(linha_separadora())
    emitir(f"  Total de alertas na FILA: {len(fila_alertas)}")
    for alerta in alertas_ordenados:
        emitir(f"\n  [{alerta['severidade']}] modulo: {alerta['modulo']}")
        emitir(f"     descricao: {alerta['descricao']}")
        emitir(f"     acao.....: {alerta['acao']}")

    # [6/7] Forecasting -------------------------------------------------------
    emitir("\n[6/7] PREVISAO DE RESERVA DE ENERGIA (FORECASTING)")
    emitir(linha_separadora())
    emitir(f"  Serie historica (reserva %): {estruturas['historico_reserva']}")
    emitir(f"  Tecnica 1 - Media movel (janela 3): "
           f"{[round(m, 1) for m in forecast['medias_moveis']]}")
    emitir(f"     Tendencia recente: {forecast['tendencia_mm']:.1f} pp por ciclo")
    emitir(f"  Tecnica 2 - Regressao linear:")
    emitir(f"     Equacao: reserva = {forecast['coef_a']:.1f} "
           f"+ ({forecast['coef_b']:.1f}) * ciclo")
    for ciclo, valor in forecast["previsoes"]:
        emitir(f"     Ciclo {ciclo}: {valor:.1f}%")
    if forecast["esgotamento_previsto"]:
        emitir("     >> ALERTA: a projecao indica esgotamento da reserva.")
        emitir("     >> DECISAO INFLUENCIADA: estado elevado para CRITICO.")

    # [7/7] Diagnostico final e recomendacoes --------------------------------
    emitir("\n[7/7] DIAGNOSTICO FINAL E RECOMENDACOES")
    emitir(linha_separadora())
    emitir(f"\n  *** ESTADO DA MISSAO: {estado} ***\n")
    emitir("  Recomendacoes priorizadas:")
    for i, (prioridade, texto) in enumerate(recomendacoes, start=1):
        emitir(f"    {i}. [{prioridade}] {texto}")

    emitir("\n" + "=" * 62)
    emitir("        FIM DO RELATORIO - ARES-1 HMS")
    emitir("=" * 62)


def exportar_log(caminho):
    """Salva todo o relatorio da sessao em um arquivo de texto."""
    try:
        with open(caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write("\n".join(LINHAS_RELATORIO))
        print(f"\n[log] Relatorio da sessao exportado para: {caminho}")
    except OSError as erro:
        print(f"\n[log] Nao foi possivel exportar o log: {erro}")


# ---------------------------------------------------------------------------
# 7. ORQUESTRACAO
# ---------------------------------------------------------------------------

def main():
    # 1. Carregar dados e montar estruturas.
    dados = carregar_dados(CAMINHO_DADOS)
    estruturas = montar_estruturas(dados)

    # 2. Detectar inconsistencias fisicas.
    anomalias = detectar_inconsistencias(dados)
    ha_inconsistencia = len(anomalias) > 0

    # 3. Reserva atual = ultimo valor da serie temporal (lista).
    reserva_atual = estruturas["historico_reserva"][-1]

    # 4. Classificar modulos e estado da missao.
    tabela_modulos = classificar_modulos(dados["modulos"])
    estado = classificar_estado_missao(
        dados["modulos"], dados["ambiente"], reserva_atual, ha_inconsistencia)

    # 5. Gerar e ordenar alertas.
    fila_alertas = gerar_alertas(
        dados["modulos"], dados["ambiente"], reserva_atual, anomalias)
    alertas_ordenados = ordenar_alertas_por_severidade(fila_alertas)

    # 6. Forecasting da reserva de energia.
    forecast = executar_forecasting(estruturas["historico_reserva"])

    # A previsao pode ELEVAR o estado para CRITICO (decisao influenciada).
    if forecast["esgotamento_previsto"] and estado != "CRITICO":
        estado = "CRITICO"

    # 7. Recomendacoes e relatorio.
    recomendacoes = gerar_recomendacoes(estado, alertas_ordenados, forecast)
    exibir_relatorio(dados, estruturas, anomalias, tabela_modulos,
                     fila_alertas, alertas_ordenados, forecast,
                     estado, recomendacoes)
    exportar_log(CAMINHO_LOG)


if __name__ == "__main__":
    main()
