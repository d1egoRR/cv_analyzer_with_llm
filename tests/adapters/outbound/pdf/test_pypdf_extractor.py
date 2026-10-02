from io import BytesIO
from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

from cv_analyzer.adapters.outbound.pdf.pypdf_extractor import (
    PyPDFExtractor,
)
from cv_analyzer.domain.exceptions import (
    EmptyPDFError,
    PDFExtractionError,
)


def test_extract_text_success() -> None:
    """Test successful text extraction with page headers."""
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "John Doe\nSoftware Engineer"

    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = "Experience:\n5 years in Python"

    mock_reader = MagicMock()
    mock_reader.pages = [mock_page1, mock_page2]

    with patch("pypdf.PdfReader", return_value=mock_reader):
        extractor = PyPDFExtractor()
        result = extractor.extract_text(BytesIO(b"fake pdf content"))

    assert "--- PAGE 1 ---" in result
    assert "John Doe\nSoftware Engineer" in result
    assert "--- PAGE 2 ---" in result
    assert "Experience:\n5 years in Python" in result


def test_extract_text_empty_pdf_raises_empty_pdf_error() -> None:
    """Test that EmptyPDFError is raised when PDF contains no text."""
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "   "

    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]

    with patch("pypdf.PdfReader", return_value=mock_reader):
        extractor = PyPDFExtractor()

        with pytest.raises(EmptyPDFError) as exc_info:
            extractor.extract_text(BytesIO(b"fake pdf content"))

    assert "contains no extractable text" in str(exc_info.value)


def test_extract_text_corrupt_stream_raises_pdf_extraction_error() -> None:
    """Test that PDFExtractionError is raised when pypdf fails to parse."""
    with patch("pypdf.PdfReader", side_effect=Exception("Invalid PDF header")):
        extractor = PyPDFExtractor()

        with pytest.raises(PDFExtractionError) as exc_info:
            extractor.extract_text(BytesIO(b"corrupt content"))

    assert "Failed to process PDF file" in str(exc_info.value)
