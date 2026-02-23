from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Initialize Flask to serve static files (HTML) from the current directory
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enables the HTML file to talk to this Python script

# --- API CLIENT & KNOWLEDGE BASE ---

# Check for API key and initialize the Groq client
if not os.environ.get("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY not found. Please create a .env file and add your key.")
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MENU_ITEMS = {
    "espresso": {"price": "₹120", "desc": "Pure, intense single origin shot"},
    "cappuccino": {"price": "₹160", "desc": "Espresso, steamed milk, microfoam"},
    "hazelnut": {"price": "₹220", "desc": "Rich espresso with hazelnut syrup"},
    "chai": {"price": "₹140", "desc": "Spiced tea with warm milk"},
    "cold brew": {"price": "₹200", "desc": "12-hour steep, served over ice"},
    "smoothie": {"price": "₹280", "desc": "Mixed berries, yogurt, honey"},
    "mojito": {"price": "₹150", "desc": "Fresh mint, lime, soda"},
    "mushroom": {"price": "₹350", "desc": "Sourdough, creamy truffle mushrooms"},
    "avocado": {"price": "₹260", "desc": "Sourdough, smashed avocado, chilli"},
    "fries": {"price": "₹220", "desc": "Crispy fries, cheddar sauce, herbs"},
    "waffle": {"price": "₹240", "desc": "Nutella, strawberries, cream"},
    "custard": {"price": "₹150", "desc": "French crème caramel"},
}

SPECIALS = [
    "Hazelnut Cappuccino (₹220)",
    "Truffle Mushroom Toast (₹350)",
    "Berry Blast Smoothie (₹280)",
    "Caramel Custard (₹150)"
]

# This string formats all your café's data into a single block for the LLM
KNOWLEDGE_BASE = f"""
- Menu Items: {MENU_ITEMS}
- Today's Specials: {", ".join(SPECIALS)}
- Hours: We are open every day from 06:00 AM to 01:00 AM.
- Location: 2nd Floor Rooftop, Pavitra Landmark, Opposite Panchmukhi Hanuman Mandir, Vasna Bhayli Main Road, Vadodara, Gujarat.
- Reservations: You can book a table using the 'Reserve' form on the page or by calling us directly at +91 87588 38722.
- Delivery: Home delivery is coming soon! For now, please visit us for the full experience.
- Contact Phone: +91 87588 38722.
"""

SYSTEM_PROMPT = f"""
You are a friendly and enthusiastic chatbot assistant for 'BrewRaga', a modern rooftop café.
Your goal is to answer customer questions accurately based ONLY on the information provided below.
Do not make up information. If a question cannot be answered from the context, politely say you are not sure and provide the café's phone number.

Keep your answers concise, friendly, and use emojis where appropriate (e.g., ☕, 📍, ⏰).

Here is all the information about BrewRaga:
{KNOWLEDGE_BASE}
"""

# ——— LLM-POWERED LOGIC ENGINE ———
def get_bot_response(user_msg):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ],
            model="llama-3.1-8b-instant",  # Updated to currently supported model
            temperature=0.7,
            max_tokens=150,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return "I'm having a little trouble connecting to my brain right now! 🧠 Please try again in a moment, or call us at +91 87588 38722."

# Serve the HTML file at the root URL
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    user_message = data.get('message', '')
    bot_reply = get_bot_response(user_message)
    return jsonify({"reply": bot_reply})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"☕ BrewRaga Chatbot Server Running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
