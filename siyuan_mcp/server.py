"""MCP server for SiYuan Note wiki."""

import json
import os
import urllib.request
from typing import Any

from mcp.server.fastmcp import FastMCP

SIYUAN_URL = os.environ.get("SIYUAN_URL", "http://127.0.0.1:6806")
SIYUAN_TOKEN = os.environ.get("SIYUAN_TOKEN", "")

mcp = FastMCP("siyuan")


def _call(endpoint: str, payload: dict[str, Any] | None = None) -> Any:
    """Call the SiYuan API."""
    url = f"{SIYUAN_URL}{endpoint}"
    data = json.dumps(payload or {}).encode()
    headers = {"Content-Type": "application/json"}
    if SIYUAN_TOKEN:
        headers["Authorization"] = f"Token {SIYUAN_TOKEN}"
    req = urllib.request.Request(
        url, data=data, headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    if result.get("code") != 0:
        raise RuntimeError(f"SiYuan API error: {result.get('msg', 'unknown')}")
    return result.get("data", {})


# ── Notebooks ──────────────────────────────────────────────


@mcp.tool()
def list_notebooks() -> str:
    """List all notebooks in SiYuan."""
    data = _call("/api/notebook/lsNotebooks")
    notebooks = data.get("notebooks", [])
    lines = []
    for nb in notebooks:
        status = "closed" if nb.get("closed") else "open"
        lines.append(f"- {nb['name']} (id: {nb['id']}, {status})")
    return "\n".join(lines) or "No notebooks found."


# ── Search ─────────────────────────────────────────────────


@mcp.tool()
def search(query: str, page: int = 0) -> str:
    """Full-text search across all notes.

    Returns matching blocks with their IDs and content.
    """
    data = _call(
        "/api/search/fullTextSearchBlock",
        {"query": query, "page": page},
    )
    blocks = data.get("blocks", [])
    if not blocks:
        return "No results found."
    lines = []
    for b in blocks:
        doc = b.get("hPath", b.get("rootID", ""))
        lines.append(
            f"### {doc}\n"
            f"- Block ID: {b['id']}\n"
            f"- Type: {b.get('type', '?')}\n"
            f"- Content: {b.get('content', '')[:500]}\n"
        )
    return "\n".join(lines)


@mcp.tool()
def sql_query(stmt: str) -> str:
    """Execute a SQL query against SiYuan's block database.

    Useful for advanced filtering. Key columns: id, content,
    type (d=doc, p=paragraph, h=heading, l=list, c=code),
    root_id, box, path, created, updated.
    """
    data = _call("/api/query/sql", {"stmt": stmt})
    rows = data if isinstance(data, list) else []
    if not rows:
        return "No results."
    return json.dumps(rows[:50], ensure_ascii=False, indent=2)


# ── Read ───────────────────────────────────────────────────


@mcp.tool()
def get_document(doc_id: str) -> str:
    """Get the full Markdown content of a document by its ID."""
    data = _call("/api/export/exportMdContent", {"id": doc_id})
    return data.get("content", "No content.")


@mcp.tool()
def get_block(block_id: str) -> str:
    """Get a block's content in Kramdown format."""
    data = _call("/api/block/getBlockKramdown", {"id": block_id})
    return data.get("kramdown", "No content.")


@mcp.tool()
def get_child_blocks(block_id: str) -> str:
    """Get all direct child blocks of a block/document."""
    data = _call("/api/block/getChildBlocks", {"id": block_id})
    if not data:
        return "No child blocks."
    lines = []
    for b in data:
        lines.append(
            f"- [{b.get('type', '?')}] {b['id']}: "
            f"{b.get('subType', '')} {b.get('content', '')[:200]}"
        )
    return "\n".join(lines)


@mcp.tool()
def list_docs(notebook_id: str, path: str = "/") -> str:
    """List documents in a notebook at the given path."""
    data = _call(
        "/api/filetree/listDocsByPath",
        {"notebook": notebook_id, "path": path},
    )
    files = data.get("files", [])
    if not files:
        return "No documents found."
    lines = []
    for f in files:
        name = f.get("name", "").replace(".sy", "")
        lines.append(
            f"- {name} (id: {f.get('id', '')}, "
            f"subFiles: {f.get('subFileCount', 0)})"
        )
    return "\n".join(lines)


# ── Write ──────────────────────────────────────────────────


@mcp.tool()
def create_document(notebook_id: str, path: str, markdown: str) -> str:
    """Create a new document with Markdown content.

    Path example: '/Notes/My New Page'.
    """
    data = _call(
        "/api/filetree/createDocWithMd",
        {
            "notebook": notebook_id,
            "path": path,
            "markdown": markdown,
        },
    )
    return f"Document created with ID: {data}"


@mcp.tool()
def append_block(parent_id: str, markdown: str) -> str:
    """Append a Markdown block to the end of a document or
    parent block."""
    data = _call(
        "/api/block/appendBlock",
        {
            "parentID": parent_id,
            "dataType": "markdown",
            "data": markdown,
        },
    )
    if isinstance(data, list):
        ops = data[0].get("doOperations", []) if data else []
    else:
        ops = data.get("doOperations", [])
    if ops:
        return f"Block appended. New block ID: {ops[0].get('id', 'unknown')}"
    return "Block appended."


@mcp.tool()
def insert_block(
    markdown: str, previous_id: str = "", parent_id: str = ""
) -> str:
    """Insert a Markdown block after a specific sibling block,
    or as first child of a parent."""
    payload = {"dataType": "markdown", "data": markdown}
    if previous_id:
        payload["previousID"] = previous_id
    if parent_id:
        payload["parentID"] = parent_id
    data = _call("/api/block/insertBlock", payload)
    if isinstance(data, list):
        ops = data[0].get("doOperations", []) if data else []
    else:
        ops = data.get("doOperations", [])
    if ops:
        return f"Block inserted. ID: {ops[0].get('id', 'unknown')}"
    return "Block inserted."


@mcp.tool()
def update_block(block_id: str, markdown: str) -> str:
    """Update an existing block's content with new Markdown."""
    _call(
        "/api/block/updateBlock",
        {
            "id": block_id,
            "dataType": "markdown",
            "data": markdown,
        },
    )
    return f"Block {block_id} updated."


@mcp.tool()
def delete_block(block_id: str) -> str:
    """Delete a block by its ID."""
    _call("/api/block/deleteBlock", {"id": block_id})
    return f"Block {block_id} deleted."


@mcp.tool()
def rename_document(doc_id: str, title: str) -> str:
    """Rename a document."""
    _call(
        "/api/filetree/renameDocByID",
        {
            "id": doc_id,
            "title": title,
        },
    )
    return f"Document {doc_id} renamed to '{title}'."


@mcp.tool()
def delete_document(doc_id: str) -> str:
    """Delete a document by its ID."""
    _call("/api/filetree/removeDocByID", {"id": doc_id})
    return f"Document {doc_id} deleted."


# ── Attributes ─────────────────────────────────────────────


@mcp.tool()
def get_block_attrs(block_id: str) -> str:
    """Get all attributes of a block (including custom-*
    attributes)."""
    data = _call("/api/attr/getBlockAttrs", {"id": block_id})
    return json.dumps(data, ensure_ascii=False, indent=2)


@mcp.tool()
def set_block_attrs(block_id: str, attrs: dict[str, str]) -> str:
    """Set attributes on a block.

    Custom attributes must use 'custom-' prefix.
    """
    _call(
        "/api/attr/setBlockAttrs",
        {
            "id": block_id,
            "attrs": attrs,
        },
    )
    return f"Attributes set on block {block_id}."


def main():
    mcp.run()


if __name__ == "__main__":
    main()
