import os
import sys
import time
import webbrowser
import threading
import uvicorn

def open_browser():
    time.sleep(1.5)
    print("Opening BugFlow in your default browser...")
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    # Change working directory to backend
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "backend")
    os.chdir(backend_dir)
    sys.path.insert(0, backend_dir)

    # Launch browser in separate thread
    threading.Thread(target=open_browser, daemon=True).start()

    print("=" * 60)
    print("🚀 Starting BugFlow Platform on http://127.0.0.1:8000")
    print("=" * 60)
    
    # Run uvicorn server
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
