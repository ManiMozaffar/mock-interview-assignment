from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

model = SentenceTransformerEmbeddings()

documents = [Document(page_content="Hey")]
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)
texts = ["FAISS is an important library", "LangChain supports FAISS"]
db = FAISS.from_texts(texts, model)
db.add_documents(docs)

print(db.similarity_search("Something important for python developers", k=1))
