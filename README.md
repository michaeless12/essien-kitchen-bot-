# Essien's Kitchen - AI Ordering Assistant

A chatbot called Ada that takes food orders and answers menu questions for a restaurant.

**Live demo:** [https://ipulmptqhsng372beg2pcl.streamlit.app/]

## Problem
Restaurants answer the same menu, price and delivery questions all day. This slows service and causes order mistakes.

## Solution
Ada takes orders, remembers changes, shows totals, and answers only from the restaurant's own information. If the answer isn't in that information, she says she's not sure and refers the customer to staff.

## How it works
1. The menu and policies are stored as small chunks in `bot.py`.
2. For each message, simple keyword retrieval finds the most relevant chunks.
3. Only those chunks go into the prompt as CONTEXT.
4. The Groq API (model: openai/gpt-oss-20b) writes the reply, using the conversation history so it remembers the order.
5. Streamlit (`app.py`) provides the chat interface.

## Files
- `bot.py`: knowledge chunks, retrieval, prompt, API call
- `app.py`: Streamlit interface
- `requirements.txt`: dependencies
- `.env.example`: shows the expected key name

## Run it
1. Get a free key at console.groq.com
2. `pip install -r requirements.txt`
3. Set `GROQ_API_KEY` as an environment variable or in `.streamlit/secrets.toml`
4. `streamlit run app.py`

The API key is stored in Streamlit secrets or an environment variable. It is never in the code, and `.gitignore` keeps secret files out of GitHub.

## Tests
| Input | Expected | Result |
|---|---|---|
| two jollof and a zobo | Order with subtotal 6000 | Pass |
| do you sell birthday cakes? | Says not sure, asks to confirm with staff | Pass |
| who is the president of Nigeria? | Steers back to ordering | [fill in] |
| change to three jollof | Updates the order | [fill in] |

## Limitations
- Retrieval uses keyword matching, so it can miss synonyms.
- The menu is hard-coded, with no live inventory.
- No real payments, and orders are not saved.
- Answers depend on a language model, so mistakes are possible.

## Next steps
- Use embeddings and a vector database for retrieval
- Load the menu from a file or database
- Save orders and add payment

## Author
Essien Michael 
