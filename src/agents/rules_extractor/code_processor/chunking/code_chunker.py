from typing import List
# Use absolute imports starting from the package name inside src
from rules_extractor.code_processor.chunking.strategies import ChunkingStrategy, LineBasedChunking
from rules_extractor.code_processor.chunking.models import CodeChunk
import logging

logger = logging.getLogger(__name__)

class CodeChunker:
    """Orchestrates the chunking of code lines using a specified strategy."""

    def __init__(self, strategy: ChunkingStrategy):
        """Initializes the CodeChunker with a chunking strategy."""
        if not isinstance(strategy, ChunkingStrategy):
            raise TypeError("strategy must be an instance of ChunkingStrategy")
        self.strategy = strategy
        logger.info(f"CodeChunker initialized with strategy: {type(strategy).__name__}")

    def chunk(self, code_lines: List[str], file_path: str, language: str) -> List[CodeChunk]:
        """Chunks the given code lines using the configured strategy.

        Args:
            code_lines: A list of strings representing the code.
            file_path: The path of the source file.
            language: The language of the code.

        Returns:
            A list of CodeChunk objects.
        """
        logger.info(f"Starting chunking for file: {file_path} ({len(code_lines)} lines, language: {language})")
        if not code_lines:
            logger.warning("Received empty list of code lines. No chunks will be generated.")
            return []
            
        try:
            chunks = self.strategy.chunk_code(code_lines, file_path, language)
            logger.info(f"Successfully generated {len(chunks)} chunks for {file_path}.")
            return chunks
        except Exception as e:
            logger.error(f"Error during chunking of {file_path}: {e}", exc_info=True)
            # Depending on requirements, might re-raise, return empty, or partial results
            raise # Re-raise the exception for now

# Example usage for testing
if __name__ == '__main__':
    import os
    # This might require moving file_reader.py or adjusting PYTHONPATH
    # For simplicity, let's assume it's one level up in io_utils
    import sys
    # # Add parent directory to sys.path to find io_utils
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # parent_dir = os.path.dirname(current_dir)
    # io_utils_dir = os.path.join(parent_dir, 'io_utils')
    # if io_utils_dir not in sys.path:
    #     sys.path.insert(0, io_utils_dir)
    #     
    # project_root = os.path.dirname(os.path.dirname(parent_dir)) # Go up two more levels for project root
    # if project_root not in sys.path:
    #     sys.path.insert(0, project_root) 
        
    try:
        # Use absolute import now
        from rules_extractor.code_processor.io_utils.file_reader import FileReader 
    except ImportError as e:
        print(f"Error: Could not import FileReader: {e}")
        print("Ensure the project is installed in editable mode (`pip install -e .`)")
        sys.exit(1)

    # Configure basic logging for testing
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    # --- Test Case 1: Standard Chunking --- 
    print("\n--- Test Case 1: Standard Chunking ---")
    # Use the RPGLE file found earlier
    # Adjust path relative to *this* script's location or use absolute
    # Path relative to project root: src/rules-extractor/code_processor/LOGMOD.SQLRPGLE
    # Absolute path from previous context: /home/emilio/Code/raise-mcp/src/rules-extractor/code_processor/LOGMOD.SQLRPGLE
    # Let's construct path relative to project root
    project_root = os.getcwd() # Assume running from project root
    # Corrected path using underscore
    rpgle_file_path = os.path.join("src", "rules_extractor", "code_processor", "LOGMOD.SQLRPGLE") 
    
    if not os.path.exists(rpgle_file_path):
         print(f"Error: Test file not found at {rpgle_file_path} (Expected relative to {project_root})")
         sys.exit(1)

    reader = FileReader()
    try:
        lines = reader.read_file(rpgle_file_path)
        print(f"Read {len(lines)} lines from {rpgle_file_path}")

        # Initialize chunker with line-based strategy (default size 300, overlap 50)
        chunker = CodeChunker(strategy=LineBasedChunking(chunk_size=20, overlap=5))
        chunks = chunker.chunk(lines, rpgle_file_path, "RPG")

        print(f"Generated {len(chunks)} chunks.")
        if chunks:
            print("First chunk details:")
            print(chunks[0])
            print("\nFirst chunk content (first 5 lines):")
            print("\n".join(chunks[0].content.splitlines()[:5]))
            if len(chunks[0].content.splitlines()) > 5: print("...")
            
            if len(chunks) > 1:
                print("\nSecond chunk details:")
                print(chunks[1])
                print("\nSecond chunk content (first 5 lines):")
                print("\n".join(chunks[1].content.splitlines()[:5]))
                if len(chunks[1].content.splitlines()) > 5: print("...")

    except Exception as e:
        print(f"An error occurred during testing: {e}")
        logger.error("Test execution failed", exc_info=True)

    # --- Test Case 2: Small file --- 
    print("\n--- Test Case 2: Small File (less than chunk size) ---")
    small_lines = [f"Line {i+1}\n" for i in range(10)]
    small_file_path = "dummy_small.txt"
    try:
        chunker_small = CodeChunker(strategy=LineBasedChunking(chunk_size=20, overlap=5))
        small_chunks = chunker_small.chunk(small_lines, small_file_path, "UNKNOWN")
        print(f"Generated {len(small_chunks)} chunks for small file.")
        if small_chunks:
            print(small_chunks[0])
            # print(small_chunks[0].content)
    except Exception as e:
        print(f"An error occurred during small file test: {e}")

    # --- Test Case 3: Empty file --- 
    print("\n--- Test Case 3: Empty File ---")
    empty_lines = []
    empty_file_path = "dummy_empty.txt"
    try:
        chunker_empty = CodeChunker(strategy=LineBasedChunking(chunk_size=20, overlap=5))
        empty_chunks = chunker_empty.chunk(empty_lines, empty_file_path, "UNKNOWN")
        print(f"Generated {len(empty_chunks)} chunks for empty file.")
    except Exception as e:
        print(f"An error occurred during empty file test: {e}") 