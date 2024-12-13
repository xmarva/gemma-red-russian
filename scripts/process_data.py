import os
import json
import re
import codecs
import chardet
import subprocess
import textract


def detect_encoding(file_path):
    """Detects file encoding using chardet."""
    try:
        with open(file_path, "rb") as f:
          raw_data = f.read()
          result = chardet.detect(raw_data)
          return result['encoding']
    except Exception as e:
        print(f"Error detecting encoding for {file_path}: {e}")
        return "utf-8"  # Default encoding is utf-8


def extract_text_from_doc(doc_path):
    """Extracts text from a DOC file using textract."""
    try:
        text = textract.process(doc_path).decode('utf-8', errors='replace').strip()
        return text
    except Exception as e:
        print(f"Error extracting text from DOC {doc_path} with textract: {e}")
        return ""


def extract_text_from_docx(docx_path):
    """Extracts text from a DOCX file using textract."""
    try:
        text = textract.process(docx_path).decode('utf-8', errors='replace').strip()
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX {docx_path} with textract: {e}")
        return ""


def extract_text_from_fb2(fb2_path):
    """Extracts text from an FB2 file using pandoc."""
    try:
      command = ["pandoc", fb2_path, "-t", "plain"]
      result = subprocess.run(command, capture_output=True, text=False, check=False)
      if result.returncode != 0:
          print(f"Error processing FB2 {fb2_path}: pandoc returned non-zero exit status {result.returncode}")
          return ""
      encoding = chardet.detect(result.stdout)['encoding'] or 'utf-8'
      return result.stdout.decode(encoding, errors='replace').strip()
    except Exception as e:
        print(f"Error processing FB2 {fb2_path}: {e}")
        return ""


def extract_text_from_txt(txt_path):
    """Extracts text from a TXT file."""
    text = ""
    try:
        with open(txt_path, "rb") as f:
           raw_data = f.read()
           encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
           text = raw_data.decode(encoding, errors='replace')
    except Exception as e:
       print(f"Error processing TXT {txt_path}: {e}")
    return text.strip()


def clean_text(text):
    """Removes page numbers, table of contents markers, and other technical elements."""
    # Remove page numbers
    text = re.sub(r'\s*\d+\s*', '', text)
    # Remove table of contents markers
    text = re.sub(r'^[A-ZА-ЯЁ]+\s*$', '', text, flags=re.MULTILINE)  # Remove TOC style headings
    text = re.sub(r'^\s*Contents\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)  # Remove "Contents" word
    text = re.sub(r'^\s*[\.\,\;\:\- ]*\s*$', '', text, flags=re.MULTILINE)  # Remove blank or punctuation-only lines
    # Remove multiple line breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def convert_text(text, input_encoding='utf-8', output_encoding='utf-8'):
    """
    Convert a text from one encoding to another.
    
    Args:
    text (str): The text to convert
    input_encoding (str): Source file encoding (default: utf-8)
    output_encoding (str): Target file encoding (default: utf-8)
    """
    try:
        encoded_text = text.encode(input_encoding, errors='ignore') #Encode with the input encoding
        return encoded_text.decode(output_encoding, errors='ignore') #Decode to the desired output encoding
    except UnicodeError as e:
        print(f"Encoding error: {e}")
        return text #If there are any errors, return the original text
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return text #If there are any errors, return the original text


def process_book_files(input_dir, output_dir):
    """
    Processes book files from input directory, saves cleaned text to a combined JSONL, and writes each text as TXT to sibling directory.

    Args:
        input_dir: Path to the directory with book files.
        output_dir: Path to the directory where output will be saved.
    """

    os.makedirs(output_dir, exist_ok=True)
    jsonl_output_path = os.path.join(output_dir, "dataset.json")
    all_data = []

    for author_dir_name in os.listdir(input_dir):
        if author_dir_name.startswith('.'):
            continue  # Skip hidden files
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

                    if ext.lower() == ".doc":
                        text = extract_text_from_doc(filepath)
                    elif ext.lower() == ".docx":
                        text = extract_text_from_docx(filepath)
                    elif ext.lower() == ".fb2":
                        text = extract_text_from_fb2(filepath)
                    elif ext.lower() == ".txt":
                        text = extract_text_from_txt(filepath)
                    else:
                        print(f"Skipping file {filename} due to unknown file type: {ext}")
                        continue

                    if text:
                        cleaned_text = clean_text(text)
                        converted_text = convert_text(cleaned_text)
                        all_data.append({"text": converted_text, "author": author, "filename":filename})

                        # Save individual author's txt
                        author_output_dir = os.path.join(output_dir, author)
                        os.makedirs(author_output_dir, exist_ok=True)
                        author_txt_path = os.path.join(author_output_dir, f"{base_filename}.txt")

                        with codecs.open(author_txt_path, "w", encoding="utf-8") as f:
                            f.write(converted_text)
                        print(f"Text for {filename} saved in {author_txt_path}")
    # Save combined JSONL
    with codecs.open(jsonl_output_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4) #Save the list to json
    print(f"Combined data saved in {jsonl_output_path}")


if __name__ == "__main__":
    input_directory = "/Users/arcsinx/gh/red_gemma/data/full"  # Replace with the actual input directory.
    output_directory = "./processed_books"  # Output directory within the project
    process_book_files(input_directory, output_directory)