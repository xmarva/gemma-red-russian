import os
import json
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import docx
import re
import fb2_parser


def extract_text_from_epub(epub_path):
    """Extracts text from an EPUB file."""
    text = ""
    try:
        book = epub.read_epub(epub_path)
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text += soup.get_text()
    except Exception as e:
        print(f"Error processing EPUB {epub_path}: {e}")
    return text.strip()


def extract_text_from_doc(doc_path):
    """Extracts text from a .doc file."""
    text = ""
    try:
        document = docx.Document(doc_path)
        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error processing DOC {doc_path}: {e}")
    return text.strip()
  
def extract_text_from_fb2(fb2_path):
    """Extracts text from an FB2 file."""
    text = ""
    try:
      with open(fb2_path, 'r', encoding='utf-8') as fb2_file:
        fb2_content = fb2_file.read()
      parsed_fb2 = fb2_parser.FB2Parser(fb2_content)
      text = parsed_fb2.get_text()
    except Exception as e:
       print(f"Error processing FB2 {fb2_path}: {e}")
    return text.strip()

def extract_text_from_txt(txt_path):
    """Extracts text from a TXT file."""
    text = ""
    try:
        with open(txt_path, "r", encoding="utf-8", errors='replace') as f:
            text = f.read()
    except Exception as e:
        print(f"Error processing TXT {txt_path}: {e}")
    return text.strip()


def clean_text(text):
    """Removes page numbers, table of contents markers and other technical elements."""
    #Remove page numbers
    text = re.sub(r'\s*\d+\s*', '', text)
    # Remove table of contents markers
    text = re.sub(r'^[A-ZА-ЯЁ]+\s*$', '', text, flags=re.MULTILINE) #Remove TOC style headings
    text = re.sub(r'^\s*Contents\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE) #Remove "Contents" word
    text = re.sub(r'^\s*[\.\,\;\:\- ]*\s*$', '', text, flags=re.MULTILINE) #Remove blank or punctuation-only lines
    # Remove multiple line breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def process_book_files(input_dir, output_dir):
    """
    Processes book files from input directory and saves the cleaned text into a combined JSONL.

    Args:
        input_dir: Path to the directory with book files.
        output_dir: Path to the directory where output will be saved.
    """

    os.makedirs(output_dir, exist_ok=True)
    jsonl_output_path = os.path.join(output_dir, "combined_dataset.jsonl")
    all_data = []

    for author_dir_name in os.listdir(input_dir):
        if author_dir_name.startswith('.'):
            continue  
        author_dir_path = os.path.join(input_dir, author_dir_name)
        if os.path.isdir(author_dir_path):
            for filename in os.listdir(author_dir_path):
                if filename.startswith('.'):
                    continue
                filepath = os.path.join(author_dir_path, filename)
                if os.path.isfile(filepath):
                  author = author_dir_name
                  text = ""
                  base_filename, ext = os.path.splitext(filename)
                  
                  if ext.lower() == ".epub":
                     text = extract_text_from_epub(filepath)
                  elif ext.lower() == ".doc":
                      text = extract_text_from_doc(filepath)
                  elif ext.lower() == ".fb2":
                      text = extract_text_from_fb2(filepath)
                  elif ext.lower() == ".txt":
                      text = extract_text_from_txt(filepath)
                  else:
                      print(f"Skipping file {filename} due to unknown file type: {ext}")
                      continue

                  if text:
                    cleaned_text = clean_text(text)
                    all_data.append({"text": cleaned_text, "author": author, "filename":filename})
           

    with open(jsonl_output_path, "w", encoding="utf-8") as f:
        for item in all_data:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")
    print(f"Combined data saved in {jsonl_output_path}")


if __name__ == "__main__":
    input_directory = "../data/full"
    output_directory = os.path.join(os.path.dirname(input_directory), "processed_books") 
    process_book_files(input_directory, output_directory)