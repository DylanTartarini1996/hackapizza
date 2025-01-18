# from langchain_community.tools import WikipediaQueryRun
# from langchain_community.utilities import WikipediaAPIWrapper
# from langchain_ollama import OllamaEmbeddings
# from langchain_core.documents import Document
#
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.docstore.in_memory import InMemoryDocstore
# from langchain_community.vectorstores import FAISS
# import faiss
# from uuid import uuid4
# from typing import List
#
# from langchain_core.runnables import chain
#
# embedder = OllamaEmbeddings(model="nomic-embed-text")
#
# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=500, chunk_overlap=200, add_start_index=True
# )
# index = faiss.IndexFlatL2(len(embedder.embed_query("hello world")))
# vector_store = FAISS(
#     embedding_function=embedder,
#     index=index,
#     docstore=InMemoryDocstore(),
#     index_to_docstore_id={},
# )
#
# def knowledge_base():
#     text = """text to embed
#     """
#     cit_text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=500, chunk_overlap=10, add_start_index=True
#     )
#     doc = Document(page_content=text)
#     all_splits = cit_text_splitter.split_documents([doc])
#     uuids = [str(uuid4()) for _ in range(len(all_splits))]
#     vector_store.add_documents(documents=all_splits, ids=uuids)
#
# # def ingest(text):
# #     all_splits = text_splitter.split_documents([doc])
# #     uuids = [str(uuid4()) for _ in range(len(all_splits))]
# #     vector_store.add_documents(documents=all_splits, ids=uuids)
# #     knowledge_base()
#
# @chain
# def retriever(query: str) -> List[Document]:
#     return "\n\n".join([x.page_content for x in vector_store.similarity_search(query, k=4)])
#


from models.ingestors.model import IngestorConfiguration
from models.vectordb.model import VectorDBConfiguration
from models.embedder.model import EmbedderConfiguration

ingestor_configuration = IngestorConfiguration()
vectordb_configuration = VectorDBConfiguration()
embedder_configuration = EmbedderConfiguration()

ingestor = ...
