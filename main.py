# Main file, based on autogen-magnetic-one examples
import asyncio
import logging

from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.application.logging import EVENT_LOGGER_NAME
from autogen_core.base import AgentId, AgentProxy
from autogen_core.components.code_executor import CodeBlock

from autogen_magentic_one.agents.orchestrator import LedgerOrchestrator
from autogen_magentic_one.agents.user_proxy import UserProxy
from autogen_magentic_one.messages import RequestReplyMessage
from autogen_magentic_one.utils import LogHandler

from file_manager.file_manager import FileManager
from utils import create_completion_client_from_env

async def confirm_code(code: CodeBlock) -> bool:
    response = await asyncio.to_thread(
        input,
        f"Executor is about to execute code (lang: {code.language}):\n{code.code}\n\nDo you want to proceed? (yes/no): ",
    )
    return response.lower() == "yes"

async def main():
    runtime = SingleThreadedAgentRuntime()

    # Create a model client
    client = create_completion_client_from_env()

    # Register agents
    await FileManager.register(runtime, "FileManager", lambda: FileManager(model_client=client))
    file_manager = AgentProxy(AgentId("FileManager", "default"), runtime)

    await UserProxy.register(runtime, "UserProxy", lambda: UserProxy())
    user_proxy = AgentProxy(AgentId("UserProxy", "default"), runtime)

    # Register the LedgerOrchestrator
    await LedgerOrchestrator.register(
        runtime,
        "orchestrator",
        lambda: LedgerOrchestrator(
            agents=[file_manager], # coder, executor, user_proxy
            model_client=client,
            max_rounds=50,
            description="Ledger-based task orchestrator",
        ),
    )

    # Start the runtime
    runtime.start()

    # Send a task to the orchestrator via the user proxy
    await runtime.send_message(RequestReplyMessage(), user_proxy.id)

    # Stop when the orchestrator is idle
    await runtime.stop_when_idle()

if __name__ == "__main__":
    logger = logging.getLogger(EVENT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    log_handler = LogHandler()
    logger.handlers = [log_handler]
    asyncio.run(main())