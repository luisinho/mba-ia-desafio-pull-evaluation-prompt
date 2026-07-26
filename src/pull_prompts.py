"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import sys
from pathlib import Path
from langsmith import Client
from dotenv import load_dotenv
from langchain_core.load.dump import dumpd
from langchain_core.prompts import ChatPromptTemplate
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

def pull_prompts_from_langsmith():

    print_section_header("Iniciando pull do prompt")

    try:

        base_dir = Path(__file__).resolve().parent.parent

        prompts_dir = base_dir / "prompts"

        prompts_dir.mkdir(parents=True, exist_ok=True)

        file_path = prompts_dir / "bug_to_user_story_v1.yml"

        check_env_vars(
            [
              "LANGSMITH_TRACING",
              "LANGSMITH_API_KEY",
              "LANGSMITH_PROJECT"
            ]
        )

        client = Client()

        prompt: ChatPromptTemplate = client.pull_prompt("leonanluppi/bug_to_user_story_v1",
                                                        include_model=True, 
                                                        dangerously_pull_public_prompt=True)

        data = dumpd(prompt)

        save_yaml(data, str(file_path))

    except Exception as e:
         print(f"Erro: {e}")
         return

    print("Prompt salvo com sucesso!")

 
def load_prompt_v2() -> dict:
    """
    Carrega o prompt bug_to_user_story_v2.yml.

    Returns:
        dict: Conteúdo do YAML carregado.
        None caso não consiga carregar.
    """

    try:

        base_dir = Path(__file__).resolve().parent.parent

        prompts_dir = base_dir / "prompts"

        prompts_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path = prompts_dir / "bug_to_user_story_v2.yml"


        if not file_path.exists():

            print(
                f"❌ Arquivo do prompt não encontrado: {file_path}"
            )

            return None


        print(
            f"Carregando prompt: {file_path}"
        )


        prompt_data = load_yaml(
            str(file_path)
        )


        if not prompt_data:

            print(
                "❌ Não foi possível carregar o conteúdo do prompt."
            )

            return None


        return prompt_data


    except Exception as e:

        print(
            f"❌ Erro ao carregar prompt: {e}"
        )

        return None   

def main():
    """Função principal"""

    pull_prompts_from_langsmith()

    return 0

if __name__ == "__main__":
    sys.exit(main())