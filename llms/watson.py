from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
import os

load_dotenv("../config.env")

credentials = Credentials(
    url=os.environ["ENDPOINT"],
    api_key=os.environ["WATSONX_APIKEY"]
)
parameters = {
    "temperature": 0.5,
    "top_p": 1,
}

llm = ModelInference(
    model_id="meta-llama/llama-3-3-70b-instruct", #codellama/codellama-34b-instruct-hf
    credentials=credentials,
    project_id=os.environ["PROJECT_ID"],
    params=parameters
)
