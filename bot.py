import os
import http.server
import socketserver
import threading
from neonize.client import NewClient
from neonize.events import ConnectedEv, event

# --- 1. WEB SERVER (Satisfies Render's port requirement) ---
def run_fake_server():
    PORT = int(os.environ.get("PORT", 10000))
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 Web server running on port {PORT}")
        httpd.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

# --- 2. WHATSAPP BOT ---
client = NewClient("whatsapp_session.sqlite3")

@client.event(ConnectedEv)
def on_connected(_: NewClient, __: ConnectedEv):
    print("⚡ WhatsApp Client Connected!")

if __name__ == "__main__":
    print("🚀 Booting up... Watch for a Pairing Code below.")
    client.connect()
    event.wait()
