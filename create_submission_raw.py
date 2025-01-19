from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv

load_dotenv("config.env")

from llms.watson import llm as llm

import os
import json
import ast
import pandas as pd



#
db = SQLDatabase.from_uri("sqlite:///data_sql.db")

print(db.get_usable_table_names())


with open('HackapizzaDataset/Misc/dish_mapping.json', 'r') as f:
    dishes_mapping = json.load(f)
    dishes_mapping = {k.replace(" ", "").replace("-", "").lower(): v for k,v in dishes_mapping.items()}

def run(question, convert = True):

    print(question)
    system_prompt = f"""
    You are a extremely accurate SQL expert. 
    You are provided with the data model of a DB about alien cuisine. Besides the dishes and its ingredients, dishes can be cooked with particular techniques, and
    restaurants (and their chefs) are associated to licenses that allow them to use specific techniques. Restaurants are located on planets.
    You should write a SQL Query whose result can answer the given question.
    The query must be based only on the provided data model.
    
    When writing WHERE clauses, always use the LOWER function to make the query case-insensitive and use LOWER LIKE '%value%' statement. Also, remove all whitespaces with REPLACE.
    If you need to escape characters, use the ' character before the character to escape, for example LOWER LIKE '%l''esempio%'
    
    'id' columns must only be used to join tables. Avoid comparing IDs with < or > operators, just use = operator. 
    When asked about "ristoranti X anni luce da PIANETA", find other planets within the provided range from PIANETA.
        
    Example 1:
    - Question: Quali piatti sono preparati con la tecnica della marinatura temporale non sincronizzata e del congelamento luminiscente sincronico?
      SQL Query: SELECT d.name 
        FROM dishes d 
        JOIN technique t1 ON d.id = t1.dish_id 
        JOIN technique t2 ON d.id = t2.dish_id 
        WHERE REPLACE(LOWER(t1.name),' ','') LIKE REPLACE(LOWER('%Marinatura Temporale Non Sincronizzata%'),' ','') 
        AND REPLACE(LOWER(t2.name),' ','') LIKE REPLACE(LOWER('%Congelamento Luminiscente Sincronico%'),' ','') 
    Example 2:
    - Question: Quali piatti speciali sono stati creati utilizzando le tecniche di impasto del di Sirius Cosmo?
      SQL Query: SELECT DISTINCT d.name 
                FROM dishes d 
                JOIN technique t ON d.id = t.dish_id 
                WHERE REPLACE(LOWER(t.name),' ','') LIKE REPLACE(LOWER('%Impasto%'),' ','') 
                
    Data Model: {db.get_context()} 
    """

    question_prompt = f"""
    Return only the SQL query. This task is very important for me, so write the query with care. Follow the provided instructions and the request carefully.

    Question: {question}
    SQL Query:
    """
    result = llm.chat(messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': question_prompt}])['choices'][0]['message']['content']


    result = result.replace("```sql", "").replace("```", "")
    try:
        print(result)
        query_res = db.run(result)
        print(query_res)
        if convert:
            query_res = ast.literal_eval(query_res)
            query_res = [dishes_mapping[x[0].replace(" ", "").replace("-", "").lower()] for x in query_res]
            query_res = list(set(query_res)) #remove duplicates
            print(query_res)
        else:
            format_prompt = f"""
            Format a short and brief answer to the question using a verbose and friendly tone and the provided dishes that answer the question.
            The answer should be one sentence long.
            Do not make up information that was not provided within the prompt.
            DISHES: {query_res}"""

            user_prompt=f"""
            QUESTION: {question}
            """

            query_res = llm.chat(messages=[
                {'role': 'system', 'content': format_prompt},
                {'role': 'user', 'content': user_prompt}])['choices'][0]['message']['content']

    except Exception as e:
        print(e)
        query_res = [('empty',)] #return INVALID
        query_res = [dishes_mapping.get(x[0].replace(" ", "").replace("-", "").lower(), -1) for x in query_res]

    return query_res

if __name__ == "__main__":
    import os

    test_set = pd.read_csv("HackapizzaDataset/domande.csv")

    results = test_set.head(2).domanda.apply(run)
    results_as_df = pd.DataFrame(results).reset_index()
    results_as_df.to_csv("results_raw.csv")
    results_as_df.columns = ["row_id", "result"]
