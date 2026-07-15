import os
import os.path
from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv, event

# --- 1. BOT INITIALIZATION ---
# This looks for the session file. 
# REMEMBER: If the bot is still stuck, make sure 'whatsapp_session.sqlite3' is NOT in your GitHub files.
client = NewClient("whatsapp_session.sqlite3")

@client.event(ConnectedEv)
def on_connected(_: NewClient, __: ConnectedEv):
    print("⚡ WhatsApp Client Connected Successfully!")

# --- 2. START UP ---
if __name__ == "__main__":
    print("🚀 Booting up... Watch for a Pairing Code below.")
    
    # This connects and initiates the pairing sequence
    client.connect()
    
    # The event loop waits for the pairing code or messages
    event.wait()
