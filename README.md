# A2A education - Philantropy Agent

An educational A2A demo that helps people learning how the A2A protocol works.

Here is what this live Demo does:

The client sends a text message, the server always completes a **task** with a thank-you **status message** and a **structured artifact** (ETH + BTC addresses).

## How they work together

1. The server advertises itself with an **AgentCard** at `{BASE_URL}/.well-known/agent-card.json` (locally `http://localhost:8001`).
2. The client fetches that card, then opens an A2A client on the advertised interface.
3. The client sends a `SendMessageRequest` with a user `Message` (CLI args joined into one string, or empty).
4. The server’s executor reads the text (or `(empty)`), builds a completed `Task`, and returns:
   - **status message** — thanks you, repeats what you sent, and points at the artifact
   - **artifact** `wallet_addresses` — a JSON dict `{ "ETH": "...", "BTC": "..." }` (constants in `A2A/server.py`)
5. The client prints the status text and the artifact payload.

```
client.py  --discover AgentCard-->  server.py
           --SendMessage--------->
           <--completed Task------  (status message + artifact)
```

## Setup

Once from the repo root (creates `.venv` and installs dependencies):

```bash
uv sync
```

`uv run` always uses this project's `.venv`. You do not need to `source .venv/bin/activate`.
If an old `.venv` is running type this command in terminal first: `deactivate`.

## Run

From the repo root. Server:

```bash
uv run python A2A/server.py
```

Client (another terminal), with text or without — same reply shape:

```bash
uv run python A2A/client.py Hello from A2A
uv run python A2A/client.py
```

Against the live demo at [learn-a2a.com](https://learn-a2a.com) (no local server needed):

```bash
A2A_URL=https://learn-a2a.com uv run python A2A/client.py Hello from A2A
```

## License

Source-available for **personal learning** only. You may clone, run locally, and study the code. You may **not** republish this demo (including swapping the donation addresses) as your own public site. See [LICENSE](LICENSE).
