# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

## Objetivo

Você deve entregar um software capaz de:

1. **Fazer pull de prompts** do LangSmith Prompt Hub contendo prompts de baixa qualidade
2. **Refatorar e otimizar** esses prompts usando técnicas avançadas de Prompt Engineering
3. **Fazer push dos prompts otimizados** de volta ao LangSmith
4. **Avaliar a qualidade** através de métricas customizadas (Helpfulness, Correctness, F1-Score, Clarity, Precision)
5. **Atingir pontuação mínima** de 0.9 (90%) em todas as métricas de avaliação

---

## Exemplo no CLI

**Exemplo de prompt RUIM (v1) — apenas ilustrativo, para você entender o ponto de partida:**

```
==================================================
Prompt: {seu_username}/bug_to_user_story_v1
==================================================

Métricas Derivadas:
  - Helpfulness: 0.45 ✗
  - Correctness: 0.52 ✗

Métricas Base:
  - F1-Score: 0.48 ✗
  - Clarity: 0.50 ✗
  - Precision: 0.46 ✗

❌ STATUS: REPROVADO
⚠️  Métricas abaixo de 0.9: helpfulness, correctness, f1_score, clarity, precision
```

**Exemplo de prompt OTIMIZADO (v2) — seu objetivo é chegar aqui:**

```bash
# Após refatorar os prompts e fazer push
python src/push_prompts.py

# Executar avaliação
python src/evaluate.py

Executando avaliação dos prompts...
==================================================
Prompt: {seu_username}/bug_to_user_story_v2
==================================================

Métricas Derivadas:
  - Helpfulness: 0.94 ✓
  - Correctness: 0.96 ✓

Métricas Base:
  - F1-Score: 0.93 ✓
  - Clarity: 0.95 ✓
  - Precision: 0.92 ✓

✅ STATUS: APROVADO - Todas as métricas >= 0.9
```
---

## Tecnologias obrigatórias

- **Linguagem:** Python 3.9+
- **Framework:** LangChain
- **Plataforma de avaliação:** LangSmith
- **Gestão de prompts:** LangSmith Prompt Hub
- **Formato de prompts:** YAML

---

## Pacotes recomendados

```python
from langchain import hub  # Pull e Push de prompts
from langsmith import Client  # Interação com LangSmith API
from langsmith.evaluation import evaluate  # Avaliação de prompts
from langchain_openai import ChatOpenAI  # LLM OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI  # LLM Gemini
```

---

## OpenAI

- Crie uma **API Key** da OpenAI: https://platform.openai.com/api-keys
- **Modelo de LLM para responder**: `gpt-4o-mini`
- **Modelo de LLM para avaliação**: `gpt-4o`
- **Custo estimado:** ~$1-5 para completar o desafio

## Gemini (modelo free)

- Crie uma **API Key** da Google: https://aistudio.google.com/app/apikey
- **Modelo de LLM para responder**: `gemini-2.5-flash`
- **Modelo de LLM para avaliação**: `gemini-2.5-flash`
- **Limite:** 15 req/min, 1500 req/dia

---

## Requisitos

### 1. Pull do Prompt inicial do LangSmith

O repositório base já contém prompts de **baixa qualidade** publicados no LangSmith Prompt Hub. Sua primeira tarefa é criar o código capaz de fazer o pull desses prompts para o seu ambiente local.

**Tarefas:**

1. Configurar suas credenciais do LangSmith no arquivo `.env` (conforme o arquivo `.env.example`)
2. Implementar o script `src/pull_prompts.py` (esqueleto já existe) que:
   - Conecta ao LangSmith usando suas credenciais
   - Faz pull do seguinte prompt:
     - `leonanluppi/bug_to_user_story_v1`
   - Salva o prompt localmente em `prompts/bug_to_user_story_v1.yml`

---

### 2. Otimização do Prompt

Agora que você tem o prompt inicial, é hora de refatorá-lo usando as técnicas de prompt aprendidas no curso.

**Tarefas:**

1. Analisar o prompt em `prompts/bug_to_user_story_v1.yml`
2. Criar um novo arquivo `prompts/bug_to_user_story_v2.yml` com suas versões otimizadas
3. Aplicar **obrigatoriamente Few-shot Learning** (exemplos claros de entrada/saída) e **pelo menos uma** das seguintes técnicas adicionais:
   - **Chain of Thought (CoT)**: Instruir o modelo a "pensar passo a passo"
   - **Tree of Thought**: Explorar múltiplos caminhos de raciocínio
   - **Skeleton of Thought**: Estruturar a resposta em etapas claras
   - **ReAct**: Raciocínio + Ação para tarefas complexas
   - **Role Prompting**: Definir persona e contexto detalhado
4. Documentar no `README.md` quais técnicas você escolheu e por quê

**Requisitos do prompt otimizado:**

- Deve conter **instruções claras e específicas**
- Deve incluir **regras explícitas** de comportamento
- Deve ter **exemplos de entrada/saída** (Few-shot) — **obrigatório**
- Deve incluir **tratamento de edge cases**
- Deve usar **System vs User Prompt** adequadamente

---

### 3. Push e Avaliação

Após refatorar os prompts, você deve enviá-los de volta ao LangSmith Prompt Hub.

**Tarefas:**

1. Implementar o script `src/push_prompts.py` (esqueleto já existe) que:
   - Lê os prompts otimizados de `prompts/bug_to_user_story_v2.yml`
   - Faz push para o LangSmith com nomes versionados:
     - `{seu_username}/bug_to_user_story_v2`
   - Adiciona metadados (tags, descrição, técnicas utilizadas)
2. Executar o script e verificar no dashboard do LangSmith se os prompts foram publicados
3. Deixá-lo público

---

### 4. Iteração

- Espera-se 3-5 iterações.
- Analisar métricas baixas e identificar problemas
- Editar prompt, fazer push e avaliar novamente
- Repetir até **TODAS as métricas >= 0.9**

### Critério de Aprovação:

```
- Helpfulness >= 0.9
- Correctness >= 0.9
- F1-Score >= 0.9
- Clarity >= 0.9
- Precision >= 0.9

MÉDIA das 5 métricas >= 0.9
```

**IMPORTANTE:** TODAS as 5 métricas devem estar >= 0.9, não apenas a média!

### 5. Testes de Validação

**O que você deve fazer:** Edite o arquivo `tests/test_prompts.py` e implemente, no mínimo, os 6 testes abaixo usando `pytest`:

- `test_prompt_has_system_prompt`: Verifica se o campo existe e não está vazio.
- `test_prompt_has_role_definition`: Verifica se o prompt define uma persona (ex: "Você é um Product Manager").
- `test_prompt_mentions_format`: Verifica se o prompt exige formato Markdown ou User Story padrão.
- `test_prompt_has_few_shot_examples`: Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot).
- `test_prompt_no_todos`: Garante que você não esqueceu nenhum `[TODO]` no texto.
- `test_minimum_techniques`: Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas.

**Como validar:**

```bash
pytest tests/test_prompts.py
```

---

## Estrutura obrigatória do projeto

Faça um fork do repositório base: **[Clique aqui para o template](https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt)**

```
mba-ia-pull-evaluation-prompt/
├── .env.example              # Template das variáveis de ambiente
├── requirements.txt          # Dependências Python
├── README.md                 # Sua documentação do processo
│
├── prompts/
│   ├── bug_to_user_story_v1.yml  # Prompt inicial (já incluso)
│   └── bug_to_user_story_v2.yml  # Seu prompt otimizado (criar)
│
├── datasets/
│   └── bug_to_user_story.jsonl   # 15 exemplos de bugs (já incluso)
│
├── src/
│   ├── pull_prompts.py       # Pull do LangSmith (implementar)
│   ├── push_prompts.py       # Push ao LangSmith (implementar)
│   ├── evaluate.py           # Avaliação automática (pronto)
│   ├── metrics.py            # 5 métricas implementadas (pronto)
│   └── utils.py              # Funções auxiliares (pronto)
│
├── tests/
│   └── test_prompts.py       # Testes de validação (implementar)
│
```

**O que você deve implementar:**

- `prompts/bug_to_user_story_v2.yml` — Criar do zero com seu prompt otimizado
- `src/pull_prompts.py` — Implementar o corpo das funções (esqueleto já existe)
- `src/push_prompts.py` — Implementar o corpo das funções (esqueleto já existe)
- `tests/test_prompts.py` — Implementar os 6 testes de validação (esqueleto já existe)
- `README.md` — Documentar seu processo de otimização

**O que já vem pronto (não alterar):**

- `src/evaluate.py` — Script de avaliação completo
- `src/metrics.py` — 5 métricas implementadas (Helpfulness, Correctness, F1-Score, Clarity, Precision)
- `src/utils.py` — Funções auxiliares
- `datasets/bug_to_user_story.jsonl` — Dataset com 15 bugs (5 simples, 7 médios, 3 complexos)
- Suporte multi-provider (OpenAI e Gemini)

## Repositórios úteis

- [Repositório boilerplate do desafio](https://github.com/devfullcycle/mba-ia-prompt-engineering)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

## VirtualEnv para Python

Crie e ative um ambiente virtual antes de instalar dependências:

```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Ordem de execução

### 1. Executar pull dos prompts ruins

```bash
python src/pull_prompts.py
```

### 2. Refatorar prompts

Edite manualmente o arquivo `prompts/bug_to_user_story_v2.yml` aplicando as técnicas aprendidas no curso.

### 3. Fazer push dos prompts otimizados

```bash
python src/push_prompts.py
```

### 4. Executar avaliação

```bash
python src/evaluate.py
```

---

## Entregável

1. **Repositório público no GitHub** (fork do repositório base) contendo:

   - Todo o código-fonte implementado
   - Arquivo `prompts/bug_to_user_story_v2.yml` 100% preenchido e funcional
   - Arquivo `README.md` atualizado com:

2. **README.md deve conter:**

   A) **Seção "Técnicas Aplicadas (Fase 2)"**:

   - Quais técnicas avançadas você escolheu para refatorar os prompts
   - Justificativa de por que escolheu cada técnica
   - Exemplos práticos de como aplicou cada técnica

   B) **Seção "Resultados Finais"**:

   - Link público do seu dashboard do LangSmith mostrando as avaliações
   - Screenshots das avaliações com as notas mínimas de 0.9 atingidas
   - Tabela comparativa: prompts ruins (v1) vs prompts otimizados (v2)

   C) **Seção "Como Executar"**:

   - Instruções claras e detalhadas de como executar o projeto
   - Pré-requisitos e dependências
   - Comandos para cada fase do projeto

3. **Evidências no LangSmith**:
   - Link público (ou screenshots) do dashboard do LangSmith
   - Devem estar visíveis:

     - Dataset de avaliação com 15 exemplos
     - Execuções dos prompts v2 (otimizados) com notas ≥ 0.9
     - Tracing detalhado de pelo menos 3 exemplos

---

## Dicas Finais

- **Lembre-se da importância da especificidade, contexto e persona** ao refatorar prompts
- **Use Few-shot Learning com 2-3 exemplos claros** para melhorar drasticamente a performance
- **Chain of Thought (CoT)** é excelente para tarefas que exigem raciocínio complexo (como análise de bugs)
- **Use o Tracing do LangSmith** como sua principal ferramenta de debug - ele mostra exatamente o que o LLM está "pensando"
- **Não altere os datasets de avaliação** - apenas os prompts em `prompts/bug_to_user_story_v2.yml`
- **Itere, itere, itere** - é normal precisar de 3-5 iterações para atingir 0.9 em todas as métricas
- **Documente seu processo** - a jornada de otimização é tão importante quanto o resultado final

---

# 📄 Documentação da Solução

> As seções abaixo documentam a resolução do desafio: técnicas aplicadas na refatoração do
> prompt, resultados das avaliações e instruções de execução.

## A) Técnicas Aplicadas (Fase 2)

A refatoração do prompt `bug_to_user_story_v1` → `bug_to_user_story_v2` aplicou **três técnicas**
de Prompt Engineering (o desafio exige Few-shot + ao menos uma adicional). Todas estão
declaradas no campo `techniques_applied` do arquivo
[`prompts/bug_to_user_story_v2.yml`](prompts/bug_to_user_story_v2.yml).

### 1. Few-shot Learning (obrigatória)

**O que é:** fornecer ao modelo exemplos completos de entrada (relato de bug) e saída
(User Story) para que ele aprenda o formato esperado por demonstração.

**Por que escolhi:** a métrica **F1-Score** (e seu componente *recall*) compara a resposta
gerada com a *ground truth* do dataset. Os exemplos de referência seguem um formato muito
específico (frase "Como um... eu quero... para que...", critérios em Gherkin, seções de
contexto técnico, e — nos casos complexos — blocos delimitados por `=== ... ===`). Sem exemplos,
o modelo improvisa formatos diferentes e o *recall* despenca. Com Few-shot, ele reproduz o
formato esperado, elevando F1, Clarity e Precision simultaneamente.

**Como apliquei:** incluí **3 exemplos** no `system_prompt`, um para cada nível de complexidade
do dataset (5 simples, 7 médios, 3 complexos):
- **Simples** (bug de uma frase) → história + ~5 critérios Gherkin.
- **Médio** (com logs/endpoints) → história + Gherkin + seção `Contexto Técnico:`.
- **Complexo** (múltiplos problemas + impacto) → seções `=== USER STORY PRINCIPAL ===`,
  `=== CRITÉRIOS DE ACEITAÇÃO ===` (grupos A/B/C/D), `=== CRITÉRIOS TÉCNICOS ===`,
  `=== CONTEXTO DO BUG ===` e `=== TASKS TÉCNICAS SUGERIDAS ===`.

### 2. Chain of Thought (CoT)

**O que é:** instruir o modelo a "pensar passo a passo" antes de responder.

**Por que escolhi:** transformar um bug em User Story exige raciocínio — identificar a persona,
a ação desejada, o valor de negócio e derivar critérios de aceitação que cubram todos os
cenários. O CoT melhora a qualidade e a completude da resposta (impacta F1 e Precision).

**Como apliquei:** o `system_prompt` traz a seção *"Como raciocinar"* com 5 passos
(quem → o quê → para quê → complexidade → critérios). **Importante:** instruí o modelo a
**raciocinar internamente e devolver APENAS o resultado final** — isso evita que o raciocínio
"vaze" na saída, o que prejudicaria a métrica **Clarity** e o *precision* do F1.

### 3. Role Prompting

**O que é:** atribuir uma persona/papel claro ao modelo.

**Por que escolhi:** definir a persona calibra o tom, o vocabulário e o nível de detalhe da
resposta para o domínio de produto/ágil, melhorando a relevância (Precision) e a clareza.

**Como apliquei:** o prompt começa com
*"Você é um Product Manager Sênior, especialista em metodologias ágeis e na escrita de
User Stories de alta qualidade."*, seguido de regras explícitas de comportamento, formato e
tratamento de *edge cases* (relato vago, vazio ou com múltiplos problemas).

### Resumo do uso de System vs. User Prompt

| Mensagem | Conteúdo | Variável |
|----------|----------|----------|
| **System** | Persona, regras, CoT, formato por complexidade, edge cases e os 3 exemplos Few-shot (estático) | — |
| **User** | Apenas o relato do bug | `{bug_report}` |

Manter o `system_prompt` **estático e sem variáveis** garante que a única variável de template
seja `{bug_report}` — exatamente o que o `evaluate.py` injeta a partir do dataset.

---

## B) Resultados Finais

### Tabela comparativa: v1 (ruim) vs v2 (otimizado)

Avaliação executada no LangSmith sobre o dataset `prompt-optimization-challenge-eval`
(15 exemplos). Responder: `gemini-2.5-flash`; Juiz (LLM-as-Judge): `gemini-2.5-pro`.

| Métrica | v1 (baseline)¹ | v2 (otimizado)² | Meta | Status |
|---------|:-------------:|:--------------:|:----:|:------:|
| Helpfulness | 0.45 | **0.9523** | ≥ 0.90 | ✅ |
| Correctness | 0.52 | **0.9335** | ≥ 0.90 | ✅ |
| F1-Score | 0.48 | **0.9017** | ≥ 0.90 | ✅ |
| Clarity | 0.50 | **0.9393** | ≥ 0.90 | ✅ |
| Precision | 0.46 | **0.9653** | ≥ 0.90 | ✅ |
| **Média geral** | ~0.48 | **0.9385** | ≥ 0.90 | ✅ |

> ✅ **STATUS: APROVADO** — todas as 5 métricas ≥ 0.90.
>
> ¹ Valores de v1 conforme o baseline ilustrativo do enunciado (prompt sem persona, sem
> few-shot e sem instruções de formato). ² Valores de v2 do experiment
> `v2-fix-recall-69dd487d` registrado no LangSmith.

### Jornada de otimização do F1-Score (a métrica mais difícil)

O F1 foi a única métrica que exigiu iteração dedicada. Usando os **experiments registrados
no LangSmith**, analisei o F1 exemplo a exemplo e descobri que a causa não era qualidade,
mas **recall**: o prompt v2 produzia respostas corretas (precision ~1.0), porém **omitia
seções inteiras que o gabarito esperava** (ex.: `Critérios Técnicos`, `Critérios de
Acessibilidade`, `Critérios Adicionais para Admins`, e um bloco de prevenção para cenários
de concorrência). Como o F1 = média harmônica de precision × recall, cada seção omitida
derrubava o recall e o F1.

| Iteração (experiment) | F1-Score | Demais métricas | Resultado |
|---|:---:|:---:|:---:|
| `v2-eval-e4079e6c` | 0.8563 | todas ≥ 0.90 | ❌ F1 abaixo da meta |
| `v2-fix-recall-69dd487d` | **0.9017** | todas ≥ 0.90 | ✅ **APROVADO** |

**Correção aplicada** (commit `69992a0b` do prompt no Hub): tornei as seções derivadas
**obrigatórias por gatilho** (causa técnica → `Critérios Técnicos:`; UI/UX →
`Critérios de Acessibilidade:`; múltiplos papéis → `Critérios Adicionais para [papel]:`;
regra de negócio com concorrência → `Critérios de Prevenção:`), adicionei regra
anti-precision para metas de performance (não cristalizar o tempo ruim como meta) e um
novo exemplo Few-shot de bug técnico. Efeito medido: o bug "App Android (notificações)"
subiu de F1 0.667 → 0.947, e o F1 médio de 0.856 → 0.902.

### Evidências no LangSmith

- **🔗 Link público (dataset + experiments) — abre sem login:**
  https://smith.langchain.com/public/482c1ac5-b48c-480d-afd6-caaef28d2be8/d

  Este link compartilha o dataset de avaliação (`prompt-optimization-challenge-eval`, **15
  exemplos**) junto com **todos os experiments** rodados sobre ele. Por aqui o avaliador
  pode confirmar, na própria plataforma, as 5 métricas ≥ 0.9 por exemplo, o tracing
  detalhado e o *reasoning* do juiz — exatamente o que os screenshots mostram.

  > Aparecem **dois experiments**, evidenciando a iteração exigida pelo desafio:
  > `#1 v2-eval-e4079e6c` (F1 0.86 — reprovado) → `#2 v2-fix-recall-69dd487d`
  > (**todas as 5 métricas ≥ 0.9 — aprovado**). O experiment final aprovado é o `#2`.

- **Link público do prompt (v2):**
  https://smith.langchain.com/prompts/bug_to_user_story_v2/69992a0b?organizationId=02a073ba-dcec-4290-93c4-7a01c4d4900e
- **Screenshots:** em `screenshots/`, as capturas mostrando (a) as 5 métricas ≥ 0.9
  na tela de comparação do experiment, (b) o dataset com 15 exemplos e (c) o tracing
  detalhado de pelo menos 3 exemplos.

> ℹ️ **Como os resultados são registrados no LangSmith:** o `src/evaluate.py` (imutável)
> calcula as métricas e as imprime no terminal, mas **não** cria um *Experiment* no
> LangSmith. Para gerar a evidência exigida (tela com as 5 métricas + link público), use o
> runner `run_experiment.py` (na raiz do projeto), que usa a API oficial
> `langsmith.evaluation.evaluate()` reaproveitando exatamente as mesmas funções de juiz de
> `src/metrics.py` e as mesmas fórmulas derivadas de `evaluate.py`. Veja a seção
> *Como Executar*.

### Diferenças-chave entre v1 e v2

| Aspecto | v1 | v2 |
|---------|----|----|
| Persona | Nenhuma ("assistente" genérico) | Product Manager Sênior (Role Prompting) |
| Exemplos | Nenhum | 3 exemplos Few-shot (simples/médio/complexo) |
| Raciocínio | Nenhum | Chain of Thought interno (5 passos) |
| Formato | Vago ("crie uma user story") | Formato canônico + Gherkin + seções por complexidade |
| Edge cases | Não tratados | Relato vago/vazio/múltiplos problemas tratados |
| Variável `{bug_report}` | Duplicada em system + user (bug) | Apenas no user prompt |

---

## C) Como Executar

### Pré-requisitos

- Python 3.9+ (testado em 3.11)
- Conta no [LangSmith](https://smith.langchain.com) com **API Key** e um **Hub handle** público
- API Key de um provider de LLM:
  - **Google Gemini** (gratuito): https://aistudio.google.com/app/apikey — usado nesta solução
  - ou **OpenAI**: https://platform.openai.com/api-keys

### 1. Ambiente virtual e dependências

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

Copie `.env.example` para `.env` e preencha:

```bash
cp .env.example .env   # Windows: copy .env.example .env
```

```env
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=<sua-chave-langsmith>
LANGSMITH_PROJECT=prompt-optimization-challenge
USERNAME_LANGSMITH_HUB=<seu-handle>      # preencher após o 1º push público
GOOGLE_API_KEY=<sua-chave-google>
LLM_PROVIDER=google
LLM_MODEL=gemini-2.5-flash
EVAL_MODEL=gemini-2.5-flash
```

> 💡 **Windows / acentuação no terminal:** os scripts imprimem emojis e acentos. Se aparecer
> `UnicodeEncodeError`, rode com saída em UTF-8:
> ```powershell
> $env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
> ```

### 3. Pull do prompt inicial (v1)

```bash
python src/pull_prompts.py
```
Faz pull de `leonanluppi/bug_to_user_story_v1` do Hub e salva em
`prompts/bug_to_user_story_v1.yml`.

### 4. (Já incluso) Otimizar o prompt

O prompt otimizado já está em [`prompts/bug_to_user_story_v2.yml`](prompts/bug_to_user_story_v2.yml).
Edite-o para iterar.

### 5. Push do prompt otimizado (v2)

```bash
python src/push_prompts.py
```
Publica `bug_to_user_story_v2` no seu Hub. Por padrão tenta publicar como **público**; se a
conta ainda não tiver um *Hub handle*, publica como **privado** e instrui você a torná-lo
público pela interface (isso cria o handle). Você pode forçar privado com
`PROMPT_PUBLIC=false`. Após o push, copie seu handle da URL e preencha
`USERNAME_LANGSMITH_HUB` no `.env`.

### 6. Avaliar (resumo no terminal)

```bash
python src/evaluate.py
```
Cria/atualiza o dataset de 15 exemplos, puxa o `v2` do Hub, executa contra o dataset, calcula as
5 métricas e **imprime o resumo no terminal**. Repita os passos 4–6 até **todas ≥ 0.9**.

### 6b. Registrar o Experiment no LangSmith (evidência printável + link público)

```bash
python run_experiment.py
```
O `evaluate.py` não cria um *Experiment* no LangSmith (só imprime no terminal). Este runner
externo usa a API oficial `langsmith.evaluation.evaluate()` para registrar um **Experiment**
com as 5 métricas por exemplo — gerando a tela de comparação e o **link público** exigidos
como evidência. Ele reaproveita as mesmas funções de juiz de `src/metrics.py` e as mesmas
fórmulas derivadas de `evaluate.py`, então o resultado é equivalente, porém persistido.

Variáveis úteis (opcionais):
- `EVAL_THROTTLE_SECONDS` (default `7`): pausa antes de cada chamada de LLM (evita HTTP 429
  no tier gratuito do Gemini).
- `EXPERIMENT_PREFIX` (default `v2-eval`): prefixo do nome do experiment no dashboard.

```powershell
# Windows (UTF-8 + throttle)
$env:PYTHONUTF8="1"; $env:PYTHONIOENCODING="utf-8"; $env:EVAL_THROTTLE_SECONDS="7"
python run_experiment.py
```

Ao final, o experiment aparece em *Datasets & Experiments → `prompt-optimization-challenge-eval`
→ aba Experiments*, e o link direto é impresso no terminal.

### 7. Testes de validação (estáticos, sem rede)

```bash
pytest tests/test_prompts.py -v
```

---

## Notas de Implementação

- **Arquivos implementados:** `src/pull_prompts.py`, `src/push_prompts.py`,
  `prompts/bug_to_user_story_v2.yml`, `tests/test_prompts.py`,
  `run_experiment.py` (runner externo que registra o Experiment no LangSmith — ver passo 6b).
- **Não alterados (já vinham prontos):** `src/evaluate.py`, `src/metrics.py`, `src/utils.py`,
  `datasets/bug_to_user_story.jsonl`. O `run_experiment.py` NÃO altera nenhum deles —
  apenas importa e reaproveita as funções de `metrics.py`/`utils.py`.
- **Provider:** Google Gemini (`gemini-2.5-flash`) para responder e avaliar.
- **Contrato de avaliação:** o `evaluate.py` faz `hub.pull("{USERNAME_LANGSMITH_HUB}/bug_to_user_story_v2")`
  esperando um `ChatPromptTemplate` cuja única variável seja `{bug_report}`. O `push_prompts.py`
  monta esse template a partir do YAML e valida essa restrição antes de publicar.
