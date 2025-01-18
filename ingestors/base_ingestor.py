from models.ingestors.model import IngestorConfiguration
from models.tagged_chunks.model import TaggedChunk
from typing import List
from abc import abstractmethod

class BaseIngestor():

    def __init__(self, conf: IngestorConfiguration):
        self.conf: IngestorConfiguration = conf

    @abstractmethod
    def run(self) -> List[TaggedChunk]:
        pass



