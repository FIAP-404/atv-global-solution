# Roteiro do vídeo de apresentação — ARES-1 HMS (GRUPO 404)

**Duração-alvo:** até 4 minutos · **Formato:** YouTube "Não listado"
**Dica:** dividam as falas entre os 3 integrantes e mostrem o terminal rodando ao vivo (critério da rubrica: 2,0 pts).

---

## Bloco 1 — Abertura e problema (0:00 – 0:35)

**[Slide 1 — Capa]**

> "Olá! Somos o Grupo 404 da FIAP. Este é o ARES-1 Habitat Monitoring System,
> nossa solução para o Global Solution 2026 sobre a indústria espacial.
> Eu sou o Fernando, e comigo estão o Caetano e o Joedson."

**[Slide 2 — O problema]**

> "O cenário é um habitat científico em Marte com seis astronautas. A comunicação
> com a Terra é intermitente, então os dados dos sensores são a principal fonte de
> decisão. Nosso sistema lê essa telemetria, identifica situações críticas, gera
> alertas e recomenda ações para manter a missão segura."

---

## Bloco 2 — Dados e estruturas (0:35 – 1:20)

**[Slide 3 — Dados simulados]**

> "Os dados ficam num CSV com quatro seções: status binário de 6 módulos, 6 ciclos
> de energia, variáveis ambientais e um log de 9 eventos. Plantamos uma
> inconsistência proposital: o sensor de pressão reportando -999 kPa, que é
> fisicamente impossível."

**[Slide 4 — Estruturas de dados]**

> "Organizamos tudo em estruturas que estudamos nas três fases: uma lista para a
> série temporal da reserva, uma fila FIFO para os alertas, uma pilha LIFO para os
> eventos críticos, dicionários para acesso rápido aos módulos, uma hierarquia por
> área da missão e uma matriz ciclo por variável."

---

## Bloco 3 — Demonstração ao vivo (1:20 – 2:40)

**[Trocar para o TERMINAL — rodar `python src/sistema.py`]**

> "Vamos rodar o sistema."

Mostre apontando para a tela, na ordem em que aparece:

> "Ele carrega os dados, classifica cada módulo... aqui ele já detectou a
> inconsistência da pressão e marcou o sensor como não confiável."

> "Na seção de alertas, repare que eles vêm ordenados por severidade: primeiro os
> CRÍTICOS — reserva em 12% e radiação alta — depois os de ALERTA. Cada alerta já
> traz a ação recomendada."

> "Aqui está a previsão: usamos média móvel e regressão linear feitas à mão. A reta
> é reserva = 87,5 menos 12,5 vezes o ciclo. A projeção do ciclo 7 dá quase zero por
> cento — ou seja, esgotamento iminente."

---

## Bloco 4 — Diagnóstico e decisão defendida (2:40 – 3:25)

**[Slide 5 — Lógica e diagnóstico]**

> "O diagnóstico final é CRÍTICO. E o ponto-chave: foi a *previsão* que elevou o
> estado para crítico. A expressão booleana principal combina suporte à vida,
> energia, reserva, comunicação e radiação com AND, OR e NOT."

**[Slide 6 — Recomendações]**

> "Por isso o sistema recomenda, em ordem: manter suporte à vida e comunicação de
> emergência, desligar o laboratório, redirecionar energia para o habitat e
> racionar consumo. Cada recomendação é rastreável a um alerta, uma regra ou à
> previsão."

---

## Bloco 5 — Fechamento (3:25 – 4:00)

**[Slide 7 — Encerramento]**

> "Resumindo: estruturas de dados bem aplicadas, regras lógicas claras e uma
> previsão simples que influencia a decisão real do sistema — tudo em Python puro,
> sem bibliotecas externas. O código, os dados e o relatório completo estão no nosso
> repositório no GitHub. Obrigado!"

---

### Checklist antes de gravar
- [ ] Terminal com fonte grande e legível.
- [ ] Rodar `python src/sistema.py` uma vez antes para garantir que está limpo.
- [ ] Falar com calma — 4 minutos é o teto, melhor sobrar.
- [ ] Os três integrantes aparecem/falam.
- [ ] Subir no YouTube como **Não listado** e colar o link em `docs/link_video.txt`.
