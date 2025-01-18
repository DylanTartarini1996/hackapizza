from models.tagged_chunks.model import TaggedChunk
from models.vectordb.model import VectorDBConfiguration
from embedder import Embedder
from models.tagged_chunks.model import TaggedChunk
from abc import abstractmethod
from typing import List

class VectorDB:
    def __init__(self, conf: VectorDBConfiguration):
        self.conf = conf
        self._configure()

    @abstractmethod
    def _configure(self):
        # init vectordb instance

    @property
    def retriever(self):
        #return langchain like retriever

    def ingest(self, chunks: List[TaggedChunk], embedder):
        pass


