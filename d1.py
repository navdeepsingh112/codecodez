import os
from PyPDF2 import PdfReader, PdfWriter

def extract_pages(input_path, start_page, end_page, output_path="output.pdf"):
    """
    Extracts pages from start_page to end_page (inclusive)
    and saves them into a single PDF file.
    Page numbers are 1-based.
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()

    # Validate page range
    total_pages = len(reader.pages)
    if start_page < 1 or end_page > total_pages or start_page > end_page:
        raise ValueError(f"Invalid page range. PDF has {total_pages} pages.")

    # Add selected pages
    for i in range(start_page - 1, end_page):  # 0-based indexing
        writer.add_page(reader.pages[i])

    # Write output
    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"Saved: {output_path} (Pages {start_page} to {end_page})")

if __name__ == "__main__":
    extract_pages("input.pdf", start_page=9, end_page=17, output_path="17.pdf")
