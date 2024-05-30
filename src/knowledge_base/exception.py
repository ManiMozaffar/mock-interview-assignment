from src.knowledge_base.type import EmbeddedDocumentId, KnowledgeBaseId


class BaseKnowledgeException(Exception):
    """Base class for exceptions in the knowledge base module."""


class DocumentDoesNotExist(BaseKnowledgeException):
    """Raised when a document does not exist in a knowledge base.

    Attributes:
        document_id: The id of the document that does not exist.
        knowledge_base_id: The id of the knowledge base in which the document does not exist.
    """

    def __init__(self, document_id: EmbeddedDocumentId, knowledge_base_id: KnowledgeBaseId):
        self.document_id = document_id
        self.knowledge_base_id = knowledge_base_id
        super().__init__(
            f"Document {document_id} does not exist in knowledge base {knowledge_base_id}."
        )


class FAISSCreationFailed(BaseKnowledgeException):
    """Raised when the creation of a FAISS index fails. Happens only if there are no documents in the knowledge base.

    Attributes:
        kb_id: The id of the knowledge base for which the index creation failed.
    """

    def __init__(self, kb_id: KnowledgeBaseId):
        self.kb_id = kb_id
        super().__init__(f"""Failed to create FAISS index for knowledge base {kb_id}.
                         Faiss can be only created if there is at least one document in the knowledge base.""")
