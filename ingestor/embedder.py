from logging import getLogger
from typing import Union, List

from langchain.embeddings import HuggingFaceEmbeddings
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_openai.embeddings import OpenAIEmbeddings

from ingestor.config import EmbedderConf
from ingestor.chunk import Chunk

logger = getLogger(__name__)


class ChunkEmbedder:
    """ Contains methods to embed Chunks from a (list of) `ProcessedDocument`."""
    def __init__(self, conf: EmbedderConf):
        self.conf = conf
        self.embeddings = self.get_embeddings()

        if self.embeddings:
            logger.info(f"Embedder of type '{self.conf.type}' initialized.")


    def get_embeddings(self) -> Union[HuggingFaceEmbeddings, OllamaEmbeddings, OpenAIEmbeddings, None]:

        if self.conf.type == "ollama":
            embeddings = OllamaEmbeddings(
                model=self.conf.model
            )
        elif self.conf.type == "openai":
            embeddings = OpenAIEmbeddings(
                model=self.conf.model,
                api_key=self.conf.api_key,
                deployment=self.conf.deployment,
            )
        elif self.conf.type == "trf":
            embeddings = HuggingFaceEmbeddings(
                model=self.conf.model,
                endpoint=self.conf.endpoint,
            )
        else: 
            logger.warning(f"Embedder type '{self.conf.type}' not supported.")
            embeddings = None

        return embeddings
    

    def embed_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        if self.embeddings is not None:
            for chunk in chunks:
                chunk.embedding = self.embeddings.embed_documents([chunk.text])
                chunk.embeddings_model = self.conf.model
            logger.info(f"Embedded {len(chunks)} chunks.")
        return chunks