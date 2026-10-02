from typing import BinaryIO, Protocol


class PDFExtractorPort(Protocol):
    """Port interface defining PDF text extraction capabilities."""

    def extract_text(self, file_stream: BinaryIO) -> str:
        """Extract text content from a binary PDF stream.

        Args:
            file_stream: A readable binary stream of a PDF file.

        Returns:
            Extracted text content as a string.
        """
        ...
