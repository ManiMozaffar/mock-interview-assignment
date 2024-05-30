from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

import src.knowledge_base.type as t


class EmbeddedDocument(BaseModel):
    """
    A document that has been embedded.
    Once document is embedded, it is immutable.

    Attributes:
        id: The id of the document.
        text: The text of the document.
        embedding: The embedding of the document.
        model_config: The configuration of the model used to embed the document.
    """

    id: t.EmbeddedDocumentId

    text: str

    embedding: list[float]

    model_config = ConfigDict(frozen=True)


class KnowledgeBase(BaseModel):
    """A collection of documents.

    Attributes:
        id: The id of the knowledge base.
        name: The name of the knowledge base, to be shown to the user in UI.
        documents: The documents in the knowledge base.
    """

    id: t.KnowledgeBaseId = Field(default_factory=uuid4)

    name: str

    documents: dict[t.EmbeddedDocumentId, EmbeddedDocument]

    def hashable_key(self) -> t.KnowledgeBaseHashId:
        return t.KnowledgeBaseHashId(hash((self.id, tuple(self.documents.keys()))))
