"""OKF (Open Knowledge Format) Navigation Tools for Altostrat Singapore HR Agent."""

import os
import pathlib
import re
from typing import Dict, Any, List, Tuple
import yaml

from agent import config

# Base directory for the knowledge bundle
KNOWLEDGE_DIR = pathlib.Path(config.KNOWLEDGE_DIR)

RESERVED_FILES = {"index.md", "log.md"}
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

def _parse_file(text: str) -> Tuple[Dict[str, Any], str]:
    """Split YAML frontmatter from markdown body."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        data = {}
    body = text[m.end():]
    return data, body

def list_concepts() -> Dict[str, List[Dict[str, str]]]:
    """
    Lists all available HR policy concepts in the Altostrat Singapore OKF catalog.
    Returns:
        {"concepts": [{"id": str, "title": str, "description": str}, ...]}
        where `id` is the concept path without the .md suffix (e.g. "04-travel-expense-te-guidelines/4.3-lodging-transportation-caps").
    """
    concepts = []
    k_dir = KNOWLEDGE_DIR.resolve()

    for root, _, files in os.walk(k_dir):
        for f in files:
            if not f.endswith(".md") or f in RESERVED_FILES:
                continue

            full_path = pathlib.Path(root) / f
            rel_path = full_path.relative_to(k_dir)
            concept_id = str(rel_path.with_suffix("")).replace("\\", "/")

            try:
                text = full_path.read_text(encoding="utf-8")
                frontmatter, _ = _parse_file(text)
            except Exception:
                continue

            concepts.append({
                "id": concept_id,
                "title": frontmatter.get("title", f.replace(".md", "").replace("-", " ").title()),
                "description": frontmatter.get("description", "")
            })

    concepts.sort(key=lambda c: c["id"])
    return {"concepts": concepts}

def read_concept(concept_id: str) -> Dict[str, Any]:
    """
    Reads the exact text and citation metadata for a single HR policy concept.
    Args:
        concept_id: e.g. "01-paid-time-off-leave-operations/1.1-outpatient-sick-time-hospitalization-leave-singapore"
    Returns:
        {"content": str, "title": str, "resource": str | None}
    """
    clean_id = concept_id.strip()
    if clean_id.endswith(".md"):
        clean_id = clean_id[:-3]

    k_dir = KNOWLEDGE_DIR.resolve()
    target_path = (k_dir / f"{clean_id}.md").resolve()

    # Security check: guard against directory traversal
    if not str(target_path).startswith(str(k_dir)):
        return {"error": f"Invalid concept_id '{concept_id}': access outside knowledge bundle forbidden."}

    if not target_path.is_file():
        return {
            "error": f"Concept '{clean_id}' not found in knowledge bundle. Invoke list_concepts to inspect valid concept IDs."
        }

    try:
        text = target_path.read_text(encoding="utf-8")
        frontmatter, body = _parse_file(text)
    except Exception as e:
        return {"error": f"Failed to read concept '{clean_id}': {e}"}

    resource = frontmatter.get("source") or frontmatter.get("resource") or clean_id
    title = frontmatter.get("title", clean_id)

    return {
        "content": body.strip(),
        "title": title,
        "resource": resource
    }
