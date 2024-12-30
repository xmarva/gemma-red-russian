import os
import json
import glob


def create_dataset(directory_path, json_filename):
    """
    Collects all .txt files from author subfolders in a given directory
    and creates a dataset in .json format with the specified structure.

    Args:
        directory_path (str): The path to the directory containing author subfolders.
        json_filename (str): The desired name for the output .json file.
    """

    dataset = []

    # Check if the provided directory exists
    if not os.path.isdir(directory_path):
        print(f"Error: Directory not found: {directory_path}")
        return

    # Iterate through each subdirectory (author)
    for author_dir in os.listdir(directory_path):
        author_path = os.path.join(directory_path, author_dir)

        # Skip any files in the main directory
        if not os.path.isdir(author_path):
            continue

        author_name = author_dir
        author_txt_files = glob.glob(os.path.join(author_path, "*.txt"))

        for i, file_path in enumerate(author_txt_files):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    book_entry = {
                        f"author_name": author_name,
                        f"book_name": os.path.basename(file_path).replace(".txt", ""),  # Extract filename without .txt
                        f"book_content": content
                    }
                    dataset.append(book_entry)
            except UnicodeDecodeError:
                print(f"Warning: Could not decode file: {file_path}. Skipping.")
            except Exception as e:
                print(f"Error reading file: {file_path}. Error: {e}. Skipping.")

    # Check if we found any data
    if not dataset:
        print(f"Warning: No data found in the directory {directory_path}. No file created.")
        return

    # Save the dataset to a json file
    try:
        with open(json_filename, "w", encoding="utf-8") as outfile:
            json.dump(dataset, outfile, indent=4, ensure_ascii=False)
        print(f"Dataset saved to {json_filename}")
    except Exception as e:
        print(f"Error writing to json file {json_filename}. Error: {e}")


if __name__ == "__main__":
    directory_path = "../data/txt"
    json_filename = "../data/red_russian_dataset.json"

    create_dataset(directory_path, json_filename)