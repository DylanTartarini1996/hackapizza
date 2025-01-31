import json
from logging import getLogger

from enum import Enum
from pydantic import BaseModel
from typing import Optional


logger = getLogger(__name__)


class ModelType(str, Enum):
    """
    Type of embedders available in the toolkit
    """
    TRANSFORMERS = "trf"
    OPENAI = "openai"
    OLLAMA = "ollama"
    IBM = "ibm"


class ChunkerType(str, Enum):
    """
    Type of chunkers available in the toolkit
    """
    RECURSIVE = "recursive"
    # PLAIN = "plain" # TODO implement plain chunker
    # SEMANTIC = "semantic" # TODO implement SEMANTIC chunker


class Source(BaseModel):
    folder: str
    # TODO add specific source configurations


class ChunkerConf(BaseModel):
    type: ChunkerType = "recursive"
    chunk_size: int = 1000
    chunk_overlap: int = 100


class LLMConf(BaseModel):
    """
    Configuration for a LLM
    -----------
    attributes:
    -----------
    `type`: LLM `ModelType` 
    `temperature`: LLM temperature param
    `deployment`: represents the name of the deployment.
    `model`: represents the name of the model
    `api_key`: reference to the OpenAI key, if any
    `endpoint`: reference to the endpoint of the model, if any
    """
    model: str
    temperature: float = 0.0
    type: ModelType="openai"
    deployment: Optional[str]=None
    api_key: Optional[str]=None
    endpoint: Optional[str]=None


class EmbedderConf(BaseModel):
    """
    Embeddings model configuration  

    -----------
    attributes:
    -----------
    `type`: LLM `ModelType` 
    `deployment`: represents the name of the deployment.
    `model`: represents the name of the model
    `api_key`: reference to the OpenAI key, if any
    `endpoint`: reference to the endpoint of the model, if any
    """
    type: ModelType = "openai"
    model: Optional[str] = "text-embedding-ada-002"
    deployment: Optional[str] = None
    api_key: Optional[str] = None
    endpoint: Optional[str] = None


class Configuration(BaseModel):
    """
    Configuration for the Knowledge Base Project. 
    This will include configurations for the backend (the Graph DB of choice) as well as 
    configurations for users and for models in charge of producing and deleting entities in the KB.

    -----------
    attributes:
    -----------
    `kb_database`: configuration to access the Graph Database
    `document_source`: configuration storing informations on where to fetch documents from
    `extraction_model_conf`: configuration for the LLM in charge of extracting data models from documents
    `embedder_conf`: configuration for the Embeddings model that will create vectors out of documents
    `qa_model`: configuration for the Q&A model (LLM) that will interact with the user
    """
    chunker_conf: Optional[ChunkerConf] = None
    source_conf: Optional[Source] = None
    extraction_model_conf: Optional[LLMConf] = None
    embedder_conf: Optional[EmbedderConf] = None
    qa_model: Optional[LLMConf] = None
    
    
    @classmethod
    def from_file(cls, filename):
        with open(filename, "r") as f:
            configuration_data = json.load(f)

        configuration = Configuration(**configuration_data)
        logger.info(f"Loaded configuration from {filename}")
        return configuration
