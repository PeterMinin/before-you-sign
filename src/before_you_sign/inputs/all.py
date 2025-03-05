"""
Common API for various input conversion methods.
"""

from pathlib import Path

from .exceptions import ConversionSkipped
from .markitdown import convert_with_markitdown
from .pandoc import convert_with_pandoc

_manual_assignments = {
    # Handle HTML with Pandoc.
    # It's not perfect, but probably better than MarkItDown, because Pandoc
    # tries to extract the main text and strip the header, footer, etc.
    ".html": convert_with_pandoc,
    ".htm": convert_with_pandoc,
}


def get_as_markdown(input_path: str) -> str:
    """
    Converts any supported file format to Markdown.

    :param input_path: source file path.

    :return: the document text.

    :raises ValueError: for unsupported formats or broken files.
    """
    if manual_assignment := _manual_assignments.get(Path(input_path).suffix.lower()):
        return manual_assignment(input_path)
    try:
        return convert_with_markitdown(input_path)
    except ConversionSkipped:
        pass
    return convert_with_pandoc(input_path)
