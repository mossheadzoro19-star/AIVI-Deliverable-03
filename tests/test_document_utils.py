from document_utils import extract_document_text


def test_extract_text_file():
    text = extract_document_text("resume.txt", b"Python\nSQL\nMachine Learning")
    assert "Python" in text
    assert "SQL" in text


def test_reject_empty_text_file():
    try:
        extract_document_text("resume.txt", b"")
    except ValueError as exc:
        assert "empty" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError for empty text")


def test_reject_unsupported_file():
    try:
        extract_document_text("resume.docx", b"content")
    except ValueError as exc:
        assert "unsupported" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError for unsupported file")
