# ARES-1 Habitat Monitoring System (HMS)

**Global Solution 2026 – Indústria Espacial | FIAP – GRUPO 404**

Sistema inteligente de monitoramento operacional para um habitat científico
experimental em Marte. O programa lê a telemetria da missão, interpreta o
estado dos módulos, detecta inconsistências, gera alertas automáticos, prevê o
comportamento da reserva de energia e emite recomendações técnicas priorizadas.

## Equipe e RMs

| Nome | RM |
| ------------------------- | -------- |
| Fernando dos Santos Motta | RM570046 |
| Caetano de Medeiros Bona | RM569262 |
| Joedson da Silva Souza | RM573981 |
| Mylena Ramalho da Silva Torquato | RM572383 |
| Erik Fabiano de Jesus Appe | RM571067 |

## 1. Resumo do problema e cenário analisado

A Missão **ARES-1** mantém um habitat semi-autônomo em Marte com 6 astronautas.
Em ambientes onde a comunicação com a Terra é intermitente, os dados dos
sensores são a principal fonte de decisão. O sistema processa um pacote de
telemetria de um ciclo crítico em que ocorrem, simultaneamente: dano em painel
solar (queda de geração), falha no módulo de comunicação primário, pico de
radiação acima do limite seguro, queda acentuada da reserva de energia e uma
**leitura inconsistente** do sensor de pressão (`-999 kPa`, fisicamente
impossível). O desafio é diagnosticar a situação, separar dado confiável de
ruído e recomendar ações que protejam a tripulação e os equipamentos.

## 2. Estruturas de dados usadas e por quê

| Estrutura | Onde aparece | Por que foi escolhida |
| --- | --- | --- |
| **Lista** | `historico_reserva`, `matriz_leituras[i]` | Série temporal ordenada da reserva de energia; acesso por índice e iteração no forecasting. |
| **Fila (FIFO)** | `fila_alertas` (`append` / `pop(0)`) | Alertas são tratados na ordem em que chegam — o primeiro gerado é o primeiro a ser respondido. |
| **Pilha (LIFO)** | `pilha_eventos_criticos` (`append` / `pop`) | Acesso rápido ao evento crítico **mais recente** analisado (topo da pilha). |
| **Dicionário / hash** | `modulos`, cada alerta, cada evento | Acesso O(1) ao status de um módulo pelo nome (ex.: `modulos["comunicacao"]`). |
| **Hierarquia (dict de dicts)** | `areas_missao` | Agrupa os módulos por área operacional: vida, energia, comunicação e habitat. |
| **Matriz (lista de listas)** | `matriz_leituras` | Visão tabular ciclo × variável (ciclo, geração, consumo, reserva). |

## 3. Regras lógicas principais do diagnóstico

O estado é classificado com `if`/`elif`/`else` e operadores `and`/`or`/`not`
em três regras distintas (CRÍTICO, ALERTA, NORMAL).

**Expressão booleana principal (estado CRÍTICO):**

```text
CRITICO = (suporte_vida == 0) OR (energia == 0) OR
          (reserva < 20 AND comunicacao == 0) OR
          (radiacao > 8.0 AND reserva < 30)
```

- **CRÍTICO** — um módulo essencial caiu, **ou** energia e comunicação falharam
 juntas, **ou** há radiação alta combinada com reserva baixa. São combinações
 que ameaçam diretamente a vida da tripulação.
- **ALERTA** — `NOT crítico` **e** alguma condição de risco isolada (reserva
 < 40%, comunicação offline, radiação > 5.0, temperatura interna fora de
 18–28 °C ou inconsistência de sensor). Situação degradada, mas controlável.
- **NORMAL** — nem crítico nem alerta: operação nominal.

Há ainda uma **regra de interpretação por faixas de segurança**: toda variável
ambiental é validada contra um intervalo físico plausível; a pressão `-999 kPa`
viola a faixa `(0, 200)` e é marcada como leitura não confiável.

## 4. Técnica de previsão utilizada e resultado

Forecasting da **reserva de energia** com duas técnicas implementadas em Python
puro (sem NumPy/Pandas):

1. **Média móvel (janela = 3 ciclos)** — suaviza o ruído e revela a tendência
 (~ −13 pontos percentuais por ciclo).
2. **Regressão linear simples (mínimos quadrados, feita à mão)** — ajusta a reta
 `reserva = 87.5 − 12.5 × ciclo` sobre os 6 ciclos observados.

**Resultado:** a projeção indica `Ciclo 7 ≈ 0,1%` e valores **negativos** nos
ciclos 8 e 9, ou seja, **esgotamento iminente** da reserva. Esse resultado
**eleva o estado da missão para CRÍTICO** e dispara a recomendação de racionar
consumo e priorizar recarga das baterias.

## 5. Como executar

Requer apenas Python 3 (biblioteca padrão, sem dependências externas):

```bash
python src/sistema.py
```

O programa lê `data/dados.csv`, imprime o relatório completo no terminal e
exporta a sessão para `data/log_sessao.txt`.

## 6. Exemplo de entrada e saída

**Entrada (trecho de `data/dados.csv`):** reserva no ciclo 6 = 12%, consumo = 80
kWh, geração = 10 kWh, `suporte_vida=1`, `comunicacao=0`, radiação = 8,7 mSv/h,
pressão = −999 kPa (inconsistência).

**Saída (resumo):**

```text
*** ESTADO DA MISSAO: CRITICO ***

[CRITICO] energia          -> Reserva de energia critica (12%).
[CRITICO] ambiente         -> Radiacao muito elevada (8.7 mSv/h).
[ALERTA]  comunicacao      -> Modulo de comunicacao primario offline.
[ALERTA]  pressao_interna  -> Leitura -999 kPa fora da faixa fisica valida.

Previsao (regressao): reserva = 87.5 - 12.5 * ciclo  ->  Ciclo 7 ~= 0.1%
```

## 7. Recomendações geradas pelo sistema

1. **[CRÍTICA]** Manter suporte à vida e comunicação de emergência ativos.
2. **[ALTA]** Desligar laboratório e sistemas não essenciais.
3. **[ALTA]** Redirecionar energia para habitat e carregamento de baterias.
4. **[CRÍTICA]** Previsão de esgotamento da reserva: racionar consumo agora e
 priorizar recarga das baterias.

## 8. Link do vídeo (YouTube – Não Listado)

> O link final está em [`docs/link_video.txt`](docs/link_video.txt).
> _Substituir pelo link real após a publicação._

## 9. Conclusões e aprendizados

O projeto mostrou, na prática, como estruturas de dados fundamentais (listas,
filas, pilhas, dicionários, hierarquias e matrizes) organizam telemetria
heterogênea de forma que regras lógicas claras consigam transformar números em
decisões operacionais. A separação entre dado confiável e ruído (a pressão
`-999 kPa`) reforçou a importância de validar a entrada antes de confiar nela. A
previsão simples por regressão linear, mesmo sem bibliotecas avançadas, foi
suficiente para antecipar uma falha de recurso e **influenciar diretamente** a
classificação e as recomendações — exatamente o tipo de raciocínio esperado de
um sistema de apoio à decisão em uma operação espacial crítica.

## Estrutura do repositório

```text
atv-global-solution/
├── README.md
├── src/sistema.py
├── data/dados.csv
└── docs/
    ├── relatorio.pdf
    ├── link_video.txt
    └── uso_ia.md
```
