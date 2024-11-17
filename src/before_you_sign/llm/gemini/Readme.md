# Using Google Gemini

## Capabilities

Long context window, no need for chunking.

Performance on the long context window is optimized for **single-answer retrieval** tasks ([docs](https://ai.google.dev/gemini-api/docs/long-context#long-context-limitations)). It's recommended to split multi-answer retrieval tasks into pieces.

Context Caching makes repeated quieries with the same data faster and cheaper.

## Approach

### For a quick start

Try asking for all intermediate results and the summary in one prompt.

### For optimal quality

When extracting unusual points, ask for a single point each time.
Probably guide the process by intructions like "after *location X*", where the location of the previous point is generated by the model itself.
Potential problem to avoid: infinite loop.

When extracting a list of concerns, separate the generation of the questions and answering each of them.