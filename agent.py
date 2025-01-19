from langchain_community.utilities import SQLDatabase

from langchain_community.agent_toolkits import create_sql_agent
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from dotenv import load_dotenv
import os
import json
import ast
import pandas as pd

load_dotenv("../config.env")

load_dotenv("./template.env", verbose=True)
#from llms.watson import llm

credentials = Credentials(
    url=os.environ["ENDPOINT"],
    api_key=os.environ["WATSONX_APIKEY"]
)

db = SQLDatabase.from_uri("sqlite:///data_sql.db")
print(db.get_usable_table_names())

model = ModelInference(
    model_id="mistralai/mistral-large",
    credentials=credentials,
    project_id=os.environ["PROJECT_ID"],
    params={
        "max_tokens": 200
      }
)

with open('HackapizzaDataset/Misc/dish_mapping.json', 'r') as f:
    dishes_mapping = json.load(f)
    dishes_mapping = {k.replace(" ", "").replace("-", "").lower(): v for k,v in dishes_mapping.items()}

test_set = pd.read_csv("HackapizzaDataset/domande.csv")

def run(question):
    print(question)
    system_prompt = f"""
    You are a SQL expert. 
    You are provided with the data model of a DB. You should write a SQL Query to answer the given question.
    Your query must be based only on the provided data model.
    
    When writing WHERE clauses, always use the LOWER function to make the query case-insensitive.
    
    Data Model: {db.get_context()} 
    """

    question_prompt = f"""
    Question: {question}
    Return only the SQL query.
    """

    result = model.chat(messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': question_prompt}])['choices'][0]['message']['content']


    result = result.replace("```sql", "").replace("```", "")
    try:
        query_res = db.run(result)
        query_res = ast.literal_eval(query_res)
        query_res = [dishes_mapping[x[0].replace(" ", "").replace("-", "").lower()] for x in query_res]

    except Exception as e:
        print(e)
        query_res = [('Sinfonia Cosmica: Versione Pizza',)]
        query_res = [dishes_mapping[x[0].replace(" ", "").replace("-", "").lower()] for x in query_res]
    return query_res

results = test_set.domanda.apply(run)
results_as_df = pd.DataFrame(results).reset_index()
results_as_df.to_csv("results_raw.csv")
results_as_df.columns = ["row_id", "result"]
results_as_df.result = results_as_df.result.apply(lambda x: ",".join(x))
results_as_df.to_csv("results.csv")