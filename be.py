import json

from langchain_ibm import WatsonxLLM
from langchain_core.output_parsers import StrOutputParser
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.wml_client_error import WMLClientError
from dotenv import load_dotenv
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableParallel

from knowledge_base import retriever
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from pydantic import BaseModel, root_validator, Field


load_dotenv('template.env')

parameters = {
    "decoding_method": "sample",
    "max_new_tokens": 100,
    "min_new_tokens": 1,
    "temperature": 0.5,
    "top_k": 50,
    "top_p": 1,
}

class WatsonLLMConfig(BaseModel):
    decoding_method: str
    max_new_tokens: int
    min_new_tokens: int
    temperature: float
    top_k: int
    top_p: int

    @root_validator(pre=True)
    def validate(cls, values):

        assert values["top_k"] > 0 and values["top_p"] > 0
        return values

conf = WatsonLLMConfig(**parameters)

try:
    llm = WatsonxLLM(
        model_id="ibm/granite-13b-instruct-v2",
        url="https://us-south.ml.cloud.ibm.com",
        project_id="PASTE YOUR PROJECT_ID HERE",
        params=conf.model_dump(),
    )
except WMLClientError:
    print("IBM Token missing, importing OLLAMA as fallback")
    from langchain_ollama import ChatOllama
    llm = ChatOllama(
        model="llama3.1",
        temperature=0
    )

class OutputLLM(BaseModel):
    response: str = Field(description="Textual response")
    reasoning: str = Field(description="Your reasoning")


from langchain_core.output_parsers import PydanticOutputParser

system_prompt_template = """
test
{context}

"""
human_prompt_template = """
Question: {question}.
Answer:
"""
# parser = PydanticOutputParser(pydantic_object=OutputLLM)
# human_prompt_template += parser.get_format_instructions()

def filter(x):
    return x["out"]

chat_history_for_chain = ChatMessageHistory()

retriever_chain = {"context": retriever, "question": RunnablePassthrough()}
main_chain = ChatPromptTemplate.from_messages([("system", system_prompt_template), MessagesPlaceholder("chat_history"),("human", human_prompt_template)]) | \
    RunnableParallel({"out":llm, "log": RunnableLambda(print)}) | RunnableLambda(filter) |  StrOutputParser()

chain_with_message_history = RunnableWithMessageHistory(
    main_chain,
    lambda session_id: chat_history_for_chain,
    input_messages_key="question",
    history_messages_key="chat_history",
)

conv_chain = retriever_chain | chain_with_message_history

def run(human_message:str):
    out = conv_chain.invoke(human_message, {"configurable": {"session_id": "12345678"}})
    return out

print(run("Chi sei"))