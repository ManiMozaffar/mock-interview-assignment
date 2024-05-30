from typing import NewType
from uuid import UUID

EmbeddedDocumentId = NewType("EmbeddedDocumentId", UUID)
"""A type stated type for EmbeddedDocument."""

KnowledgeBaseId = NewType("KnowledgeBaseId", UUID)
"""A type stated type for KnowledgeBase."""

KnowledgeBaseHashId = NewType("KnowledgeBaseHashId", int)
"""A type stated type for KnowledgeBaseHash."""
