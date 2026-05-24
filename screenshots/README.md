# Screenshots da entrega

Coloque aqui as capturas de tela exigidas pelo desafio. Abra cada link no navegador
**logado** na sua conta do LangSmith e capture:

## 1. As 5 métricas ≥ 0.9 (evidência principal)
Arquivo sugerido: `01-metricas-aprovadas.png`

- Abra o Experiment aprovado:
  https://smith.langchain.com/o/02a073ba-dcec-4290-93c4-7a01c4d4900e/datasets/cd998d48-52b2-42f4-a5a4-2d06891975ae/compare?selectedSessions=0133b8f1-7ceb-402a-9be1-b26ee1a5bc15
- Capture a tabela de comparação mostrando as colunas
  **helpfulness, correctness, f1_score, clarity, precision** com as médias ≥ 0.9.

## 2. Dataset com 15 exemplos
Arquivo sugerido: `02-dataset-15-exemplos.png`

- Vá em **Datasets & Experiments → `prompt-optimization-challenge-eval`**.
- Capture a lista mostrando os **15 examples**.

## 3. Tracing detalhado de pelo menos 3 exemplos
Arquivo sugerido: `03-tracing-exemplo-1.png`, `04-tracing-exemplo-2.png`, `05-tracing-exemplo-3.png`

- Dentro do Experiment, clique em uma linha (um exemplo) para abrir o trace.
- Capture a entrada (bug), a saída gerada (User Story) e os scores das métricas com o
  *reasoning* do juiz. Repita para 3 exemplos diferentes (sugestão: um simples, um médio
  e um complexo).

## 4. (opcional) Prompt público no Hub
Arquivo sugerido: `06-prompt-hub.png`

- Abra:
  https://smith.langchain.com/prompts/bug_to_user_story_v2/69992a0b?organizationId=02a073ba-dcec-4290-93c4-7a01c4d4900e
- Capture mostrando o badge **Public** e o conteúdo do system prompt.
