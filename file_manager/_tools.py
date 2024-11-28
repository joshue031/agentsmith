# File manager tools definitions
from autogen_core.components.tools import ParametersSchema, ToolSchema

TOOL_LS = ToolSchema(
    name="list_files",
    description="List all files and directories in the current working directory.",
)

TOOL_MKDIR = ToolSchema(
    name="make_directory",
    description="Create a new directory in the current working directory.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "directory_name": {
                "type": "string",
                "description": "The name of the new directory to create.",
            },
        },
        required=["directory_name"],
    ),
)

TOOL_CD = ToolSchema(
    name="change_directory",
    description="Change the current working directory.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "path": {
                "type": "string",
                "description": "The relative or absolute path to change to.",
            },
        },
        required=["path"],
    ),
)

TOOL_CAT = ToolSchema(
    name="read_file",
    description="Read the contents of a text file.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "file_path": {
                "type": "string",
                "description": "The relative or absolute path of the file to read.",
            },
        },
        required=["file_path"],
    ),
)

TOOL_WRITE = ToolSchema(
    name="write_file",
    description="Write content to a file. Creates the file if it does not exist.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "file_path": {
                "type": "string",
                "description": "The relative or absolute path of the file to write to.",
            },
            "content": {
                "type": "string",
                "description": "The content to write to the file.",
            },
        },
        required=["file_path", "content"],
    ),
)