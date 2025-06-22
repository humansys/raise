# Implementation Plan: User Story RAISE-31 - Read Source Code File

**User Story:** [RAISE-31] Read source code file
**As** a developer working on the MVP,
**I want** to read a given COBOL or RPG source file from a local directory,
**so that** the pipeline can programmatically access code lines for further processing.

**Feature:** [RAISE-30]: Basic Code Preprocessing

---

## 1. Goal

Implement a Python component that reliably reads a specified source code file (COBOL/RPG) from the filesystem, handles potential character encoding issues (UTF-8, EBCDIC, Latin-1), and returns the content as a list of strings (lines).

## 2. Technical Design & Implementation Steps

### 2.1. Project Structure

-   Create a new directory `src/rules-extractor/code_processor/io_utils`.
-   Create a new file `src/rules-extractor/code_processor/io_utils/file_reader.py`.

### 2.2. Component: `FileReader`

-   **Location:** `src/rules-extractor/code_processor/io_utils/file_reader.py`
-   **Class:** `FileReader`
    -   **Purpose:** Encapsulates logic for reading source files with encoding detection.
    -   **Method:** `read_file(self, file_path: Union[str, Path]) -> List[str]`
        -   **Input:** `file_path` (string or `pathlib.Path` object)
        -   **Output:** A list of strings, where each string is a line from the file.
        -   **Logic:**
            1.  Convert `file_path` to `Path` object if it's a string.
            2.  Check if the file exists using `file_path.exists()`. Raise `FileNotFoundError` if not.
            3.  Attempt to open and read the file using `utf-8` encoding.
            4.  If `UnicodeDecodeError` occurs, attempt reading with common EBCDIC encodings (e.g., `cp500`, `ibm037`). *Initial implementation might start with just `cp500`.*
            5.  If EBCDIC also fails, attempt reading with `latin-1` as a fallback.
            6.  If all attempts fail, raise an `IOError` indicating encoding issues.
            7.  Use `readlines()` to get a list of lines. Strip trailing newline characters from each line for consistency.
            8.  Return the list of lines.
    -   **Error Handling:** Implement specific `try...except` blocks for `FileNotFoundError`, `UnicodeDecodeError`, and general `IOError`.

### 2.3. Dependencies

-   Python Standard Library (`pathlib`, `typing`)

## 3. Testing Strategy

-   **Unit Tests:** Create tests (e.g., using `pytest`) for the `FileReader` class.
    -   Test reading a standard UTF-8 encoded text file.
    -   Test reading a known EBCDIC encoded file (a small sample `.cbl` or `.rpg` file should be placed in a test fixtures directory).
    -   Test reading a Latin-1 encoded file.
    -   Test handling of `FileNotFoundError`.
    -   Test handling of files with unsupported encodings (should raise the specific `IOError`).
    -   Test with empty files.
    -   Test with files containing various line endings (though `readlines()` often handles this).

## 4. Integration

-   This `FileReader` component will be utilized by the subsequent "Chunking" component ([RAISE-32]) which will receive the list of lines as input.

## 5. Documentation

-   Add clear docstrings to the `FileReader` class and its `read_file` method explaining purpose, parameters, return values, and potential exceptions.
-   Briefly document the supported encodings and the fallback mechanism.

## 6. Acceptance Criteria Checklist

-   [ ] Source file path can be provided as input.
-   [ ] Script successfully reads a UTF-8 encoded file.
-   [ ] Script successfully reads a common EBCDIC encoded file (e.g., `cp500`).
-   [ ] Script successfully reads a Latin-1 encoded file.
-   [ ] Script returns content as a list of strings (lines).
-   [ ] Script raises `FileNotFoundError` for non-existent files.
-   [ ] Script raises an appropriate `IOError` for unreadable/unsupported encodings.
-   [ ] Basic docstrings are present.

---

This plan outlines the necessary steps to implement the `FileReader` component for User Story [RAISE-31].