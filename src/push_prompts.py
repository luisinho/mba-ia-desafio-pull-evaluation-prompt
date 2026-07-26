"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
# from langchain import hub
from langsmith import Client
from dotenv import load_dotenv
from langchain_core.load import load
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:

    print_section_header("Iniciando push do prompt")

    try:        

        check_env_vars(
            [
              "LANGSMITH_TRACING",
              "LANGSMITH_API_KEY",
              "LANGSMITH_PROJECT"
            ]
        )

        print("Convertendo YAML para ChatPromptTemplate...")

        prompt: ChatPromptTemplate = load(prompt_data)

        if not isinstance(prompt, ChatPromptTemplate):
            print("Objeto carregado não é um ChatPromptTemplate")
            return False
        
        description = """
        Prompt otimizado para transformar relatos de bugs
        em User Stories utilizando técnicas avançadas
        de Prompt Engineering.
        """

        tags = [
            "bug-analysis",
            "user-story",
            "software-development",
            "few-shot-learning",
            "role-prompting",
            "skeleton-of-thought"
        ]

        readme = """
        # Bug To User Story V2

        ## Objetivo

        Transformar relatos técnicos de bugs em User Stories
        prontas para desenvolvimento.

        ## Técnicas utilizadas

        ### Few-shot Learning

        Foram adicionados exemplos completos de entrada e saída
        para ensinar o padrão esperado.


        ### Role Prompting

        O modelo assume o papel de Product Owner Sênior.


        ### Skeleton of Thought

        A transformação segue etapas internas:

        1. Identificar usuário.
        2. Identificar problema.
        3. Identificar objetivo.
        4. Identificar benefício.
        5. Criar User Story.
        6. Criar critérios de aceitação.

        ## Formato de saída

        User Story:

        Como [usuário],
        eu quero [objetivo],
        para que [benefício].

        Critérios de Aceitação:

        - Dado que...
        - Quando...
        - Então...
        - E...
        """


        print("Enviando prompt para LangSmith Hub...")


        # url = hub.push(
        #    repo_full_name=prompt_name,
        #    object=prompt,
        #    new_repo_is_public=True,
        #    new_repo_description=description,
        #    readme=readme,
        #    tags=tags
        # )

        client = Client()

        url = client.push_prompt(
            prompt_identifier=prompt_name,
            object=prompt,
            is_public=True,
            description=description,
            readme=readme,
            tags=tags,
            commit_description=(
                "Versão 2 otimizada com Few-shot Learning, "
                "Role Prompting e Skeleton of Thought."
            )
        )

        print("Prompt enviado com sucesso!")
        print(f"URL: {url}")

        return True

    except Exception as e:

        print(f"Erro ao fazer push do prompt: {e}")

        return False    


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:    

    errors = []

    try:

        if not isinstance(prompt_data, dict):
            errors.append("Prompt deve ser um objeto YAML válido.")
            return False, errors        

        required_root_fields = [
            "lc",
            "type",
            "id",
            "kwargs"
        ]

        for field in required_root_fields:
            if field not in prompt_data:
                errors.append(
                    f"Campo obrigatório ausente no prompt: '{field}'"
                )

        if errors:
            return False, errors

        kwargs = prompt_data.get("kwargs", {})

        if not isinstance(kwargs, dict):
            errors.append(
                "Campo 'kwargs' deve ser um objeto."
            )
            return False, errors

        input_variables = kwargs.get(
            "input_variables",
            []
        )

        if "bug_report" not in input_variables:
            errors.append(
                "Variável obrigatória 'bug_report' não encontrada em input_variables."
            )        

        messages = kwargs.get("messages")

        if not messages:
            errors.append(
                "Campo 'messages' não encontrado ou vazio."
            )

            return False, errors


        if not isinstance(messages, list):
            errors.append(
                "Campo 'messages' deve ser uma lista."
            )

            return False, errors

        system_found = False
        human_found = False

        templates = []

        for message in messages:

            if not isinstance(message, dict):
                continue

            message_id = message.get("id", [])

            if "SystemMessagePromptTemplate" in message_id:
                system_found = True


            if "HumanMessagePromptTemplate" in message_id:
                human_found = True

            try:

                template = (
                    message
                    .get("kwargs", {})
                    .get("prompt", {})
                    .get("kwargs", {})
                    .get("template", "")
                )

                if template:
                    templates.append(template)

            except Exception:
                pass

        if not system_found:
            errors.append(
                "SystemMessagePromptTemplate não encontrado."
            )

        if not human_found:
            errors.append(
                "HumanMessagePromptTemplate não encontrado."
            )        

        complete_template = "\n".join(templates)

        if "{bug_report}" not in complete_template:
            errors.append(
                "O prompt não possui o placeholder {bug_report}."
            )        

        required_techniques = [
            "Few-shot Learning",
            "Role Prompting",
            "Skeleton of Thought"
        ]

        for technique in required_techniques:

            if technique.lower() not in complete_template.lower():

                errors.append(
                    f"Técnica obrigatória não encontrada: {technique}"
                )        

        metadata = kwargs.get(
            "metadata",
            {}
        )

        if metadata:

            techniques_metadata = metadata.get(
                "techniques",
                []
            )

            for technique in required_techniques:

                if technique not in techniques_metadata:

                    errors.append(
                        f"Técnica '{technique}' ausente nos metadados."
                    )

        else:

            errors.append(
                "Metadata do prompt não encontrada."
            )

        return len(errors) == 0, errors

    except Exception as e:

        errors.append(
            f"Erro inesperado na validação do prompt: {e}"
        )

        return False, errors

def load_prompt_v2() -> dict:
    
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
                f"Arquivo do prompt não encontrado: {file_path}"
            )

            return None


        print(
            f"Carregando prompt: {file_path}"
        )


        prompt_data = load_yaml(
            str(file_path)
        )


        if not prompt_data:

            print("Não foi possível carregar o conteúdo do prompt.")

            return None


        return prompt_data


    except Exception as e:

        print(
            f"Erro ao carregar prompt: {e}"
        )

        return None

def main():
    
    try:
         
        prompt_data = load_prompt_v2()


        if not prompt_data:

            return 1
        
        is_valid, errors = validate_prompt(prompt_data)

        if not is_valid:

            print("\n Prompt inválido:")

            for error in errors:
                    print(
                        f"   - {error}"
                    )

            return 1
        
        print("Prompt validado com sucesso.")

        prompt_name = (f"{os.getenv('USERNAME_LANGSMITH_HUB')}/bug_to_user_story_v2")

        if push_prompt_to_langsmith(prompt_name, prompt_data):
            print("Push realizado com sucesso.")
            return 0

        print("Erro no push do prompt.")
        return 1
    
    except Exception as e:

        print(f"Erro inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())