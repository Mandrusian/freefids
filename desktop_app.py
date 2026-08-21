import webview
import threading
import uvicorn
import time
from server import app

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

if __name__ == '__main__':
    # Start FastAPI backend quietly in a background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Give the backend a brief moment to initialize
    time.sleep(1)

    # Launch native OS window shell pointing to the local app engine
    webview.create_window(
        title='Cairns Airport FIDS Operational Telemetry',
        url='http://127.0.0.1:8000',
        width=1400,
        height=900,
        resizable=True,
        min_size=(900, 600)
    )
    webview.start()
