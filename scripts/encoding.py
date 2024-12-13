import codecs

def convert_text(input_filename, output_filename, input_encoding='windows-1251', output_encoding='utf-8'):
    """
    Convert a Russian text file from one encoding to another.
    
    Args:
    input_filename (str): Path to the input file
    output_filename (str): Path to save the converted file
    input_encoding (str): Source file encoding (default: windows-1251)
    output_encoding (str): Target file encoding (default: utf-8)
    """
    try:
        with codecs.open(input_filename, 'r', encoding=input_encoding) as file:
            text = file.read()
        
        with codecs.open(output_filename, 'w', encoding=output_encoding) as file:
            file.write(text)
        
        print(f"File successfully converted from {input_encoding} to {output_encoding}")
    
    except FileNotFoundError:
        print(f"Error: File {input_filename} not found.")
    except UnicodeError as e:
        print(f"Encoding error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Convert the specific file
convert_text('commie.txt', 'commie_converted.txt')