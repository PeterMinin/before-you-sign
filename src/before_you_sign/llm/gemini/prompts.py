SYSTEM_PROMPT = """
You should read the legal document and help the end-user considering to accept the terms.
Answer in English.
"""

METADATA_PROMPT = """
Write a JSON like this, without the comments:
{
   # Full name of the document's language.
   "document_language": "...",

   # Category like "Terms of Service" or "Privacy Policy".
   "document_type": "...",

   # Name of the service.
   "service_name": "...",

   # Short description of its nature,
   # such as "a web store for gardening", "a multiplayer online videogame"
   # or "a dating platform with a focus on video calls".
   "service_nature": "..."
}
"""

INTERMEDIATE_PROMPT_TEMPLATE = """
Document type: {document_type}.
Document language: {document_language}.
Service: {service_nature}.

1. Compared to typical documents of this type, are there any unusual provisions?
   If yes, cite a few of the most unusual ones.
2. What concerns do users generally voice for documents of this type?
   How are these concerns addressed in the document?
3. Does the nature of the service involve any risks for the user? How serious are they?
   How are these risk addressed in the document?
"""

SUMMARY_PROMPT = """
Finish with a general score of how much attention the user should pay to the rules
on a scale from A to F and a one-sentence summary.
- "A" means "Nothing to worry about",
- "B" means "Reasonable limitations to keep in mind",
- "C" means "Notable restrictions or inconveniences",
- "D" means "Major restrictions or risks",
- "E" means "Extreme caution required",
- "F" means "Obviously unreasonable terms".

Reply in JSON:
{
   "score": "A",
   "comment": "..."  # the summary
}
"""

# """
#
# Then the user may ask additional questions. By default, keep the answers concise.
# Include citations from the document if appropriate.
# """
