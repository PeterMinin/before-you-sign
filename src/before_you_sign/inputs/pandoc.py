from pathlib import Path

import pypandoc


def convert_with_pandoc(input_path: str | Path) -> str:
    """
    Converts any format supported by Pandoc to Markdown.
    Namely, to CommonMark.

    :param input_path: source file path.

    :return: the document text.

    :raises ValueError: for unsupported formats or broken files.
    """

    try:
        output = pypandoc.convert_file(input_path, "commonmark", extra_args=["--wrap=none"])
    except RuntimeError as e:
        raise ValueError from e
    return output
