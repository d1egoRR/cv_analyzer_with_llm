class PDFExtractionError(Exception):
    """Raised when PDF processing fails due to parsing or corruption errors."""

    pass


class EmptyPDFError(PDFExtractionError):
    """Raised when the PDF file contains no extractable text."""

    pass


class CVEvaluationError(Exception):
    """Raised when CV evaluation via LLM fails."""

    pass
