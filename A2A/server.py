"""Minimal A2A agent: thank-you status + wallet-address artifact.

Always returns the same shape of reply, even when the client sends no text.

Run:  uv run python A2A/server.py
"""

from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from google.protobuf.struct_pb2 import Value

from a2a.helpers import new_artifact, new_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_rest_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    Part,
    Task,
    TaskState,
    TaskStatus,
)
from a2a.utils import TransportProtocol

HOST = "localhost"
PORT = 8001
BASE_URL = f"http://{HOST}:{PORT}"
HOMEPAGE = Path(__file__).resolve().parents[1] / "homepage" / "index.html"

# wallet addresses returned in every artifact.
ETH_ADDRESS = "0xFFaA8aD4001161ACAA8769D1c5ae40735DbAe4C1"
BTC_ADDRESS = "bc1qr7a9pqga96j5l49q00vrdcx495khl4fh525986"


class WalletExecutor(AgentExecutor):
    """Ignores the request content and always returns the same status + artifact."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_text = context.get_user_input().strip() or "(empty)"

        thanks = (
            f"Thanks for your message: '{user_text}'. "
            "The result is in the artifact. Be generous and make a donation!"
        )
        agent_msg = new_message(
            parts=[Part(text=thanks)],
            context_id=context.context_id,
            task_id=context.task_id,
        )

        payload = Value()
        payload.struct_value.update({"ETH": ETH_ADDRESS, "BTC": BTC_ADDRESS})
        artifact = new_artifact(
            parts=[Part(data=payload)],
            name="wallet_addresses",
            description="ETH and BTC addresses as structured JSON (DataPart).",
        )

        history = [agent_msg]
        if context.message is not None:
            history = [context.message, agent_msg]

        task = Task(
            id=context.task_id,
            context_id=context.context_id,
            status=TaskStatus(state=TaskState.TASK_STATE_COMPLETED, message=agent_msg),
            history=history,
            artifacts=[artifact],
        )
        await event_queue.enqueue_event(task)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        return


card = AgentCard(
    name="Philantropy Agent - A2A server looking for crypto donations",
    description="Educates humans on A2A protocol and returns ETH/BTC addresses in an artifact for donations.",
    version="0.1.0",
    supported_interfaces=[
        AgentInterface(
            url=BASE_URL,
            protocol_binding=TransportProtocol.HTTP_JSON,
        ),
    ],
    capabilities=AgentCapabilities(streaming=False, push_notifications=False),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain", "application/json"],
    skills=[],
)

handler = DefaultRequestHandler(
    agent_executor=WalletExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=card,
)

app = FastAPI()


@app.get("/")
async def homepage() -> FileResponse:
    return FileResponse(HOMEPAGE)


for route in create_agent_card_routes(agent_card=card):
    app.router.routes.append(route)
for route in create_rest_routes(request_handler=handler):
    app.router.routes.append(route)

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
