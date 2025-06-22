# Implementation Plan: [RAISE-32] Chunk source code files

**User Story:** As an LLM integrator, I need a script to chunk the code lines into separate text blocks, so that each chunk is small enough for the LLM's context window.

**Goal:** Create a `CodeChunker` component capable of splitting a list of code lines into smaller, configurable chunks, suitable for LLM processing.

**Approach:**

1.  **Define `CodeChunk` Model:**
    *   Create a Pydantic model (`CodeChunk`) to represent a single chunk of code.
    *   Fields: `content` (str), `source_file` (str), `start_line` (int), `end_line` (int), `language` (str, e.g., "COBOL", "RPG"), potentially `chunk_index` (int).
    *   Include basic validation (e.g., start/end lines are valid).

2.  **Design `ChunkingStrategy` Interface:**
    *   Define an abstract base class or protocol (`ChunkingStrategy`) with a method like `chunk_code(code_lines: List[str], file_path: str, language: str) -> List[CodeChunk]`.
    *   This allows for different chunking methods later (e.g., semantic chunking).

3.  **Implement `LineBasedChunking` Strategy:**
    *   Create a concrete implementation (`LineBasedChunking`) of `ChunkingStrategy`.
    *   Constructor accepts `chunk_size` (int, number of lines) and `overlap` (int, number of overlapping lines between chunks).
    *   Implement the `chunk_code` method to split the input `code_lines` based on `chunk_size` and `overlap`.
    *   Each generated chunk should be a `CodeChunk` object populated with correct metadata (content, file path, start/end lines, language).
    *   Handle edge cases (e.g., file smaller than chunk size, final chunk).

4.  **Create `CodeChunker` Class:**
    *   This class will orchestrate the chunking process.
    *   It takes a `ChunkingStrategy` instance during initialization (Dependency Injection).
    *   Method `chunk(code_lines: List[str], file_path: str, language: str) -> List[CodeChunk]` uses the provided strategy to perform the chunking.
    *   Include logging for chunk boundaries (e.g., "Chunk 1: lines 1-300", "Chunk 2: lines 251-550" if overlap=50).

5.  **Integration and Testing:**
    *   Integrate the `CodeChunker` with the existing `FileReader`. A higher-level `CodeProcessor` class might be introduced later to manage both reading and chunking.
    *   For now, add a test block (`if __name__ == '__main__':`) to `code_chunker.py`:
        *   Read a sample file (e.g., `LOGMOD.SQLRPGLE`) using `FileReader`.
        *   Instantiate `CodeChunker` with `LineBasedChunking`.
        *   Call the `chunk` method.
        *   Print the number of chunks created and details of the first few chunks (start/end lines, line count).
        *   Test with different chunk sizes and overlaps.

**Files to Create/Modify:**

*   `src/rules-extractor/code_processor/chunking/models.py`: Define `CodeChunk`.
*   `src/rules-extractor/code_processor/chunking/strategies.py`: Define `ChunkingStrategy` and `LineBasedChunking`.
*   `src/rules-extractor/code_processor/chunking/code_chunker.py`: Define `CodeChunker`.
*   (Potentially create `__init__.py` files in the new `chunking` directory).

**Next Steps:**

*   Implement the `CodeChunk` model.
*   Implement the `ChunkingStrategy` interface and `LineBasedChunking`.
*   Implement the `CodeChunker` class.
*   Add test execution block. 