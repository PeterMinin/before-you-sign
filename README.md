# Before You Sign

This assistant aims to bring a little more truth into "I have read and understood the Terms and Conditions".

Inspired by the [TOS;DR](tosdr.org) project, powered by LLMs. No guarantees, just a best-effort.

## High-level design

- Usage: with minimum typing.  
  Enter the document, maybe answer a question, and get a summary.  
  Optionally, ask follow-up questions.
- Advanced scenario: process a pack of related documents.
- Input formats: plain text, PDF, DOCX, URL, images.
- Multi-lingual: can read languages other than English.
- Web UI.
- Based on a free LLM API. Later may be extended to a local solution.

## Status

The basics work. Tested with synthetic examples (in [tests/data](tests/data/): "YourDiary"): a good example gets a good score (left picture below), while the same document with a clause replaced with an unreasonable one gets a very bad score (right picture).

A similar test with a larger real document (in [tests/data](tests/data/): "Wikimedia") currently fails to detect the problem.

| Good example | Bad example |
|---|---|
| [![](docs/example_good.png)](docs/example_good.png) | [![](docs/example_bad.png)](docs/example_bad.png) |

Main TODOs:
- Input formats:
  - ~PDF support.~
  - URL and better HTML support. Current HTML conversion can leave a lot of noise.
- Handle multiple documents.
- Request user category.
- More granular requests for better quality. See [llm/gemini/Readme.md](src/before_you_sign/llm/gemini/Readme.md).
- Chat for follow-up questions.

## Implementation design sketch

- Modalities: primarily text-only; may add an experimental image modality.
  Because vision LLMs are generally less multi-lingual.  
  Extract text with specialized tools.
  Ideally, format the input as Markdown, preserving tables and basic formatting.
  - Solution for many formats: Pandoc.
    Can convert DOCX, simple HTML and many others into Markdown (various flavors), or to plain text.
    Can not read PDF.
  - Another wide-range solution: [MarkItDown](https://github.com/microsoft/markitdown).
    Can read PDF.
    Not perfect, because it doesn't seem to recognize tables in PDF.
    From limited testing, handles DOCX better than Pandoc.
    (Namely, converts tables to clean Markdown tables instead of embedded HTML.)
    But is worse for HTML, because it doesn't seem to strip the header, footer, etc.
- Prompting strategy: predefined intermediate questions, then summarization.
  - User input request: user category. If it seems important, ask the user to select a description that matches them well or to enter their own.
- Output presentation: first a score and a summary, then a set of spoilers with the intermediate results.
- UI framework: Gradio. Domain-specific and easy to start.
- Cloud LLM: Gemini. Free tier, large context window.  
  Note: data used for training. Should warn in the chat, otherwise not a problem.
- Prompting tactics for cloud LLMs:
  - Include all the document(s) in all prompts, or most.
  - Use a context caching API, and only put static instructions before the data.
  - Upd: see also [llm/gemini/Readme.md](src/before_you_sign/llm/gemini/Readme.md).
- Prompting tactics for local execution on consumer GPUs:
  - Chunking. Store the document(s) in memory in chunks. Preferrably split on document sections.
  - Summarization
    - Initial analysis based on the beginnings of the documents.
    - Prepare a list of questions.
    - Process document by document, chuck by chunk.
    - Put the answers together, summarize.
  - Chat
    - In short: RAG over chunks.
    - Only compute the embeddings after the summary is done.
- Test data:
  - Take a basic T&C and add a bad provision. Make several versions, from absurd to just weird.
  - Take some examples from [TOS;DR](tosdr.org), if their license allows. Adjust their score to my criteria.
- Configuration: API key.

## Usage

### Installation

You can use the standard:
```
pip install .
```

#### For development

Install the Project and Dependency Manager: [PDM](https://pdm-project.org/). I suggest using pipx for that:
```
pipx install pdm
```

Then, prepare the project's virtual env. Run from the project's root:
```
pdm install
```

### Config

It's a YAML file:

```yaml
# API key for a Google Cloud project with Gemini
GOOGLE_API_KEY: '...'

# Path where experiments will be logged in subfolders.
# Its parent must exist.
log_dir: '...'
```

Default location: `<project_root>/local/config.yaml`.

### Launch

After installing the app, run:
```
python -m before_you_sign.app -c path/to/config.yaml
```

Or, for development:
```
pdm dev_serve
```
In this case the config must be in the default location.

## License

While this project is available under the MIT license, it has a transitive dependency on GPL2 software, [Pandoc](https://github.com/jgm/pandoc).
