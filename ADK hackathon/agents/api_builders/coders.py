import os
import subprocess
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent

CODE_GENERATION_DESCRIPTION = """
This agent transforms a validated OpenAPI specification into functional code by generating server-side API stubs and 
client SDKs for specified languages. It automates boilerplate code creation and commits the generated assets to version 
control.
"""

OPENAPI_SAVER_INSTRUCTIONS = """
Read state["current_definition"] and save this OpenAPI definition using the tool `save_yaml_file`. If the operation was 
successful, save the file path returned in state["openapi_yaml_file"].
"""

STUB_GENERATION_INSTRUCTIONS = """
Read state["current_definition"] and state["openapi_yaml_file"] and extract the api_name and api_version.
Then call 'generate_server_stub' tool using spec_file_path from input, using python-fastapi generation_framework.
"""

SDK_GENERATION_INSTRUCTIONS = """
Read state["current_definition"] and state["openapi_yaml_file"] and extract the api_name and api_version.
Then Call 'generate_client_sdk' tool using spec_file_path from input with go, java, python, and ruby as generation_framework.
"""

DOCUMENTATION_GENERATION_INSTRUCTIONS = """
Read state["current_definition"] and state["openapi_yaml_file"] and extract the api_name and api_version.
Then call 'generate_documentation' tool using spec_file_path using html2 as generation_framework.
"""

def save_yaml_file(openapi_definition: str, api_name: str) -> str:
    """Saves content to a file.

    Parameters:
        openapi_definition (str): OpenAPI YAML specification.
        api_name (str): The name of the API.

    Returns:
        str: URL of the saved file.
    """
    path = os.path.join(os.getenv('API_REQUIREMENTS_PATH'), api_name)
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, "swagger.yaml")
    with open(file_path, "w") as f:
        f.write(openapi_definition)
    return file_path

def _generate_openapi_component(component: str, spec_file_path: str, generation_framework: str, api_name: str, api_version: str) -> dict:
    output_directory = f"{api_name}_{component}_{generation_framework}_v{api_version}".lower().replace(' ', '_').replace('-', '_')

    try:
        command = [
            os.getenv("OPENAPI_COMMAND", "openapi-generator-cli"), "generate",
            "-i", spec_file_path,
            "-g", generation_framework,
            "-o", f"{os.getenv('API_REQUIREMENTS_PATH')}/{output_directory}"
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        # print(f"OpenAPI Generator Output:\n{result.stdout}")
        # print(f"OpenAPI Generator Errors (if any):\n{result.stderr}")

        return {
            'status': 'success',
            'path': output_directory,
            'message': f"{component} for {generation_framework} generated successfully in {output_directory}"
        }
    except subprocess.CalledProcessError as e:
        return {
            'status': 'error',
            'message': f"Failed to generate {component}: {e.stderr}",
            'details': str(e)
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f"An unexpected error occurred: {str(e)}"
        }

def generate_server_stub(spec_file_path: str, generation_framework: str, api_name: str, api_version: str) -> dict:
    """Generates a server stub from an OpenAPI specification using openapi-generator-cli.

    Args:
        spec_file_path (str): The path to the OpenAPI YAML file.
        generation_framework (str): The target stub language (e.g., "python", "java", "typescript-angular", "go").
        api_name (str): The name of the API.
        api_version (str): The target API version.

    Returns:
        dict: A dictionary indicating success/failure and the path to the generated code.
              Example: {'status': 'success', 'path': '/path/to/client_sdk', 'message': '...'}
                       {'status': 'error', 'message': '...', 'details': '...'}
    """
    return _generate_openapi_component("server-stub", spec_file_path, generation_framework, api_name, api_version)

def generate_client_sdk(spec_file_path: str, generation_framework: str, api_name: str, api_version: str) -> dict:
    """Generates a client-side SDK from an OpenAPI specification using openapi-generator-cli.

    Args:
        spec_file_path (str): The path to the OpenAPI YAML file.
        generation_framework (str): The target client language (e.g., "python-flask", "spring", "go-server", "scalatra").
        api_name (str): The name of the API.
        api_version (str): The target API version.

    Returns:
        dict: A dictionary indicating success/failure and the path to the generated code.
              Example: {'status': 'success', 'path': '/path/to/client_sdk', 'message': '...'}
                       {'status': 'error', 'message': '...', 'details': '...'}
    """
    return _generate_openapi_component("client-sdk", spec_file_path, generation_framework, api_name, api_version)

def generate_documentation(spec_file_path: str, generation_framework: str, api_name: str, api_version: str):
    """Generates a documentation from an OpenAPI specification using openapi-generator-cli.

        Args:
            spec_file_path (str): The path to the OpenAPI YAML file.
            generation_framework (str): The target docs language (e.g., "html2", "markdown", "cwiki", "dynamic-html").
            api_name (str): The name of the API.
            api_version (str): The target API version.

        Returns:
            dict: A dictionary indicating success/failure and the path to the generated code.
                  Example: {'status': 'success', 'path': '/path/to/client_sdk', 'message': '...'}
                           {'status': 'error', 'message': '...', 'details': '...'}
        """
    return _generate_openapi_component("documentation", spec_file_path, generation_framework, api_name, api_version)


class CodeGenerationAgent:
    @staticmethod
    def get_agent():
        saver = LlmAgent(
            name="openapi_saver",
            model=os.getenv("LLM_MODEL"),
            instruction=OPENAPI_SAVER_INSTRUCTIONS,
            tools=[save_yaml_file],
            output_key="openapi_yaml_file"
        )
        stub_generator = LlmAgent(
            name="openapi_stub_generator",
            model=os.getenv("LLM_MODEL"),
            instruction=STUB_GENERATION_INSTRUCTIONS,
            tools=[generate_server_stub],
            output_key="stub_directory"
        )
        sdk_generator = LlmAgent(
            name="openapi_sdk_generator",
            model=os.getenv("LLM_MODEL"),
            instruction=SDK_GENERATION_INSTRUCTIONS,
            tools=[generate_client_sdk],
            output_key="sdk_directories"
        )
        docs_generator = LlmAgent(
            name="openapi_docs_generator",
            model=os.getenv("LLM_MODEL"),
            instruction=DOCUMENTATION_GENERATION_INSTRUCTIONS,
            tools=[generate_documentation],
            output_key="docs_directory"
        )
        commit_code= LlmAgent(
            name="commit_code_generator",
            model=os.getenv("LLM_MODEL"),
            instruction="Read the state and make a summary with the location of the OpenAPI resources",
            tools=[],
            output_key="result"
        )

        return SequentialAgent(
            name="openapi_generator",
            sub_agents=[
                saver,
                ParallelAgent(
                    name="openapi_components_generator",
                    sub_agents=[
                        stub_generator,
                        sdk_generator,
                        docs_generator,
                    ]
                ),
                commit_code
            ],
        )