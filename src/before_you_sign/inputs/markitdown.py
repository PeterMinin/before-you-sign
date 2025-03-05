import markitdown

from .exceptions import ConversionSkipped


def convert_with_markitdown(input_path: str) -> str:
    """
    Converts URLs and file formats supported by Microsoft's MarkItDown,
    including the optional PDF and DOCX, to Markdown.

    :param input_path: source file path or URL.

    :return: the document text.

    :raises api.ConversionSkipped: for unsupported formats.
    :raises ValueError: for broken files.
    """
    md = markitdown.MarkItDown()
    try:
        result = md.convert(input_path)
    except markitdown.UnsupportedFormatException as e:
        raise ConversionSkipped from e
    except markitdown.FileConversionException as e:
        raise ValueError from e
    return result.text_content
