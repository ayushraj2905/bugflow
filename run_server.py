import os
import sys
import time
import webbrowser
import threading
import uvicorn

import subprocess

def free_port(port=8000):
    try:
        if sys.platform == "win32":
            output = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True).decode()
            for line in output.strip().split('\n'):
                parts = line.strip().split()
                if len(parts) >= 5 and f":{port}" in parts[1] and ("LISTENING" in parts or "Listen" in parts):
                    pid = parts[-1]
                    if pid.isdigit() and int(pid) != os.getpid():
                        print(f"🧹 Port {port} occupied by PID {pid}. Freeing port automatically...")
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        time.sleep(1)
    except Exception:
        pass

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

    # Automatically free port 8000 if already in use
    free_port(8000)

    # Launch browser in separate thread
    threading.Thread(target=open_browser, daemon=True).start()

    print("=" * 60)
    print("🚀 Starting BugFlow Platform on http://127.0.0.1:8000")
    print("=" * 60)
    
    # Run uvicorn server
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)

