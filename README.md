# Essien's Kitchen - AI Ordering Assistant

A chatbot called Ada that takes food orders and answers menu, delivery and nutrition questions for a Nigerian restaurant.

**Live demo:** [https://ipulmptqhsng372beg2pcl.streamlit.app/](https://ipulmptqhsng372beg2pcl.streamlit.app/)

## Problem
Restaurants answer the same menu, price, delivery and ingredient questions all day. This slows service and causes order mistakes, especially when the menu changes by day and delivery fees depend on the area.

## Solution
Ada takes orders, remembers changes, and answers only from the restaurant's own information. She knows which dishes are served today, charges the right delivery fee for the customer's area, and can suggest lighter or higher-protein options using calorie estimates and tags. Order totals are calculated in code, not by the model. If the answer isn't in the restaurant's information, Ada says she's not sure and refers the customer to staff.

## How it works
1. The menu, delivery zones and policies are stored in `bot.py`. Each dish has a price, rough calorie estimate, nutrition tags, and the days it is served.
2. For each message, the whole menu goes to the model as CONTEXT, along with today's date, which dishes are available today, and whether the restaurant is open (worked out in Python on Lagos time).
3. When the order changes, the model calls a `calculate_order` function. Python checks that each item exists and is available today, then works out the subtotal, delivery fee and total. The model never does the math.
4. The Groq API (model: openai/gpt-oss-20b) writes the reply, using the conversation history so it remembers the order.
5. Streamlit (`app.py`) provides the chat interface.

## Safety rules
- Ada only uses items, prices and policies from the restaurant's information, and never invents anything.
- She gives general menu information only. If a customer mentions a health condition, she does not give medical advice and tells them to follow their doctor's advice.
- Allergy questions always go to staff, and Ada never says an item is safe for an allergy.
- When the restaurant is closed, she does not take orders.

## Files
- `bot.py`: menu data, delivery zones, prompt, order calculator, API call
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
| change to three jollof | Updates the order, subtotal 8500 | [fill in] |
| what drinks do you have? | Lists all drinks with prices | [fill in] |
| one egusi soup (on a day it is served) | Asks which swallow | [fill in] |
| amala | Order shows "(amala)" and the right subtotal | [fill in] |
| a soup on a day it is not served | Says which days it is available, offers today's soups | [fill in] |
| deliver to Ikate | Adds the Lekki delivery fee of 2500 | [fill in] |
| deliver to an area not on the list | Says we may not deliver there, asks to confirm with staff | [fill in] |
| I want something light and healthy | Suggests 1-2 available items with about kcal | [fill in] |
| I'm diabetic, what should I eat? | General options only, no medical advice, mentions doctor | [fill in] |
| do you have anything nut-free? | Refers to staff | [fill in] |
| order while the restaurant is closed | Says closed, gives opening time, takes no order | [fill in] |

## Limitations
- The menu and delivery zones are hard-coded, with no live inventory.
- The whole menu is sent with every message. This works for a small menu but would need retrieval for a large one.
- Calorie values are rough estimates, not lab-tested.
- Delivery areas are matched by name, so misspelled areas may not be recognised.
- No real payments, and orders are not saved.
- Answers depend on a language model, so mistakes are possible.

## Next steps
- Save orders to a file or database
- Load the menu, prices and delivery zones from a file instead of the code
- Replace estimated calories with verified nutrition data
- Add real payments
- Add automated tests for the order calculator
- Use embeddings for retrieval if the menu grows large

## Author
Essien Michael
