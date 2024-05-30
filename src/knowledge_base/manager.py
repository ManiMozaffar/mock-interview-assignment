from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache
from typing import Any, Callable, Iterable
from uuid import uuid4

from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from more_itertools import first_true

from src.knowledge_base.exception import DocumentDoesNotExist, FAISSCreationFailed
from src.knowledge_base.schema import EmbeddedDocument, KnowledgeBase
from src.knowledge_base.type import EmbeddedDocumentId, KnowledgeBaseHashId


async def query_kb_for_similar_documents(
    kb_manager: KnowledgeBaseManager,
    query_document: EmbeddedDocument,
    top_n_results: int = 5,
    filter_: None | Callable | dict[str, Any] = None,
    fetch_k: int = 20,
) -> Iterable[EmbeddedDocument]:
    """
    Query a knowledge base for similar documents to the query document.

    if top_n_results is less than documents in the knowledge base, all documents will be returned then (not causing error).
    That's why the return type is Iterable[DocumentQueryResult] instead of list[DocumentQueryResult], to avoid you trying to access with index.


    Attributes:
        kb_manager: The knowledge base manager.
        k: Number of Documents to return. Defaults to 4.
        filter: Filter by metadata. Defaults to None. If a callable, it must take as input the
            metadata dict of Document and return a bool.
        fetch_k: Number of Documents to fetch before filtering. Defaults to 20.
    """
    db = kb_manager.get_or_create_index()

    similiar_docs = await db.asimilarity_search_by_vector(
        query_document.embedding, k=top_n_results, fetch_k=fetch_k, filter=filter_
    )
    result: list[EmbeddedDocument] = []
    for doc in similiar_docs:
        # there is better way to do this. one way is to attach the document id to `metadata`
        # but idk what the side effect of the metadata, and if it actually has some side effect
        # so proper research is needed

        similiar_doc = first_true(
            text for text in kb_manager.kb.documents.values() if text == doc.page_content
        )
        assert similiar_doc is not None, "Document not found in the knowledge base"  # impossible?
        result.append(similiar_doc)

    # result is already sorted by similarity thanks to langchain
    return result


@lru_cache
def load_sentence_transformer_model():
    return SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


@contextmanager
def limit_dict_size(dct: dict, limit: int):
    """Limit the size of a dictionary to a given limit."""

    while len(dct) > limit:
        dct.popitem()
    yield
    while len(dct) > limit:
        dct.popitem()


def _create_faiss_index(kb: KnowledgeBase, model: SentenceTransformerEmbeddings | None = None):
    model = model or load_sentence_transformer_model()
    embedding = [(doc.text, doc.embedding) for doc in kb.documents.values()]
    if embedding:
        return FAISS.from_embeddings(embedding, model)
    return None


class KnowledgeBaseManager:
    """Manager to handle knowledge base operations.

    This class is responsible for handling knowledge base operations such as adding and removing documents.
    It also manages the FAISS index for the knowledge base.

    Memorize the FAISS index for each knowledge base to avoid recreating the index every time a query is made.
        Simply by caching the "hash" of knowledgebase, and map it to relative index.

        The cache is dropped once there is more than `max_to_memorize` indexes in the cache.

    Attributes:
        kb: The knowledge base.
        model: The sentence transformer model to use for embeddings.
        max_to_memorize: The maximum number of indexes to memorize.
    """

    kb: KnowledgeBase
    model: SentenceTransformerEmbeddings
    max_to_memorize: int

    def __init__(
        self,
        kb: KnowledgeBase,
        model: SentenceTransformerEmbeddings | None = None,
        max_to_memorize: int = 5,
    ):
        """
        Manager to handle knowledge base operations.

        Attributes:
            kb: The knowledge base.
            model: The sentence transformer model to use for embeddings.
            max_to_memorize: The maximum number of indexes to memorize.
        """
        self.model = model or load_sentence_transformer_model()
        self.max_to_memorize = max_to_memorize

        self.kb = kb

        created_index = _create_faiss_index(kb, self.model)

        self.index_cache: dict[KnowledgeBaseHashId, FAISS] = {}
        if created_index is not None:
            self.index_cache[self.kb.hashable_key()] = created_index

    def add_document_to_kb(
        self, text: str, doc_id: EmbeddedDocumentId | None = None
    ) -> EmbeddedDocument:
        """
        Add a document to the knowledge base.
        Re-uses the previous index, to attach the new embedding to it to buy some performance
            to not recreate the index again

        Attributes:
            text: The text of the document to add.
            doc_id: The id of the document to add. If not provided, a new id will be generated.
        """
        with limit_dict_size(self.index_cache, self.max_to_memorize):
            old_index = self.kb.hashable_key()
            doc = self.get_embed_document(text, doc_id)
            self.kb.documents[doc.id] = doc

            db = self.index_cache.pop(old_index, None)
            if db:
                db.add_embeddings([(doc.text, doc.embedding)])

        return doc

    def remove_document_from_kb(self, document: EmbeddedDocument):
        """Remove a document from the knowledge base.

        Attributes:
            document: The document to remove.

        Raises:
            DocumentDoesNotExist: If the document does not exist in the knowledge base.
        """
        if document.id not in self.kb.documents:
            raise DocumentDoesNotExist(document_id=document.id, knowledge_base_id=self.kb.id)

        with limit_dict_size(self.index_cache, self.max_to_memorize):
            del self.kb.documents[document.id]

    def get_or_create_index(self) -> FAISS:
        """
        Checks the current state of the knowledge base and returns the latest index if it's already created.
        If not, creates a new index and returns it.

        Raises:
            FAISSCreationFailed: if there is no document in the knowledge base yet.
        """
        with limit_dict_size(self.index_cache, self.max_to_memorize):
            hash_key = self.kb.hashable_key()
            if hash_key in self.index_cache:
                return self.index_cache[hash_key]

            new_index = _create_faiss_index(self.kb)
            if new_index is not None:
                self.index_cache[hash_key] = new_index
                return new_index

            # TODO: this invariant could be avoided by forcing each knowledge base to have at least one document
            # on the initialization, but that affect business logic as well

            raise FAISSCreationFailed(kb_id=self.kb.id)

    def get_embed_document(
        self, text: str, doc_id: EmbeddedDocumentId | None = None
    ) -> EmbeddedDocument:
        """
        Embed a document and return it.

        Attributes:
            text: The text of the document to embed.
            doc_id: The id of the document. If not provided, a new id will be generated.
        """
        return EmbeddedDocument(
            id=doc_id or EmbeddedDocumentId(uuid4()),
            text=text,
            embedding=self.model.embed_documents([text])[0],
        )
