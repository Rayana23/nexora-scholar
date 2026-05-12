import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import ListSortOrder

load_dotenv()


def get_agents_client() -> AgentsClient:
    endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")

    if not endpoint:
        raise ValueError("Missing FOUNDRY_PROJECT_ENDPOINT in .env")

    return AgentsClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )


def _extract_latest_assistant_text(messages) -> str:
    assistant_outputs = []

    for message in messages:
        if message.role == "assistant" and message.text_messages:
            assistant_outputs.append(message.text_messages[-1].text.value)

    if not assistant_outputs:
        return "No assistant response was returned."

    return assistant_outputs[-1]


def call_foundry_agent(agent_id: str, user_input: str) -> str:
    if not agent_id:
        raise ValueError("Missing agent ID. Check your .env file.")

    agents_client = get_agents_client()

    thread = agents_client.threads.create()

    agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input,
    )

    run = agents_client.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent_id,
    )

    if run.status == "failed":
        error_text = str(run.last_error) if run.last_error else "Unknown error"
        raise RuntimeError(f"Agent run failed: {error_text}")

    messages = agents_client.messages.list(
        thread_id=thread.id,
        order=ListSortOrder.ASCENDING,
    )

    return _extract_latest_assistant_text(messages)


def run_scheduler_agent(payload: str) -> str:
    return call_foundry_agent(os.getenv("SCHEDULER_AGENT_ID"), payload)


def run_trainer_agent(payload: str) -> str:
    return call_foundry_agent(os.getenv("TRAINER_AGENT_ID"), payload)


def run_dietician_agent(payload: str) -> str:
    return call_foundry_agent(os.getenv("DIETICIAN_AGENT_ID"), payload)