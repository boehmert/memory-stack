"""MCP server: exposes an Obsidian knowledge-base vault as agent tools.

Tools
-----
vault_search  — full-text search across all curated documents
vault_get     — fetch a single document by id or filename
vault_related — get documents linked via related:/up: from a given document
vault_list    — list / filter documents by tag or type
vault_context — return an LLM-ready context block for a query (best for injection)
vault_write   — create a new document in the vault with frontmatter
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)

from vault_mcp.vault import get_index

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("vault-mcp")

# ---------------------------------------------------------------------------
# Server instance
# ---------------------------------------------------------------------------

server = Server("vault-mcp")


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

_TOOLS: list[Tool] = [
    Tool(
        name="vault_search",
        description=(
            "Full-text search across all curated Obsidian vault documents. "
            "Returns matching documents sorted by relevance with title, id, tags and a body excerpt."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search terms (case-insensitive, plain text)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default 10, max 30)",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="vault_get",
        description=(
            "Fetch a single document from the vault by its KB id (e.g. 'KB-Example-001') "
            "or by filename stem (e.g. 'Context_Engineering_Best_Practices'). "
            "Returns full metadata and body text."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "doc_id": {
                    "type": "string",
                    "description": "Document id (from frontmatter id:) or filename without .md",
                },
            },
            "required": ["doc_id"],
        },
    ),
    Tool(
        name="vault_related",
        description=(
            "Return all documents directly linked from a given document via its "
            "'related:' and 'up:' frontmatter fields. Useful for graph traversal."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "doc_id": {
                    "type": "string",
                    "description": "Document id or filename stem",
                },
            },
            "required": ["doc_id"],
        },
    ),
    Tool(
        name="vault_list",
        description=(
            "List documents in the vault, optionally filtered by tag or document_type. "
            "Returns title, id, tags and document_type — no body text."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "tag": {
                    "type": "string",
                    "description": "Filter by tag substring (e.g. 'engineering', 'status/draft')",
                },
                "document_type": {
                    "type": "string",
                    "description": "Filter by document_type substring (e.g. 'Knowledge Distillate')",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results (default 50)",
                    "default": 50,
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="vault_context",
        description=(
            "Return a formatted, LLM-ready context block for a search query. "
            "Best tool for injecting vault knowledge directly into a prompt or answer. "
            "Returns top-N matching documents with title, id, tags and a body excerpt."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Topic or question to retrieve context for",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of documents to include (default 5)",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="vault_write",
        description=(
            "Create a new document in the Obsidian vault with proper frontmatter. "
            "Use this to persist knowledge distillates, learnings or curated content "
            "directly into the vault where it becomes searchable via vault_search. "
            "The document gets an auto-generated KB id and is tagged status/draft by default."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Document title (used for filename and frontmatter)",
                },
                "body": {
                    "type": "string",
                    "description": "Markdown body content of the document",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of tags (default: ['status/draft'])",
                },
                "document_type": {
                    "type": "string",
                    "description": "Document type (default: 'Knowledge Distillate')",
                    "default": "Knowledge Distillate",
                },
                "up": {
                    "type": "string",
                    "description": "Parent document wikilink (default: '[[MOC_Start]]')",
                    "default": "[[MOC_Start]]",
                },
                "related": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of related document wikilinks, e.g. ['[[KB-Example-001]]']",
                },
                "created_by": {
                    "type": "string",
                    "description": "Author identifier (default: 'copilot')",
                    "default": "copilot",
                },
            },
            "required": ["title", "body"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------

def _node_summary(node: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": node["id"],
        "title": node["title"],
        "tags": node["tags"],
        "document_type": node["document_type"],
        "related": node["related"],
        "up": node["up"],
        "body_preview": node["body"][:400].strip() + (" …" if len(node["body"]) > 400 else ""),
    }


def _node_full(node: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": node["id"],
        "title": node["title"],
        "tags": node["tags"],
        "document_type": node["document_type"],
        "related": node["related"],
        "up": node["up"],
        "path": node["path"],
        "body": node["body"],
    }


@server.list_tools()
async def list_tools() -> ListToolsResult:
    return ListToolsResult(tools=_TOOLS)


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
    idx = get_index()

    try:
        # ----------------------------------------------------------------
        if name == "vault_search":
            query = arguments["query"]
            limit = min(int(arguments.get("limit", 10)), 30)
            hits = idx.search(query, limit=limit)
            result = {
                "query": query,
                "total": len(hits),
                "vault_size": idx.size,
                "results": [_node_summary(n) for n in hits],
            }
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            )

        # ----------------------------------------------------------------
        elif name == "vault_get":
            doc_id = arguments["doc_id"]
            node = idx.get(doc_id)
            if not node:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Document not found: {doc_id!r}")]
                )
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(_node_full(node), ensure_ascii=False, indent=2))]
            )

        # ----------------------------------------------------------------
        elif name == "vault_related":
            doc_id = arguments["doc_id"]
            nodes = idx.related(doc_id)
            result = {
                "source": doc_id,
                "count": len(nodes),
                "related": [_node_summary(n) for n in nodes],
            }
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            )

        # ----------------------------------------------------------------
        elif name == "vault_list":
            tag = arguments.get("tag")
            document_type = arguments.get("document_type")
            limit = min(int(arguments.get("limit", 50)), 200)
            nodes = idx.list_docs(tag=tag, document_type=document_type, limit=limit)
            result = {
                "filter": {"tag": tag, "document_type": document_type},
                "count": len(nodes),
                "vault_size": idx.size,
                "documents": [
                    {"id": n["id"], "title": n["title"], "tags": n["tags"], "document_type": n["document_type"]}
                    for n in nodes
                ],
            }
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            )

        # ----------------------------------------------------------------
        elif name == "vault_context":
            query = arguments["query"]
            limit = min(int(arguments.get("limit", 5)), 15)
            context = idx.context_for(query, limit=limit)
            return CallToolResult(
                content=[TextContent(type="text", text=context)]
            )

        # ----------------------------------------------------------------
        elif name == "vault_write":
            title = arguments["title"]
            body = arguments["body"]
            tags = arguments.get("tags")
            document_type = arguments.get("document_type", "Knowledge Distillate")
            up = arguments.get("up", "[[MOC_Start]]")
            related = arguments.get("related")
            created_by = arguments.get("created_by", "copilot")

            node = idx.write_doc(
                title=title,
                body=body,
                tags=tags,
                document_type=document_type,
                up=up,
                related=related,
                created_by=created_by,
            )
            result = {
                "status": "created",
                "id": node["id"],
                "title": node["title"],
                "path": node["path"],
                "tags": node["tags"],
                "vault_size": idx.size,
            }
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            )

        # ----------------------------------------------------------------
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {name!r}")]
            )

    except Exception as exc:  # noqa: BLE001
        log.exception("Tool %r failed", name)
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error in {name!r}: {exc}")]
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def _run() -> None:
    idx = get_index()
    idx.ensure_loaded()
    log.info("vault-mcp: loaded %d documents from %s", idx.size, idx._root)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
