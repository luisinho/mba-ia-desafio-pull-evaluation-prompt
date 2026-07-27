"""
Testes automatizados para validação de prompts.
"""
import sys
import yaml
import pytest
from pathlib import Path
from typing import Any, Dict

# Adicionar src ao path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from utils import validate_prompt_structure

PROMPT_V2_PATH = BASE_DIR / "prompts" / "bug_to_user_story_v2.yml"

def load_prompt(file_path: Path) -> Dict[str, Any]:
    """Carrega os dados de um arquivo YAML."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Arquivo de prompt não encontrado: {file_path}"
        )

    with file_path.open("r", encoding="utf-8") as file:
        prompt_data = yaml.safe_load(file)

    if not isinstance(prompt_data, dict):
        raise ValueError(
            f"O conteúdo do arquivo não é um objeto YAML válido: {file_path}"
        )

    return prompt_data

def get_system_prompt(prompt_data: dict) -> str:
        """Extrai o texto do SystemMessagePromptTemplate."""

        messages = prompt_data.get("kwargs", {}).get("messages", [])

        for message in messages:
            if not isinstance(message, dict):
                continue

            message_id = message.get("id", [])

            if "SystemMessagePromptTemplate" in message_id:
                return (
                    message
                    .get("kwargs", {})
                    .get("prompt", {})
                    .get("kwargs", {})
                    .get("template", "")
                )

        return ""

def get_metadata(prompt_data: dict) -> dict:
    """Retorna o metadata do ChatPromptTemplate."""

    return (
        prompt_data
        .get("kwargs", {})
        .get("metadata", {})
    )

class TestPrompts:

    def test_prompt_has_system_prompt(self):
        """Verifica se existe um System Prompt e se ele não está vazio."""

        prompt_data = load_prompt(PROMPT_V2_PATH)

        system_prompt = get_system_prompt(prompt_data)

        assert isinstance(system_prompt, str), (
            "O conteúdo do System Prompt deve ser uma string"
        )

        assert system_prompt.strip(), (
            "SystemMessagePromptTemplate não encontrado ou vazio "
            "em bug_to_user_story_v2.yml"
        ) 

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""

        prompt_data = load_prompt(PROMPT_V2_PATH)

        system_prompt = get_system_prompt(prompt_data)

        expected_role = "Você é um Product owner Sênior"

        assert expected_role.casefold() in system_prompt.casefold()       

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""

        prompt_data = load_prompt(PROMPT_V2_PATH)

        system_prompt = get_system_prompt(prompt_data)

        assert (
            "user story" in system_prompt.lower()
            or "como um" in system_prompt.lower()
        )    

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""

        prompt_data = load_prompt(PROMPT_V2_PATH)

        system_prompt = get_system_prompt(prompt_data)

        assert "exemplo" in system_prompt.lower()
        assert "relato de bug" in system_prompt.lower()
        assert "saída esperada" in system_prompt.lower()        

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""

        prompt_data = load_prompt(PROMPT_V2_PATH)

        system_prompt = get_system_prompt(prompt_data)

        assert "TODO" not in system_prompt     

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""

        prompt_data = load_prompt(PROMPT_V2_PATH)

        metadata = get_metadata(prompt_data)

        techniques = metadata.get("techniques", [0])

        if len(techniques) < 3:
            pytest.fail("Erro ao validar metadados techniques")

        assert "Few-shot Learning" in techniques[0]
        assert "Role Prompting" in techniques[1]

    def test_validate_prompt_structure(self):
        """Verifica a estrutura do prompt usando o validador fornecido."""

        prompt_data = load_prompt(PROMPT_V2_PATH)

        system_prompt = get_system_prompt(prompt_data)
        metadata = get_metadata(prompt_data)

        validation_data = {
            "description": metadata.get("description", ""),
            "system_prompt": system_prompt,
            "version": metadata.get("version", ""),
            "techniques_applied": metadata.get("techniques", []),
        }

        is_valid, errors = validate_prompt_structure(validation_data)

        assert is_valid, (
            "A estrutura de bug_to_user_story_v2.yml é inválida:\n"
            + "\n".join(f"- {error}" for error in errors)
        )

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])