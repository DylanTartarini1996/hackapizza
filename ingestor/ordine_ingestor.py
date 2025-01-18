from pprint import pprint

import unicodedata

from ingestor.base import BaseIngestor
import re
import fitz
from ingestor.ingestion.cleaner import Cleaner

from schemas.pydantic_schemas import OrderEnum, Order


class OrderIngestor(BaseIngestor):
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

    def parse_order_chunk(self, chunk: str) -> Order:
        header_pattern = r"<h3>(.*?)</h3>"  # Matches the <h3> tag (emoji + order name)
        description_pattern = r"</h3>(.*?)$"  # Matches the description after the </h3> tag

        # Extract header (emoji + name)
        header_match = re.search(header_pattern, chunk)
        header = header_match.group(1) if header_match else ""
        emoji, name = header.split(" ", 1)  # Split into emoji and name

        # Extract description
        description_match = re.search(description_pattern, chunk, re.DOTALL)
        description = description_match.group(1).strip() if description_match else ""

        # Map name to the correct OrderEnum category
        name_to_enum = {
            "Ordine della Galassia di Andromeda": OrderEnum.ANDROMEDA,
            "Ordine dei Naturalisti": OrderEnum.NATURALISTI,
            "Ordine degli Armonisti": OrderEnum.ARMONISTI,
        }

        # Default to UNKNOWN if the name doesn't match
        category = name_to_enum.get(name, OrderEnum.UNKNOWN)

        # Create the Order model
        order = Order(name=name, description=description, category=category, emoji=emoji)

        return order

    def run(self, pdf_path):
        pattern = r'(?=<h1>.*?</h1>)'

        html_output = self.extract_text_by_font_size(pdf_path)
        html_content = "\n".join(html_output)

        chunks = re.split(pattern, html_content)
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

        capitolo_2 = chunks[2]

        pattern = r'(?=<h3>.*?</h3>)'
        capitolo_2_chunks = re.split(pattern, capitolo_2)

        capitolo_2_clean_chunks = [self.cleaner._clean_text(chunk.strip()) for chunk in capitolo_2_chunks]
        capitolo_2_clean_chunks = [self.clean_corrupted_text(chunk) for chunk in capitolo_2_clean_chunks]

        orders = []
        for chunk in capitolo_2_clean_chunks:
            if chunk.startswith("<h3"):
                orders.append(self.parse_order_chunk(chunk))
        return orders



if __name__=="__main__":
    ingestor = OrderIngestor()
    pdf_path = "../Hackapizza Dataset/Misc/Manuale di Cucina.pdf"
    orders = ingestor.run(pdf_path=pdf_path)
    for order in orders:
        pprint(order)

