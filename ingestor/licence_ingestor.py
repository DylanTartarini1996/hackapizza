from pprint import pprint

from typing import List
import unicodedata
import uuid
import os

from ingestor.base import BaseIngestor
import re
import fitz
from ingestor.ingestion.cleaner import Cleaner
from ingestor.chunk import Chunk

from schemas.pydantic_schemas import OrderEnum, Order
from src.models.manuals import LicenseCategory, LicenseLevel


def uuid_from_filename(filename, chunk_id: int):
    namespace = uuid.NAMESPACE_URL
    return str(uuid.uuid5(namespace, filename+"chunk_"+str(chunk_id)))


class LicenceIngestor(BaseIngestor):
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

    def parse_category_chunk(self, chunk: str) -> LicenseCategory:
        # Regex patterns
        header_pattern = r"<h3>(.*?)</h3>"  # Extract the header inside <h3> tags
        level_pattern = r"Livello\s([0-9IVXLn+]+):\s(.*?)(?=Livello\s[0-9IVXLn+]+:|$)"  # Extract levels and descriptions

        # Extract header
        header_match = re.search(header_pattern, chunk)
        header = header_match.group(1) if header_match else "Unknown Header"

        # Extract levels
        levels = []
        for level_match in re.finditer(level_pattern, chunk, re.DOTALL):
            level = level_match.group(1)
            description = level_match.group(2).strip()
            levels.append(LicenseLevel(level=level, level_description=description))

        # Create and return the Pydantic model
        return LicenseCategory(name=header, available_levels=levels)

    def run(self, pdf_path):
        pattern = r'(?=<h1>.*?</h1>)'

        html_output = self.extract_text_by_font_size(pdf_path)
        html_content = "\n".join(html_output)

        chunks = re.split(pattern, html_content)
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

        capitolo_1 = self.cleaner._clean_text(self.clean_corrupted_text(chunks[1]))

        pattern = r'(?=<h3>.*?</h3>)'
        capitolo_1_chunks = re.split(pattern, capitolo_1)

        capitolo_1_clean_chunks = [chunk.strip() for chunk in capitolo_1_chunks if chunk.strip()]

        licences = []
        for chunk in capitolo_1_clean_chunks:
            if chunk.startswith("<h3"):
                licences.append(self.parse_category_chunk(chunk))
        return licences
    

    def chunks_from_doc(self, file_path: str) -> List[Chunk]:
        pattern = r'(?=<h1>.*?</h1>)'

        html_output = self.extract_text_by_font_size(file_path)
        html_content = "\n".join(html_output)

        chunks = re.split(pattern, html_content)
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

        capitolo_1 = self.cleaner._clean_text(self.clean_corrupted_text(chunks[1]))

        pattern = r'(?=<h3>.*?</h3>)'
        capitolo_1_chunks = re.split(pattern, capitolo_1)

        capitolo_1_clean_chunks = [chunk.strip() for chunk in capitolo_1_chunks if chunk.strip()]
        
        filename = os.path.basename(file_path)
        final_chunks = []

        for i, c in enumerate(capitolo_1_clean_chunks):

            chunk = Chunk(
                id=uuid_from_filename(filename=filename, chunk_id=i),
                filename=filename, 
                text=c
            )
            final_chunks.append(chunk)

        return final_chunks

if __name__=="__main__":
    ingestor = LicenceIngestor()
    pdf_path = "../Hackapizza Dataset/Misc/Manuale di Cucina.pdf"
    licences = ingestor.run(pdf_path=pdf_path)
    for licence in licences:
        pprint(licence)
