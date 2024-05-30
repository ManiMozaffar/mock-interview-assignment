from pydantic import BaseModel

from src.knowledge_base.type import EmbeddedDocumentId, KnowledgeBaseId


class AddDocumentInput(BaseModel):
    knowledge_base_id: KnowledgeBaseId
    # could be a list of ids as well, if we wanted to allow client to write to many kbs at once
    text: str


class AddDocumentOutput(BaseModel):
    document_id: EmbeddedDocumentId


class AddKnowledgeBaseInput(BaseModel):
    name: str


class AddKnowledgeBaseOutput(BaseModel):
    knowledge_base_id: KnowledgeBaseId


class QueryForSimilarDocumentsInput(BaseModel):
    knowledge_base_id: KnowledgeBaseId
    text: str
    k: int


class SimiliarDocument(BaseModel):
    id: EmbeddedDocumentId
    text: str
