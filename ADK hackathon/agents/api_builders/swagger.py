import json
import os
from typing import AsyncGenerator

import yaml
from google.adk.agents import LlmAgent, BaseAgent, LoopAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from openapi_spec_validator import validate
from openapi_spec_validator.validation.exceptions import OpenAPIValidationError


def validate_openapi_spec(openapi_definition: str) -> dict:
    """Validates an OpenAPI specification.

    Parameters:
        openapi_definition (str): OpenAPI YAML specification.

    Returns:
        dict: A dictionary with a status key ('success' or 'error') and a message key (validation result or error details).
    """
    try:
        validate(yaml.safe_load(openapi_definition))
        return {"status": "valid", "message": "It is a valid OpenAPI Specification"}
    except OpenAPIValidationError as e:
        return {"status": "invalid", "message": f"It is NOT a valid OpenAPI Specification: {e}"}
    except yaml.YAMLError as e:
        return {"status": "invalid", "message": f"It is NOT a valid YAML string: {e}"}
    except Exception as e:
        return {"status": "invalid", "message": f"An error occurred while processing Specification: {e}"}


OPENAPI_DEFINITION_DESCRIPTION = """
This agent translates structured API requirements into a valid OpenAPI (Swagger) YAML specification. It includes a 
self-validation step to ensure accuracy before outputting the final, machine-readable API definition.
"""

IMPLEMENTOR_INSTRUCTIONS = """
You are an expert in OpenAPI Specification (OAS/Swagger), version 3.x. Your primary responsibility is to take detailed 
API requirements and accurately translate them into a valid, well-structured OpenAPI YAML definition. 

First, read state['current_definition'] and state['status'] (if they exist) and use this information together with the 
OpenAPI Specification to generate/refine YAML definition in order to follow the specification and fix the errors. Save 
to state['current_definition'].
"""

VALIDATOR_INSTRUCTIONS =  """
Your task is to validate the OpenAPI definition present in the state key 'openapi_definition' using the 
`validate_openapi_spec` tool. Set state['status'] with 'The OpenAPI specification is valid' or 
'The OpenAPI specification is invalid: 'errors message...' depending of tool result, and append at the end of the invalid 
message the reasons of your status.
"""

COMMITER_INSTRUCTIONS = """
Your task is to commit the OpenAPI YAML definition. Read state['current_definition'] and state['status'] (if they exist) 
and if the status is valid, use `save_yaml_file` tool to save the YAML specification.
"""

class OpenAPIDefinitionAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        status = ctx.session.state.get("status", "invalid")
        should_stop = ("is valid" in status.lower())
        yield Event(author=self.name, actions=EventActions(escalate=should_stop))

    @staticmethod
    def get_agent():
        implementor = LlmAgent(
            name="openapi_implementor",
            model=os.getenv("LLM_MODEL"),
            instruction=IMPLEMENTOR_INSTRUCTIONS,
            output_key="current_definition"
        )
        validator = LlmAgent(
            name="openapi_validator",
            model=os.getenv("LLM_MODEL"),
            instruction=VALIDATOR_INSTRUCTIONS,
            output_key="status",
            tools=[validate_openapi_spec]
        )
        return LoopAgent(
            name="openapi_definition_agent",
            max_iterations=5,
            description=OPENAPI_DEFINITION_DESCRIPTION,
            sub_agents=[implementor, validator, OpenAPIDefinitionAgent(name="openapi_checker")],
        )