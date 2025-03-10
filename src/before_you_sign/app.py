"""
The entry point of the app
"""

import argparse
import traceback
from datetime import datetime
from pathlib import Path

import gradio as gr

from before_you_sign.config import Config, load_config
from before_you_sign.inputs.all import get_as_markdown
from before_you_sign.llm.gemini.assistant import GeminiAssistant


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
    """
    The main processing function.
    Takes the document and produces the response.
    """
    document = value["text"]
    files = value["files"]
    if not (document or files):
        return gr.skip()
    assert document and not files
    global config
    exp_log_dir = get_exp_log_dir(config["log_dir"])
    assistant = GeminiAssistant(config, exp_log_dir, on_retry=gr.Warning)
    metadata = assistant.start(document)
    summary, thoughts = assistant.summarize(metadata)
    assistant.finalize()
    return {
        doc_type: metadata.document_type,
        doc_lang: metadata.document_language,
        service_name: metadata.service_name,
        service_descr: metadata.service_nature,
        score: summary.score,
        comment: summary.comment,
        details: thoughts,
    }


def get_exp_log_dir(base_dir: Path) -> Path:
    """
    Creates a subfolder for the experiment's logs.
    """
    base_dir.mkdir(exist_ok=True)
    name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    path = base_dir / name
    path.mkdir()
    return path


def try_get_as_markdown(filepath: str) -> str:
    try:
        return get_as_markdown(filepath)
    except ValueError:
        gr.Warning(f"Couldn't read the file\n({ Path(filepath).name })")
        traceback.print_exc()
        return ""


def preprocess_document_input(value: dict[str, str | list]):
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
    with gr.Accordion("Metadata", open=False):
        with gr.Row():
            doc_type = gr.Textbox(label="Document type", key="doc_type")
            doc_lang = gr.Textbox(label="Language", key="doc_lang")
        with gr.Row():
            service_name = gr.Textbox(label="Service", key="name")
            service_descr = gr.Textbox(label="Description", key="descr")
    score = gr.Textbox(label="Score", key="score")
    comment = gr.Textbox(label="Comment", key="comment")
    with gr.Accordion("Details", open=False):
        details = gr.Markdown(key="details")
    document.submit(
        process_document,
        document,
        [doc_type, doc_lang, service_name, service_descr, score, comment, details],
    )

if __name__ == "__main__":
    demo.launch()
