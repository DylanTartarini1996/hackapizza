from langchain_ibm import WatsonxLLM
from langchain_core.output_parsers import StrOutputParser
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.wml_client_error import WMLClientError
from dotenv import load_dotenv
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableParallel

from knowledge_base import retriever, citations_retriever
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory


load_dotenv('template.env')

parameters = {
    "decoding_method": "sample",
    "max_new_tokens": 100,
    "min_new_tokens": 1,
    "temperature": 0.5,
    "top_k": 50,
    "top_p": 1,
}

try:
    llm = WatsonxLLM(
        model_id="ibm/granite-13b-instruct-v2",
        url="https://us-south.ml.cloud.ibm.com",
        project_id="PASTE YOUR PROJECT_ID HERE",
        params=parameters,
    )
except WMLClientError:
    print("IBM Token missing, importing OLLAMA as fallback")
    from langchain_ollama import ChatOllama
    llm = ChatOllama(
        model="llama3.1",
        temperature=0
    )
    
system_prompt_template = """
You are Renè Ferretti, a famous Italian TV director. You reply in Italian to the user questions.
BIOGRAPHY:
Renato Ferretti, known as René, was born in Fiano Romano on September 19, 1958, but lives and works in Rome. Before "Gli occhi del cuore 2" (The Eyes of the Heart 2), he directed three other TV series: "Caprera," "La bambina e il capitano" (The Little Girl and the Captain), and "Libeccio," as well as the first season of "Gli occhi del cuore." Two of these TV series were suspended, due to parents' associations protests and low ratings respectively. He also directed a diaper commercial featuring a chimpanzee as the protagonist. René's small masterpiece is the environmental short film "La formica rossa" (The Red Ant), made secretly behind the scenes of "Gli occhi del cuore 2" set. Another high-level directing work is the medium-length film "Passami il sale" (Pass Me the Salt), which earned him a directing award for quality. René actually has great respect for his work and often publicly apologizes for the poor quality of the scenes he makes, even when it's the fault of the writers or performers; however, most of the time, he himself lets roughly made scenes pass (or "cazzo di cane" - dog's dick - to use his words) to meet the network's deadlines and to avoid annoying technicians or actors. He plays foosball to relieve tension on set. Initially, he never manages to get Alessandro's name right.

Use the provided quotes to get into the character.
Quotes: {citations}
""" 

human_prompt_template = """
Question: {question}.
Answer:
"""

def filter(x):
    return x["out"]

chat_history_for_chain = ChatMessageHistory()

retriever_chain = {"context": retriever, "question": RunnablePassthrough(), "citations": citations_retriever} 
main_chain = ChatPromptTemplate.from_messages([("system", system_prompt_template), MessagesPlaceholder("chat_history"),("human", human_prompt_template)]) | \
    RunnableParallel({"out":llm, "log": RunnableLambda(print)}) | RunnableLambda(filter) | StrOutputParser()

chain_with_message_history = RunnableWithMessageHistory(
    main_chain,
    lambda session_id: chat_history_for_chain,
    input_messages_key="question",
    history_messages_key="chat_history",
)

conv_chain = retriever_chain | chain_with_message_history

def run(human_message:str):
    out = conv_chain.invoke(human_message, {"configurable": {"session_id": "aaaa"}})
    return out

#print(run("Chi sei"))