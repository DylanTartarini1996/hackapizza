from models.embedder.model import EmbedderConfiguration
from abc import abstractmethod

class Embedder:
    def __init__(self, conf: EmbedderConfiguration):
        self.conf = conf

    @abstractmethod
    def embed(self):
        pass