import os
import requests
import google.generativeai as genai
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Setup Gemini AI
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    print("✅ Gemini AI enabled")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=data, timeout=10)
    except Exception as e:
        print(f"Error: {e}")

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if update and 'message' in update:
            chat_id = update['message']['chat']['id']
            text = update['message'].get('text', '')
            
            if text:
                # Try AI if API key exists
                if GEMINI_KEY:
                    try:
                        response = model.generate_content(
                            f"You are BizAssist AI, a business assistant. Reply short and helpful. User: {text}"
                        )
                        reply = response.text.strip()
                    except Exception as e:
                        reply = f"AI error: {e}"
                else:
                    reply = f"Add GEMINI_API_KEY to enable AI. You said: {text}"
                
                send_message(chat_id, reply)
        
        return 'ok', 200
    except Exception as e:
        print(f"Error: {e}")
        return 'ok', 200

@app.route('/')
def home():
    return "BizAssist AI Bot is running!"

if __name__ == '__main__':
    # Set webhook
    webhook_url = f"https://businessassitbot-yhj7.onrender.com/{TOKEN}"
    set_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"
    response = requests.post(set_url)
    print(f"Webhook set: {response.json()}")
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=False)
