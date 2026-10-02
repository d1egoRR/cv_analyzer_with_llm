from typing import BinaryIO

from cv_analyzer.application.ports.pdf_extractor import PDFExtractorPort


class PDFService:
    """Application service for orchestrating PDF text extraction operations."""

    def __init__(self, extractor: PDFExtractorPort) -> None:
        """Initialize PDFService with a PDFExtractorPort implementation.

        Args:
            extractor: Outbound adapter matching PDFExtractorPort protocol.
        """
        self._extractor = extractor

    def extract_text_from_stream(self, stream: BinaryIO) -> str:
        """Extract text from an open binary file stream.

        Args:
            stream: Readable binary stream of a PDF.

        Returns:
            Extracted text content.
        """
        return self._extractor.extract_text(stream)

    def extract_text_from_file_path(self, file_path: str) -> str:
        """Extract text directly from a file system path.

        Args:
            file_path: Path to the PDF file on disk.

        Returns:
            Extracted text content.
        """
        with open(file_path, "rb") as file_stream:
            return self._extractor.extract_text(file_stream)
