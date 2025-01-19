from pprint import pprint
from typing import List
import uuid
import os
import unicodedata

from ingestor.base import BaseIngestor
import re
import fitz
from ingestor.ingestion.cleaner import Cleaner
from ingestor.chunk import Chunk

from schemas.pydantic_schemas import OrderEnum, Order, TechniqueSubCategory, Technique, MacroTechnique
from src.models.manuals import LicenseCategory, LicenseLevel

def uuid_from_cat_name(name: str):
    namespace = uuid.NAMESPACE_URL
    return str(uuid.uuid5(namespace, name))


class TechniqueIngestor(BaseIngestor):
    def __init__(self):
        self.cleaner = Cleaner()

    def extract_text_by_font_size(
            self,
            pdf_path,
            h1_font_size: int = 18,
            h2_font_size: int = 15,
            h3_font_size: int = 12
    ):
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
                            if font_size >= h1_font_size:
                                text_output.append(f"<h1>{text}</h1>")  # Representing chapter
                            elif font_size >= h2_font_size:
                                text_output.append(f"<h2>{text}</h2>")
                            elif font_size >= h3_font_size:
                                text_output.append(f"<h3>{text}</h3>")
                            else:
                                text_output.append(f"<p>{text}</p>")  # Regular text

        return text_output

    def clean_corrupted_text(self, input_text):
        # Normalize text to separate base characters from combining marks
        normalized_text = unicodedata.normalize('NFKD', input_text)
        # Remove combining marks using a regex
        cleaned_text = re.sub(r'[\u0300-\u036f]', '', normalized_text)
        # Remove excessive spaces
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        return cleaned_text

    def parse_sub_technique_chunk(self, chunk: str) -> TechniqueSubCategory:
        # Regex patterns to extract different sections of the text
        header_pattern = r"<h3>(.*?)</h3>"  # Matches the <h3> tag (technique name)
        how_it_works_pattern = r"Come funziona: (.*?) Vantaggi:"  # Matches how it works part
        pros_pattern = r"Vantaggi: (.*?) Svantaggi:"  # Matches pros part
        cons_pattern = r"Svantaggi: (.*)$"  # Matches cons part, everything after Svantaggi:

        # Extract name from the <h3> tag
        header_match = re.search(header_pattern, chunk)
        name = header_match.group(1) if header_match else ""

        # Extract "how it works" part
        how_it_works_match = re.search(how_it_works_pattern, chunk, re.DOTALL)
        how_it_works = how_it_works_match.group(1).strip() if how_it_works_match else ""

        # Extract "pros" part
        pros_match = re.search(pros_pattern, chunk, re.DOTALL)
        pros = pros_match.group(1).strip() if pros_match else ""

        # Extract "cons" part
        cons_match = re.search(cons_pattern, chunk, re.DOTALL)
        cons = cons_match.group(1).strip() if cons_match else ""

        # Create the TechniqueSubCategory model
        return TechniqueSubCategory(name=name, how_it_works=how_it_works, pros=pros, cons=cons)

    def parse_technique_chunk(self, chunk: str) -> Technique:
        # Regex patterns to extract different sections of the text
        category_pattern = r"<h2>(.*?)</h2>"  # Matches the <h2> tag (category name)
        description_pattern = r"<h2>.*?</h2>(.*)"  # Matches everything after the <h2> tag (description)

        # Extract category from the <h2> tag
        category_match = re.search(category_pattern, chunk)
        category = category_match.group(1) if category_match else ""

        # Extract description part
        description_match = re.search(description_pattern, chunk, re.DOTALL)
        description = description_match.group(1).strip() if description_match else ""

        # Create the Technique model
        return Technique(category=category, description=description)

    def parse_macro_technique_chunk(self, chunk: str) -> MacroTechnique:
        # Regex pattern to extract the name without the chapter number and 'Capitolo'
        name_pattern = r"<h1>Capitolo \d+: (.*?)</h1>"  # Exclude 'Capitolo' and chapter number
        description_pattern = r"<h1>.*?</h1>(.*)"  # Matches everything after the <h1> tag (description)

        # Extract name from the <h1> tag, excluding 'Capitolo' and number
        name_match = re.search(name_pattern, chunk)
        name = name_match.group(1) if name_match else ""

        # Extract description part
        description_match = re.search(description_pattern, chunk, re.DOTALL)
        description = description_match.group(1).strip() if description_match else ""

        # Create the MacroTechnique model
        return MacroTechnique(name=name, description=description)


    def run(self, pdf_path) -> List[MacroTechnique]:
        pattern = r'(?=<h1>.*?</h1>)'

        html_output = self.extract_text_by_font_size(pdf_path)
        html_content = "\n".join(html_output)

        chunks = re.split(pattern, html_content)
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

        tech_pattern = r'(?=<h2>.*?</h2>)'
        sub_tech_pattern = r'(?=<h3>.*?</h3>)'

        macro_techniques = []
        for i in range(3, 6):
            cap = self.cleaner._clean_text(chunks[i])
            cap = self.clean_corrupted_text(cap)

            cap_techniques = re.split(tech_pattern, cap)
            cap_techniques_clean = [chunk.strip() for chunk in cap_techniques if chunk.strip()]

            macro_tech = self.parse_macro_technique_chunk(cap_techniques_clean[0])

            techniques = []
            for technique in cap_techniques[1:]:
                chunks_t = re.split(sub_tech_pattern, technique)
                chunks_t_clean = [chunk.strip() for chunk in chunks_t if chunk.strip()]

                sub_techs = []
                for c in chunks_t_clean[1:]:
                    sub_techs.append(self.parse_sub_technique_chunk(c))

                tech = self.parse_technique_chunk(chunks_t_clean[0])
                tech.sub_categories = sub_techs
                techniques.append(tech)

            macro_tech.techniques = techniques
            macro_techniques.append(macro_tech)

        return macro_techniques
    

    def chunks_from_doc(self, file_path: str) -> List[Chunk]:
        chunks = []

        macro_techniques = self.run(file_path)

        filename = os.path.basename(file_path)

        for mt in macro_techniques:

            chunk = Chunk(
                id=uuid_from_cat_name(mt.name),
                filename=filename,
                text=mt.name+"\n"+mt.description
            )

            chunks.append(chunk)

            for t in mt.techniques:

                _chunk = Chunk(
                    id=uuid_from_cat_name(t.category),
                    filename=filename,
                    text=t.category+"\n"+t.description
                )

                chunks.append(_chunk)

                for st in t.sub_categories:
                    __chunk = Chunk(
                        id=uuid_from_cat_name(st.name),
                        filename=filename,
                        text=st.name+"\n"+st.how_it_works+"\n PROS: "+st.pros+"\n CONS: "+st.cons
                    )

                    chunks.append(__chunk)
        
        return chunks


if __name__=="__main__":
    ingestor = TechniqueIngestor()
    pdf_path = "../Hackapizza Dataset/Misc/Manuale di Cucina.pdf"
    techniques = ingestor.run(pdf_path=pdf_path)
    for technique in techniques:
        pprint(technique)
