import os
import os.path
import http.server
import socketserver
import threading
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv, event
from neonize.utils import build_jid

# --- 1. FAKE WEB SERVER ---
def run_fake_server():
    PORT = int(os.environ.get("PORT", 10000))
    Handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"🌐 Fake Web Server active on port {PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"⚠️ Web server error: {e}")

threading.Thread(target=run_fake_server, daemon=True).start()

# --- 2. GOOGLE CONFIGURATION ---
SCOPES = ['https://www.googleapis.com/auth/contacts']
# Ensure your client_secret file name on GitHub matches this EXACTLY
SECRET_FILE = 'client_secret_842710013211-37ha8jgkg0p3hdof8hj7ktmjlkc7sti6.apps.googleusercontent.com.json'

def get_google_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        raise RuntimeError("Google auth failed: missing or expired token.json")
    return build('people', 'v1', credentials=creds)

def save_to_google_contacts(phone_number, first_name="Gain", last_name="Contact"):
    try:
        service = get_google_service()
        service.people().createContact(
            body={
                "names": [{"givenName": first_name, "familyName": last_name}],
                "phoneNumbers": [{"value": phone_number, "type": "mobile"}]
            }
        ).execute()
        return True
    except Exception as e:
        print(f"🟥 [Google Error]: {e}")
        return False

# --- 3. WHATSAPP BOT ENGINE ---
client = NewClient("whatsapp_session.sqlite3")

@client.event(ConnectedEv)
def on_connected(_: NewClient, __: ConnectedEv):
    print("⚡ WhatsApp Client Connected!")

@client.event(MessageEv)
def on_message(client: NewClient, message: MessageEv):
    sender_phone = message.Info.MessageSource.Sender.User
    msg_text = (message.Message.conversation or 
                (message.Message.extendedTextMessage and message.Message.extendedTextMessage.text) or "")
    
    if message.Info.MessageSource.IsFromMe:
        if ".info" in msg_text:
            client.send_message(message.Info.MessageSource.Chat, text="🤖 Bot is Online & Ready")
        return

    if msg_text.strip():
        print(f"📥 Message received from {sender_phone}")
        save_to_google_contacts(sender_phone, "Gain", sender_phone[-4:])

# --- 4. START UP ---
if __name__ == "__main__":
    print("🚀 Booting up WhatsApp Cloud Engine...")
    
    # We initiate the client and wait for the network to handshake
    client.connect()
    
    # This loop keeps the script alive and waiting for QR/Pairing input
    # In cloud logs, if it needs pairing, it will print the code here
    event.wait()
