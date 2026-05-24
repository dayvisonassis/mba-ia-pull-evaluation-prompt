"""
run_experiment.py  —  Runner EXTERNO que registra um Experiment real no LangSmith.

Por que este arquivo existe
---------------------------
O `src/evaluate.py` (arquivo IMUTÁVEL do desafio) calcula as 5 métricas chamando os
juízes LLM diretamente e apenas IMPRIME a média no terminal. Ele NÃO usa
`langsmith.evaluation.evaluate()`, então nenhum resultado fica registrado como
"Experiment" no LangSmith — por isso o dataset `prompt-optimization-challenge-eval`
aparece com 0 experimentos no dashboard.

Este runner resolve isso SEM tocar em nenhum arquivo imutável: ele usa a API oficial
`evaluate()` para produzir um Experiment com as 5 métricas (helpfulness, correctness,
f1_score, clarity, precision) por exemplo, gerando uma tela printável e um link público
compartilhável — exatamente o que o README do desafio pede como evidência.

Fidelidade ao evaluate.py
-------------------------
- Responder: mesmo `get_llm(temperature=0)` (LLM_MODEL do .env).
- Juízes base: as MESMAS funções de `src/metrics.py`
  (`evaluate_f1_score`, `evaluate_clarity`, `evaluate_precision`).
- Derivadas: mesma fórmula de evaluate.py
  `helpfulness=(clarity+precision)/2`, `correctness=(f1+precision)/2`.
- Para não julgar 2x (custo), as 3 métricas-base são calculadas uma única vez por
  exemplo e cacheadas; as derivadas reaproveitam o cache.

Uso
---
    $env:PYTHONUTF8="1"; $env:PYTHONIOENCODING="utf-8"
    .\venv\Scripts\python.exe run_experiment.py

Variáveis opcionais:
    EVAL_THROTTLE_SECONDS  (default 7)  -> sleep antes de cada invoke do Gemini (anti-429)
    EXPERIMENT_PREFIX      (default "v2-eval")
    EVAL_CONCURRENCY       (default 1)  -> mantenha 1 com Gemini free p/ não estourar rate

NÃO COMMITAR mudanças de credenciais. Este arquivo é seguro p/ commit (não tem segredo).
"""

import os
import sys
import time

# Garante que `import metrics`/`utils` funcione (eles vivem em src/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dotenv import load_dotenv
load_dotenv()

# --- Throttle anti-429 (monkeypatch no invoke do provider ativo) -------------------
_THROTTLE = float(os.getenv("EVAL_THROTTLE_SECONDS", "7"))
_provider = os.getenv("LLM_PROVIDER", "openai").lower()

if _provider == "google":
    import langchain_google_genai as _g
    _Base = _g.ChatGoogleGenerativeAI

    class _ThrottledGoogle(_Base):
        def invoke(self, *a, **k):
            time.sleep(_THROTTLE)
            return super().invoke(*a, **k)

    _g.ChatGoogleGenerativeAI = _ThrottledGoogle
elif _provider == "openai":
    import langchain_openai as _o
    _Base = _o.ChatOpenAI

    class _ThrottledOpenAI(_Base):
        def invoke(self, *a, **k):
            time.sleep(_THROTTLE)
            return super().invoke(*a, **k)

    _o.ChatOpenAI = _ThrottledOpenAI

# Imports que dependem do provider já patchado vêm DEPOIS do monkeypatch.
from langsmith import Client
from langsmith.evaluation import evaluate
from langchain import hub

from utils import get_llm as _get_configured_llm, check_env_vars
from metrics import evaluate_f1_score, evaluate_clarity, evaluate_precision


def get_llm():
    return _get_configured_llm(temperature=0)


# --- Cache de métricas-base por exemplo (evita julgar 2x p/ as derivadas) ----------
# chave: id(run) -> {"f1":..., "clarity":..., "precision":...}
_BASE_CACHE: dict = {}


def _extract_io(run, example):
    """Extrai (question, answer, reference) de forma robusta."""
    answer = ""
    if run is not None and getattr(run, "outputs", None):
        out = run.outputs
        # target() retorna {"answer": "..."}; mas cobrimos outras chaves comuns
        answer = out.get("answer") or out.get("output") or out.get("content") or ""
        if not answer and len(out) == 1:
            answer = next(iter(out.values()))

    inputs = getattr(example, "inputs", {}) or {}
    question = inputs.get("question") or inputs.get("bug_report") or inputs.get("pr_title") or "N/A"

    ref = ""
    outs = getattr(example, "outputs", {}) or {}
    if isinstance(outs, dict):
        ref = outs.get("reference", "")
    return question, str(answer), str(ref)


def _get_base_scores(run, example):
    key = id(run)
    if key in _BASE_CACHE:
        return _BASE_CACHE[key]

    question, answer, reference = _extract_io(run, example)
    if not answer:
        scores = {"f1": 0.0, "clarity": 0.0, "precision": 0.0,
                  "f1_reason": "resposta vazia", "clarity_reason": "", "precision_reason": ""}
        _BASE_CACHE[key] = scores
        return scores

    f1 = evaluate_f1_score(question, answer, reference)
    clarity = evaluate_clarity(question, answer, reference)
    precision = evaluate_precision(question, answer, reference)

    scores = {
        "f1": f1["score"], "clarity": clarity["score"], "precision": precision["score"],
        "f1_reason": f1.get("reasoning", ""),
        "clarity_reason": clarity.get("reasoning", ""),
        "precision_reason": precision.get("reasoning", ""),
    }
    _BASE_CACHE[key] = scores
    return scores


# --- Os 5 evaluators (assinatura run, example -> dict) -----------------------------
def f1_evaluator(run, example):
    s = _get_base_scores(run, example)
    return {"key": "f1_score", "score": s["f1"], "comment": s["f1_reason"][:250]}


def clarity_evaluator(run, example):
    s = _get_base_scores(run, example)
    return {"key": "clarity", "score": s["clarity"], "comment": s["clarity_reason"][:250]}


def precision_evaluator(run, example):
    s = _get_base_scores(run, example)
    return {"key": "precision", "score": s["precision"], "comment": s["precision_reason"][:250]}


def helpfulness_evaluator(run, example):
    s = _get_base_scores(run, example)
    return {"key": "helpfulness", "score": round((s["clarity"] + s["precision"]) / 2, 4),
            "comment": "derivada: (clarity + precision) / 2"}


def correctness_evaluator(run, example):
    s = _get_base_scores(run, example)
    return {"key": "correctness", "score": round((s["f1"] + s["precision"]) / 2, 4),
            "comment": "derivada: (f1 + precision) / 2"}


def main():
    provider = os.getenv("LLM_PROVIDER", "openai")
    llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    eval_model = os.getenv("EVAL_MODEL", "gpt-4o")
    username = os.getenv("USERNAME_LANGSMITH_HUB", "")
    project = os.getenv("LANGSMITH_PROJECT", "prompt-optimization-challenge")
    dataset_name = f"{project}-eval"
    prefix = os.getenv("EXPERIMENT_PREFIX", "v2-eval")
    concurrency = int(os.getenv("EVAL_CONCURRENCY", "1"))

    print("=" * 70)
    print("REGISTRANDO EXPERIMENT NO LANGSMITH (runner externo)")
    print("=" * 70)
    print(f"Provider:        {provider}")
    print(f"Responder:       {llm_model}")
    print(f"Juiz:            {eval_model}")
    print(f"Throttle:        {_THROTTLE}s/invoke  | concurrency={concurrency}")
    print(f"Dataset:         {dataset_name}")
    print(f"Hub prompt:      {username}/bug_to_user_story_v2")
    print(f"Experiment pfx:  {prefix}")
    print("=" * 70)

    required = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    required.append("OPENAI_API_KEY" if provider == "openai" else "GOOGLE_API_KEY")
    if not check_env_vars(required):
        return 1

    client = Client()

    # Confere se o dataset existe (não recria; evaluate.py já cria os 15 exemplos)
    datasets = [d for d in client.list_datasets(dataset_name=dataset_name) if d.name == dataset_name]
    if not datasets:
        print(f"\n❌ Dataset '{dataset_name}' não existe ainda.")
        print("   Rode `python src/evaluate.py` ao menos uma vez para criá-lo,")
        print("   ou crie-o com os 15 exemplos antes de registrar o experiment.")
        return 1
    print(f"✓ Dataset encontrado: {dataset_name} "
          f"({datasets[0].example_count} exemplos)")

    # Puxa o prompt v2 do Hub UMA vez (fonte da verdade, igual evaluate.py)
    prompt_name = f"{username}/bug_to_user_story_v2"
    print(f"\nPuxando prompt do Hub: {prompt_name} ...")
    prompt_template = hub.pull(prompt_name)
    print("✓ Prompt carregado.")

    llm = get_llm()
    chain = prompt_template | llm

    def target(inputs: dict) -> dict:
        """Roda o prompt v2 sobre um exemplo do dataset. Igual ao evaluate.py."""
        resp = chain.invoke(inputs)
        return {"answer": resp.content}

    print("\nIniciando avaliação (isto fará ~15 gerações + 45 julgamentos)...\n")
    results = evaluate(
        target,
        data=dataset_name,
        evaluators=[
            f1_evaluator,
            clarity_evaluator,
            precision_evaluator,
            helpfulness_evaluator,
            correctness_evaluator,
        ],
        experiment_prefix=prefix,
        max_concurrency=concurrency,
        metadata={
            "provider": provider,
            "responder_model": llm_model,
            "judge_model": eval_model,
            "prompt": prompt_name,
            "source": "run_experiment.py",
        },
    )

    # Resumo agregado (mesma lógica de aprovação do evaluate.py)
    print("\n" + "=" * 70)
    print("RESUMO AGREGADO")
    print("=" * 70)

    try:
        import statistics as st
        df = results.to_pandas()
        metric_cols = {
            "helpfulness": None, "correctness": None,
            "f1_score": None, "clarity": None, "precision": None,
        }
        # nomes de colunas no pandas vêm como "feedback.<key>"
        for key in list(metric_cols.keys()):
            col = f"feedback.{key}"
            if col in df.columns:
                metric_cols[key] = round(float(df[col].mean()), 4)

        all_ok = True
        for key, val in metric_cols.items():
            if val is None:
                print(f"  - {key:<12}: (sem dados)")
                all_ok = False
                continue
            ok = val >= 0.9
            all_ok = all_ok and ok
            print(f"  - {key:<12}: {val:.4f} {'✓' if ok else '✗'}")

        vals = [v for v in metric_cols.values() if v is not None]
        if vals:
            print(f"\n  MÉDIA GERAL: {sum(vals)/len(vals):.4f}")
        print("\n" + ("✅ APROVADO — todas as métricas ≥ 0.9" if all_ok
                       else "❌ REPROVADO — alguma métrica < 0.9"))
    except Exception as e:
        print(f"(não consegui agregar via pandas: {e})")

    print("\n" + "=" * 70)
    print("✓ Experiment registrado no LangSmith.")
    print(f"  Abra: Datasets & Experiments -> {dataset_name} -> aba Experiments")
    print("  (ou veja o link impresso pelo evaluate() acima).")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
