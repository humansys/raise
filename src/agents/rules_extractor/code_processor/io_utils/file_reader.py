from pathlib import Path
from typing import List, Union
import logging
import argparse # Import argparse

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FileReader:
    """
    Component responsible for reading source code files from the filesystem,
    handling potential character encoding issues common in legacy systems.
    """

    def read_file(self, file_path: Union[str, Path]) -> List[str]:
        """
        Reads a source code file and returns its content as a list of lines.

        Attempts to read using UTF-8, then common EBCDIC encodings (cp500),
        and finally Latin-1 as fallbacks.

        Args:
            file_path: The path to the source code file (string or Path object).

        Returns:
            A list of strings, where each string is a line from the file,
            with trailing newline characters stripped.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            IOError: If the file cannot be read due to encoding issues or other I/O errors.
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)

        if not file_path.is_file():
            logger.error(f"File not found at path: {file_path}")
            raise FileNotFoundError(f"The file {file_path} does not exist or is not a file.")

        encodings_to_try = ['utf-8', 'cp500', 'latin-1']
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    logger.info(f"Successfully opened {file_path} with encoding {encoding}")
                    # Read lines and strip trailing newline characters
                    lines = [line.rstrip('\n\r') for line in file.readlines()]
                    return lines
            except UnicodeDecodeError:
                logger.warning(f"Failed to decode {file_path} with encoding {encoding}. Trying next...")
                continue
            except Exception as e:
                logger.error(f"An unexpected error occurred while reading {file_path} with {encoding}: {e}")
                # Raise a general IOError for other file reading issues
                raise IOError(f"Failed to read file {file_path} due to an unexpected error: {str(e)}")

        # If all encodings failed
        error_message = f"Could not read file {file_path} with any of the attempted encodings: {encodings_to_try}"
        logger.error(error_message)
        raise IOError(error_message)

# Example usage (now using argparse)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Read a file and attempt various encodings.")
    parser.add_argument("file_path", type=str, help="Path to the file to read.")
    args = parser.parse_args()

    reader = FileReader()
    file_to_read = args.file_path

    try:
        print(f"--- Reading file: {file_to_read} ---")
        lines = reader.read_file(file_to_read)
        print(f"Successfully read {len(lines)} lines.")
        print("First 5 lines:")
        for i, line in enumerate(lines[:5]):
            print(f"{i+1}: {line}")
        if len(lines) > 5:
            print("...")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except IOError as e:
        print(f"Error reading file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # --- Keeping dummy file tests commented out for reference, focus is on CLI arg ---
    # # Create dummy files for testing
    # test_dir = Path("./test_files")
    # test_dir.mkdir(exist_ok=True)
    # 
    # utf8_content = "Line 1: Hello UTF-8\nLine 2: More text\n"
    # latin1_content = "Line 1: ¡Hola Latin-1!\nLine 2: Müller\n".encode('latin-1')
    # # Note: Simulating EBCDIC (cp500) is harder without specific libraries/data
    # # cp500_content = b'...' # EBCDIC bytes would go here
    # 
    # utf8_file = test_dir / "test_utf8.txt"
    # latin1_file = test_dir / "test_latin1.txt"
    # 
    # with open(utf8_file, "w", encoding="utf-8") as f:
    #     f.write(utf8_content)
    #     
    # with open(latin1_file, "wb") as f: # Write bytes for non-utf8
    #     f.write(latin1_content)
    # 
    # try:
    #     print(f"--- Reading UTF-8 file: {utf8_file} ---")
    #     lines_utf8 = reader.read_file(utf8_file)
    #     print(lines_utf8)
    # except Exception as e:
    #     print(f"Error reading UTF-8: {e}")
    # 
    # try:
    #     print(f"--- Reading Latin-1 file: {latin1_file} ---")
    #     lines_latin1 = reader.read_file(latin1_file)
    #     print(lines_latin1)
    # except Exception as e:
    #     print(f"Error reading Latin-1: {e}")
    # 
    # try:
    #     print("--- Attempting to read non-existent file ---")
    #     reader.read_file("./non_existent_file.txt")
    # except Exception as e:
    #     print(f"Caught expected error: {e}")
    # 
    # # Clean up dummy files
    # # import shutil
    # # shutil.rmtree(test_dir)
    # print("\nNote: EBCDIC (cp500) testing requires a specific file encoded in cp500.") 