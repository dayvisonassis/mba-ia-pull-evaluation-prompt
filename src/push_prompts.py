"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()

# Nome do prompt otimizado (sem prefixo de username; o push usa o handle autenticado).
PROMPT_NAME = "bug_to_user_story_v2"

# Caminho do prompt otimizado.
V2_PATH = str(Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml")


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica do prompt otimizado.

    Reaproveita utils.validate_prompt_structure, que exige os campos
    description / system_prompt / version / techniques_applied (>= 2) e
    garante que o system_prompt não esteja vazio nem contenha TODOs.

    Args:
        prompt_data: Dados do prompt (dict carregado do YAML)

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Monta um ChatPromptTemplate com uma mensagem de sistema (system_prompt) e
    uma mensagem do usuário (user_prompt), garantindo que a única variável de
    template seja {bug_report} — o que o evaluate.py espera ao invocar o prompt.

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    system_prompt = prompt_data.get("system_prompt", "")
    user_prompt = prompt_data.get("user_prompt", "{bug_report}")

    template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", user_prompt),
        ]
    )

    # Guard: o evaluate.py invoca o prompt com inputs = {"bug_report": ...}.
    # Qualquer outra variável (chave { } solta no system_prompt) quebraria a avaliação.
    input_vars = sorted(template.input_variables)
    if input_vars != ["bug_report"]:
        print("   ❌ O prompt tem variáveis de template inesperadas.")
        print(f"      Esperado: ['bug_report'] | Encontrado: {input_vars}")
        print("      Verifique se há chaves { } soltas no system_prompt.")
        return False

    # Metadados: descrição + técnicas aplicadas (também viram tags).
    techniques = prompt_data.get("techniques_applied", [])
    description = prompt_data.get("description", "")
    if techniques:
        description = f"{description} | Técnicas: {', '.join(techniques)}"

    tags = list(prompt_data.get("tags", []))
    for technique in techniques:
        tags.append(f"technique:{technique}")

    # is_public controlável via .env. Em contas sem "Hub handle" criado ainda,
    # o LangSmith não permite push público direto: nesse caso publicamos como
    # privado (o que CRIA o handle do tenant) e o usuário pode torná-lo público
    # depois pela interface web.
    want_public = os.getenv("PROMPT_PUBLIC", "true").strip().lower() in ("1", "true", "yes")

    client = Client()

    def _do_push(is_public: bool):
        return client.push_prompt(
            prompt_name,
            object=template,
            description=description,
            tags=tags,
            is_public=is_public,
        )

    try:
        url = _do_push(want_public)
        visibility = "PÚBLICO" if want_public else "PRIVADO"
        print(f"   ✓ Push concluído ({visibility}): {prompt_name}")
        print(f"   🔗 URL: {url}")
        return True

    except Exception as e:
        msg = str(e)

        # "Nothing to commit" significa que o prompt já está idêntico no Hub.
        if "Nothing to commit" in msg:
            print(f"   ✓ Prompt já está atualizado no Hub (nada a commitar): {prompt_name}")
            return True

        # Conta sem handle público: faz fallback para push privado.
        if want_public and ("handle" in msg.lower() or "public prompt" in msg.lower()):
            print("   ⚠️  A conta ainda não tem um 'Hub handle' público.")
            print("   ↪️  Publicando como PRIVADO (isso cria o handle do tenant).")
            try:
                url = _do_push(False)
                print(f"   ✓ Push concluído (PRIVADO): {prompt_name}")
                print(f"   🔗 URL: {url}")
                print("   ➡️  Abra a URL no LangSmith e clique em 'Make public' para torná-lo público.")
                return True
            except Exception as e2:
                if "Nothing to commit" in str(e2):
                    print(f"   ✓ Prompt já está atualizado no Hub (nada a commitar): {prompt_name}")
                    return True
                print(f"   ❌ Erro ao fazer push privado: {e2}")
                return False

        print(f"   ❌ Erro ao fazer push: {e}")
        print("\nVerifique:")
        print("- LANGSMITH_API_KEY está configurada corretamente no .env")
        print("- Sua conexão com a internet está funcionando")
        return False


def main() -> int:
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS AO LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    prompt_data = load_yaml(V2_PATH)
    if prompt_data is None:
        print(f"❌ Não foi possível carregar o prompt: {V2_PATH}")
        return 1

    print(f"Validando prompt: {V2_PATH}")
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1
    print("   ✓ Prompt válido\n")

    print(f"Fazendo push: {PROMPT_NAME}")
    success = push_prompt_to_langsmith(PROMPT_NAME, prompt_data)

    if success:
        print("\n✅ Push concluído com sucesso.")
        print("\nPróximos passos:")
        print("1. Copie seu username da URL acima (https://smith.langchain.com/hub/<USERNAME>/...)")
        print("2. Defina USERNAME_LANGSMITH_HUB=<USERNAME> no arquivo .env")
        print("3. Confirme que o prompt está público no dashboard do LangSmith")
        print("4. Execute a avaliação: python src/evaluate.py")
        return 0

    print("\n❌ Push falhou. Verifique as mensagens acima.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
