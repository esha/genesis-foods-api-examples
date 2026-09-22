# Genesis GraphQL subscriptions

`subscribe.py` is an interactive client for the Genesis Foods GraphQL over WebSocket subscriptions:

- **TenantEvents** — tenant-wide document lifecycle events (create, delete, approve, version)
- **DocumentEvents** — change events and audits for a single document

Incoming payloads are printed as indented JSON. Press Ctrl+C to disconnect.

## Requirements

- Python 3.10 or newer
- A Genesis Foods GraphQL HTTPS endpoint
- An API key with access to subscriptions

Install dependencies from this folder:

```bash
pip install -r requirements.txt
```

That installs `gql` with the WebSockets extra.

## Run

From this directory:

```bash
python subscribe.py
```

The script prompts for anything it does not already have:

1. **GraphQL endpoint (https)** — for example `https://api.trustwell.com/genesis`. An `http`/`https` URL is converted to `ws`/`wss` automatically.
2. **API key** — sent as the `X-Api-Key` header on the WebSocket connection.
3. **Subscription type** — `1` for TenantEvents or `2` for DocumentEvents.
4. **Subscription input** — flags (tenant) or a document id (document). See below.

You can skip the first two prompts with environment variables:

```bash
# Windows PowerShell
$env:GENESIS_GRAPHQL_URL = "https://api.trustwell.com/genesis"
$env:GENESIS_API_KEY = "your-api-key"
python subscribe.py
```

```bash
# bash
export GENESIS_GRAPHQL_URL="https://api.trustwell.com/genesis"
export GENESIS_API_KEY="your-api-key"
python subscribe.py
```

Use the matching host for your environment (dev, preview, or production). This script does not read `src/genesis/config.ini`.

## TenantEvents

Choose `1` (or type `TenantEvents`).

You are asked for `TenantDocumentEventFlags`. Enter `all`, or a comma-separated list of names:

| Flag | Typical meaning |
| --- | --- |
| `IngredientCreated` | Ingredient created |
| `IngredientDeleted` | Ingredient deleted |
| `IngredientApproved` | Ingredient approved |
| `IngredientVersioned` | Ingredient versioned |
| `RecipeCreated` | Recipe created |
| `RecipeDeleted` | Recipe deleted |
| `RecipeApproved` | Recipe approved |
| `RecipeVersioned` | Recipe versioned |
| `LabelCreated` | Label created |
| `LabelDeleted` | Label deleted |

Example: `RecipeCreated, RecipeApproved`

Each event includes `id` and `events`.

## DocumentEvents

Choose `2` (or type `DocumentEvents`), then enter the document id to watch.

Each event includes `documentId`, `updatedDocumentId`, `modified`, `eventType`, and `audits` (old/new values, category, user, version).

## Connection details

- Transport: GraphQL over WebSockets (`graphql-ws` subprotocol)
- Auth: `X-Api-Key`
- Unexpected WebSocket failures print `WebSocket error:` and exit with status 1
