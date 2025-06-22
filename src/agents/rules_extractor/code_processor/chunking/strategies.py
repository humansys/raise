from abc import ABC, abstractmethod
from typing import List
from rules_extractor.code_processor.chunking.models import CodeChunk
import logging

logger = logging.getLogger(__name__)

class ChunkingStrategy(ABC):
    """Abstract base class for code chunking strategies."""

    @abstractmethod
    def chunk_code(self, code_lines: List[str], file_path: str, language: str) -> List[CodeChunk]:
        """Splits the code into chunks based on the strategy.

        Args:
            code_lines: A list of strings, where each string is a line of code.
            file_path: The path to the source file.
            language: The detected language of the code ('COBOL', 'RPG', 'UNKNOWN').

        Returns:
            A list of CodeChunk objects.
        """
        pass

class LineBasedChunking(ChunkingStrategy):
    """Chunks code based on a fixed number of lines with optional overlap."""

    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        """Initializes the line-based chunking strategy.

        Args:
            chunk_size: The target number of lines per chunk.
            overlap: The number of lines to overlap between consecutive chunks.
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be less than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap
        logger.info(f"Initialized LineBasedChunking with chunk_size={chunk_size}, overlap={overlap}")

    def chunk_code(self, code_lines: List[str], file_path: str, language: str) -> List[CodeChunk]:
        """Performs line-based chunking."""
        chunks: List[CodeChunk] = []
        total_lines = len(code_lines)
        chunk_idx = 0
        current_pos = 0

        if total_lines == 0:
            logger.warning(f"File {file_path} is empty, no chunks generated.")
            return chunks

        while current_pos < total_lines:
            start_line_idx = current_pos
            end_line_idx = min(current_pos + self.chunk_size, total_lines)

            # Adjust end index to ensure it doesn't go beyond total lines
            # No need, min() already handles this.
            
            chunk_content_lines = code_lines[start_line_idx:end_line_idx]
            # Strip trailing newline from the last line if present
            # No, join adds them back as needed.
            chunk_content = "".join(chunk_content_lines) # Use empty string join, lines already have newlines

            # Line numbers are 1-indexed
            start_line_1_indexed = start_line_idx + 1
            end_line_1_indexed = end_line_idx 

            chunk = CodeChunk(
                content=chunk_content,
                source_file=file_path,
                start_line=start_line_1_indexed,
                end_line=end_line_1_indexed,
                language=language,
                chunk_index=chunk_idx
            )
            chunks.append(chunk)
            logger.debug(f"Created {chunk}")

            chunk_idx += 1
            next_start_pos = current_pos + self.chunk_size - self.overlap

            # Prevent infinite loops if step size is zero or negative (shouldn't happen with validation)
            if next_start_pos <= current_pos:
                 if total_lines > current_pos + self.chunk_size: # check if there is still code to process
                     logger.warning(f"Chunking step size is non-positive ({self.chunk_size - self.overlap}). Moving by 1 to avoid loop.")
                     next_start_pos = current_pos + 1 
                 else: # already processed the last chunk
                     break 
            
            current_pos = next_start_pos
            
            # Break if we've covered all lines (the last chunk might have ended exactly at total_lines)
            if start_line_idx + self.chunk_size >= total_lines:
                 break

        logger.info(f"Generated {len(chunks)} chunks for {file_path}")
        return chunks 