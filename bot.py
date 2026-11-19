import re

KNOWLEDGE = [
    "Jollof Rice - 2500 (main)",
    "Fried Rice - 2500 (main)",
    "Egusi Soup + Pounded Yam - 3500 (main)",
    "Ofada Rice + Sauce - 3000 (main)",
    "Suya portion - 3000 (protein add-on)",
    "Grilled Chicken - 2000 (protein add-on)",
    "Fried Fish - 2500 (protein add-on)",
    "Plantain (dodo) - 800 (add-on)",
    "Chapman - 1500 (drink)",
    "Zobo - 1000 (drink)",
    "Malt - 800 (drink)",
    "Water - 300 (drink)",
    "Pickup is free, ready in 20 minutes",
    "Payment: transfer or pay on delivery",
    "No refunds after cooking starts. Wrong or missing items are fixed on delivery.",
    "Nothing on the menu is guaranteed allergen-free. Ask staff about allergies.",
]

ALWAYS = [
    "Delivery: 1000 within Lagos, 40-60 minutes",
    "Hours: 9am-10pm daily",
]

RULES = """You are Ada, the friendly ordering assistant for Essien's Kitchen in Lagos.
You are given CONTEXT retrieved from the restaurant's knowledge base. It is your only source of truth.

HOW TO TAKE AN ORDER:
1. Greet once. Don't repeat the greeting.
2. After every change, show the current order and subtotal.
3. If an item or quantity is unclear, ask ONE short question.
4. Suggest one add-on or drink at most once.
5. Before finishing, ask delivery or pickup. If delivery, ask for the address and add the delivery fee.
6. Give a final summary, then ask "Confirm?":
   ORDER SUMMARY
   - item x quantity = price
   Subtotal: N
   Delivery: N
   TOTAL: N
7. After confirmation, thank them and give the estimated time.

RULES:
- Use only items, prices and policies in the CONTEXT. Never invent anything.
- If the answer is not in the CONTEXT, say "I'm not sure, please confirm with staff."
- If asked for something not on the menu, say so and offer the closest item.
- If asked about anything unrelated to the restaurant, politely steer back to ordering.
- Keep replies to 1-3 sentences, except the order summary.
- Show money in naira (N). Do arithmetic carefully."""

def tokens(text):
    return set(re.findall(r"[a-z]+", text.lower()))

def retrieve(query, k=5):
    q = tokens(query)
    scored = [(len(q & tokens(c)), c) for c in KNOWLEDGE]
    scored = [s for s in scored if s[0] > 0]
    scored.sort(key=lambda s: s[0], reverse=True)
    chunks = [c for _, c in scored[:k]]
    for a in ALWAYS:
        if a not in chunks:
            chunks.append(a)
    return chunks

def answer(history, user_msg, client, model="openai/gpt-oss-20b"):
    recent = [m["content"] for m in history if m["role"] == "user"][-2:]
    chunks = retrieve(" ".join(recent + [user_msg]))
    system = RULES + "\n\nCONTEXT:\n" + "\n".join("- " + c for c in chunks)
    messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": user_msg}]
    try:
        r = client.chat.completions.create(model=model, messages=messages)
        return r.choices[0].message.content, chunks
    except Exception:
        return "Sorry, something went wrong. Please try again.", chunks
