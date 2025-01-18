from abc import abstractmethod

class BaseIngestor:

    @abstractmethod
    def run(self):
        pass
