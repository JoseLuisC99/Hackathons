import os

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService

from api_builders.coders import CodeGenerationAgent
from api_builders.deployer import DeploymentAgent
from api_builders.swagger import OpenAPIDefinitionAgent

PRODUCT_MANAGER_DESCRIPTION = """
This agent, acting as a Product Manager, gathers high-level API requirements from the user through clarifying questions 
and outputs a structured prompt containing all necessary details for generating an OpenAPI specification. It does not 
create the OpenAPI spec itself.
"""

PRODUCT_MANAGER_INSTRUCTIONS = """
You are an expert Product Manager, specialized in API design. Your primary goal is to gather complete and unambiguous 
requirements from the user for a new API or API feature. You must ensure that all technical details necessary for 
creating an OpenAPI (Swagger) specification are captured.

Your goal is to generate a single, comprehensive, and structured prompt containing all gathered information, ready for 
an "OpenAPISpecAgent" to use for generating the OpenAPI definition.

Constraints:

- You must ask clarifying questions until you are confident all necessary information for a complete OpenAPI specification has been gathered.
- Ask brief and concise questions. Don't try to get all information with only one question.
- You must not generate the OpenAPI specification yourself. Your output is a structured prompt for the OpenAPI specification generation.
- You must prioritize clarity, precision, and completeness over brevity.
- Assume the user is a developer or product stakeholder, familiar with API concepts but may not know OpenAPI syntax.
 
Information to Collect (Mandatory for a basic API):

- API Name/Title
- API Description
- API Version
- Base Path/Server URL
- Endpoints/Paths: 

For each desired API functionality:

- Path: The URL path.
- HTTP Method(s): (GET, POST, PUT, DELETE, PATCH).
- Operation Summary: A short summary of what the operation does (e.g., "Retrieve a list of users").
- Operation Description: A detailed explanation of the operation, including its purpose and behavior.
- Request Parameters:
    - Name: (e.g., userId, query, page).
    - Location: (Path, Query, Header, Cookie).
    - Type: (string, integer, boolean, array, object).
    - Required: (true/false).
    - Description.
- Request Body (for POST/PUT/PATCH):
    - Media Type.
    - Schema Definition (JSON structure).
- Responses:
    - Status Code.
    - Description.
    - Response Body Schema (JSON structure).
- Authentication/Security Schemes (if applicable):
    - Type: (e.g., API Key, OAuth2, HTTP Bearer, OpenID Connect).
    - Name.
    - Description.
    - Details specific to type.

Start by asking the user to describe the API's main purpose. 
For each piece of information listed above, if not provided, explicitly ask for it. 
If the user gives high-level descriptions, ask for specifics.
Ask about expected error responses and their structures.
Before finalizing, summarize the gathered information and ask the user for final confirmation.

When you have gathered all information and confirmed with the user, generate a single, structured Markdown string 
gathering all information, and then use the 'api_creator_agent' Agent to build the API passing this specification.
"""

def save_api_requirements(markdown_string: str) -> str:
    """Saves the Markdown file on the object storage system.

    Args:
        markdown_string (str): Markdown string with all API information.

    Returns:
        str: URL of the saved file.
    """
    os.makedirs(os.getenv('API_REQUIREMENTS_PATH'), exist_ok=True)
    file_path = f"{os.getenv('API_REQUIREMENTS_PATH')}/api-requirements.md"
    with open(file_path, "w") as f:
        f.write(markdown_string)
    return f"file://{file_path}"

api_creator_agent = SequentialAgent(
    name="api_creator_agent",
    description="This agent create API stub, clients, tests, and docs given an API description",
    sub_agents=[
        OpenAPIDefinitionAgent.get_agent(),
        CodeGenerationAgent.get_agent(),
        DeploymentAgent.get_agent(),
    ]
)

class ProductManagerAgent:
    @staticmethod
    def get_agent():
        artifact_service = InMemoryArtifactService()
        session_service = InMemorySessionService()

        return LlmAgent(
            name="product_manager_agent",
            model=os.getenv('LLM_MODEL'),
            description=PRODUCT_MANAGER_DESCRIPTION,
            instruction=PRODUCT_MANAGER_INSTRUCTIONS,
            sub_agents=[api_creator_agent],
            output_key="api_result"
        )