## Task for "Senior Python Backend Engineer" (f/m/d)

Thank you for your application to Parloa and your interest to solve our challenge!
To get to know you a bit more from the professional side, you will find the task in this document.

### Introduction

The challenge consists of creating a service to manage knowledge bases, add documents to a knowledge base and query the service to return similar documents.
A knowledge base is a collection of documents. Every time a document is added to a knowledge base, its embedding is calculated and appended to a vector store. In order to find similar documents to a queried document, the embedding of the new document and its distance to the other embeddings in vector space are calculated. The closer two vectors are, the more similar the corresponding documents will be.

### Task

Please create a service with the necessary endpoints to:

- Create and delete knowledge bases
- Add and remove documents from a knowledge base
- Retrieve similar documents from a knowledge base given a query document
  In-memory data structures should be used to store documents. To simplify the task we recommend using LangChain and the FAISS in-memory vector store that abstracts most of the logic around embedding calculation and document retrieval (https://python.langchain.com/docs/integrations/vectorstores/faiss). However, it is also possible to solve the challenge without it.

!!! info "Note"

    [Please use the following embedding model](https://huggingface.co/sentence-transformers/all-MiniLM-L12-v2)
    You’re expected to write clean, modular and tested code as well as Dockerfile to containerize the application.

### General information

The challenge shouldn't take longer than an afternoon. Since we understand that you have other daily obligations, we would like to ask you to inform us when we can expect your answer. Please also let us know in case you require more time. The results of the challenge will be used for our recruiting process only.
Don’t hesitate to drop us a message if you have any questions.
