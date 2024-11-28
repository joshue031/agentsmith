# File manager
import json
import os
from typing import List

from autogen_core.base import CancellationToken
from autogen_core.components import FunctionCall, default_subscription
from autogen_core.components.models import (
    ChatCompletionClient,
    SystemMessage,
    UserMessage,
)
from autogen_magentic_one.agents.base_worker import BaseWorker

from ._tools import *

@default_subscription
class FileManager(BaseWorker):
    """An agent that interacts with the file system to perform basic file operations."""

    DEFAULT_DESCRIPTION = "An agent that can handle file operations in the local file system."

    DEFAULT_SYSTEM_MESSAGES = [
        SystemMessage("""
        You are a helpful AI Assistant that performs file system operations.
        Use available tools to help the user with their file management requests."""),
    ]

    def __init__(
        self,
        model_client: ChatCompletionClient,
        description: str = DEFAULT_DESCRIPTION,
        system_messages: List[SystemMessage] = DEFAULT_SYSTEM_MESSAGES,
    ) -> None:
        super().__init__(description)
        self._model_client = model_client
        self._system_messages = system_messages
        self._tools = [TOOL_LS, TOOL_MKDIR, TOOL_CD, TOOL_CAT, TOOL_WRITE]

    async def _generate_reply(self, cancellation_token: CancellationToken):
        history = self._chat_history[0:-1]
        last_message = self._chat_history[-1]
        assert isinstance(last_message, UserMessage)

        task_content = last_message.content

        create_result = await self._model_client.create(
            messages=history + [last_message], tools=self._tools, cancellation_token=cancellation_token
        )

        response = create_result.content

        if isinstance(response, str):
            return False, response

        elif isinstance(response, list) and all(isinstance(item, FunctionCall) for item in response):
            function_calls = response
            for function_call in function_calls:
                tool_name = function_call.name

                try:
                    arguments = json.loads(function_call.arguments)
                except json.JSONDecodeError as e:
                    error_str = f"File Manager encountered an error decoding JSON arguments: {e}"
                    return False, error_str

                if tool_name == "list_files":
                    try:
                        response = os.listdir(".")
                        response = f"Files in current directory: {response}"
                    except Exception as e:
                        response = f"Error listing files: {e}"
                elif tool_name == "make_directory":
                    try:
                        os.mkdir(arguments["directory_name"])
                        response = f"Directory '{arguments['directory_name']}' created."
                    except FileExistsError:
                        response = f"Error: Directory '{arguments['directory_name']}' already exists."
                    except Exception as e:
                        response = f"Error creating directory '{arguments['directory_name']}': {e}"
                elif tool_name == "change_directory":
                    try:
                        os.chdir(arguments["path"])
                        response = f"Changed directory to '{arguments['path']}'."
                    except FileNotFoundError:
                        response = f"Error: Directory '{arguments['path']}' does not exist."
                    except Exception as e:
                        response = f"Error changing directory to '{arguments['path']}': {e}"
                elif tool_name == "read_file":
                    try:
                        with open(arguments["file_path"], "r") as file:
                            file_content = file.read()
                        response = f"Successfully read file '{arguments['file_path']}' containing content:\n{file_content}"
                    except FileNotFoundError:
                        response = f"Error: File '{arguments['file_path']}' does not exist."
                    except Exception as e:
                        response = f"Error reading file '{arguments['file_path']}': {e}"
                elif tool_name == "write_file":
                    try:
                        with open(arguments["file_path"], "w") as file:
                            file.write(arguments["content"])
                        response = f"Content written to '{arguments['file_path']}'."
                    except Exception as e:
                        response = f"Error writing to file '{arguments['file_path']}': {e}"


            return False, response

        return False, "Command execution failed."