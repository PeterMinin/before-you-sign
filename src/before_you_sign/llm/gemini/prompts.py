SYSTEM_PROMPT = """
You should read the legal document and provide a concise summary
for the end-user considering to accept the terms.
Answer in English.
"""

MAIN_PROMPT = """
First, write the name of the service and a short description of its nature,
such as "a web store for gardening", "a multiplayer online videogame"
or "a dating platform with a focus on video calls".
Then name the document, such as "Terms of Service" or "Privacy Policy".
If a document is not in English, state the language in parentheses.

Then answer these questions:
1. Compared to typical documents of this type, are there any unusual provisions?
   If yes, cite a few of the most unusual ones.
2. What concerns do users generally voice for documents of this type?
   How are these concerns addressed in the document?
3. Does the nature of the service involve any risks for the user? How serious are they?
   How are these risk addressed in the document?

Finish with a general score of user-friendliness of the conditions (not the document itself)
on a scale from A to F and a one-sentence summary.
- "A" means "Very nice, use however you like",
- "B" means "Generally good, with reasonable limitations to keep in mind",
- "C" means "Notable restrictions or inconveniences",
- "D" means "Major restrictions or risks",
- "E" means "Extreme caution required",
- "F" means "Obviously unreasonable terms".
"""

# """
#
# Then the user may ask additional questions. By default, keep the answers concise.
# Include citations from the document if appropriate.
# """
