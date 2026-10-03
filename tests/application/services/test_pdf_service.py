from io import BytesIO
from unittest.mock import MagicMock, mock_open, patch

from cv_analyzer.application.ports.pdf_extractor import PDFExtractorPort
from cv_analyzer.application.services.pdf_service import PDFService


def test_extract_text_from_stream_delegates_to_extractor() -> None:
    """Test that extract_text_from_stream delegates to PDFExtractorPort."""
    expected_text = "John Doe - Software Engineer"
    mock_extractor = MagicMock(spec=PDFExtractorPort)
    mock_extractor.extract_text.return_value = expected_text

    service = PDFService(extractor=mock_extractor)
    stream = BytesIO(b"fake pdf content")

    result = service.extract_text_from_stream(stream)

    mock_extractor.extract_text.assert_called_once_with(stream)
    assert result == expected_text


def test_extract_text_from_file_path_opens_file_and_delegates() -> None:
    """Test that extract_text_from_file_path opens the file in binary mode and delegates."""
    expected_text = "Jane Doe - Backend Developer"
    mock_extractor = MagicMock(spec=PDFExtractorPort)
    mock_extractor.extract_text.return_value = expected_text

    service = PDFService(extractor=mock_extractor)

    m = mock_open(read_data=b"fake pdf content")
    with patch("builtins.open", m):
        result = service.extract_text_from_file_path("/path/to/cv.pdf")

    m.assert_called_once_with("/path/to/cv.pdf", "rb")
    mock_extractor.extract_text.assert_called_once()
    assert result == expected_text
