import pytest

from src.knowledge_base.exception import FAISSCreationFailed
from src.knowledge_base.manager import KnowledgeBaseManager, query_kb_for_similar_documents
from src.knowledge_base.schema import KnowledgeBase


def test_memorization_state_validity():
    kb = KnowledgeBase(name="Some knowledge", documents={})
    kb_manager = KnowledgeBaseManager(kb=kb, max_to_memorize=5)
    # does not create since there are no documents
    assert len(kb_manager.index_cache) == 0

    kb_manager.add_document_to_kb("Some text")
    # is idempotent, should not create new index once it's created
    kb_manager.kb.hashable_key()
    kb_manager.get_or_create_index()
    kb_manager.get_or_create_index()
    kb_manager.get_or_create_index()
    # should still be 1, because we don't add new index on document insertion
    assert len(kb_manager.index_cache) == 1

    # adding new document should not create a new index
    # as we reuse the same index for performance
    added_document = kb_manager.add_document_to_kb("Some New Text")
    old_index = kb_manager.get_or_create_index()
    old_key = kb_manager.kb.hashable_key()
    kb_manager.get_or_create_index()
    kb_manager.get_or_create_index()
    assert len(kb_manager.index_cache) == 1

    # removing a document should create a new index always
    kb_manager.remove_document_from_kb(added_document)
    kb_manager.get_or_create_index()
    kb_manager.get_or_create_index()
    assert len(kb_manager.index_cache) == 2

    # adding back the removed document should not create a new index
    # since we already memorized the state
    kb_manager.add_document_to_kb(added_document.text, added_document.id)
    new_index = kb_manager.get_or_create_index()
    new_key = kb_manager.kb.hashable_key()
    assert new_key == old_key
    assert new_index is old_index

    # check that the index never gets more than 5
    for _ in range(10):
        kb_manager.add_document_to_kb("Some text")
        assert len(kb_manager.index_cache) <= 5


@pytest.mark.asyncio
async def test_queury_with_no_documents():
    with pytest.raises(FAISSCreationFailed):
        kb = KnowledgeBase(name="Some knowledge", documents={})
        kb_manager = KnowledgeBaseManager(kb=kb, max_to_memorize=5)
        await query_kb_for_similar_documents(
            kb_manager, kb_manager.get_embed_document("Some text"), 5
        )


# other test (like the adding of document and etc) is tested by the integration test
# and does not need to be tested here.
# because it does not offer us as high confidence as the integration test :)
