"""Dynamic agent that reads system prompt from database."""

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.func import entrypoint

from ai_agents.repository import get_default_agent
from core import get_model, settings


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
    """
    messages = inputs["messages"]
    if previous:
        messages = previous["messages"] + messages

    # Fetch default AI agent configuration from database
    agent_config = await get_default_agent()

    if agent_config:
        # Prepend system message with the configured prompt
        system_message = SystemMessage(content=agent_config.system_prompt)
        messages_with_system = [system_message] + messages

        # Use the model configured in the agent, or fallback to config/default
        model_name = config["configurable"].get("model", agent_config.model)
    else:
        # Fallback if no agent is configured
        messages_with_system = messages
        model_name = config["configurable"].get("model", settings.DEFAULT_MODEL)

    model = get_model(model_name)
    response = await model.ainvoke(messages_with_system)

    # Save messages without system prompt to avoid duplication in history
    return entrypoint.final(
        value={"messages": [response]}, save={"messages": messages + [response]}
    )
