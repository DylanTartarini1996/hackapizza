from dotenv import load_dotenv
from langchain_ibm import WatsonxLLM
import os

load_dotenv("../template.env")

parameters = {
    "decoding_method": "sample",
    "max_new_tokens": 100,
    "min_new_tokens": 1,
    "temperature": 0.5,
    "top_k": 50,
    "top_p": 1,
}

llm = WatsonxLLM(
        model_id="meta-llama/llama-3-3-70b-instruct",
        url="https://us-south.ml.cloud.ibm.com",
        project_id="953436b9-d6f8-4c6c-a62e-389fc4c9b018",
        params=parameters,
    )