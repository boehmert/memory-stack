"""Vault loader and in-memory index for a curated Obsidian knowledge base."""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import frontmatter  # python-frontmatter

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_WIKILINK_RE = re.compile(r"\[\[(.+?)(?:\|.+?)?\]\]")


def _default_vault_root() -> Path:
    """Resolve the vault root from VAULT_ROOT env var (required)."""
    env_root = os.environ.get("VAULT_ROOT")
    if env_root:
        return Path(env_root)
    raise FileNotFoundError(
        "VAULT_ROOT environment variable is not set. "
        "Point it at a directory of Markdown files with YAML frontmatter."
    )


# ---------------------------------------------------------------------------
# Data classes (plain dicts for simplicity)
# ---------------------------------------------------------------------------

def _make_node(path: Path, meta: dict[str, Any], body: str) -> dict[str, Any]:
    """Normalise a parsed frontmatter document into a vault node."""
    stem = path.stem
    # Resolve KB id — fall back to filename stem
    doc_id: str = str(meta.get("id") or stem)
    title: str = str(meta.get("title") or stem)

    # Extract wikilink targets from string / list fields
    def _links_from(value: Any) -> list[str]:
        if not value:
            return []
        text = value if isinstance(value, str) else str(value)
        return _WIKILINK_RE.findall(text)

    up_links = _links_from(meta.get("up", ""))
    related_raw = meta.get("related", [])
    related_str = (
        " ".join(related_raw)
        if isinstance(related_raw, list)
        else str(related_raw)
    )
    related_links = _links_from(related_str)

    tags: list[str] = list(meta.get("tags") or [])
    document_type: str = str(meta.get("document_type") or "")

    return {
        "id": doc_id,
        "title": title,
        "path": str(path),
        "stem": stem,
        "tags": tags,
        "document_type": document_type,
        "up": up_links,
        "related": related_links,
        "body": body,
        "meta": meta,
    }


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

class VaultIndex:
    """Lazily-loaded, in-memory index of all curated vault documents."""

    def __init__(self, vault_root: Path | None = None) -> None:
        self._root = vault_root or _default_vault_root()
        self._by_id: dict[str, dict] = {}       # id → node
        self._by_stem: dict[str, str] = {}       # filename-stem → id
        self._all: list[dict] = []
        self._loaded = False

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if self._loaded:
            return
        if not self._root.exists():
            raise FileNotFoundError(
                f"Vault root not found: {self._root}\n"
                "Set the correct path via VAULT_ROOT env var or vault_root param."
            )
        for md_path in sorted(self._root.glob("*.md")):
            try:
                post = frontmatter.load(str(md_path))
                node = _make_node(md_path, dict(post.metadata), post.content)
                self._all.append(node)
                self._by_id[node["id"]] = node
                self._by_stem[node["stem"]] = node["id"]
            except Exception:  # noqa: BLE001 – skip malformed files silently
                pass
        self._loaded = True

    def ensure_loaded(self) -> None:
        self._load()

    # ------------------------------------------------------------------
    # Lookup helpers
    # ------------------------------------------------------------------

    def _resolve(self, ref: str) -> dict | None:
        """Resolve a wikilink target or id to a node, best-effort."""
        self._load()
        # Direct id match
        if ref in self._by_id:
            return self._by_id[ref]
        # Filename-stem match
        if ref in self._by_stem:
            return self._by_id[self._by_stem[ref]]
        # Case-insensitive stem match
        ref_lower = ref.lower()
        for stem, nid in self._by_stem.items():
            if stem.lower() == ref_lower:
                return self._by_id[nid]
        return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, doc_id: str) -> dict | None:
        self._load()
        node = self._by_id.get(doc_id) or self._resolve(doc_id)
        return node

    def search(self, query: str, limit: int = 10) -> list[dict]:
        """Simple case-insensitive full-text search across title + body."""
        self._load()
        q = query.lower()
        scored: list[tuple[int, dict]] = []
        for node in self._all:
            score = 0
            if q in node["title"].lower():
                score += 10
            body_lower = node["body"].lower()
            score += body_lower.count(q)
            if score > 0:
                scored.append((score, node))
        scored.sort(key=lambda x: -x[0])
        return [n for _, n in scored[:limit]]

    def related(self, doc_id: str) -> list[dict]:
        """Return all nodes directly linked via the 'related:' field."""
        self._load()
        node = self.get(doc_id)
        if not node:
            return []
        result: list[dict] = []
        seen: set[str] = set()
        for ref in node["related"] + node["up"]:
            linked = self._resolve(ref)
            if linked and linked["id"] not in seen:
                seen.add(linked["id"])
                result.append(linked)
        return result

    def list_docs(
        self,
        tag: str | None = None,
        document_type: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """List documents, optionally filtered by tag and/or document_type."""
        self._load()
        results = []
        for node in self._all:
            if tag and not any(tag.lower() in t.lower() for t in node["tags"]):
                continue
            if document_type and document_type.lower() not in node["document_type"].lower():
                continue
            results.append(node)
            if len(results) >= limit:
                break
        return results

    def context_for(self, query: str, limit: int = 5) -> str:
        """
        Return a formatted context block suitable for injection into an LLM prompt.
        Includes title, id, tags and the first 600 chars of each matching body.
        """
        hits = self.search(query, limit=limit)
        if not hits:
            return f"No documents found for query: {query!r}"
        parts: list[str] = [f"# Vault context for: {query!r}\n"]
        for i, node in enumerate(hits, 1):
            snippet = node["body"][:600].strip()
            if len(node["body"]) > 600:
                snippet += " …"
            parts.append(
                f"## [{i}] {node['title']}\n"
                f"**ID:** `{node['id']}`  \n"
                f"**Tags:** {', '.join(node['tags']) or '—'}  \n"
                f"**Type:** {node['document_type'] or '—'}\n\n"
                f"{snippet}\n"
            )
        return "\n---\n".join(parts)

    @property
    def size(self) -> int:
        self._load()
        return len(self._all)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def write_doc(
        self,
        title: str,
        body: str,
        *,
        doc_id: str | None = None,
        filename: str | None = None,
        tags: list[str] | None = None,
        document_type: str = "Knowledge Distillate",
        up: str = "[[MOC_Start]]",
        related: list[str] | None = None,
        created_by: str = "copilot",
        extra_meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Write a new document to the vault and add it to the in-memory index.

        Returns the node dict of the created document.
        Raises ValueError if a document with the same id already exists.
        Raises ValueError if the filename resolves outside the vault root.
        """
        self._load()

        # Generate id from timestamp if not provided
        if not doc_id:
            doc_id = "KB-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

        # Check for duplicate id
        if doc_id in self._by_id:
            raise ValueError(f"Document with id {doc_id!r} already exists")

        # Build filename
        if not filename:
            slug = re.sub(r"[^\w\s-]", "", title)
            slug = re.sub(r"[\s]+", "_", slug).strip("_")
            filename = f"{slug}.md"
        if not filename.endswith(".md"):
            filename += ".md"

        target = (self._root / filename).resolve()
        # Path traversal guard
        if not str(target).startswith(str(self._root.resolve())):
            raise ValueError("Filename must not escape the vault directory")

        if target.exists():
            raise ValueError(f"File already exists: {filename}")

        # Assemble frontmatter metadata
        meta: dict[str, Any] = {
            "id": doc_id,
            "title": title,
            "document_type": document_type,
            "tags": tags or ["status/draft"],
            "aliases": [],
            "up": up,
            "related": related or [],
            "created_by": created_by,
            "created": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        }
        if extra_meta:
            meta.update(extra_meta)

        # Write file
        post = frontmatter.Post(body, **meta)
        target.write_text(
            frontmatter.dumps(post), encoding="utf-8"
        )

        # Update in-memory index
        node = _make_node(target, meta, body)
        self._all.append(node)
        self._by_id[node["id"]] = node
        self._by_stem[node["stem"]] = node["id"]

        return node


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_INDEX: VaultIndex | None = None


def get_index(vault_root: Path | None = None) -> VaultIndex:
    """Return (and lazily create) the module-level VaultIndex singleton."""
    global _INDEX  # noqa: PLW0603
    if _INDEX is None:
        env_root = os.environ.get("VAULT_ROOT")
        root = vault_root or (Path(env_root) if env_root else None)
        _INDEX = VaultIndex(vault_root=root)
    return _INDEX
