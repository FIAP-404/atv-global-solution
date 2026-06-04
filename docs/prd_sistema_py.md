# PRD — sistema.py
## Projeto: ARES-1 Habitat Monitoring System
### Missão: Habitat em Marte — Monitoramento Inteligente de Operações

---

## 1. Visão Geral

**Nome do sistema:** ARES-1 HMS (Habitat Monitoring System)  
**Arquivo principal:** `src/sistema.py`  
**Execução:** `python src/sistema.py` — totalmente automático, sem interação do usuário  
**Dados:** lidos de `data/dados.csv` no início da execução  
**Saída:** relatório completo impresso no terminal, seção por seção  
**Dependências externas:** nenhuma (somente biblioteca padrão do Python)

---

## 2. Cenário da Missão

Habitat científico em Marte, Missão ARES-1. A base abriga 6 astronautas e opera
de forma semi-autônoma. O sistema monitora continuamente os módulos críticos,
detecta riscos gerados por tempestades de areia, radiação solar e falhas de
equipamento, e recomenda ações para manter a operação segura.

**Justificativa do cenário:** Marte oferece variáveis ambientais ricas
(radiação, temperatura extrema, tempestades) que tornam os dados mais dramáticos
e a lógica de decisão mais defensável na apresentação.

---

## 3. Fonte de Dados

**Arquivo:** `data/dados.csv`  
**Leitura:** função dedicada `carregar_dados(caminho)` usando módulo `csv` nativo  
**Tratamento de erros:** se o arquivo não existir ou tiver linha corrompida,
o sistema exibe aviso e encerra com mensagem clara

### 3.1 Estrutura do CSV

O arquivo terá seções separadas por linhas de cabeçalho comentadas (`#`).
O parser ignora linhas que começam com `#` e linhas vazias.

**Seção 1 — Módulos críticos (binário 0/1)**
```
modulo,status
suporte_vida,1
energia,1
comunicacao,0
habitat,1
laboratorio,1
armazenamento,1
```

**Seção 2 — Leituras de energia ao longo do tempo (6+ registros)**
```
ciclo,geracao_kWh,consumo_kWh,reserva_pct
1,45,60,72
2,40,65,65
3,30,70,52
4,20,75,38
5,15,78,24
6,10,80,12
```

**Seção 3 — Variáveis ambientais**
```
variavel,valor,unidade
temperatura_interna,21.5,C
temperatura_externa,-63.0,C
radiacao,8.7,mSv/h
qualidade_comunicacao,34,pct
velocidade_vento,112,km/h
pressao_interna,101.3,kPa
```

**Seção 4 — Log de eventos (8+ registros)**
```
timestamp,tipo,descricao
2026-06-01T06:00,INFO,Sistema ARES-1 inicializado
2026-06-01T07:15,ALERTA,Tempestade de areia detectada — visibilidade reduzida
2026-06-01T08:30,CRITICO,Painel solar A danificado — geracao reduzida 55%
2026-06-01T09:00,INFO,Modo economia de energia ativado
2026-06-01T10:45,ALERTA,Sensor de radiacao registrou pico acima do limite
2026-06-01T11:00,CRITICO,Falha no modulo de comunicacao primario
2026-06-01T12:30,INFO,Sistema de backup de comunicacao ativado (degradado)
2026-06-01T13:00,ALERTA,Reserva de energia abaixo de 40%
2026-06-01T14:00,ERRO,Leitura inconsistente: sensor de pressao reportou -999 kPa
```

**Inconsistência intencional:** leitura de pressão `-999 kPa` — impossível fisicamente.
O sistema deve detectar, registrar na fila de alertas e explicar o diagnóstico.

---

## 4. Estruturas de Dados

Cada estrutura tem justificativa explícita (cobrada na rubrica).

| Estrutura | Variável no código | O que armazena | Justificativa |
|---|---|---|---|
| **Lista** | `historico_energia` | Reservas de energia por ciclo (série temporal) | Acesso por índice, iteração para forecasting |
| **Lista** | `leituras_ambientais` | Temperatura, radiação, vento etc. | Sequência ordenada de variáveis contínuas |
| **Fila** | `fila_alertas` | Alertas pendentes por ordem de chegada | FIFO — primeiro alerta gerado é o primeiro tratado |
| **Pilha** | `pilha_eventos_criticos` | Eventos críticos analisados | LIFO — acesso rápido ao evento mais recente |
| **Dicionário** | `modulos` | Status de cada módulo por nome | Acesso O(1) por chave — ex: `modulos["comunicacao"]` |
| **Hierarquia** | `areas_missao` | Dict de dicts agrupando módulos por área | Representa áreas: energia, habitat, comunicação, vida |
| **Matriz** | `matriz_leituras` | Linhas = ciclos, colunas = variáveis | Visão tabular de todas as variáveis ao longo do tempo |

### Implementação de Fila e Pilha

Sem bibliotecas externas — implementadas com listas e métodos nativos:

```python
# Fila (FIFO)
fila_alertas = []
fila_alertas.append(alerta)      # enqueue
fila_alertas.pop(0)              # dequeue

# Pilha (LIFO)
pilha_eventos_criticos = []
pilha_eventos_criticos.append(evento)   # push
pilha_eventos_criticos.pop()            # pop
```

---

## 5. Módulos Críticos e Hierarquia

```python
areas_missao = {
    "vida": {
        "suporte_vida": modulos["suporte_vida"]
    },
    "energia": {
        "energia": modulos["energia"]
    },
    "comunicacao": {
        "comunicacao": modulos["comunicacao"]
    },
    "habitat": {
        "habitat":       modulos["habitat"],
        "laboratorio":   modulos["laboratorio"],
        "armazenamento": modulos["armazenamento"]
    }
}
```

---

## 6. Regras Lógicas de Diagnóstico

### Estado da missão: CRÍTICO
```python
estado == "CRITICO" if (
    modulos["suporte_vida"] == 0
    or modulos["energia"] == 0
    or (reserva_energia < 20 and modulos["comunicacao"] == 0)
    or (radiacao > 8.0 and reserva_energia < 30)
)
```

### Estado da missão: ALERTA
```python
estado == "ALERTA" if (
    not estado == "CRITICO"
    and (
        reserva_energia < 40
        or modulos["comunicacao"] == 0
        or radiacao > 5.0
        or temperatura_interna < 18 or temperatura_interna > 28
        or inconsistencia_detectada
    )
)
```

### Estado da missão: NORMAL
```python
estado == "NORMAL" if (
    not estado == "CRITICO"
    and not estado == "ALERTA"
)
```

**Expressão booleana principal (para o README):**
```
CRITICO = (suporte_vida == 0) OR (energia == 0) OR
          (reserva < 20 AND comunicacao == 0) OR
          (radiacao > 8.0 AND reserva < 30)
```

Cada regra será comentada no código explicando a lógica operacional por trás dela.

---

## 7. Sistema de Alertas Automáticos

Alertas gerados automaticamente e inseridos na `fila_alertas`.  
Cada alerta é um dicionário:

```python
{
    "severidade": "CRITICO",          # NORMAL | ALERTA | CRITICO
    "modulo": "comunicacao",
    "descricao": "Módulo de comunicação offline.",
    "acao": "Ativar sistema de backup e priorizar contato com a Terra."
}
```

**Gatilhos de alerta:**

| Condição | Severidade | Ação recomendada |
|---|---|---|
| `suporte_vida == 0` | CRITICO | Evacuar habitat, acionar redundâncias |
| `energia == 0` | CRITICO | Acionar baterias de emergência |
| `reserva < 20%` | CRITICO | Desligar laboratório e não-essenciais |
| `reserva < 40%` | ALERTA | Ativar modo economia |
| `comunicacao == 0` | ALERTA | Ativar backup de comunicação |
| `radiacao > 8.0 mSv/h` | CRITICO | Recolher equipe, proteger equipamentos |
| `radiacao > 5.0 mSv/h` | ALERTA | Monitorar exposição, reduzir atividade externa |
| `temp_interna fora de [18, 28]°C` | ALERTA | Verificar sistema de climatização |
| `pressao == -999` (inconsistência) | ALERTA | Sensor com falha — não usar leitura |

Os alertas são exibidos ordenados por severidade: CRITICO → ALERTA → NORMAL.

---

## 8. Forecasting — Reserva de Energia

Duas técnicas implementadas manualmente (sem NumPy/Pandas).

### 8.1 Média Móvel (janela = 3 ciclos)

```python
def media_movel(serie, janela=3):
    resultado = []
    for i in range(len(serie) - janela + 1):
        media = sum(serie[i:i+janela]) / janela
        resultado.append(media)
    return resultado
```

Uso: suavizar a série de reserva de energia para identificar tendência real,
eliminando ruído de ciclo a ciclo.

### 8.2 Regressão Linear Simples (feita à mão)

```python
def regressao_linear(x, y):
    n = len(x)
    sum_x  = sum(x)
    sum_y  = sum(y)
    sum_xy = sum(x[i] * y[i] for i in range(n))
    sum_x2 = sum(xi ** 2 for xi in x)
    b = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
    a = (sum_y - b * sum_x) / n
    return a, b   # y = a + b*x
```

Uso: extrapolar a reserva de energia para os próximos 3 ciclos.

### 8.3 Output do Forecasting

```
=== PREVISAO DE RESERVA DE ENERGIA ===
Tecnica 1 — Media Movel (janela 3 ciclos):
  Tendencia atual: -12.3 pp por ciclo

Tecnica 2 — Regressao Linear:
  Equacao: reserva = 85.4 - 12.1 * ciclo
  Ciclo 7: ~0.7%  |  Ciclo 8: -11.4% (esgotamento previsto)

DECISAO INFLUENCIADA: Estado elevado para CRITICO.
Recomendacao: desligar laboratorio imediatamente e
redistribuir energia para suporte de vida e comunicacao.
```

---

## 9. Fluxo de Execução

```
1. carregar_dados()
      └─ Lê dados.csv, popula todas as estruturas

2. detectar_inconsistencias()
      └─ Valida ranges físicos, gera alertas para anomalias

3. classificar_modulos()
      └─ Monta tabela de status dos 6 módulos

4. gerar_alertas()
      └─ Avalia todas as condições, popula fila_alertas

5. classificar_estado_missao()
      └─ Aplica regras booleanas → NORMAL / ALERTA / CRITICO

6. executar_forecasting()
      └─ Média móvel + regressão linear na reserva de energia
      └─ Resultado pode elevar o estado da missão

7. gerar_recomendacoes()
      └─ Baseadas no estado final + alertas críticos pendentes

8. exibir_relatorio()
      └─ Imprime tudo formatado no terminal, seção por seção
      └─ Exporta log da sessão para data/log_sessao.txt
```

---

## 10. Estrutura do Output no Terminal

```
╔══════════════════════════════════════════════════════╗
║         ARES-1 HABITAT MONITORING SYSTEM             ║
║         Missão: Habitat em Marte — Ciclo 6           ║
╚══════════════════════════════════════════════════════╝

[1/7] CARREGAMENTO DE DADOS
[2/7] STATUS DOS MODULOS CRITICOS
[3/7] VARIAVEIS AMBIENTAIS
[4/7] LOG DE EVENTOS
[5/7] ALERTAS AUTOMATICOS
[6/7] PREVISAO DE ENERGIA (FORECASTING)
[7/7] DIAGNOSTICO FINAL E RECOMENDACOES
```

Separadores ASCII claros entre seções. Tabelas alinhadas com espaços.  
Estado final em destaque: `*** ESTADO DA MISSAO: CRITICO ***`

---

## 11. Funções Previstas

| Função | Responsabilidade |
|---|---|
| `carregar_dados(caminho)` | Lê CSV e retorna estruturas populadas |
| `detectar_inconsistencias(dados)` | Valida ranges, retorna lista de anomalias |
| `classificar_modulos(modulos)` | Gera tabela de status dos módulos |
| `gerar_alertas(modulos, ambiente, reserva)` | Popula fila_alertas |
| `classificar_estado_missao(modulos, ambiente, reserva)` | Retorna NORMAL/ALERTA/CRITICO |
| `media_movel(serie, janela)` | Calcula média móvel |
| `regressao_linear(x, y)` | Calcula coeficientes a, b |
| `executar_forecasting(historico)` | Orquestra as duas técnicas, retorna previsão |
| `gerar_recomendacoes(estado, alertas)` | Retorna lista de recomendações priorizadas |
| `exibir_relatorio(...)` | Imprime todas as seções no terminal |
| `exportar_log(relatorio)` | Salva sessão em data/log_sessao.txt |
| `main()` | Orquestra tudo em ordem |

---

## 12. Checklist de Requisitos Cobertos

| Requisito do brief | Solução |
|---|---|
| 6+ módulos críticos com binário | ✅ 6 módulos no CSV |
| 6+ leituras de energia | ✅ 6 ciclos no CSV |
| Variáveis ambientais | ✅ temperatura, radiação, vento, pressão, comunicação |
| Log com 8+ eventos | ✅ 9 eventos incluindo inconsistência |
| Inconsistência intencional | ✅ pressão -999 kPa detectada e documentada |
| Lista | ✅ historico_energia, leituras_ambientais |
| Fila | ✅ fila_alertas (FIFO com list + append/pop(0)) |
| Pilha | ✅ pilha_eventos_criticos (LIFO com list + append/pop()) |
| Dicionário | ✅ modulos, cada alerta, cada evento |
| Hierarquia | ✅ areas_missao (dict de dicts) |
| Matriz | ✅ matriz_leituras (lista de listas) |
| if/elif/else | ✅ em classificar_estado_missao e gerar_alertas |
| and/or/not em 3+ regras | ✅ nas 3 regras de diagnóstico |
| Expressão booleana no README | ✅ documentada na seção 6 deste PRD |
| Alertas com severidade + descrição + ação | ✅ dicionário por alerta |
| Forecasting sem bibliotecas avançadas | ✅ média móvel + regressão linear manuais |
| Previsão influencia decisão | ✅ estado pode ser elevado para CRITICO |
| Leitura de arquivo externo | ✅ CSV lido por carregar_dados() |
| Sem dependências externas | ✅ somente biblioteca padrão |
