from pathlib import Path
import os
import json
import re
import shutil
from fuzzywuzzy import fuzz
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

downloads_folder = "downloads"
matched_downloads_folder = "matched_downloads"
founded_books_json = "founded_books.json"

def search_books(downloads_folder):
    books = []
    downloads_path = Path(downloads_folder)
    if not downloads_path.is_dir():
        raise ValueError(f"'{downloads_folder}' is not a valid directory")
    
    for file in downloads_path.rglob('*'):
        if file.is_file():
            relative_path = str(file.relative_to(downloads_path)).replace('\xa0', ' ')
            name = os.path.basename(relative_path)
            path = relative_path
            books.append({
                "name": name,
                "path": path
            })
    return books

def normalize_name(name):
    """
    Normalize the book name to improve fuzzy matching accuracy.
    Steps:
    - Convert to lowercase.
    - Remove punctuation.
    - Replace underscores and hyphens with spaces.
    - Remove extra whitespace.
    - Remove common substrings like 'by', author names, etc.
    - Remove channel prefixes (e.g., @BooksFree4U).
    """
    original_name = name
    
    # Remove file extension
    name = os.path.splitext(original_name)[0]

    # Replace invalid characters with underscores
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    
    # Convert to lowercase
    name = name.lower()
    
    # Replace underscores and hyphens with spaces
    name = re.sub(r'[_\-]', ' ', name)
    
    # Remove punctuation
    name = re.sub(r'[^\w\s]', '', name)

    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name).strip()

    # This pattern removes any leading '@' followed by non-space characters and a space or underscore
    name = re.sub(r'^@\S+[\s_]+', '', name)
    

    common_phrases = ['premium ebooks']
    for phrase in common_phrases:
        name = name.replace(phrase, '')

    # Remove common words (optional)
    common_words = ['by', 'the', 'a', 'an', 'booksfree4u', 'freebooks', 'ebooks', 'book', 'variabletribe', 'iamvariable', 'selfhelpbooks','selfhelpbooks4u', 'pdf', 'pdfdrive']
    name_tokens = name.split()
    name = ' '.join([word for word in name_tokens if word not in common_words])

    return name

def identify_fuzzy_duplicates(books, threshold=85):
    unique_books = []
    normalized_names = []
    
    for book in books:
        normalized = normalize_name(book['name'])
        # Check against all unique_books using their normalized names
        match_found = False
        for idx, unique_normalized in enumerate(normalized_names):
            similarity = fuzz.token_set_ratio(normalized, unique_normalized)
            if similarity >= threshold:
                unique_books[idx]['colisions'].append(book['path'])
                logging.info(f"Duplicate found: '{book['name']}' matches '{unique_books[idx]['name']}' with similarity {similarity}")
                match_found = True
                break
        if not match_found:
            unique_books.append({
                "name": book['name'],
                "path": book['path'],
                "colisions": []
            })
            normalized_names.append(normalized)
    
    return unique_books

def save_as_json(books, output_file="founded_books.json"):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=4)
    print(f"Books have been saved to {output_file}")

def pretty_print(books):
    print(json.dumps(books, ensure_ascii=False, indent=4))

def sanitize_folder_name(name):

    base_name, extension = os.path.splitext(name)
    base_name = normalize_name(base_name)
    #captalize first letter of every word
    base_name = ' '.join([word.capitalize() for word in base_name.split()])
    max_length = 255 - len(extension)
    base_name = base_name[:max_length]
    return (base_name + extension).strip()

def create_matched_folders(unique_books, downloads_folder, matched_downloads_folder):
    """
    Create a 'matched_downloads' folder with subfolders for each unique book.
    Copy the unique book and its collisions into the respective subfolders.
    If the folder already exists, it will be deleted and recreated.
    """
    matched_path = Path(matched_downloads_folder)
    
    # Delete the matched_downloads folder if it exists
    if matched_path.exists():
        logging.info(f"Deleting existing '{matched_downloads_folder}' folder.")
        shutil.rmtree(matched_path)
    
    # Create a new matched_downloads folder
    matched_path.mkdir(exist_ok=True)
    logging.info(f"Created new '{matched_downloads_folder}' folder.")

    downloads_path = Path(downloads_folder).resolve()  # Get absolute path

    for book in unique_books:
        # Sanitize folder name
        folder_name = sanitize_folder_name(book['name'])
        folder_name = os.path.splitext(folder_name)[0]
        book_folder = matched_path / folder_name
        book_folder.mkdir(exist_ok=True)
        logging.info(f"Created folder: '{book_folder}'")
        
        # Source path for the unique book
        source_unique = downloads_path / Path(book['path'].replace('\xa0', ' '))
        if source_unique.is_file():
            dest_unique = book_folder / sanitize_folder_name(source_unique.name)
            try:
                shutil.copy2(str(source_unique), str(dest_unique))
                logging.info(f"Copied unique book: '{source_unique}' to '{dest_unique}'")
            except Exception as e:
                logging.error(f"Error copying unique book '{source_unique}': {str(e)}")
        else:
            logging.warning(f"Unique book file not found: '{source_unique}'")
        
        # Copy collision files
        for collision_path in book['colisions']:
            source_collision = downloads_path / Path(collision_path.replace('\xa0', ' '))
            if source_collision.is_file():
                dest_collision = book_folder / sanitize_folder_name(source_collision.name)
                
                # If collision file already exists, rename it
                if dest_collision.exists():
                    name_stem = dest_collision.stem
                    name_suffix = dest_collision.suffix
                    # Append a unique identifier or timestamp
                    unique_suffix = "_duplicate"
                    dest_collision = book_folder / f"{name_stem}{unique_suffix}{name_suffix}"
                    logging.info(f"Renaming collision file to '{dest_collision.name}' to avoid overwrite.")
                
                try:
                    shutil.copy2(str(source_collision), str(dest_collision))
                    logging.info(f"Copied collision book: '{source_collision}' to '{dest_collision}'")
                except Exception as e:
                    logging.error(f"Error copying collision book '{source_collision}': {str(e)}")
            else:
                logging.warning(f"Collision book file not found: '{source_collision}'")

if __name__ == "__main__":
    # Step 1: Search and identify books
    founded_books = search_books(downloads_folder)
    
    # Sort the books alphabetically by name (case-insensitive)
    founded_books = sorted(founded_books, key=lambda x: x['name'].lower())
    
    # Identify duplicates based on fuzzy matching with normalization
    unique_books = identify_fuzzy_duplicates(founded_books, threshold=85)
    
    # Save the unique books with collisions to a JSON file
    save_as_json(unique_books, founded_books_json)
    
    # Optionally, pretty print the JSON object to the console
    # pretty_print(unique_books)
    
    # Step 2: Create matched_downloads structure and copy files
    create_matched_folders(unique_books, downloads_folder, matched_downloads_folder)
    
    # Optional: Print summary statistics
    print(f"Number of books: {len(founded_books)}")
    print(f"Number of unique books: {len(unique_books)}")
    print(f"Number of collisions: {sum(len(book['colisions']) for book in unique_books)}")
    print(f"Number of books with no collisions: {sum(len(book['colisions']) == 0 for book in unique_books)}")
    print(f"Number of books with collision: {sum(len(book['colisions']) >= 1 for book in unique_books)}")
