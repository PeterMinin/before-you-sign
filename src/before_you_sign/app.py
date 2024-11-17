"""
The entry point of the app
"""

import argparse
import traceback
from pathlib import Path

import gradio as gr

from before_you_sign.config import Config, load_config
from before_you_sign.inputs.pandoc import convert_with_pandoc
from before_you_sign.llm.gemini import GeminiAssistant


def get_args():
    project_root = Path(__file__).parents[2]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        help="Config YAML file. Default: <project_root>/local/config.yaml.",
        default=project_root / "local/config.yaml",
    )
    args = parser.parse_args()
    return args


def process_document(value: dict[str, str | list]):
    document = value["text"]
    files = value["files"]
    if not (document or files):
        return gr.skip()
    assert document and not files
    global config
    assistant = GeminiAssistant(config, on_retry=gr.Warning)
    response = assistant.process(document)
    return response


def try_get_as_markdown(filepath: str) -> str:
    try:
        return convert_with_pandoc(filepath)
    except ValueError:
        gr.Warning(f"Couldn't read the file\n({ Path(filepath).name })")
        traceback.print_exc()
        return ""


def preprocess_document_input(value: dict[str, str | list], progress=gr.Progress()):
    """
    Does nothing if just text is entered.
    If a file is uploaded, converts it to text (if possible).
    Ensures that no previously entered text is overwritten.
    """
    if value["text"] and value["files"]:
        gr.Warning("Please clear the text if you want to replace it")
        return gr.MultimodalTextbox(submit_btn=False)
    elif not value["files"]:
        return gr.MultimodalTextbox(submit_btn=True)
    else:
        assert len(value["files"]) == 1
        filepath = value["files"][0]
        progress((1, None), "Converting to Markdown")
        text = try_get_as_markdown(filepath)
        value["text"] = text
        del value["files"][0]
        return gr.MultimodalTextbox(submit_btn=True, value=value)


def clear_document_input():
    return gr.MultimodalTextbox(value=None)


args = get_args()
config: Config = load_config(args.config)

with gr.Blocks(title="Before You Sign") as demo:
    document = gr.MultimodalTextbox(
        label="Document",
        placeholder="Paste here, or upload the file",
        lines=10,
        max_lines=10,
        autoscroll=False,
        stop_btn="Clear",
    )
    document.change(preprocess_document_input, document, document)
    document.stop(clear_document_input, outputs=document)
    response = gr.Markdown()
    document.submit(process_document, document, response)

if __name__ == "__main__":
    demo.launch()
