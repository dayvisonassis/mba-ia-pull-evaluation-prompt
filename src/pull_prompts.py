"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt de baixa qualidade publicado no Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

Usa a serialização nativa do LangChain (hub.pull) para extrair o prompt.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

# Prompt de baixa qualidade publicado no Hub (fonte fixa do desafio).
SOURCE_PROMPT = "leonanluppi/bug_to_user_story_v1"

# Caminho de saída (conforme o README).
OUTPUT_PATH = str(Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v1.yml")


def _extract_messages(prompt) -> dict:
    """
    Extrai os templates de system e human de um ChatPromptTemplate retornado
    pelo Hub. Tolerante a diferentes formatos de mensagem.

    Returns:
        dict com as chaves "system_prompt" e "user_prompt" (strings).
    """
    system_prompt = ""
    user_prompt = ""

    messages = getattr(prompt, "messages", None) or []

    for message in messages:
        # Cada item costuma ser um *MessagePromptTemplate com .prompt.template,
        # mas pode ser uma tupla (role, template) ou já uma mensagem concreta.
        template = ""
        inner = getattr(message, "prompt", None)
        if inner is not None and hasattr(inner, "template"):
            template = inner.template
        elif hasattr(message, "content"):
            template = message.content
        elif isinstance(message, (tuple, list)) and len(message) == 2:
            template = message[1]

        role = (
            getattr(message, "type", "")
            or getattr(message, "role", "")
            or (message[0] if isinstance(message, (tuple, list)) else "")
        )
        role = str(role).lower()

        if "system" in role:
            system_prompt = template
        elif "human" in role or "user" in role:
            user_prompt = template
        elif not system_prompt:
            # Fallback: se não há papel identificável, assume system.
            system_prompt = template

    # Prompt de texto simples (PromptTemplate, sem mensagens).
    if not system_prompt and not user_prompt and hasattr(prompt, "template"):
        system_prompt = prompt.template

    return {"system_prompt": system_prompt, "user_prompt": user_prompt or "{bug_report}"}


def pull_prompts_from_langsmith() -> bool:
    """
    Faz pull do prompt do LangSmith Hub e salva localmente em YAML.

    Returns:
        True se sucesso, False caso contrário.
    """
    print(f"Fazendo pull do prompt: {SOURCE_PROMPT}")

    try:
        prompt = hub.pull(SOURCE_PROMPT)
        print("   ✓ Prompt carregado do Hub")
    except Exception as e:
        print(f"   ❌ Erro ao fazer pull do Hub: {e}")
        print("\nVerifique:")
        print("- LANGSMITH_API_KEY está configurada corretamente no .env")
        print("- Sua conexão com a internet está funcionando")
        print(f"- O prompt '{SOURCE_PROMPT}' existe e está público")
        return False

    extracted = _extract_messages(prompt)

    # Monta a estrutura aninhada (mesmo formato do arquivo original v1).
    data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories (pull do LangSmith Hub)",
            "system_prompt": extracted["system_prompt"],
            "user_prompt": extracted["user_prompt"],
            "version": "v1",
            "created_at": "2025-01-15",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    if save_yaml(data, OUTPUT_PATH):
        print(f"   ✓ Prompt salvo em: {OUTPUT_PATH}")
        return True

    print("   ❌ Falha ao salvar o prompt localmente")
    return False


def main() -> int:
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    success = pull_prompts_from_langsmith()

    if success:
        print("\n✅ Pull concluído com sucesso.")
        print("\nPróximos passos:")
        print("1. Analise prompts/bug_to_user_story_v1.yml")
        print("2. Refine prompts/bug_to_user_story_v2.yml")
        print("3. Faça push: python src/push_prompts.py")
        return 0

    print("\n❌ Pull falhou. Verifique as mensagens acima.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
