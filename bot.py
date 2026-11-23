import re
import json
import difflib
from datetime import datetime, timezone, timedelta

LAGOS = timezone(timedelta(hours=1))  # Lagos time (UTC+1)
OPEN_HOUR = 9    # opens 9am
CLOSE_HOUR = 22  # closes 10pm

SWALLOWS = ["pounded yam", "amala"]

# days: None = available every day, otherwise a list of days
# NOTE: prices and kcal below are PLACEHOLDERS. Replace them with your real values.
# kcal is a rough estimate per serving.
MENU = [
    {"name": "Jollof Rice", "price": 2500, "type": "main", "kcal": 550, "tags": "high-carb, spicy", "days": None},
    {"name": "Fried Rice", "price": 2500, "type": "main", "kcal": 600, "tags": "high-carb", "days": None},
    {"name": "Ofada Rice + Sauce", "price": 3000, "type": "main", "kcal": 650, "tags": "spicy, oily", "days": None},

    {"name": "Egusi Soup + swallow", "price": 3500, "type": "main", "kcal": 750, "tags": "filling, high-calorie, high-carb (swallow)", "days": ["Monday", "Wednesday", "Saturday"]},
    {"name": "Ogbono Soup + swallow", "price": 3500, "type": "main", "kcal": 700, "tags": "filling, high-carb (swallow)", "days": ["Tuesday", "Friday"]},
    {"name": "Efo Riro + swallow", "price": 3500, "type": "main", "kcal": 600, "tags": "vegetable-rich, high-carb (swallow)", "days": ["Monday", "Thursday"]},
    {"name": "Afang Soup + swallow", "price": 4000, "type": "main", "kcal": 650, "tags": "vegetable-rich, high-carb (swallow)", "days": ["Wednesday", "Saturday"]},
    {"name": "Oha Soup + swallow", "price": 4000, "type": "main", "kcal": 650, "tags": "vegetable-rich, high-carb (swallow)", "days": ["Tuesday", "Saturday"]},
    {"name": "Banga Soup + Starch", "price": 4000, "type": "main", "kcal": 750, "tags": "rich, high-calorie", "days": ["Thursday", "Sunday"]},
    {"name": "Owo Soup + Starch", "price": 4500, "type": "main", "kcal": 800, "tags": "rich, high-calorie", "days": ["Friday", "Sunday"]},

    {"name": "Moi Moi", "price": 1000, "type": "add-on", "kcal": 200, "tags": "light, plant protein, steamed", "days": None},
    {"name": "Suya portion", "price": 3000, "type": "protein add-on", "kcal": 350, "tags": "high-protein, grilled, spicy", "days": None},
    {"name": "Grilled Chicken", "price": 2000, "type": "protein add-on", "kcal": 300, "tags": "high-protein, grilled", "days": None},
    {"name": "Fried Fish", "price": 2500, "type": "protein add-on", "kcal": 280, "tags": "high-protein, fried, contains fish", "days": None},
    {"name": "Plantain (dodo)", "price": 800, "type": "add-on", "kcal": 200, "tags": "fried, sweet", "days": None},

    {"name": "Chapman", "price": 1500, "type": "drink", "kcal": 150, "tags": "sugary", "days": None},
    {"name": "Zobo", "price": 1000, "type": "drink", "kcal": 80, "tags": "light, sugar level varies", "days": None},
    {"name": "Malt", "price": 800, "type": "drink", "kcal": 150, "tags": "sugary", "days": None},
    {"name": "Water", "price": 300, "type": "drink", "kcal": 0, "tags": "zero-calorie", "days": None},
]

DELIVERY_ZONES = {
    "Victoria Island & Ikoyi": {
        "areas": ["Victoria Island", "Ikoyi", "Oniru", "Lagos Island", "Banana Island"],
        "fee": 2000,
        "eta": "25-45 minutes",
    },
    "Lekki": {
        "areas": ["Lekki", "Lekki Phase 1", "Lekki Phase 2", "Ikate", "Agungi", "Osapa London", "Chevron"],
        "fee": 2500,
        "eta": "35-60 minutes",
    },
    "Ajah": {
        "areas": ["Ajah", "VGC", "Ikota", "Sangotedo", "Awoyaya", "Badore"],
        "fee": 3500,
        "eta": "50-90 minutes",
    },
    "Ikeja": {
        "areas": ["Ikeja", "Allen Avenue", "Opebi", "Maryland", "Ogba", "Alausa", "Adeniyi Jones"],
        "fee": 1500,
        "eta": "20-45 minutes",
    },
    "Mainland Central": {
        "areas": ["Yaba", "Surulere", "Gbagada", "Ilupeju", "Mushin", "Ebute Metta", "Bariga"],
        "fee": 2500,
        "eta": "35-60 minutes",
    },
    "Western Mainland": {
        "areas": ["Festac", "Amuwo-Odofin", "Mile 2", "Isolo", "Apapa", "Okota", "Satellite Town"],
        "fee": 3500,
        "eta": "45-75 minutes",
    },
}

POLICIES = [
    "Hours: 9am-10pm daily",
    "Soups come with one swallow: pounded yam or amala. Banga and Owo come with starch.",
    "Pickup is free, ready in 20 minutes",
    "Payment: transfer or pay on delivery",
    "No refunds after cooking starts. Wrong or missing items are fixed on delivery.",
    "Nothing on the menu is guaranteed allergen-free. Ask staff about allergies.",
    "Contact staff: call or WhatsApp [08125606373]",
]

RULES = """You are Ada, the friendly ordering assistant for Essien's Kitchen in Lagos.
You are given CONTEXT retrieved from the restaurant's knowledge base. It is your only source of truth.

HOW TO TAKE AN ORDER:
1. Greet once. Don't repeat the greeting.
2. If an item or quantity is unclear, ask ONE short question. For soups with swallow, ask which swallow (pounded yam or amala) before adding it.
3. After every change to the order, call calculate_order with the COMPLETE current order (every item and quantity, not only the new one). Put the swallow choice in the item's note field. Then show the order, subtotal and total exactly as the tool returns them.
4. Suggest one add-on or drink at most once.
5. Before finishing, ask delivery or pickup. If delivery, ask for their area.
6. Give a final summary, then ask "Confirm?":
   ORDER SUMMARY
   - item x quantity = price
   Subtotal: N
   Delivery: N
   TOTAL: N
7. After confirmation, thank them and give the estimated time.

RULES:
- NEVER calculate prices, subtotals, delivery fees or totals yourself. Only use numbers returned by calculate_order.
- If calculate_order returns problems, tell the customer in simple words and fix them.
- Use only items, prices and policies in the CONTEXT. Never invent anything.
- Items marked NOT AVAILABLE TODAY cannot be ordered today. Tell the customer which days they are available and offer an available item instead.
- If the customer's area is not in the delivery zones, say we may not deliver there and ask them to confirm with staff.
- If the CONTEXT says the restaurant is CLOSED, say we are closed, say we open at 9am, and do not take orders.
- If the answer is not in the CONTEXT, say "I'm not sure, please confirm with staff."
- If asked for something not on the menu, say so and offer the closest item.
- If asked for the menu, list today's available items grouped by type (mains, add-ons, drinks) with prices.
- If asked about anything unrelated to the restaurant, politely steer back to ordering.
- Keep replies to 1-3 sentences, except the order summary and nutrition suggestions (up to 4 sentences).
- Show money in naira (N).

NUTRITION AND HEALTH:
- Use only the kcal and tags in the CONTEXT. Calories are rough estimates, so say "about".
- If the customer asks for light, healthy, high-protein or similar choices, suggest 1-2 matching items available today and give their kcal.
- If the customer mentions a health condition, do not diagnose or give medical advice. Say you can only share general menu information, suggest items by their tags, and tell them to follow their doctor's advice.
- Never say an item is safe for an allergy. Send allergy questions to staff."""

TOOLS = [{
    "type": "function",
    "function": {
        "name": "calculate_order",
        "description": "Calculates the subtotal, delivery fee and total for the customer's COMPLETE current order. Call it after every change to the order.",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "description": "Every item in the order, using exact menu names. If the same item has different notes, list it as separate entries.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "quantity": {"type": "integer"},
                            "note": {
                                "type": "string",
                                "description": "The swallow for soups with swallow: 'pounded yam' or 'amala'. Leave empty for other items.",
                            },
                        },
                        "required": ["name", "quantity"],
                    },
                },
                "mode": {
                    "type": "string",
                    "enum": ["pickup", "delivery", "undecided"],
                    "description": "How the customer will receive the order",
                },
            },
            "required": ["items", "mode"],
        },
    },
}]


def describe(item):
    return (item["name"] + " - " + str(item["price"]) + " (" + item["type"] + ")"
            + " | about " + str(item["kcal"]) + " kcal | " + item["tags"])


def find_item(name):
    name = name.lower().strip()
    names = {i["name"].lower(): i for i in MENU}
    if name in names:
        return names[name]
    hits = [i for n, i in names.items() if name in n or n in name]
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        return None  # unclear, so the customer must clarify
    close = difflib.get_close_matches(name, list(names), n=1, cutoff=0.6)
    return names[close[0]] if close else None


def find_delivery_zone(user_texts):
    # Check the newest message first, so a changed address wins
    for text in reversed(user_texts):
        text = text.lower()
        for zone, d in DELIVERY_ZONES.items():
            for area in d["areas"]:
                if re.search(r"\b" + re.escape(area.lower()) + r"\b", text):
                    return {"area": area, "zone": zone, "fee": d["fee"], "eta": d["eta"]}
    return None


def calculate_order(items, mode, user_texts):
    today = datetime.now(LAGOS).strftime("%A")
    lines = []
    problems = []
    subtotal = 0

    for it in items:
        item = find_item(str(it.get("name", "")))
        note = str(it.get("note", "") or "").strip()
        try:
            qty = int(it.get("quantity", 1))
        except (TypeError, ValueError):
            qty = 1
        if item is None:
            problems.append("Could not match '" + str(it.get("name", "")) + "' to one menu item. Ask the customer to clarify.")
            continue
        if item["days"] is not None and today not in item["days"]:
            problems.append(item["name"] + " is not available today. Available on: " + ", ".join(item["days"]))
            continue
        if item["name"].endswith("+ swallow") and not any(s in note.lower() for s in SWALLOWS):
            problems.append(item["name"] + ": ask the customer which swallow they want (pounded yam or amala).")
            continue
        if qty < 1:
            continue
        label = item["name"] + (" (" + note + ")" if note else "")
        line_total = item["price"] * qty
        subtotal += line_total
        lines.append(label + " x" + str(qty) + " = " + str(line_total))

    delivery_fee = 0
    eta = None
    if mode == "delivery":
        match = find_delivery_zone(user_texts)
        if match:
            delivery_fee = match["fee"]
            eta = match["eta"]
        else:
            problems.append("Delivery area unknown or not in our zones. Ask the customer for their area.")
    elif mode == "pickup":
        eta = "ready in 20 minutes"

    return json.dumps({
        "lines": lines,
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "total": subtotal + delivery_fee,
        "estimated_time": eta,
        "problems": problems,
    })


def retrieve(query=""):
    now = datetime.now(LAGOS)
    today = now.strftime("%A")
    status = "OPEN" if OPEN_HOUR <= now.hour < CLOSE_HOUR else "CLOSED"
    chunks = ["Today is " + today + ". Current time in Lagos: " + now.strftime("%I:%M %p")
              + ". The restaurant is " + status + " right now."]
    for item in MENU:
        if item["days"] is None or today in item["days"]:
            chunks.append(describe(item))
        else:
            chunks.append("NOT AVAILABLE TODAY: " + item["name"] + " (available on " + ", ".join(item["days"]) + ")")
    for zone, d in DELIVERY_ZONES.items():
        chunks.append("Delivery to " + zone + ": fee " + str(d["fee"]) + ", " + d["eta"]
                      + ". Areas: " + ", ".join(d["areas"]))
    chunks += POLICIES
    return chunks


def answer(history, user_msg, client, model="openai/gpt-oss-20b"):
    user_texts = [m["content"] for m in history if m["role"] == "user"] + [user_msg]
    chunks = retrieve()
    match = find_delivery_zone(user_texts)
    if match:
        chunks.append("Customer delivery area: " + match["area"] + " (zone " + match["zone"]
                      + "), fee " + str(match["fee"]) + ", " + match["eta"])

    system = RULES + "\n\nCONTEXT:\n" + "\n".join("- " + c for c in chunks)
    messages = [{"role": "system", "content": system}] + history[-20:] + [{"role": "user", "content": user_msg}]

    try:
        for _ in range(3):  # allow up to 3 rounds of tool calls
            r = client.chat.completions.create(
                model=model, messages=messages, temperature=0.2, tools=TOOLS
            )
            msg = r.choices[0].message
            if not msg.tool_calls:
                return msg.content, chunks

            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {"id": tc.id, "type": "function",
                     "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in msg.tool_calls
                ],
            })
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except Exception:
                    args = {}
                if tc.function.name == "calculate_order":
                    result = calculate_order(args.get("items", []), args.get("mode", "undecided"), user_texts)
                else:
                    result = json.dumps({"error": "unknown tool"})
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

        return "Sorry, something went wrong. Please try again.", chunks
    except Exception as e:
        print(e)
        return "Sorry, something went wrong. Please try again.", chunks
