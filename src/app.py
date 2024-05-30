from typing import Annotated

from fastapi import Body, FastAPI, HTTPException, Path

from src.knowledge_base.exception import FAISSCreationFailed
from src.knowledge_base.manager import (
    KnowledgeBaseManager,
    query_kb_for_similar_documents,
)
from src.knowledge_base.schema import KnowledgeBase
from src.knowledge_base.type import EmbeddedDocumentId, KnowledgeBaseId
from src.schema import (
    AddDocumentInput,
    AddDocumentOutput,
    AddKnowledgeBaseInput,
    AddKnowledgeBaseOutput,
    QueryForSimilarDocumentsInput,
    SimiliarDocument,
)

app = FastAPI()


# in an ideal world, we would not make the FastAPI stateful by loading ML directly inside it.
# because then it is harder to scale and maintain it. and client MUST wait for the model to load, and respond
# it also is CPU intensive and blocks the event loop, which is bad for async programming.
# instead, we should make a separate service that loads the model and serves the predictions.
# and talks to the FastAPI service via HTTP, GRPC or some other protocol according to our needs and scale.


# probably read and write from db, but to simplify, we will just use in-memory storage as mentioned in the task description
KBS: dict[KnowledgeBaseId, KnowledgeBaseManager] = {}


def get_kb_manager(knowledge_base_id: KnowledgeBaseId) -> KnowledgeBaseManager:
    if knowledge_base_id not in KBS:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return KBS[knowledge_base_id]


@app.post("/knowledge-base")
async def add_knowledge_base(
    body: Annotated[AddKnowledgeBaseInput, Body()],
) -> AddKnowledgeBaseOutput:
    """Add a knowledge base, with no documents, to the database"""
    kb = KnowledgeBase(name=body.name, documents={})
    KBS[kb.id] = KnowledgeBaseManager(kb)
    return AddKnowledgeBaseOutput(knowledge_base_id=kb.id)


@app.get("/knowledge-base/{knowledge_base_id}")
async def get_knowledge_base(
    knowledge_base_id: Annotated[KnowledgeBaseId, Path()],
) -> KnowledgeBase:
    """Get a knowledge base by its id"""
    kb_manager = get_kb_manager(knowledge_base_id)
    return kb_manager.kb


@app.post("/documents")
async def add_document(body: Annotated[AddDocumentInput, Body()]) -> AddDocumentOutput:
    """Add a document to the knowledge base"""
    # we could abstract it and not use the router function directly
    kb_manager = get_kb_manager(body.knowledge_base_id)
    doc = kb_manager.add_document_to_kb(body.text)
    return AddDocumentOutput(document_id=doc.id)


# query parameter on browser by default has a limit of lenght of 500
# so better to use post, since document passed is huge and we don't want to expose it in the URL as well
# because it might contain some important stuff as well


# PUT is bad for this, because this endpoint is actually not idempotent.
@app.post("/documents/query-similar")
async def query_for_similar_documents(
    query: Annotated[QueryForSimilarDocumentsInput, Body()],
) -> list[SimiliarDocument]:
    """Query for similar documents in the knowledge base"""
    kb_manager = get_kb_manager(query.knowledge_base_id)
    embedded_docuemnt = kb_manager.get_embed_document(query.text)

    try:
        results = await query_kb_for_similar_documents(kb_manager, embedded_docuemnt, query.k)
    except FAISSCreationFailed:
        raise HTTPException(
            status_code=422,
            detail="Failed to create FAISS index, because there is no document in the knowledge base.",
        )

    return [SimiliarDocument(id=doc.id, text=doc.text) for doc in results]


@app.delete("/documents/{knowledge_base_id}/{document_id}")
async def delete_document(
    knowledge_base_id: Annotated[KnowledgeBaseId, Path()],
    document_id: Annotated[EmbeddedDocumentId, Path()],
) -> None:
    """Delete a document from the knowledge base"""
    kb_manager = get_kb_manager(knowledge_base_id)
    to_be_deleted_doc = kb_manager.kb.documents.get(document_id, None)

    # note that this is still idempotent.
    # sending many requests is equal to sending one request, from the "state" of the backend.
    if to_be_deleted_doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    kb_manager.remove_document_from_kb(to_be_deleted_doc)
