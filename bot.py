import os
import os.path
import http.server
import socketserver
import threading
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv, event
from neonize.utils import build_jid

# --- 1. FAKE WEB SERVER (Must start FIRST for Render) ---
def run_fake_server():
    PORT = int(os.environ.get("PORT", 10000))
    Handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"🌐 Fake Web Server running on port {PORT} to keep Render alive")
            httpd.serve_forever()
    except Exception as e:
        print(f"⚠️ Web server notice: {e}")

# Start the fake server immediately in the background
threading.Thread(target=run_fake_server, daemon=True).start()

# --- 2. GOOGLE CONFIGURATION ---
SCOPES = ['https://www.googleapis.com/auth/contacts']
SECRET_FILE = 'client_secret_842710013211-37ha8jgkg0p3hdof8hj7ktmjlkc7sti6.apps.googleusercontent.com.json'

def get_google_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        
        if not creds:
            # NOTE: run_local_server will fail on Render because it is a headless cloud environment.
            # For a permanent cloud fix, a Google Cloud Service Account (.json key) is required.
            raise RuntimeError("Google credentials expired or missing token.json. Cloud server cannot open a browser auth window.")

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
        print(f"🟩 [Google] Successfully saved {first_name} ({phone_number})")
        return True
    except Exception as e:
        print(f"🟥 [Google Error] Could not save contact on cloud: {e}")
        return False

# --- 3. WHATSAPP BOT ENGINE ---
client = NewClient("whatsapp_session.sqlite3")

@client.event(ConnectedEv)
def on_connected(_: NewClient, __: ConnectedEv):
    print("⚡ WhatsApp Client Connected Successfully!")

@client.event(MessageEv)
def on_message(client: NewClient, message: MessageEv):
    sender_jid = message.Info.MessageSource.Sender
    sender_phone = sender_jid.User
    
    msg_text = ""
    if message.Message.conversation:
        msg_text = message.Message.conversation
    elif message.Message.extendedTextMessage and message.Message.extendedTextMessage.text:
        msg_text = message.Message.extendedTextMessage.text
        
    msg_text = msg_text.strip()
    is_from_me = message.Info.MessageSource.IsFromMe
    
    if is_from_me:
        # --- COMMANDS ---
        if msg_text.startswith(".status "):
            status_content = msg_text.replace(".status ", "")
            status_jid = build_jid("status@broadcast")
            client.send_message(status_jid, text=status_content)
            print(f"📢 Status updated to: {status_content}")
            
        elif msg_text == ".info":
            chat_jid = message.Info.MessageSource.Chat
            client.send_message(chat_jid, text="🤖 Bot Status: Active\nPlatform: 100% Free Cloud")
        return

    # --- AUTO CONTACT-GAIN ---
    if msg_text:
        print(f"📥 New message from {sender_phone}: {msg_text}")
        save_to_google_contacts(phone_number=sender_phone, first_name="Gain", last_name=sender_phone[-4:])

# --- 4. START UP ---
if __name__ == "__main__":
    print("🚀 Booting up the WhatsApp Cloud Engine...")
    client.connect()
    event.wait()
