"""Dynamic agent that reads system prompt from database.

Supports @variable template syntax for dynamic content:
- @current_datetime (and variations like .weekday, .time, etc.)
- @model_name
- @thread_id

Context variables (@contact_*, @channel_*, etc.) should be pre-processed
by the caller and passed via config["configurable"]["system_prompt"].
"""

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from langchain_core.runnables import RunnableConfig
from langgraph.func import entrypoint

from agents.template_processor import process_template_variables
from ai_agents.repository import get_default_agent
from core import get_model, settings


def trim_conversation(
    messages: list[BaseMessage],
    max_tokens: int | None = 16000,
    # max_messages: int | None = 50,  # TODO: implement later
) -> list[BaseMessage]:
    """
    Trim conversation history to fit within token limits.

    This prevents timeout issues with long conversations by limiting
    the context sent to the LLM while preserving the full history
    in checkpoints.

    Args:
        messages: Full message history from checkpoint
        max_tokens: Maximum tokens to keep (None = no limit)

    Returns:
        Trimmed message list ready for LLM invocation
    """
    if not messages:
        return messages

    result = messages

    # TODO: Limit by message count (implement later)
    # if max_messages and len(result) > max_messages:
    #     result = result[-max_messages:]

    # Limit by token count using LangChain's trim_messages
    if max_tokens:
        result = trim_messages(
            result,
            strategy="last",  # Keep most recent messages
            token_counter=count_tokens_approximately,
            max_tokens=max_tokens,
            start_on="human",  # Start on user message for coherence
            end_on=("human", "tool"),
            include_system=False,  # System prompt added separately
        )

    return list(result)


@entrypoint()
async def dynamic_agent(
    inputs: dict[str, list[BaseMessage]],
    *,
    previous: dict[str, list[BaseMessage]],
    config: RunnableConfig,
):
    """
    A dynamic agent that fetches its system prompt from the database.

    This agent reads the default AI Agent configuration from the database
    and uses its system_prompt, model, and other settings.

    Features:
    - Message trimming to prevent timeout on long conversations
    - Template variable processing (@current_datetime, @model_name, @thread_id)
    - Support for runtime system_prompt override via config

    Template variables processed:
    - @current_datetime (and .weekday, .time, .date, etc.)
    - @model_name - the LLM model being used
    - @thread_id - the conversation thread ID
    """
    messages = inputs["messages"]
    if previous:
        messages = previous["messages"] + messages

    # Get config values
    thread_id = config["configurable"].get("thread_id", "")

    # Check for runtime system_prompt override (for pre-processed context variables from Core)
    runtime_system_prompt = config["configurable"].get("system_prompt")

    # Fetch default AI agent configuration from database
    agent_config = await get_default_agent()

    if agent_config:
        # Apply memory limits to prevent timeout on long conversations
        trimmed_messages = trim_conversation(
            messages,
            max_tokens=agent_config.max_tokens,
            # max_messages=agent_config.max_messages,  # TODO: implement later
        )

        # Use runtime override if provided, otherwise use database prompt
        base_prompt = runtime_system_prompt or agent_config.system_prompt
        model_name = config["configurable"].get("model", agent_config.model)

        # Process template variables (@current_datetime, @model_name, @thread_id)
        processed_prompt = process_template_variables(
            base_prompt,
            model_name=model_name,
            thread_id=thread_id,
        )

        system_message = SystemMessage(content=processed_prompt)
        messages_with_system = [system_message] + trimmed_messages
    else:
        # Fallback - use default limits
        trimmed_messages = trim_conversation(messages)
        model_name = config["configurable"].get("model", settings.DEFAULT_MODEL)

        if runtime_system_prompt:
            # Process template variables even without agent_config
            processed_prompt = process_template_variables(
                runtime_system_prompt,
                model_name=model_name,
                thread_id=thread_id,
            )
            system_message = SystemMessage(content=processed_prompt)
            messages_with_system = [system_message] + trimmed_messages
        else:
            messages_with_system = trimmed_messages

    model = get_model(model_name)
    response = await model.ainvoke(messages_with_system)

    # Save FULL history (without trimming) to checkpoint for future reference
    return entrypoint.final(
        value={"messages": [response]},
        save={"messages": messages + [response]}
    )
