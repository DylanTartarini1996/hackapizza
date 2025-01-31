from typing import List
from ingestor.base import BaseIngestor
import os
from os.path import isfile, join
import re
import fitz
import json
import uuid
from pprint import pprint
from ingestor.chunk import Chunk
from ingestor.ingestion.cleaner import Cleaner

from schemas.pydantic_schemas import RistoranteSchema, PiattoSchema

def uuid_from_filename(filename, chunk_id: int):
    namespace = uuid.NAMESPACE_URL
    return str(uuid.uuid5(namespace, filename+"chunk_"+str(chunk_id)))


class MenuIngestor(BaseIngestor):
    def __init__(self, llm):
        self.cleaner = Cleaner()
        self.llm = llm

    def extract_text_by_font_size(self, pdf_path, disc_font_size: int = 18):
        doc = fitz.open(pdf_path)
        text_output = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if block['type'] == 0:  # Text block
                    for line in block['lines']:
                        for span in line['spans']:
                            font_size = span['size']
                            text = span['text'].strip()

                            # Use font size to determine hierarchy
                            if font_size > disc_font_size:
                                text_output.append(f"<h1>{text}</h1>")  # Representing chapter
                            else:
                                text_output.append(f"<p>{text}</p>")  # Regular text

        return text_output

    def run(self, base_dir):
        restaurants = []
        restuarants_dst_dir = os.path.join(base_dir, 'output2', 'restaurants')
        dishes_dst_dir = os.path.join(base_dir, 'output2', 'dishes')
        errors_file = os.path.join(base_dir, 'output2', 'errors.txt')
        os.makedirs(restuarants_dst_dir, exist_ok=True)
        os.makedirs(dishes_dst_dir, exist_ok=True)
        files_to_process = os.listdir(base_dir)
        print(f"{len(files_to_process)} files to process")
        for filename in files_to_process:
            restaurant_out_file = os.path.join(restuarants_dst_dir, filename.replace('.pdf', '.json'))
            dish_out_file = os.path.join(dishes_dst_dir, filename.replace('.pdf', '.json'))

            if os.path.exists(restaurant_out_file) and os.path.exists(dish_out_file):
                continue
            if filename.endswith(".pdf"):
                print(filename)
                pattern = r'(?=<h1>.*?</h1>)'

                html_output = self.extract_text_by_font_size(os.path.join(base_dir,filename), 12)

                html_content = "\n".join(html_output)

                chunks = re.split(pattern, html_content)

                chunks = [self.cleaner._clean_text(chunk.strip()) for chunk in chunks if chunk.strip()]
                chunk_desc_ristorante = chunks[0]
                chunks_piatti = []
                ristorante_schema = RistoranteSchema(text=chunk_desc_ristorante)

                ristorante_schema.fill_llm_generated(self.llm)
                print(ristorante_schema.llm_generated)
                piatti_schemas = []
                for iter, chunk in enumerate(chunks[1:]):
                    if chunk.startswith("<h1>Menu</h1>"):
                        pass
                    elif chunk.startswith("<h1>Legenda Ordini"):
                        pass
                    else:
                        print(f"processing {iter} chunk")

                        piatti_schema = PiattoSchema(text=chunk)
                        piatti_schema.fill_llm_generated(self.llm)
                        piatti_schemas.append(piatti_schema)



                #ristorante_schema.piatti = piatti_schemas
                print(piatti_schemas)
                print(f"saving {restaurant_out_file}...")
                with open(restaurant_out_file, "w") as f:
                    json.dump(json.loads(ristorante_schema.model_dump_json(indent=2)), f, indent=2)
                with open(dish_out_file, "w") as f:
                    json.dump([json.loads(x.model_dump_json(indent=2)) for x in piatti_schemas], f, indent=2)

        return restaurants
    

    def chunks_from_docs(self, base_dir: str) -> List[Chunk]:
        final_chunks = []
        for filename in os.listdir(base_dir):
            if filename.endswith(".pdf"):
                pattern = r'(?=<h1>.*?</h1>)'

                html_output = self.extract_text_by_font_size(os.path.join(base_dir,filename), 12)

                html_content = "\n".join(html_output)

                chunks = re.split(pattern, html_content)

                chunks = [self.cleaner._clean_text(chunk.strip()) for chunk in chunks if chunk.strip()]
                

                for i, text in enumerate(chunks):
                    if text.startswith("<h1>Legenda Ordini"):
                        pass
                    fin_chunk = Chunk(
                        id=uuid_from_filename(filename, i),
                        filename=filename,
                        text=text
                    )
                    final_chunks.append(fin_chunk)
                
        return final_chunks

    

if __name__=="__main__":
    from llms.ollama import llm
    from dotenv import load_dotenv

    load_dotenv("../config.env")

    load_dotenv("template.env")

    # llama_conf = GroqConf(
    #     api_key=os.environ["GROQ_APIKEY"],
    #     model="llama3-70b-8192",
    #     temperature=0
    # )
    #
    # llm = ChatGroq(
    #     api_key=llama_conf.api_key,
    #     model=llama_conf.model,
    #     temperature=llama_conf.temperature
    # )

    ingestor = MenuIngestor(llm)

    restaurants = ingestor.run('../HackapizzaDataset/Menu')
    print(restaurants)



