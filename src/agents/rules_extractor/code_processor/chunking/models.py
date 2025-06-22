from pydantic import BaseModel, Field, validator
from typing import Literal

class CodeChunk(BaseModel):
    """Represents a segment of code processed with metadatos."""
    content: str = Field(..., description="Contenido del segmento de código")
    source_file: str = Field(..., description="Archivo fuente de origen")
    start_line: int = Field(..., ge=1, description="Número de línea inicial (1-indexed)")
    end_line: int = Field(..., ge=1, description="Número de línea final (1-indexed)")
    language: Literal["COBOL", "RPG", "UNKNOWN"] = Field(..., description="Lenguaje del código detectado")
    chunk_index: int = Field(..., ge=0, description="Índice del chunk en la secuencia")

    @validator('end_line')
    def end_line_must_be_gte_start_line(cls, v, values):
        """Ensure end_line is not before start_line."""
        if 'start_line' in values and v < values['start_line']:
            raise ValueError('end_line cannot be less than start_line')
        return v

    @property
    def line_count(self) -> int:
        """Returns the number of lines in the chunk."""
        return self.end_line - self.start_line + 1

    def __str__(self) -> str:
        return f"Chunk {self.chunk_index} ({self.language}): {self.source_file} [Lines {self.start_line}-{self.end_line}] ({self.line_count} lines)" 