import os
from neonize.client import NewClient
from neonize.events import ConnectedEv, event

# --- BOT INITIALIZATION ---
# We add a user_agent string to look like a real browser and bypass the 502 error
client = NewClient(
    "whatsapp_session.sqlite3",
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

@client.event(ConnectedEv)
def on_connected(_: NewClient, __: ConnectedEv):
    print("⚡ WhatsApp Client Connected Successfully!")

# --- START UP ---
if __name__ == "__main__":
    print("🚀 Booting up... Watch for a Pairing Code below.")
    
    # This initiates the connection
    client.connect()
    
    # Keeps the bot running
    event.wait()
