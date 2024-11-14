# Before You Sign

This assistant aims to bring a little more truth into "I have read and understood the Terms and Conditions".

Inspired by the [TOS;DR](tosdr.org) project, powered by LLMs. No guarantees, just a best-effort.

## High-level design

- Usage: just enter the document and get a summary, no initial prompt.
  Optionally, ask follow-up questions.
- Advanced scenario: process a pack of related documents.
- Input formats: plain text, PDF, DOCX, URL, images.
- Multi-lingual: can read languages other than English.
- Web GUI.
- Based on a free API. Later may be extended to a local solution.

## Implementation design sketch

- Modalities: primarily text-only; may add an experimental image modality.
  Because vision LLMs are generally less multi-lingual.  
  Extract text with specialized tools.
  Ideally, format the input as Markdown, preserving tables and basic formatting.
- Prompting strategy: predefined intermediate questions (behind the scenes), then summarization.
- Output presentation: first a score and a summary, then a set of spoilers with the intermediate results.
- UI framework: Gradio. Domain-specific and easy to start.
- Cloud LLM: Gemini. Free tier, large context window.  
  Note: data used for training. Should warn in the chat, otherwise not a problem.
- Prompting tactics for cloud LLMs:
  - Include all the document(s) in all prompts, or most.
  - Use a context caching API, and only put static instructions before the data.
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
