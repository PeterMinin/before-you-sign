from pathlib import Path

import pypandoc


def convert_with_pandoc(input_path: str | Path) -> str:
    """
    Converts any format supported by Pandoc to Markdown.
    Namely, to original unextended Markdown.

    :param input_path: source file path.

    :return: the document text.

    :raises ValueError: for unsupported formats or broken files.
    """

    try:
        output = pypandoc.convert_file(input_path, 'markdown_strict')
    except RuntimeError as e:
        raise ValueError from e
    return output
