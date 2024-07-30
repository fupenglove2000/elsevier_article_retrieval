import os
import pikepdf
import logging

logging.basicConfig(filename='pdf_check.log', level=logging.ERROR)

def is_pdf_valid_pikepdf(file_path):
    try:
        with pikepdf.open(file_path) as pdf:
            # Just open and check the PDF, do not save it
            pass
        return True
    except pikepdf.PdfError as e:
        logging.error(f"pikepdf error opening {file_path}: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error for {file_path} with pikepdf: {e}")
        return False

def find_invalid_pdfs(directory):
    invalid_pdfs = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".pdf"):
                file_path = os.path.join(root, file)
                if not is_pdf_valid_pikepdf(file_path):
                    invalid_pdfs.append(file_path)
    return invalid_pdfs

# Set the root directory to check
base_directory = "(silicon-photonics)-AND-TE-TM-mode-converter"

invalid_pdfs = find_invalid_pdfs(base_directory)

# Output a PDF file that cannot be opened properly
if invalid_pdfs:
    print("The following PDF files cannot be opened properly:")
    for pdf in invalid_pdfs:
        print(pdf)
else:
    print("All PDF files can be opened normally.")