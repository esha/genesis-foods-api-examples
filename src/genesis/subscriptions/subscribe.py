import asyncio
import json
import os
import sys
from urllib.parse import urlparse, urlunparse

from gql import Client, gql
from gql.transport.exceptions import TransportError
from gql.transport.websockets import WebsocketsTransport

TENANT_DOCUMENT_EVENT_FLAGS = [
    "IngredientCreated",
    "IngredientDeleted",
    "IngredientApproved",
    "IngredientVersioned",
    "RecipeCreated",
    "RecipeDeleted",
    "RecipeApproved",
    "RecipeVersioned",
    "LabelCreated",
    "LabelDeleted",
]

TENANT_EVENTS_QUERY = gql(
    """
    subscription TenantEvents($input: TenantEventsInput!) {
      tenantEvents(input: $input) {
        id
        events
      }
    }
    """
)

DOCUMENT_EVENTS_QUERY = gql(
    """
    subscription DocumentEvents($input: DocumentEventsInput!) {
      documentEvents(input: $input) {
        documentId
        updatedDocumentId
        modified
        eventType
        audits {
          id
          item
          oldValue
          newValue
          category
          createdOn
          modifiedBy {
            id
            name
            email
          }
          version {
            id
            versionName
            began
            entityId
          }
        }
      }
    }
    """
)


def prompt(message: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{message}{suffix}: ").strip()
    if value:
        return value
    if default is not None:
        return default
    print("A value is required.", file=sys.stderr)
    return prompt(message, default)


def https_to_wss(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme in ("ws", "wss"):
        return url
    if parsed.scheme == "https":
        scheme = "wss"
    elif parsed.scheme == "http":
        scheme = "ws"
    else:
        raise ValueError(f"Unsupported URL scheme: {parsed.scheme or '(none)'}")
    return urlunparse(parsed._replace(scheme=scheme))


def choose_subscription() -> str:
    print("Subscription type:")
    print("  1) TenantEvents")
    print("  2) DocumentEvents")
    choice = prompt("Choose 1 or 2")
    if choice in ("1", "tenant", "tenantevents", "TenantEvents"):
        return "tenant"
    if choice in ("2", "document", "documentevents", "DocumentEvents"):
        return "document"
    print("Enter 1 or 2.", file=sys.stderr)
    return choose_subscription()


def choose_flags() -> list[str]:
    print("TenantDocumentEventFlags:")
    for flag in TENANT_DOCUMENT_EVENT_FLAGS:
        print(f"  {flag}")
    raw = prompt("Flags (comma-separated names, or all)")
    if raw.lower() == "all":
        return list(TENANT_DOCUMENT_EVENT_FLAGS)
    flags = [part.strip() for part in raw.split(",") if part.strip()]
    unknown = [flag for flag in flags if flag not in TENANT_DOCUMENT_EVENT_FLAGS]
    if unknown:
        print(f"Unknown flags: {', '.join(unknown)}", file=sys.stderr)
        return choose_flags()
    if not flags:
        print("Send at least one flag (or all).", file=sys.stderr)
        return choose_flags()
    return flags


def print_payload(result: object) -> None:
    print(json.dumps(result, indent=2, default=str), flush=True)


async def run() -> None:
    http_url = os.environ.get("GENESIS_GRAPHQL_URL") or prompt("GraphQL endpoint (https)")
    api_key = os.environ.get("GENESIS_API_KEY") or prompt("API key")
    ws_url = https_to_wss(http_url)

    kind = choose_subscription()
    if kind == "tenant":
        query = TENANT_EVENTS_QUERY
        variables = {"input": {"flags": choose_flags()}}
    else:
        query = DOCUMENT_EVENTS_QUERY
        variables = {"input": {"documentId": prompt("Document id")}}

    transport = WebsocketsTransport(
        url=ws_url,
        headers={"X-Api-Key": api_key},
        subprotocols=[WebsocketsTransport.GRAPHQLWS_SUBPROTOCOL],
    )
    client = Client(transport=transport, execute_timeout=None)

    print(f"Connecting to {ws_url} …", flush=True)
    async with client as session:
        print("Subscribed. Waiting for events (Ctrl+C to stop).", flush=True)
        async for result in session.subscribe(query, variable_values=variables):
            print_payload(result)


def main() -> None:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)
    except TransportError as exc:
        print(f"WebSocket error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
