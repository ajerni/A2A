"""Minimal A2A client.

    uv run python A2A/client.py
    uv run python A2A/client.py Hello from A2A

    or

    A2A_URL=https://learn-a2a.com uv run python A2A/client.py Hello from A2A
"""

import asyncio
import json
import os
import sys

import httpx
from google.protobuf.json_format import MessageToDict

from a2a.client import ClientConfig, create_client
from a2a.client.card_resolver import A2ACardResolver
from a2a.helpers import get_message_text, new_text_message
from a2a.types import Role, SendMessageRequest

BASE_URL = os.environ.get("A2A_URL", "http://localhost:8001")


async def main() -> None:
    text = " ".join(sys.argv[1:])

    async with httpx.AsyncClient(timeout=30) as http:
        card = await A2ACardResolver(http, BASE_URL).get_agent_card()
        client = await create_client(
            card,
            client_config=ClientConfig(
                supported_protocol_bindings=[
                    card.supported_interfaces[0].protocol_binding
                ],
                httpx_client=http,
                streaming=False,
                polling=False,
            ),
        )

        try:
            request = SendMessageRequest(
                message=new_text_message(text=text, role=Role.ROLE_USER)
            )
            async for reply in client.send_message(request):
                task = reply.task if reply.HasField("task") else reply

                if task.status.HasField("message"):
                    print(get_message_text(task.status.message))

                for artifact in task.artifacts:
                    print(f"\nartifact={artifact.name}")
                    for part in artifact.parts:
                        if part.HasField("data"):
                            print(
                                json.dumps(
                                    MessageToDict(part.data),
                                    ensure_ascii=False,
                                    indent=2,
                                )
                            )
                break
        finally:
            await client.close()


if __name__ == "__main__":
    asyncio.run(main())
