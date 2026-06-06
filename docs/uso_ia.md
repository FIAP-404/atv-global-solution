# Uso de Inteligência Artificial

Conforme a seção 13 do enunciado, registramos de forma transparente como a IA
foi utilizada no projeto e qual validação crítica a equipe realizou.

## Em quais partes a IA apoiou

- **Organização de ideias e estruturação do PRD** (`docs/prd_sistema_py.md`):
  a IA ajudou a transformar os requisitos do enunciado em uma especificação
  técnica organizada, com tabela de estruturas de dados e fluxo de execução.
- **Revisão de texto** do README e do relatório, melhorando clareza e coesão.
- **Sugestão de cenário** (habitat em Marte) coerente com a narrativa das fases
  1, 2 e 3 da disciplina.
- **Apoio na redação dos comentários** do código e na padronização de nomes.

## O que foi feito pela equipe

- **Toda a lógica computacional** — regras booleanas de diagnóstico, montagem
  das estruturas (fila, pilha, hierarquia, matriz), geração e priorização de
  alertas e implementação manual da média móvel e da regressão linear — foi
  escrita e compreendida pela equipe. Nenhum bloco de código ou análise foi
  copiado diretamente de IA sem entendimento.
- **Definição dos dados simulados** e da inconsistência intencional
  (`pressão = -999 kPa`), escolhidos para exercitar a capacidade de diagnóstico.
- **Decisões técnicas** (faixas de segurança, gatilhos de severidade, política
  de elevação do estado pela previsão) foram debatidas e definidas pela equipe.

## Validação crítica realizada

1. **Conferência matemática da regressão linear.** Recalculamos manualmente os
   coeficientes pelos mínimos quadrados — `a = 87,53`, `b = -12,49` — e
   confirmamos que batem com a saída do programa e com a projeção do ciclo 7
   (~0,1%). A fórmula não foi aceita "no escuro".
2. **Teste de execução ponta a ponta.** Rodamos `python src/sistema.py`
   verificando que o programa executa sem erros, detecta a inconsistência,
   classifica o estado como CRÍTICO e prioriza os alertas corretamente.
3. **Revisão das regras booleanas.** Validamos manualmente que cada condição de
   `and`/`or`/`not` corresponde a uma situação operacional real e defensável,
   ajustando limiares que não faziam sentido físico.
4. **Coerência dos dados.** Verificamos se todos os requisitos mínimos do pacote
   de telemetria (6 módulos, 6 ciclos de energia, variáveis ambientais, 8+
   eventos e a inconsistência) estavam presentes e consistentes entre si.
