from pprint import pprint
from typing import Optional

from pydantic import BaseModel

from ingestor.base import BaseIngestor
import re
import fitz
from ingestor.ingestion.cleaner import Cleaner
from schemas.pydantic_schemas import OrderEnum


class MenuChunk(BaseModel):
    name: str
    description: str
    order: Optional[OrderEnum] = None


class PiattoChunkIngestor(BaseIngestor):
    def __init__(self):
        self.cleaner = Cleaner()

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

    def run(self, pdf_path):
        html_output = self.extract_text_by_font_size(pdf_path, disc_font_size=12)
        html_content = "\n".join(html_output)

        pattern = r'(?=<h1>.*?</h1>)'
        chunks = re.split(pattern, html_content)
        chunks = [self.cleaner._clean_text(chunk.strip()) for chunk in chunks if chunk.strip()]

        piatto_chunks = []
        for chunk in chunks[1:]:
            if chunk.startswith("<h1>Menu</h1>"):
                pass
            elif chunk.startswith("<h1>Legenda Ordini"):
                pass
            else:
                name_pattern = r"<h1>(.*?)</h1>"
                name_match = re.search(name_pattern, chunk)
                name = name_match.group(1) if name_match else ""

                description_pattern = r"</h1>(.*?)$"
                description_match = re.search(description_pattern, chunk, re.DOTALL)
                description = description_match.group(1).strip() if description_match else ""

                piatto_chunks.append(MenuChunk(name=name, description=description))

        return piatto_chunks


class RestaurantChunkIngestor(BaseIngestor):
    def __init__(self):
        self.cleaner = Cleaner()

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

    def run(self, pdf_path):
        html_output = self.extract_text_by_font_size(pdf_path, disc_font_size=12)
        html_content = "\n".join(html_output)

        pattern = r'(?=<h1>.*?</h1>)'
        chunks = re.split(pattern, html_content)
        chunks = [self.cleaner._clean_text(chunk.strip()) for chunk in chunks if chunk.strip()]

        return chunks[0]


if __name__=="__main__":
    # ingestor = PiattoChunkIngestor()
    # pdf_path = "../Hackapizza Dataset/Menu/Anima Cosmica.pdf"
    # piatti = ingestor.run(pdf_path=pdf_path)
    # for piatto in piatti:
    #     pprint(piatto)

    ingestor = RestaurantChunkIngestor()
    pdf_path = "../Hackapizza Dataset/Menu/Anima Cosmica.pdf"
    restaurant = ingestor.run(pdf_path=pdf_path)
    pprint(restaurant)

