"""
Testes automatizados para validação do prompt otimizado (v2).

Estes testes são estáticos: leem apenas o YAML local, sem chamar nenhuma API
ou LLM. Executam com: pytest tests/test_prompts.py
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

# Caminho do prompt otimizado a ser validado.
V2_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt_data():
    """Carrega o prompt otimizado (v2) uma vez por módulo."""
    assert V2_PATH.exists(), f"Arquivo não encontrado: {V2_PATH}"
    return load_prompts(V2_PATH)


@pytest.fixture(scope="module")
def system_prompt(prompt_data):
    """Retorna o texto do system_prompt."""
    return prompt_data.get("system_prompt", "") or ""


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' ausente no YAML"
        assert prompt_data["system_prompt"].strip(), "'system_prompt' está vazio"

    def test_prompt_has_role_definition(self, system_prompt):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        assert "Você é um" in system_prompt, "O prompt não define uma persona com 'Você é um...'"
        assert ("Product Manager" in system_prompt) or ("especialista" in system_prompt.lower()), \
            "A persona não menciona Product Manager / especialista"

    def test_prompt_mentions_format(self, system_prompt):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        assert "User Story" in system_prompt, "O prompt não menciona 'User Story'"
        assert ("Markdown" in system_prompt) or ("Critérios de Aceitação" in system_prompt), \
            "O prompt não exige formato Markdown / User Story padrão"

    def test_prompt_has_few_shot_examples(self, system_prompt):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        assert "EXEMPLO" in system_prompt, "O prompt não contém seção de exemplos (Few-shot)"
        assert system_prompt.count("Como um") >= 2, \
            "São esperados ao menos 2 exemplos de User Story (Few-shot)"

    def test_prompt_no_todos(self, system_prompt, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        assert "TODO" not in system_prompt, "O system_prompt ainda contém TODO"
        assert "[TODO]" not in system_prompt, "O system_prompt ainda contém [TODO]"
        # Garantia extra: a estrutura completa do prompt é válida.
        is_valid, errors = validate_prompt_structure(prompt_data)
        assert is_valid, f"Estrutura do prompt inválida: {errors}"

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get("techniques_applied", [])
        assert isinstance(techniques, list), "'techniques_applied' deve ser uma lista"
        assert len(techniques) >= 2, \
            f"São esperadas ao menos 2 técnicas; encontradas: {len(techniques)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
