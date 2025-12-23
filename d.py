import os
from PyPDF2 import PdfReader, PdfWriter

def split_pdf(input_path, output_dir="pdf"):
    # Make output directory if not exists
    os.makedirs(output_dir, exist_ok=True)

    reader = PdfReader(input_path)

    for i, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)

        output_path = os.path.join(output_dir, f"{i}.pdf")
        with open(output_path, "wb") as f:
            writer.write(f)

        print(f"Saved: {output_path}")

if __name__ == "__main__":
    split_pdf("input.pdf")
