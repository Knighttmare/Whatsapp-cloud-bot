from neonize.client import NewClient
from neonize.events import ConnectedEv, event

# Simple initialization
client = NewClient("whatsapp_session.sqlite3")

@client.event(ConnectedEv)
def on_connected(_: NewClient, __: ConnectedEv):
    print("⚡ WhatsApp Connected!")

if __name__ == "__main__":
    print("🚀 Booting up...")
    client.connect()
    event.wait()
