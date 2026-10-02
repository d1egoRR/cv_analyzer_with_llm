from typing import BinaryIO

import pypdf

from cv_analyzer.application.ports.pdf_extractor import (
    PDFExtractorPort,
)
from cv_analyzer.domain.exceptions import (
    EmptyPDFError,
    PDFExtractionError,
)


class PyPDFExtractor(PDFExtractorPort):
    """Outbound adapter implementing PDFExtractorPort using pypdf / PyPDF2."""

    def extract_text(self, file_stream: BinaryIO) -> str:
        """Extract text from a binary PDF stream with page headers.

        Args:
            file_stream: Binary stream of the PDF file.

        Returns:
            Extracted text content from all pages formatted with page headers.

        Raises:
            EmptyPDFError: If the PDF contains no extractable text.
            PDFExtractionError: If PDF parsing fails due to invalid or corrupt stream.
        """
        try:
            reader = pypdf.PdfReader(file_stream)
            page_chunks: list[str] = []

            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text()

                if page_text and page_text.strip():
                    page_chunks.append(
                        f"--- PAGE {page_num} ---\n{page_text.strip()}"
                    )

            if not page_chunks:
                raise EmptyPDFError(
                    "The provided PDF file contains no extractable text."
                )

            return "\n\n".join(page_chunks)

        except EmptyPDFError:
            raise
        except Exception as exc:
            raise PDFExtractionError(
                f"Failed to process PDF file: {exc}"
            ) from exc
