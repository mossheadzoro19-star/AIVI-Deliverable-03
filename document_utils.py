from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


def extract_document_text(filename: str, data: bytes) -> str:
    suffix = Path(filename).suffix.lower()

    if suffix in {".txt", ".md"}:
        text = data.decode("utf-8", errors="replace").strip()
        if not text:
            raise ValueError("The uploaded text file is empty.")
        return text

    if suffix == ".pdf":
        try:
            reader = PdfReader(BytesIO(data))
            pages = [page.extract_text() or "" for page in reader.pages]
        except Exception as exc:
            raise ValueError(f"Could not parse the PDF: {exc}") from exc

        text = "\n".join(pages).strip()
        if not text:
            raise ValueError(
                "Could not extract text from this PDF. "
                "It may be scanned/image-based; OCR is required before analysis."
            )
        return text

    raise ValueError("Unsupported file type. Upload a .txt, .md, or text-based .pdf file.")
